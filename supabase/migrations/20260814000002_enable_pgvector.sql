-- Enable pgvector and create the knowledge chunks table

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768), -- 768 dimensions for BAAI/bge-base-en-v1.5
    metadata JSONB DEFAULT '{}'::jsonb,
    source VARCHAR(255),
    document_type VARCHAR(100),
    domain VARCHAR(100),
    table_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
