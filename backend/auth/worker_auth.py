import os
import sys
from fastapi import Header, HTTPException
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import worker_store
from auth.tokens import create_token, read_token
 
 
def _public_worker(worker) -> dict:
    """Token contents are readable by the client, so never include password data."""
    secret_keys = {"password", "temp_password", "salt"}
    return {
        k: v for k, v in dict(worker).items()
        if k.lower() not in secret_keys and "hash" not in k.lower()
    }
 
 
def login_worker(identifier: str, password: str):
    worker = worker_store.verify_worker(identifier, password)
    if not worker:
        raise HTTPException(status_code=401, detail="Incorrect Worker ID, email, or password.")
 
    safe = _public_worker(worker)
    token = create_token({"role": "worker", "worker": safe})
    return token, worker
 
 
def require_worker(authorization: str = Header(None)):
    """Returns the logged-in worker's info dict."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session token.")
 
    token = authorization.removeprefix("Bearer ").strip()
    body = read_token(token)
    if not body or body.get("role") != "worker":
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
 
    return body["worker"]