-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create chunks table for vector storage
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    tokens_count INTEGER NOT NULL,
    embedding vector(384),  -- FRIDA embedding size
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create entities cache table
CREATE TABLE IF NOT EXISTS entities_cache (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    embedding vector(384),
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS entities_embedding_idx ON entities_cache 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
