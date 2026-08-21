from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, FrameBreak, NextPageTemplate,
    Paragraph, Spacer, Table, TableStyle, PageBreak
)

PAGE_W, PAGE_H = LETTER
MARGIN = 0.7 * inch
GUTTER = 0.3 * inch
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) / 2
COL_H = PAGE_H - 2 * MARGIN - 0.6 * inch  # leave room for running header

styles = getSampleStyleSheet()

title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=16, spaceAfter=4, alignment=TA_CENTER)
subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontSize=9.5, alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=14)
h1_style = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=10.5, spaceBefore=10, spaceAfter=4, textColor=colors.black)
h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=9.5, spaceBefore=8, spaceAfter=3, textColor=colors.black)
body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=8.7, leading=11.6, alignment=TA_JUSTIFY, spaceAfter=6)
running_header_style = ParagraphStyle("Running", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#555555"))
caption_style = ParagraphStyle("Caption", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#333333"), spaceAfter=8)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 0.15 * inch,
                       "NexaForge Manufacturing \u2014 internal knowledge base \u2014 MAINTENANCE QUERY AGENT")
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 0.3 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_template():
    frame_left = Frame(MARGIN, MARGIN, COL_W, COL_H, id="left", showBoundary=0)
    frame_right = Frame(MARGIN + COL_W + GUTTER, MARGIN, COL_W, COL_H, id="right", showBoundary=0)
    return PageTemplate(id="TwoCol", frames=[frame_left, frame_right], onPage=header_footer)


def full_width_frame():
    return Frame(MARGIN, PAGE_H - MARGIN - 2.6 * inch, PAGE_W - 2 * MARGIN, 2.6 * inch, id="titleblock", showBoundary=0)


doc = BaseDocTemplate(
    "thesis_manual.pdf",
    pagesize=LETTER,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
)
doc.addPageTemplates([make_template()])

story = []

# ---------------- Title block (spans both columns visually, placed at top of first page) ----------------
story.append(Paragraph("1.&nbsp;&nbsp;Introduction", h1_style))
story.append(Paragraph(
    "This document describes the design, retrieval architecture, and evaluation methodology of the "
    "<b>NexaForge Manufacturing Equipment Maintenance Query Agent</b> \u2014 a retrieval-augmented generation "
    "(RAG) system built to answer natural-language questions from equipment manuals, maintenance schedules, "
    "and troubleshooting guides for factory floor and maintenance teams.",
    body_style
))
story.append(Paragraph(
    "Manufacturing floor workers frequently need quick answers from lengthy equipment manuals during time-"
    "critical repairs. Manually searching PDF documents is slow and error-prone, especially when the required "
    "information is buried inside specification tables or multi-page troubleshooting sections. The system "
    "described here ingests manuals automatically, indexes them for hybrid semantic and keyword search, and "
    "answers operator questions with citations to the exact source page.",
    body_style
))

story.append(Paragraph("1.1&nbsp;&nbsp;System Overview", h2_style))
story.append(Paragraph(
    "The assistant is exposed through a floating chat widget available on both the Admin and Worker "
    "dashboards. Every response is generated strictly from ingested manual content and includes the source "
    "document name and page number, so operators can verify the answer against the original manual if needed.",
    body_style
))

story.append(Paragraph("2.&nbsp;&nbsp;Document Ingestion Pipeline", h1_style))
story.append(Paragraph(
    "Uploaded documents (PDF, TXT, PNG, or JPG) are processed by a background task with four stages: text "
    "extraction, chunking, embedding, and storage.",
    body_style
))
story.append(Paragraph("2.1&nbsp;&nbsp;Text and Table Extraction", h2_style))
story.append(Paragraph(
    "PDF text is extracted using pdfplumber. Specification and maintenance-schedule tables are extracted "
    "separately using table-structure detection and rewritten as explicit \u201clabel: value\u201d lines, which "
    "prevents column values from being lost when a table is flattened into plain text. Pages using a "
    "two-column academic layout are detected by checking for a wide empty vertical gutter near the horizontal "
    "center of the page; when detected, the left column is read completely before the right column, avoiding "
    "the interleaved reading order that a naive top-to-bottom text extraction would otherwise produce.",
    body_style
))
story.append(Paragraph("2.2&nbsp;&nbsp;Chunking and Embedding", h2_style))
story.append(Paragraph(
    "Extracted text is split into chunks of approximately 1200 characters with 200 characters of overlap "
    "using a recursive character splitter. Table content is chunked separately from surrounding prose to "
    "avoid a specification row being split across a chunk boundary. Each chunk is embedded using a remote "
    "sentence-transformer model (384-dimensional vectors) and stored in a PostgreSQL database with the "
    "pgvector extension.",
    body_style
))

story.append(Paragraph("3.&nbsp;&nbsp;Hybrid Retrieval and Reranking", h1_style))
story.append(Paragraph(
    "Given a query, the system runs two retrieval methods in parallel and merges their results before a "
    "final reranking pass.",
    body_style
))
story.append(Paragraph("3.1&nbsp;&nbsp;Keyword and Semantic Search", h2_style))
story.append(Paragraph(
    "Keyword search uses the BM25 Okapi algorithm over all stored chunks. Semantic search computes cosine "
    "similarity between the query embedding and each chunk embedding using pgvector\u2019s nearest-neighbor "
    "search. The two result sets are normalized to a common 0\u20131 scale and merged using a weighted average, "
    "with both methods weighted equally by default.",
    body_style
))
story.append(Paragraph("3.2&nbsp;&nbsp;LLM-Based Reranking", h2_style))
story.append(Paragraph(
    "The top candidates from hybrid search are re-scored by a large language model, which reads each "
    "candidate passage alongside the original question and returns the passages ordered from most to least "
    "relevant. This step was previously implemented with a hosted cross-encoder model, but was replaced with "
    "an LLM-based approach after the hosted model became unavailable through the inference provider being "
    "used. The reranker includes a fallback: if the reranking call fails for any reason, the system reverts "
    "to the hybrid search ranking rather than returning an error.",
    body_style
))

story.append(Paragraph("4.&nbsp;&nbsp;Conversational Agent Design", h1_style))
story.append(Paragraph(
    "Each incoming question is classified into one of four categories by a routing model before any retrieval "
    "occurs.",
    body_style
))

table_data = [
    ["Category", "Description"],
    ["search_manual", "Troubleshooting, error codes, procedures"],
    ["check_schedule", "Maintenance intervals and scheduled tasks"],
    ["log_issue", "Reporting a newly observed problem"],
    ["escalate", "Unclear, unsafe, or out-of-scope questions"],
]
t = Table(table_data, colWidths=[1.15 * inch, 1.55 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e4da")),
    ("FONTSIZE", (0, 0), (-1, -1), 7.6),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t)
story.append(Paragraph("Table 1. Query routing categories used by the agent.", caption_style))

story.append(Paragraph(
    "Questions routed to search_manual or check_schedule retrieve up to five reranked chunks, which are "
    "passed to a language model along with an instruction to answer strictly from the provided context and "
    "cite the page number. If the retrieved context does not contain the answer, the model is instructed to "
    "state this rather than speculate. Questions routed to log_issue are recorded for later review. Questions "
    "routed to escalate return a message directing the operator to a qualified technician.",
    body_style
))

story.append(Paragraph("5.&nbsp;&nbsp;Evaluation Methodology", h1_style))
story.append(Paragraph(
    "A fixed evaluation set of 25 questions was constructed, covering troubleshooting, scheduled maintenance, "
    "cross-document production-flow questions, and deliberately out-of-scope questions expected to trigger "
    "escalation. Two metrics are reported for each evaluation run.",
    body_style
))
story.append(Paragraph("5.1&nbsp;&nbsp;Escalation Accuracy", h2_style))
story.append(Paragraph(
    "Escalation accuracy measures whether the routing model made the correct decision to answer or escalate "
    "each question, compared against a manually labeled ground truth. This metric does not evaluate whether "
    "the resulting answer content was correct.",
    body_style
))
story.append(Paragraph("5.2&nbsp;&nbsp;Answer Accuracy", h2_style))
story.append(Paragraph(
    "Answer accuracy checks whether the generated answer text contains a set of required keywords defined "
    "per question \u2014 for example, a spindle speed range question requires both bound values to be present "
    "in the answer. This metric specifically catches cases where the routing decision was correct but "
    "retrieval failed to surface the correct passage, resulting in an incorrect \u201cnot found\u201d response.",
    body_style
))

story.append(Paragraph("6.&nbsp;&nbsp;Results", h1_style))
story.append(Paragraph(
    "Prior to fixing specification-table extraction, the system scored 63.6% on answer accuracy, with all "
    "observed failures corresponding to specification-table lookups such as spindle speed range and tool "
    "changer capacity. After implementing table-aware extraction and table-isolated chunking, answer accuracy "
    "improved to 90.9% on the same evaluation set, while escalation accuracy remained at 100% throughout, "
    "indicating that the routing model\u2019s category decisions were not the source of the original failures.",
    body_style
))
story.append(Paragraph(
    "The one remaining failure at the time of writing involved two passages within the same manual that both "
    "referenced spindle RPM values \u2014 one from the specification table and one from an unrelated warm-up "
    "procedure \u2014 indicating a retrieval disambiguation issue rather than a missing-data issue.",
    body_style
))

story.append(Paragraph("7.&nbsp;&nbsp;Conclusion and Future Work", h1_style))
story.append(Paragraph(
    "The evaluation results demonstrate that table-aware extraction has a measurable, significant effect on "
    "answer quality for manuals containing specification tables, independent of the routing and generation "
    "stages of the pipeline. Future work includes disambiguating near-duplicate numeric references within a "
    "single document, extending column-layout detection to mixed single/multi-column pages, and expanding the "
    "evaluation set as additional equipment manuals are ingested.",
    body_style
))

doc.build(story)
print("done")