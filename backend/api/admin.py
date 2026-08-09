import os
import sys
import uuid
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel

from admin.auth import check_credentials, require_admin
from storage import document_store, worker_store
from pipeline.ingest import ingest_file

# Import your new question generation script
from generate_questions import generate_questions_for_file

router = APIRouter(prefix="/admin")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class LoginRequest(BaseModel):
    email: str
    password: str

class AddWorkerRequest(BaseModel):
    name: str
    email: str
    phone: str
    department: str
    address: str

@router.post("/workers")
def generate_worker(req: AddWorkerRequest, token: str = Depends(require_admin)):
    """Generates a username + one-time temporary password for a new worker."""
    try:
        credentials = worker_store.generate_worker(
            name=req.name, 
            email=req.email,
            phone=req.phone, 
            department=req.department,
            address=req.address
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return credentials


@router.post("/login")
def login(req: LoginRequest):
    token = check_credentials(req.email, req.password)
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    return {"token": token, "email": req.email, "name": admin_name}


@router.get("/workers")
def list_workers(token: str = Depends(require_admin)):
    return worker_store.list_workers()


@router.delete("/workers/{worker_id}")
def delete_worker(worker_id: str, token: str = Depends(require_admin)):
    worker_store.delete_worker(worker_id)
    return {"deleted": worker_id}


@router.get("/documents")
def list_documents(token: str = Depends(require_admin)):
    return document_store.list_documents()


def process_document(doc_id: str, file_path: str, source_name: str):
    """Background task to ingest files and automatically generate test questions."""
    try:
        print(f"Starting ingestion for {source_name}...")
        
        # 1. Process the file, embed it, and save to Supabase
        page_count = ingest_file(file_path, source_name)
        
        # 2. AUTOMATICALLY generate the questions JSON file
        print(f"Generating question set for {source_name}...")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_questions")
        
        # --- UPDATED: Pass the clean source_name to the generator ---
        json_path = generate_questions_for_file(file_path, source_name=source_name, output_dir=output_dir)
        
        if json_path:
            print(f"Successfully generated questions at: {json_path}")
        else:
            print(f"No questions generated for {source_name}.")
            
        # 3. Mark the document as ready in the admin dashboard
        document_store.update_status(doc_id, "ready", pages=page_count)
        
    except Exception as e:
        print(f"[ingest error] {source_name}: {e}")
        document_store.update_status(doc_id, "failed")


@router.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(require_admin),
):
    # Allowed content types for PDFs, text files, and images
    allowed_types = [
        "application/pdf",
        "text/plain",
        "image/jpeg",
        "image/png"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Only PDF, TXT, PNG, and JPG files are accepted."
        )

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    document_store.add_document(doc_id, file.filename)
    
    # Pass it off to the background task to run the ingestion and question generation
    background_tasks.add_task(process_document, doc_id, file_path, file.filename)

    return {"id": doc_id, "name": file.filename, "status": "processing"}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, token: str = Depends(require_admin)):
    document_store.delete_document(doc_id)
    return {"deleted": doc_id}