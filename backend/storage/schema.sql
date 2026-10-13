-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Document Chunks Table (Embeddings & Content)
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Document Registry
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing', -- 'processing', 'ready', 'failed'
    pages INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Worker Accounts Table
CREATE TABLE IF NOT EXISTS workers (
    id UUID PRIMARY KEY,
    employee_no SERIAL UNIQUE,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    must_change_password BOOLEAN DEFAULT TRUE,
    phone TEXT,
    department TEXT,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Equipment Fleet Table
CREATE TABLE IF NOT EXISTS machines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'operational', -- 'operational', 'warning', 'critical'
    next_maintenance TEXT DEFAULT 'No task scheduled yet',
    next_maintenance_due TEXT DEFAULT 'No date set',
    open_issues INTEGER DEFAULT 0,
    last_check_in TEXT DEFAULT 'Just added',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Floor Maintenance Issues Table
CREATE TABLE IF NOT EXISTS issues (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    issue_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open', -- 'open', 'resolved'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- 7. Chat History Table (Attributed Multi-User Logs)
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user', 'admin', 'bot'
    text TEXT NOT NULL,
    sources JSONB DEFAULT '[]'::jsonb,
    tool TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Auto-Generated Evaluation Questions
CREATE TABLE IF NOT EXISTS generated_questions (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    question TEXT NOT NULL,
    expected_page INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);