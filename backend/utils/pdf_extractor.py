"""
PDF text extraction.

Uses pdfplumber as the primary extractor because it preserves layout /
line-breaks reasonably well. Falls back to PyPDF2 if pdfplumber fails.
If the PDF turns out to be a scanned/image-only PDF (i.e. almost no text
is extracted), it is handed off to OCR (via pdf2image + the ocr_extractor)
so scanned PDFs still work end to end.
"""

import importlib
import io
from PyPDF2 import PdfReader

MIN_CHARS_BEFORE_OCR_FALLBACK = 40


def _get_pdfplumber():
    try:
        return importlib.import_module("pdfplumber")
    except ImportError:
        return None


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    pdfplumber = _get_pdfplumber()
    if pdfplumber is None:
        raise ImportError("pdfplumber is not installed")

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(layout=True) or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def _extract_with_pypdf2(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def _extract_with_ocr_fallback(file_bytes: bytes) -> str:
    """Rasterize each page and OCR it. Requires poppler (system dep) for
    pdf2image and tesseract (system dep) for pytesseract."""
    from pdf2image import convert_from_bytes
    from .ocr_extractor import extract_text_from_image_object

    pages = convert_from_bytes(file_bytes)
    text_parts = []
    for page_image in pages:
        page_text = extract_text_from_image_object(page_image)
        if page_text.strip():
            text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Returns a dict: {"text": str, "method": str, "page_count": int|None}
    """
    method = "pdfplumber"
    text = ""
    page_count = None

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
        text = _extract_with_pdfplumber(file_bytes)
    except Exception:
        text = ""

    if len(text.strip()) < MIN_CHARS_BEFORE_OCR_FALLBACK:
        try:
            text = _extract_with_pypdf2(file_bytes)
            method = "pypdf2"
        except Exception:
            text = ""

    if len(text.strip()) < MIN_CHARS_BEFORE_OCR_FALLBACK:
        try:
            text = _extract_with_ocr_fallback(file_bytes)
            method = "ocr_fallback"
        except Exception as exc:
            raise RuntimeError(
                "Could not extract text from this PDF. It may be a scanned "
                "document and OCR fallback failed (is poppler installed?). "
                f"Original error: {exc}"
            )

    return {"text": text.strip(), "method": method, "page_count": page_count}
