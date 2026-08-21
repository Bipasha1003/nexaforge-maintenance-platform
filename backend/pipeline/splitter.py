import os
import sys
sys.path.append(os.path.dirname(__file__))
from reader import extract_pages
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Must match the marker text reader.py inserts before table data.
TABLE_MARKER = "[Table data on page"


def chunk_document(filepath, source_name=None, chunk_size=1200, chunk_overlap=200):
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

        text = page["text"]

        # Split the page into "prose" and "table" parts BEFORE chunking,
        # so a spec table (e.g. "Spindle Speed Range: 60 - 12,000 RPM")
        # never gets cut apart just because the prose above it happened
        # to fill up the chunk_size budget first. Each part is then
        # chunked normally on its own.
        if TABLE_MARKER in text:
            prose_part, _, table_part = text.partition(TABLE_MARKER)
            table_part = TABLE_MARKER + table_part
        else:
            prose_part, table_part = text, None

        for c in splitter.split_text(prose_part):
            all_chunks.append({
                "chunk_id": chunk_id,
                "page_number": page["page_number"],
                "source": source_name or os.path.basename(filepath),
                "text": c,
                "char_count": len(c)
            })
            chunk_id += 1

        if table_part and table_part.strip():
            # Tables are usually short, but still run through the
            # splitter (not just kept as one giant blob) in case a
            # page has an unusually large table.
            for c in splitter.split_text(table_part):
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