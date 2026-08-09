CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);