"""
Document Summary Assistant



Endpoints:
  GET  /api/health              -> health check
  POST /api/extract              -> upload a PDF/image, get extracted text back
  POST /api/summarize            -> given text + length, get summary/key points
  POST /api/suggestions          -> given text, get improvement suggestions
  POST /api/process              -> convenience: upload + extract + summarize + suggestions in one call
"""

import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.pdf_extractor import extract_text_from_pdf
from utils.ocr_extractor import extract_text_from_image_bytes
from utils.summarizer import summarize, split_into_sentences
from utils.suggestions import generate_suggestions

MAX_UPLOAD_SIZE_MB = 20
ALLOWED_PDF_EXTENSIONS = {"pdf"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "webp"}

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _extract_text_for_upload(file_storage):
    filename = file_storage.filename or "upload"
    ext = _get_extension(filename)
    file_bytes = file_storage.read()

    if ext in ALLOWED_PDF_EXTENSIONS:
        result = extract_text_from_pdf(file_bytes)
    elif ext in ALLOWED_IMAGE_EXTENSIONS:
        result = extract_text_from_image_bytes(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type '.{ext}'. Allowed types: "
            f"{sorted(ALLOWED_PDF_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS)}"
        )

    result["filename"] = filename
    return result


@app.errorhandler(413)
def handle_too_large(_e):
    return jsonify({"error": f"File too large. Max size is {MAX_UPLOAD_SIZE_MB}MB."}), 413


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use form field name 'file'."}), 400

    file_storage = request.files["file"]
    if not file_storage.filename:
        return jsonify({"error": "No file selected."}), 400

    try:
        result = _extract_text_for_upload(file_storage)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Unexpected error while extracting text."}), 500

    if not result["text"]:
        return jsonify({"error": "No text could be extracted from this document."}), 422

    word_count = len(result["text"].split())
    return jsonify({
        "text": result["text"],
        "filename": result["filename"],
        "extraction_method": result.get("method"),
        "page_count": result.get("page_count"),
        "word_count": word_count,
    })

@app.route("/api/summarize", methods=["POST"])
def summarize_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    length = data.get("length", "medium")

    if not text or not text.strip():
        return jsonify({"error": "No text provided to summarize."}), 400
    if length not in {"short", "medium", "long"}:
        return jsonify({"error": "length must be one of: short, medium, long"}), 400

    try:
        result = summarize(text, length=length)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Unexpected error while summarizing."}), 500

    return jsonify(result)


@app.route("/api/suggestions", methods=["POST"])
def suggestions_endpoint():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not text or not text.strip():
        return jsonify({"error": "No text provided."}), 400

    try:
        sentences = split_into_sentences(text)
        result = generate_suggestions(text, sentences)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Unexpected error while generating suggestions."}), 500

    return jsonify(result)


@app.route("/api/process", methods=["POST"])
def process_endpoint():
    """Convenience endpoint: upload a file and get extraction + summary +
    suggestions back in a single response."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use form field name 'file'."}), 400

    file_storage = request.files["file"]
    if not file_storage.filename:
        return jsonify({"error": "No file selected."}), 400

    length = request.form.get("length", "medium")
    if length not in {"short", "medium", "long"}:
        length = "medium"

    try:
        extraction = _extract_text_for_upload(file_storage)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Unexpected error while extracting text."}), 500

    text = extraction["text"]
    if not text:
        return jsonify({"error": "No text could be extracted from this document."}), 422

    try:
        sentences = split_into_sentences(text)
        summary_result = summarize(text, length=length)
        suggestions_result = generate_suggestions(text, sentences)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Unexpected error while processing document."}), 500

    return jsonify({
        "filename": extraction["filename"],
        "extraction_method": extraction.get("method"),
        "page_count": extraction.get("page_count"),
        "word_count": len(text.split()),
        "text": text,
        "summary": summary_result["summary"],
        "key_points": summary_result["key_points"],
        "suggestions": suggestions_result["suggestions"],
        "readability": suggestions_result["readability"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
