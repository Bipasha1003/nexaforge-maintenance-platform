import os
import re
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def _get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{slug}-{int(time.time() * 1000)}"


def list_machines():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, type, status, next_maintenance, "
        "next_maintenance_due, open_issues, last_check_in "
        "FROM machines ORDER BY created_at ASC;"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


def create_machine(name: str, type_: str, status: str = "operational",
                    next_maintenance: str = "No task scheduled yet",
                    next_maintenance_due: str = "No date set"):
    machine_id = _slugify(name)
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO machines (id, name, type, status, next_maintenance,
                               next_maintenance_due, open_issues, last_check_in)
        VALUES (%s, %s, %s, %s, %s, %s, 0, 'Just added')
        RETURNING id, name, type, status, next_maintenance,
                  next_maintenance_due, open_issues, last_check_in;
        """,
        (machine_id, name, type_, status, next_maintenance, next_maintenance_due),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return dict(row)


def delete_machine(machine_id: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM machines WHERE id = %s;", (machine_id,))
    conn.commit()
    cur.close()
    conn.close()