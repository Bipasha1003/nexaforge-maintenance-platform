import os
import sys
import secrets
from fastapi import Header, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import worker_store

_active_worker_tokens = {}


def login_worker(identifier: str, password: str):
    worker = worker_store.verify_worker(identifier, password)
    if not worker:
        # The error message is now fixed here!
        raise HTTPException(status_code=401, detail="Incorrect Worker ID, email, or password.")

    token = secrets.token_hex(16)
    _active_worker_tokens[token] = worker
    return token, worker


def require_worker(authorization: str = Header(None)):
    """Returns the logged-in worker's info dict."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session token.")

    token = authorization.removeprefix("Bearer ").strip()
    worker = _active_worker_tokens.get(token)
    if not worker:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return worker