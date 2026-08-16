import os
import sys
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import document_store

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

@router.get("/documents")
def get_public_documents():
    """Public endpoint for workers and admins to view available manuals."""
    return document_store.list_documents()

@router.get("/documents/{identifier}/download")
def download_document(identifier: str):
    """
    Downloads the file by matching either:
    1. The doc ID (UUID)
    2. The exact document name
    """
    docs = document_store.list_documents()
    
    # 1. Match by ID or Name in the database
    target_doc = next(
        (d for d in docs if str(d.get("id")) == identifier or d.get("name") == identifier),
        None
    )
    
    filename_to_find = target_doc["name"] if target_doc else identifier
    doc_id = target_doc.get("id") if target_doc else identifier

    # 2. Check the uploads directory for exact name, prefixed name, or raw filename
    possible_paths = [
        os.path.join(UPLOAD_DIR, f"{doc_id}_{filename_to_find}"),
        os.path.join(UPLOAD_DIR, filename_to_find),
    ]

    # Also search uploads folder for any file ending with the filename
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith(f"_{filename_to_find}") or f == filename_to_find:
                possible_paths.append(os.path.join(UPLOAD_DIR, f))

    actual_file_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not actual_file_path:
        raise HTTPException(
            status_code=404, 
            detail=f"File '{filename_to_find}' not found on server disk in uploads/"
        )

    # 3. Trigger native file download
    return FileResponse(
        path=actual_file_path, 
        filename=filename_to_find, 
        media_type="application/octet-stream"
    )