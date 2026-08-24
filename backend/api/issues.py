import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends
from storage import issue_store
from admin.auth import require_admin

router = APIRouter()

@router.get("/issues")
def get_issues():
    """Public — both the Worker and Admin dashboards read this to show
    the real Maintenance Log."""
    return issue_store.list_issues()

@router.post("/issues/{issue_id}/resolve")
def resolve_issue(issue_id: str, admin: dict = Depends(require_admin)):
    """Admin-only — mark a logged issue as resolved."""
    issue_store.resolve_issue(issue_id)
    return {"resolved": issue_id}