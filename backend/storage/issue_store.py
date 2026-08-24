import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def _get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def create_issue(user_id: str, issue_text: str):
    """Saves a newly reported problem so it actually shows up on the
    Worker Dashboard's Maintenance Log, instead of just being printed
    to the server console and lost."""
    conn = _get_connection()
    cur = conn.cursor()
    issue_id = str(uuid.uuid4())
    cur.execute(
        """
        INSERT INTO issues (id, user_id, issue_text, status)
        VALUES (%s, %s, %s, 'open')
        RETURNING id::text, user_id, issue_text, status,
                  TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as created_at;
        """,
        (issue_id, user_id, issue_text),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return dict(row)


def list_issues():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id::text, user_id, issue_text, status,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI') as created_at
        FROM issues ORDER BY created_at DESC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def resolve_issue(issue_id: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE issues SET status = 'resolved' WHERE id = %s;", (issue_id,))
    conn.commit()
    cur.close()
    conn.close()