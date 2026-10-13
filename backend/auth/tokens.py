"""Signed login tokens that survive server restarts (no extra packages needed).
 
A token is  <base64 payload>.<HMAC-SHA256 signature>. Anyone can read the
payload, but nobody can change it without the secret, so never put
passwords in it.
"""
import base64
import hashlib
import hmac
import json
import os
import time
 
from fastapi import HTTPException
 
TOKEN_TTL_SECONDS = 7 * 24 * 3600  # logins last 7 days
 
 
def _secret() -> bytes:
    # Set JWT_SECRET on Render. Falls back to ADMIN_PASSWORD so a missing
    # variable doesn't crash the server, but a dedicated secret is better.
    secret = os.getenv("JWT_SECRET") or os.getenv("ADMIN_PASSWORD")
    if not secret:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET is not set in the backend environment variables.",
        )
    return secret.encode()
 
 
def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
 
 
def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
 
 
def _sign(raw: str) -> str:
    return _b64(hmac.new(_secret(), raw.encode(), hashlib.sha256).digest())
 
 
def create_token(payload: dict, ttl: int = TOKEN_TTL_SECONDS) -> str:
    body = dict(payload)
    body["exp"] = int(time.time()) + ttl
    raw = _b64(json.dumps(body, default=str).encode())
    return f"{raw}.{_sign(raw)}"
 
 
def read_token(token: str):
    """Returns the payload dict, or None if the token is forged or expired."""
    try:
        raw, sig = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(sig, _sign(raw)):
        return None
    try:
        body = json.loads(_unb64(raw))
    except Exception:
        return None
    if body.get("exp", 0) < time.time():
        return None
    return body