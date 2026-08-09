import os
import sys
import psycopg2
import fitz  # PyMuPDF for image extraction
import uuid
import io    # Needed to read image bytes into PIL
from dotenv import load_dotenv
from supabase import create_client, Client
from PIL import Image
import pytesseract

# Tell pytesseract exactly where the Windows executable is
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from splitter import chunk_document
from vectorizer import embed_chunks

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Set up Supabase storage client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def store_chunks(chunks):
    """Inserts embedded chunks into the real `chunks` table, including image_url."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for c in chunks:
        image_url = c.get("image_url", None)
        
        cur.execute(
            """
            INSERT INTO chunks (chunk_id, page_number, source, text, char_count, embedding, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                c["chunk_id"], 
                c["page_number"], 
                c["source"], 
                c["text"], 
                c["char_count"], 
                c["embedding"],
                image_url
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def extract_and_upload_images(file_path, source_name):
    """Scans the PDF for images, runs OCR on them, uploads to Supabase, and maps page numbers."""
    page_image_map = {}
    pdf_file = fitz.open(file_path)
    
    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]
        image_list = page.get_images(full=True)
        
        if image_list:
            print(f"Page {page_index + 1}: Found {len(image_list)} images. Extracting and running OCR...")
            try:
                xref = image_list[0][0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Run OCR directly on the diagram/image extracted from the PDF
                img_for_ocr = Image.open(io.BytesIO(image_bytes))
                extracted_text = pytesseract.image_to_string(img_for_ocr).strip()
                
                # Unique filename generation to avoid collision
                image_filename = f"{source_name}_page_{page_index + 1}_{uuid.uuid4().hex[:8]}.{image_ext}"
                
                # Upload to Supabase Bucket
                supabase.storage.from_("manual-images").upload(
                    file=image_bytes,
                    path=image_filename,
                    file_options={"content-type": f"image/{image_ext}"}
                )
                
                # Retrieve public URL
                public_url = supabase.storage.from_("manual-images").get_public_url(image_filename)
                
                # Save BOTH the image URL and the text extracted from the image
                page_image_map[page_index + 1] = {
                    "url": public_url,
                    "text": extracted_text
                }
                print(f"Successfully uploaded image and extracted diagram text for page {page_index + 1}")
                
            except Exception as e:
                print(f"ERROR processing image on page {page_index + 1}: {e}")
            
    return page_image_map


def ingest_file(file_path, source_name):
    """Handles PDFs, Text files, and Images (OCR)."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        # Standard PDF processing
        chunks = chunk_document(file_path, source_name=source_name)
        if not chunks:
            raise ValueError("No extractable text found in this PDF.")
            
        page_image_map = extract_and_upload_images(file_path, source_name)
        
        for c in chunks:
            p_num = c["page_number"]
            if p_num in page_image_map:
                c["image_url"] = page_image_map[p_num]["url"]
                img_text = page_image_map[p_num]["text"]
                
                # Stitch the diagram text directly into the paragraph chunk
                if img_text:
                    c["text"] += f"\n\n[Text Extracted From Image Diagram on Page {p_num}]:\n{img_text}"
                    c["char_count"] = len(c["text"]) # Update character count
            else:
                c["image_url"] = None

    elif ext == ".txt":
        # Standard Text processing with context enrichment
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        text = f"Source Document Name: {source_name}\n\n{raw_text}"
        
        chunks = [{
            "chunk_id": 0, 
            "page_number": 1, 
            "source": source_name, "text": text, 
            "char_count": len(text), "image_url": None
        }]

    elif ext in [".png", ".jpg", ".jpeg"]:
        # OCR for standalone handwritten/scanned images with context enrichment
        image = Image.open(file_path)
        raw_text = pytesseract.image_to_string(image)
        if not raw_text.strip():
            raw_text = "[Image with no recognizable text]"
            
        # Enrich the text with context so the AI vector search can easily find it
        text = f"Source Image File Name: {source_name}\n"
        text += f"Document Type: Diagram / Flowchart / Image\n"
        text += f"--- Content Extracted via OCR ---\n{raw_text}\n--------------------------------"
            
        with open(file_path, "rb") as f:
            image_bytes = f.read()
            
        image_filename = f"{source_name}_{uuid.uuid4().hex[:8]}{ext}"
        try:
            supabase.storage.from_("manual-images").upload(
                file=image_bytes,
                path=image_filename,
                file_options={"content-type": f"image/{ext.replace('.', '')}"}
            )
            public_url = supabase.storage.from_("manual-images").get_public_url(image_filename)
        except Exception as e:
            print(f"Failed to upload user image: {e}")
            public_url = None

        chunks = [{
            "chunk_id": 0, 
            "page_number": 1, 
            "source": source_name, "text": text, 
            "char_count": len(text), "image_url": public_url
        }]
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Embed and store all chunks regardless of source
    chunks = embed_chunks(chunks)
    store_chunks(chunks)

    page_count = len(set(c["page_number"] for c in chunks))
    return page_count