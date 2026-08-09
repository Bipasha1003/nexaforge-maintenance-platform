import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth.worker_auth import login_worker, require_worker
from storage import worker_store

router = APIRouter(prefix="/worker")

class WorkerLoginRequest(BaseModel):
    identifier: str  # username or email
    password: str

# Added username to the update request model
class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    username: str | None = None 
    phone: str | None = None
    department: str | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
def worker_login(req: WorkerLoginRequest):
    token, worker = login_worker(req.identifier, req.password)
    return {"token": token, **worker}

@router.get("/me")
def worker_me(worker: dict = Depends(require_worker)):
    full = worker_store.get_worker(worker["id"])
    if not full:
        raise HTTPException(status_code=404, detail="Worker not found.")
    return full

@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, worker: dict = Depends(require_worker)):
    # Pass the username down to your database storage file
    worker_store.update_profile(
        worker["id"], 
        name=req.name, 
        username=req.username,
        phone=req.phone, 
        department=req.department
    )
    return worker_store.get_worker(worker["id"])

@router.post("/change-password")
def change_password(req: ChangePasswordRequest, worker: dict = Depends(require_worker)):
    if len(req.new_password) < 4:
        raise HTTPException(status_code=400, detail="New password must be at least 4 characters.")
    try:
        worker_store.change_password(worker["id"], req.current_password, req.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"changed": True}