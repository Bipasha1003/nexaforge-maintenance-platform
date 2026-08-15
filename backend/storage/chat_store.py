import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def _get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_history(user_id: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, text, sources, tool FROM chat_history WHERE user_id = %s ORDER BY created_at ASC;",
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    history = []
    for row in rows:
        r_dict = dict(row)
        r_dict["sources"] = r_dict["sources"] if r_dict["sources"] else []
        
        # THE TRICK: If the database says 'admin', tell the AI and frontend it was 'user'
        if r_dict["role"] == "admin":
            r_dict["role"] = "user"
            
        history.append(r_dict)
        
    return history

def save_message(user_id: str, role: str, text: str, sources=None, tool=None):
    conn = _get_connection()
    cur = conn.cursor()
    sources_json = json.dumps(sources) if sources else "[]"
    cur.execute(
        """
        INSERT INTO chat_history (user_id, role, text, sources, tool)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (user_id, role, text, sources_json, tool)
    )
    conn.commit()
    cur.close()
    conn.close()

def clear_history(user_id: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history WHERE user_id = %s;", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# --- ADD THE NEW FIX FUNCTION RIGHT HERE AT THE BOTTOM ---
def update_user_id(old_id: str, new_id: str):
    """Migrates all chat history from an old user_id/username to a new one."""
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE chat_history SET user_id = %s WHERE user_id = %s;",
        (new_id, old_id)
    )
    conn.commit()
    cur.close()
    conn.close()