import os
import secrets
from fastapi import Header, HTTPException

# The one admin login lives in backend/.env, never in frontend code.
# Add these two lines to your .env file:
#   ADMIN_EMAIL=you@example.com
#   ADMIN_PASSWORD=choose-something-here
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Tokens live in memory only (a plain Python set). This is fine for a
# single-instance dev/demo project — logging in again after a server
# restart is expected. A real production app would use JWTs or a
# database-backed session table instead.
_active_tokens = set()


def check_credentials(email: str, password: str) -> str:
    """Returns a new token if email + password are correct, else raises 401."""
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_EMAIL / ADMIN_PASSWORD are not set in the backend .env file.",
        )
    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = secrets.token_hex(16)
    _active_tokens.add(token)
    return token


def require_admin(authorization: str = Header(None)):
    """FastAPI dependency: attach to any route that needs a logged-in admin."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token.")

    token = authorization.removeprefix("Bearer ").strip()
    if token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired admin session.")

    return token