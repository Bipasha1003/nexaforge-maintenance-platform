import os
import sys
import json
import uuid
from langchain_groq import ChatGroq
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from splitter import chunk_document
from image_extraction import extract_image_text

load_dotenv()
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
    return _llm

QUESTION_PROMPT = """You are helping build a test set for a maintenance chatbot.
Read the excerpt below from an equipment manual and write 2 realistic questions
a factory worker or maintenance technician might ask, that this excerpt would answer.

Rules:
- Questions should sound natural, like someone actually asking, not a quiz.
- Do not mention "the excerpt" or "the document" in the questions.
- Return ONLY a JSON list of 2 strings, nothing else. Example: ["question one?", "question two?"]

Excerpt (from page {page}):
{text}
"""

def generate_questions_for_chunk(chunk):
    llm = get_llm()
    prompt = QUESTION_PROMPT.format(page=chunk["page_number"], text=chunk["text"])
    response = llm.invoke(prompt)
    raw = response.content.strip()
    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        questions = json.loads(raw[start:end]) if start != -1 and end != 0 else []
    return questions

def get_chunks_for_file(file_path, source_name=None):
    """Extracts and chunks text based on file extension (PDF, TXT, Images).
    Images now go through the same shared vision+OCR pipeline as
    ingest.py — previously this used plain pytesseract only, which
    produced much weaker text than what actually gets stored for real
    uploads, and caused image-based documents to generate 0 questions."""
    ext = os.path.splitext(file_path)[1].lower()
    actual_source_name = source_name if source_name else os.path.basename(file_path)

    if ext == ".pdf":
        chunks = chunk_document(file_path, source_name=actual_source_name)
        return chunks if chunks else []

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return [{
            "chunk_id": str(uuid.uuid4()),
            "page_number": 1,
            "source": actual_source_name,
            "text": text,
            "char_count": len(text)
        }]

    elif ext in [".png", ".jpg", ".jpeg"]:
        text = extract_image_text(file_path)
        return [{
            "chunk_id": str(uuid.uuid4()),
            "page_number": 1,
            "source": actual_source_name,
            "text": text,
            "char_count": len(text)
        }]
    else:
        print(f"Unsupported file format: {ext}")
        return []

def generate_questions_for_file(file_path, source_name=None, output_dir="generated_questions"):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Extracting text from: {file_path}...")
    chunks = get_chunks_for_file(file_path, source_name)

    if not chunks:
        print(f"No extractable text found in {file_path}.")
        return None

    all_results = []
    for i, chunk in enumerate(chunks):
        if chunk["char_count"] < 50:
            print(f"Skipping chunk {i + 1} — only {chunk['char_count']} chars, below the 50-char minimum.")
            continue

        print(f"Generating questions for chunk {i + 1}/{len(chunks)} (page {chunk['page_number']})...")
        questions = generate_questions_for_chunk(chunk)
        for q in questions:
            all_results.append({
                "question": q,
                "expected_page": chunk["page_number"],
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            })

    name_to_use = source_name if source_name else os.path.basename(file_path)
    clean_name = os.path.splitext(name_to_use)[0]

    output_path = os.path.join(output_dir, f"{clean_name}_questions.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved {len(all_results)} questions to {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_questions.py <path_to_file>")
        sys.exit(1)
    generate_questions_for_file(sys.argv[1])