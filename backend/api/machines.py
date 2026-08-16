import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from storage import machine_store

# NOTE — guessed import: I haven't seen backend/admin/auth.py, so I don't
# know the real dependency name for "require an admin token." This mirrors
# require_worker's shape from auth/worker_auth.py. If your admin auth
# function is named differently (get_current_admin, verify_admin, etc.),
# this is the one line to fix:
from admin.auth import require_admin

router = APIRouter()


class MachineCreateRequest(BaseModel):
    name: str
    type: str
    status: str = "operational"
    next_maintenance: str = "No task scheduled yet"
    next_maintenance_due: str = "No date set"


@router.get("/machines")
def get_machines():
    """Public — both the admin console and the worker dashboard read this,
    no token required."""
    return machine_store.list_machines()


@router.post("/machines")
def add_machine(req: MachineCreateRequest, admin: dict = Depends(require_admin)):
    if req.status not in ("operational", "warning", "critical"):
        raise HTTPException(status_code=400, detail="Invalid status.")
    return machine_store.create_machine(
        name=req.name.strip(),
        type_=req.type.strip(),
        status=req.status,
        next_maintenance=req.next_maintenance.strip(),
        next_maintenance_due=req.next_maintenance_due.strip(),
    )


@router.delete("/machines/{machine_id}")
def remove_machine(machine_id: str, admin: dict = Depends(require_admin)):
    machine_store.delete_machine(machine_id)
    return {"deleted": True}