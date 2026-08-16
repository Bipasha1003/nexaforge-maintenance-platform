import os
import re
import base64
import mimetypes

from PIL import Image, ImageFilter
import pytesseract
from langchain_groq import ChatGroq

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text: str) -> str:
    """Removes <think>...</think> reasoning blocks that thinking-mode
    models (like qwen3.6) prepend before their actual answer. Without
    this, the model's internal scratch reasoning gets embedded and
    searched right alongside the real extracted content."""
    cleaned = _THINK_BLOCK.sub("", text)
    return cleaned.strip()


def extract_text_with_vision(file_path):
    """Uses a Vision LLM to extract text, steps, and layout flow from an
    image/diagram. Returns cleaned final-answer text only — no reasoning
    trace. Returns "" on any failure so callers can fall back to OCR."""
    try:
        llm = ChatGroq(model="qwen/qwen3.6-27b", temperature=0)

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type not in ("image/png", "image/jpeg", "image/webp"):
            mime_type = "image/png"

        prompt = [
            ("system", "You are an expert technical OCR system. Extract every single word, label, step, and arrow connection from this manufacturing flowchart or diagram completely and accurately. Do not miss any boxes. Respond with ONLY the extracted content — no reasoning, no explanation of your process."),
            ("human", [
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                {"type": "text", "text": "Extract all text and layout steps from this flowchart."}
            ])
        ]

        response = llm.invoke(prompt)
        return _strip_thinking(response.content)
    except Exception as e:
        print(f"[VISION ERROR] {type(e).__name__}: {e} — falling back to Tesseract")
        return ""


def preprocess_image_for_ocr(img: Image.Image) -> Image.Image:
    """Resizes and cleans up diagrams for fallback Tesseract reading."""
    width, height = img.size
    img_resized = img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    gray = img_resized.convert('L')
    sharpened = gray.filter(ImageFilter.SHARPEN)
    return sharpened


def run_robust_ocr(image: Image.Image) -> str:
    """Standard Tesseract OCR with enhancements — the fallback when
    the vision model fails or returns nothing."""
    processed = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(processed, config='--psm 6').strip()

    if not text or len(text) < 15:
        alt_text = pytesseract.image_to_string(processed, config='--psm 11').strip()
        if len(alt_text) > len(text):
            text = alt_text

    if not text:
        text = pytesseract.image_to_string(image).strip()

    return text


def extract_image_text(file_path: str) -> str:
    """The single entry point both ingest.py and generate_questions.py
    should call for any standalone image file. Tries vision first, falls
    back to robust Tesseract OCR, never returns an empty string silently."""
    text = extract_text_with_vision(file_path)
    if not text.strip():
        image = Image.open(file_path)
        text = run_robust_ocr(image)
    if not text.strip():
        text = "[Image with no recognizable text]"
    return text