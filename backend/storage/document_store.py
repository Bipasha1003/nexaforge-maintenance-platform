import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def _get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def list_documents():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id::text AS id, name, status, pages, TO_CHAR(uploaded_at, 'YYYY-MM-DD') as uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC;
        """
    )
    docs = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(d) for d in docs]

def add_document(doc_id, name):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO documents (id, name, status)
        VALUES (%s, %s, 'processing');
        """,
        (doc_id, name),
    )
    conn.commit()
    cur.close()
    conn.close()

def update_status(doc_id, status, pages=None):
    conn = _get_connection()
    cur = conn.cursor()
    if pages is not None:
        cur.execute(
            "UPDATE documents SET status = %s, pages = %s WHERE id = %s;",
            (status, pages, doc_id),
        )
    else:
        cur.execute(
            "UPDATE documents SET status = %s WHERE id = %s;",
            (status, doc_id),
        )
    conn.commit()
    cur.close()
    conn.close()

def delete_document(doc_id):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM documents WHERE id = %s;", (doc_id,))
    doc = cur.fetchone()
    
    if doc:
        source_name = doc["name"]
        cur.execute("DELETE FROM chunks WHERE source = %s;", (source_name,))
        cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
        conn.commit()
        
    cur.close()
    conn.close()