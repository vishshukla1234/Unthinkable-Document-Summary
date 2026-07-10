"""
OCR text extraction for image files (scanned documents), using Tesseract
via pytesseract. No external/cloud API calls -- everything runs locally.

System requirement: the `tesseract-ocr` binary must be installed, e.g.:
    Ubuntu/Debian: sudo apt-get install tesseract-ocr
    macOS (brew):  brew install tesseract
    Windows:       https://github.com/UB-Mannheim/tesseract/wiki
"""

import io
from PIL import Image, ImageOps, ImageFilter
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def _preprocess_image(image: Image.Image) -> Image.Image:
    """Light preprocessing to improve OCR accuracy on scanned documents:
    convert to grayscale, auto-contrast, and a mild sharpen filter."""
    gray = ImageOps.grayscale(image)
    contrast = ImageOps.autocontrast(gray)
    sharpened = contrast.filter(ImageFilter.SHARPEN)
    return sharpened


def extract_text_from_image_object(image: Image.Image) -> str:
    processed = _preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    return text.strip()


def extract_text_from_image_bytes(file_bytes: bytes) -> dict:
    """
    Returns a dict: {"text": str, "method": "tesseract_ocr"}
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()
    except Exception as exc:
        raise RuntimeError(f"Could not open image file: {exc}")

    try:
        text = extract_text_from_image_object(image)
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR engine is not installed on this machine. "
            "Install it with `sudo apt-get install tesseract-ocr` "
            "(or the equivalent for your OS) and try again."
        )

    return {"text": text, "method": "tesseract_ocr"}
