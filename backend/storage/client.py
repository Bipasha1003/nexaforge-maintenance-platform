import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in .env")
    return psycopg2.connect(database_url)

def init_schema():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()

def insert_chunks(chunks):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for c in chunks:
                embedding_str = "[" + ",".join(str(x) for x in c["embedding"]) + "]"
                cur.execute(
                    """
                    INSERT INTO chunks (chunk_id, page_number, source, text, char_count, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s::vector)
                    """,
                    (c["chunk_id"], c["page_number"], c["source"], c["text"], c["char_count"], embedding_str)
                )
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_schema()
    print("Schema initialized: pgvector extension enabled, chunks table created.")