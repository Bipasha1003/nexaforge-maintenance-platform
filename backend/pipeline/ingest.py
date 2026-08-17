import os
import sys
import psycopg2
import pymupdf  # PyMuPDF for image extraction
import io    # Needed to read image bytes into PIL
from dotenv import load_dotenv
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from splitter import chunk_document
from vectorizer import embed_chunks
from image_extraction import extract_image_text, run_robust_ocr

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def store_chunks(chunks):
    """Inserts embedded chunks into the real `chunks` table without image_url.

    Deletes any existing chunks for this source first, so re-uploading
    the same file (e.g. after fixing an extraction bug, or just
    re-ingesting) replaces the old rows instead of stacking duplicates
    on top of them. Without this, every retry during debugging leaves
    stale/broken chunks permanently searchable alongside the good ones.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    sources = {c["source"] for c in chunks}
    for source in sources:
        cur.execute("DELETE FROM chunks WHERE source = %s", (source,))

    for c in chunks:
        cur.execute(
            """
            INSERT INTO chunks (chunk_id, page_number, source, text, char_count, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::vector)
            """,
            (
                c["chunk_id"],
                c["page_number"],
                c["source"],
                c["text"],
                c["char_count"],
                "[" + ",".join(str(x) for x in c["embedding"]) + "]"
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def extract_diagram_text(file_path):
    """Scans PDFs for images and extracts text using robust OCR.
    (Diagrams embedded inside a PDF page still use OCR-only, not the
    vision model — vision is reserved for standalone image uploads,
    since running it per-embedded-image on every PDF page would be
    slow and expensive. Revisit if PDF diagram quality becomes an issue.)"""
    page_ocr_map = {}
    pdf_file = pymupdf.open(file_path)

    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]
        image_list = page.get_images(full=True)

        if image_list:
            print(f"Page {page_index + 1}: Found {len(image_list)} images. Running OCR...")
            try:
                xref = image_list[0][0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]

                img_for_ocr = Image.open(io.BytesIO(image_bytes))
                extracted_text = run_robust_ocr(img_for_ocr)

                if extracted_text:
                    page_ocr_map[page_index + 1] = extracted_text
                    print(f"Successfully extracted diagram text for page {page_index + 1}")

            except Exception as e:
                print(f"ERROR processing image on page {page_index + 1}: {e}")

    return page_ocr_map


def ingest_file(file_path, source_name):
    """Handles PDFs, Text files, and Images (Vision AI + OCR), keeping text extraction while removing image_url."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        chunks = chunk_document(file_path, source_name=source_name)
        if not chunks:
            raise ValueError("No extractable text found in this PDF.")

        page_ocr_map = extract_diagram_text(file_path)

        for c in chunks:
            p_num = c["page_number"]
            if p_num in page_ocr_map:
                img_text = page_ocr_map[p_num]
                if img_text:
                    c["text"] += f"\n\n[Text Extracted From Image Diagram on Page {p_num}]:\n{img_text}"
                    c["char_count"] = len(c["text"])

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        text = f"Source Document Name: {source_name}\n\n{raw_text}"

        chunks = [{
            "chunk_id": 0,
            "page_number": 1,
            "source": source_name,
            "text": text,
            "char_count": len(text)
        }]

    elif ext in [".png", ".jpg", ".jpeg"]:
        raw_text = extract_image_text(file_path)

        text = f"Source Image File Name: {source_name}\n"
        text += f"Document Type: Diagram / Flowchart / Image\n"
        text += f"--- Content Extracted via Vision AI ---\n{raw_text}\n--------------------------------"

        chunks = [{
            "chunk_id": 0,
            "page_number": 1,
            "source": source_name,
            "text": text,
            "char_count": len(text)
        }]
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    chunks = embed_chunks(chunks)
    store_chunks(chunks)

    page_count = len(set(c["page_number"] for c in chunks))
    return page_count