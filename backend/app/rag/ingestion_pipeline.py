import os
import re
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")

# Initialize embedding model globally
print("Loading embedding model BAAI/bge-base-en-v1.5...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
print("Model loaded.")

def parse_markdown_by_heading(filepath, heading_level="## "):
    """Splits a markdown file by a specific heading level."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by the heading level. We keep the heading text by capturing it or prepending it.
    parts = content.split(heading_level)
    
    chunks = []
    # First part is usually the title/intro
    if parts[0].strip():
        chunks.append({
            "content": parts[0].strip(),
            "heading": "Introduction"
        })
        
    for part in parts[1:]:
        if not part.strip():
            continue
        lines = part.split('\n')
        heading = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        chunk_content = f"{heading_level}{heading}\n{body}"
        chunks.append({
            "content": chunk_content,
            "heading": heading
        })
        
    return chunks

def process_knowledge_base(base_dir="../../knowledge"):
    all_chunks = []
    
    # 1. Process Business Definitions (split by ##)
    def_file = os.path.join(base_dir, "business_definitions", "metrics.md")
    if os.path.exists(def_file):
        chunks = parse_markdown_by_heading(def_file, "## ")
        for c in chunks:
            all_chunks.append({
                "content": c["content"],
                "source": "metrics.md",
                "document_type": "business_definition",
                "domain": "finance",
                "table_name": None
            })

    # 2. Process Business Rules (split by ##)
    rule_file = os.path.join(base_dir, "business_rules", "returns_and_cancellations.md")
    if os.path.exists(rule_file):
        chunks = parse_markdown_by_heading(rule_file, "## ")
        for c in chunks:
            all_chunks.append({
                "content": c["content"],
                "source": "returns_and_cancellations.md",
                "document_type": "business_rule",
                "domain": "operations",
                "table_name": None
            })

    # 3. Process Schema (split tables by ###, relationships by ##)
    schema_file = os.path.join(base_dir, "schema", "table_relationships.md")
    if os.path.exists(schema_file):
        with open(schema_file, 'r') as f:
            content = f.read()
        
        # Split into main sections: Tables vs Relationships
        sections = content.split("## ")
        for section in sections:
            if section.startswith("Tables"):
                # Sub-split by ###
                tables = section.split("### ")
                for t in tables[1:]:
                    lines = t.split('\n')
                    t_name = lines[0].strip().split(' ')[-1] # e.g., '1. regions' -> 'regions'
                    t_content = "### " + t.strip()
                    all_chunks.append({
                        "content": t_content,
                        "source": "table_relationships.md",
                        "document_type": "database_schema",
                        "domain": "database",
                        "table_name": t_name
                    })
            elif section.startswith("Key Relationships"):
                all_chunks.append({
                    "content": "## " + section.strip(),
                    "source": "table_relationships.md",
                    "document_type": "database_relationships",
                    "domain": "database",
                    "table_name": None
                })
                
    return all_chunks

def ingest_to_postgres():
    # Execute chunking
    base_dir = os.path.join(os.path.dirname(__file__), "../../../knowledge")
    chunks = process_knowledge_base(base_dir)
    print(f"Generated {len(chunks)} structure-aware chunks.")

    # Generate Embeddings
    print("Generating embeddings...")
    texts = [c["content"] for c in chunks]
    
    # BGE requires "Represent this sentence for searching relevant passages: " for query, but for documents we just encode as is.
    embeddings = embedder.encode(texts, normalize_embeddings=True)
    print("Embeddings generated.")

    # Insert into PostgreSQL
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Clear existing knowledge chunks to avoid duplicates during dev
        cursor.execute("TRUNCATE TABLE knowledge_chunks RESTART IDENTITY;")
        
        for i, chunk in enumerate(chunks):
            embedding_list = embeddings[i].tolist()
            metadata = {
                "source": chunk["source"],
                "document_type": chunk["document_type"],
                "domain": chunk["domain"],
                "table_name": chunk["table_name"]
            }
            
            cursor.execute("""
                INSERT INTO knowledge_chunks (content, embedding, metadata, source, document_type, domain, table_name)
                VALUES (%s, %s::vector, %s, %s, %s, %s, %s)
            """, (
                chunk["content"],
                embedding_list,
                psycopg2.extras.Json(metadata),
                chunk["source"],
                chunk["document_type"],
                chunk["domain"],
                chunk["table_name"]
            ))
        print("Successfully inserted all chunks into pgvector.")
    except Exception as e:
        print(f"Error inserting chunks: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    ingest_to_postgres()
