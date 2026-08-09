import pdfplumber

def extract_pages(filepath):
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            pages.append({
                "page_number": page_num,
                "text": text,
                "needs_ocr": text is None or len(text.strip()) < 20
            })
    return pages

if __name__ == "__main__":
    pages = extract_pages("sample_pdfs/manual1.pdf")
    print(f"Total pages: {len(pages)}")
    ocr_needed = [p["page_number"] for p in pages if p["needs_ocr"]]
    print(f"Pages needing OCR: {ocr_needed}")
    print(pages[0]["text"][:300] if pages[0]["text"] else "NO TEXT ON PAGE 1")