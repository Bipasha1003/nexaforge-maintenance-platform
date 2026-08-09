import os
import re
import uuid
import hashlib
import secrets
import string
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def _get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _base_username(name, email):
    base = re.sub(r"[^a-z0-9]", "", email.split("@")[0].lower())
    if not base:
        base = re.sub(r"[^a-z0-9]", "", name.lower()) or "worker"
    return base


def _unique_username(cur, base):
    candidate = base
    suffix = 1
    while True:
        cur.execute("SELECT 1 FROM workers WHERE username = %s;", (candidate,))
        if not cur.fetchone():
            return candidate
        suffix += 1
        candidate = f"{base}{suffix}"


def list_workers():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id::text, employee_no, name, email, username, must_change_password, phone, department, address
        FROM workers ORDER BY created_at DESC;
        """
    )
    workers = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(w) for w in workers]


def generate_worker(name, email, phone=None, department=None, address=None):
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM workers WHERE LOWER(email) = LOWER(%s);", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise ValueError("A worker with this email already exists.")

    username = _unique_username(cur, _base_username(name, email))
    temp_password = _generate_temp_password()
    salt = secrets.token_hex(8)
    password_hash = _hash_password(temp_password, salt)
    worker_id = str(uuid.uuid4())

    cur.execute(
        """
        INSERT INTO workers (id, name, email, username, salt, password_hash, must_change_password, phone, department, address)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s, %s, %s)
        RETURNING employee_no;
        """,
        (worker_id, name, email, username, salt, password_hash, phone, department, address),
    )
    employee_no = cur.fetchone()["employee_no"]
    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": worker_id,
        "employee_no": employee_no,
        "employee_code": f"W-{employee_no:04d}",
        "name": name,
        "email": email,
        "username": username,
        "temp_password": temp_password,
    }


def delete_worker(worker_id):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM workers WHERE id = %s;", (worker_id,))
    conn.commit()
    cur.close()
    conn.close()


def verify_worker(identifier, password):
    """identifier can be an employee code (e.g., W-0002), a username, or an email."""
    conn = _get_connection()
    cur = conn.cursor()
    
    cur.execute(
        """
        SELECT id::text, employee_no, name, email, username, salt, password_hash, must_change_password
        FROM workers 
        WHERE LOWER(email) = LOWER(%s) 
           OR LOWER(username) = LOWER(%s)
           OR LOWER('W-' || LPAD(employee_no::text, 4, '0')) = LOWER(%s);
        """,
        (identifier, identifier, identifier),
    )
    worker = cur.fetchone()
    cur.close()
    conn.close()

    if worker and _hash_password(password, worker["salt"]) == worker["password_hash"]:
        return {
            "id": worker["id"],
            "employee_no": worker["employee_no"],
            "employee_code": f"W-{worker['employee_no']:04d}",
            "name": worker["name"],
            "email": worker["email"],
            "username": worker["username"],
            "must_change_password": worker["must_change_password"],
        }
    return None


def get_worker(worker_id):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id::text, employee_no, name, email, username, must_change_password, phone, department, address
        FROM workers WHERE id = %s;
        """,
        (worker_id,),
    )
    worker = cur.fetchone()
    cur.close()
    conn.close()
    if not worker:
        return None
    worker = dict(worker)
    worker["employee_code"] = f"W-{worker['employee_no']:04d}"
    return worker


def update_profile(worker_id, name=None, username=None, phone=None, department=None):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE workers
        SET name = COALESCE(%s, name),
            username = COALESCE(%s, username),
            phone = COALESCE(%s, phone),
            department = COALESCE(%s, department)
        WHERE id = %s;
        """,
        (name, username, phone, department, worker_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def change_password(worker_id, current_password, new_password):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT salt, password_hash FROM workers WHERE id = %s;", (worker_id,))
    row = cur.fetchone()

    if not row or _hash_password(current_password, row["salt"]) != row["password_hash"]:
        cur.close()
        conn.close()
        raise ValueError("Current password is incorrect.")

    new_salt = secrets.token_hex(8)
    new_hash = _hash_password(new_password, new_salt)
    cur.execute(
        """
        UPDATE workers
        SET salt = %s, password_hash = %s, must_change_password = FALSE
        WHERE id = %s;
        """,
        (new_salt, new_hash, worker_id),
    )
    conn.commit()
    cur.close()
    conn.close()