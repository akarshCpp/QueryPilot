import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")

print("Loading embedding model...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
print("Loading reranker model...")
reranker = CrossEncoder("BAAI/bge-reranker-base")
print("Models loaded.")

def vector_search(query_embedding, top_k=20):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # <=>: Cosine distance
        cursor.execute("""
            SELECT id, content, metadata, source, document_type, domain, table_name,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_embedding, query_embedding, top_k))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def keyword_search(query_text, top_k=20):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Convert plain text to tsquery. websearch_to_tsquery is great for natural language.
        cursor.execute("""
            SELECT id, content, metadata, source, document_type, domain, table_name,
                   ts_rank(fts, websearch_to_tsquery('english', %s)) AS rank
            FROM knowledge_chunks
            WHERE fts @@ websearch_to_tsquery('english', %s)
            ORDER BY rank DESC
            LIMIT %s;
        """, (query_text, query_text, top_k))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def reciprocal_rank_fusion(vector_results, keyword_results, k=60):
    # k is the constant used in RRF formula (typically 60)
    scores = {}
    docs = {}
    
    # Process vector results
    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        docs[doc_id] = doc
        scores[doc_id] = 1.0 / (k + rank + 1)
        
    # Process keyword results
    for rank, doc in enumerate(keyword_results):
        doc_id = doc["id"]
        if doc_id not in docs:
            docs[doc_id] = doc
            scores[doc_id] = 0
        scores[doc_id] += 1.0 / (k + rank + 1)
        
    # Sort by RRF score
    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    return [docs[doc_id] for doc_id, score in sorted_results]

def cross_encoder_rerank(query, candidates, top_k=5):
    if not candidates:
        return []
        
    pairs = [[query, doc["content"]] for doc in candidates]
    scores = reranker.predict(pairs)
    
    # Attach scores to candidates
    for i, doc in enumerate(candidates):
        doc["rerank_score"] = float(scores[i])
        
    # Sort by reranker score
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    
    return candidates[:top_k]

def search_knowledge_base(query, top_k=5):
    """Full Hybrid RAG Pipeline"""
    # 1. Generate query embedding (BGE format requires instruction for query)
    instruction = "Represent this sentence for searching relevant passages: "
    query_embedding = embedder.encode(instruction + query, normalize_embeddings=True).tolist()
    
    # 2. Parallel Search (Simulated serially here, could use asyncpg for real parallel)
    v_results = vector_search(query_embedding, top_k=20)
    k_results = keyword_search(query, top_k=20)
    
    # 3. Reciprocal Rank Fusion
    rrf_results = reciprocal_rank_fusion(v_results, k_results, k=60)
    
    # 4. Cross-Encoder Reranking
    final_results = cross_encoder_rerank(query, rrf_results, top_k=top_k)
    
    return final_results

if __name__ == "__main__":
    # Simple test
    query = "What happens if a customer cancels an order?"
    print(f"Searching for: {query}")
    results = search_knowledge_base(query, top_k=3)
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {r.get('rerank_score', 0):.4f}) ---")
        print(f"Source: {r['source']} ({r['document_type']})")
        print(r["content"])
