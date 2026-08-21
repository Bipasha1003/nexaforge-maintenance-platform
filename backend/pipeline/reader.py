import pdfplumber


def _format_table(table):
    """Turns a raw pdfplumber table (list of rows, each a list of cell
    strings) into clean 'Label: Value' lines - e.g. turns a mangled
    spec table row into 'Spindle Speed Range: 60 - 12,000 RPM'.

    This rescues spec/schedule tables from getting flattened into
    jumbled text where the label and value are no longer next to each
    other, which breaks keyword/semantic search."""
    lines = []
    for row in table:
        cells = [c.strip() if c else "" for c in row]
        cells = [c for c in cells if c]  # drop empty cells
        if len(cells) >= 2:
            label = cells[0]
            value = " ".join(cells[1:])
            lines.append(f"{label}: {value}")
        elif len(cells) == 1:
            lines.append(cells[0])
    return "\n".join(lines)


def _detect_column_split(page, gap_ratio_threshold=0.04, min_words_per_side=5):
    """Heuristically detects a 2-column layout by looking for a real
    empty vertical gutter near the horizontal center of the page.

    Returns the x-coordinate to split on, or None if the page looks
    like normal single-column text (e.g. a standard manual page) -
    in which case extract_pages() falls back to its original
    behavior, unchanged.

    This is deliberately conservative: it only treats a page as
    2-column if there's a clear, wide empty band with real word
    content on both sides of it. A single-column page with text
    simply spread across the width won't trigger a false split.
    """
    words = page.extract_words()
    if len(words) < min_words_per_side * 2:
        return None

    center = page.width / 2

    left_words = [w for w in words if w["x1"] <= center]
    right_words = [w for w in words if w["x0"] >= center]

    if len(left_words) < min_words_per_side or len(right_words) < min_words_per_side:
        return None  # not enough content cleanly on both sides - likely single column

    gutter_left_edge = max(w["x1"] for w in left_words)
    gutter_right_edge = min(w["x0"] for w in right_words)
    gutter_width = gutter_right_edge - gutter_left_edge

    if gutter_width > page.width * gap_ratio_threshold:
        return (gutter_left_edge + gutter_right_edge) / 2

    return None


def _extract_page_text(page):
    """Reads a page's text in correct human reading order, handling
    both normal single-column pages and 2-column academic/report-style
    layouts (like conference papers). For 2-column pages, reads the
    ENTIRE left column top-to-bottom, then the entire right column -
    not line-by-line across both, which is what pdfplumber's default
    extract_text() does and which jumbles two unrelated sentences
    together on 2-column pages."""
    split_x = _detect_column_split(page)

    if split_x is None:
        return page.extract_text() or ""

    left = page.crop((0, 0, split_x, page.height))
    right = page.crop((split_x, 0, page.width, page.height))
    left_text = left.extract_text() or ""
    right_text = right.extract_text() or ""
    return f"{left_text}\n\n{right_text}"


def extract_pages(filepath):
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = _extract_page_text(page)

            # Table extraction runs on the full, uncropped page - table
            # structures are detected by pdfplumber's own line/grid
            # analysis, which works independently of column layout.
            table_text = ""
            try:
                tables = page.extract_tables()
                if tables:
                    formatted = [_format_table(t) for t in tables if t]
                    formatted = [f for f in formatted if f.strip()]
                    table_text = "\n\n".join(formatted)
            except Exception as e:
                print(f"[TABLE EXTRACTION WARNING] page {page_num}: {e}")

            combined = text
            if table_text:
                combined = f"{text}\n\n[Table data on page {page_num}]:\n{table_text}"

            pages.append({
                "page_number": page_num,
                "text": combined,
                "needs_ocr": not combined.strip() or len(combined.strip()) < 20
            })
    return pages


if __name__ == "__main__":
    pages = extract_pages("sample_pdfs/manual1.pdf")
    print(f"Total pages: {len(pages)}")
    ocr_needed = [p["page_number"] for p in pages if p["needs_ocr"]]
    print(f"Pages needing OCR: {ocr_needed}")
    print(pages[0]["text"][:500] if pages[0]["text"] else "NO TEXT ON PAGE 1")