import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from storage import document_store

router = APIRouter()

@router.get("/documents")
def public_documents():
    """Public, read-only — just names/status/page counts, nothing sensitive."""
    docs = document_store.list_documents()
    return [{"name": d["name"], "status": d["status"], "pages": d["pages"]} for d in docs]