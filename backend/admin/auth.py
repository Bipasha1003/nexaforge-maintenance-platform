import os
import sys
from fastapi import Header, HTTPException
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.tokens import create_token, read_token
 
# The one admin login lives in backend/.env (and in Render's environment
# variables when deployed), never in frontend code:
#   ADMIN_EMAIL=you@example.com
#   ADMIN_PASSWORD=choose-something-here
#   JWT_SECRET=a-long-random-string
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
 
 
def check_credentials(email: str, password: str) -> str:
    """Returns a signed token if email + password are correct, else raises 401."""
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_EMAIL / ADMIN_PASSWORD are not set in the backend environment.",
        )
    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
 
    return create_token({"role": "admin", "email": email})
 
 
def require_admin(authorization: str = Header(None)):
    """FastAPI dependency: attach to any route that needs a logged-in admin."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token.")
 
    token = authorization.removeprefix("Bearer ").strip()
    body = read_token(token)
    if not body or body.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Invalid or expired admin session.")
 
    return token
 