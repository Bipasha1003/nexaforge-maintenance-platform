import os
import sys
sys.path.append(os.path.dirname(__file__))
from reader import extract_pages
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(filepath, source_name=None, chunk_size=500, chunk_overlap=50):
    pages = extract_pages(filepath)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    all_chunks = []
    chunk_id = 0
    for page in pages:
        if not page["text"]:
            continue  # OCR pages handled separately later
        for c in splitter.split_text(page["text"]):
            all_chunks.append({
                "chunk_id": chunk_id,
                "page_number": page["page_number"],
                "source": source_name or os.path.basename(filepath),
                "text": c,
                "char_count": len(c)
            })
            chunk_id += 1
    return all_chunks

if __name__ == "__main__":
    chunks = chunk_document("sample_pdfs/manual1.pdf")
    print(f"Total chunks: {len(chunks)}")
    print("First chunk:", chunks[0])
    print("---")
    print("Last chunk:", chunks[-1])