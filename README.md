# Unthinkable-Document-Summary Assistant

Upload a PDF or a scanned image and get a smart, extractive summary, key
points, and writing-improvement suggestions — **entirely processed locally**.
No OpenAI/Anthropic/Google/any external AI API is used anywhere in this
project. Summarization, OCR, and suggestions are all computed with
open-source libraries running on your own machine.

## How it works (no external API)

| Feature | Technique | Library |
|---|---|---|
| PDF text extraction | Layout-aware text extraction, with PyPDF2 fallback | `pdfplumber`, `PyPDF2` |
| OCR (scanned docs/images) | Local OCR engine | `pytesseract` (Tesseract) |
| Summarization | Graph-based extractive summarization (TextRank / PageRank over TF-IDF sentence similarity) | `scikit-learn`, `networkx` |
| Improvement suggestions | Readability scoring (Flesch Reading Ease), sentence-length, passive-voice, repetition heuristics | plain Python/regex |

Because summarization is **extractive** (it selects and reassembles the most
important existing sentences, rather than generating new text with an LLM),
the whole pipeline runs offline with no API keys, no billing, and no data
leaving your machine.

## Project structure

```
document-summarizer/
├── backend/
│   ├── app.py                 
│   ├── requirements.txt
│   └── utils/
│       ├── pdf_extractor.py   
│       ├── ocr_extractor.py   
│       ├── summarizer.py      
│       └── suggestions.py 
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.js / App.css
        ├── api.js             
        └── components/
            ├── FileUpload.js
            ├── SummaryOptions.js
            ├── SummaryDisplay.js
            └── Loading.js
            └── Landing.js 
```

## Prerequisites

- Python 3.9+
- Node.js 18+ and npm
- **Tesseract OCR** (system binary, required for image OCR):
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki
- **Poppler** (system binary, only needed for OCR-fallback on scanned/image-only
  PDFs — regular text PDFs work without it):
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`

## Setup & run

### 1. Backend (Flask)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API will run at `http://localhost:5000`. Health check: `GET /api/health`.

### 2. Frontend (React)

In a separate terminal:

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000` and talk to the backend at
`http://localhost:5000` (see `frontend/.env.example` — copy it to `.env` if
you need a different backend URL).

## API reference

- `POST /api/extract` — multipart form, field `file`. Returns extracted text.
- `POST /api/summarize` — JSON `{ text, length }` where `length` is
  `short | medium | long`. Returns `{ summary, key_points, ... }`.
- `POST /api/suggestions` — JSON `{ text }`. Returns writing suggestions.
- `POST /api/process` — multipart form, fields `file` + `length`. Convenience
  endpoint used by the frontend: does extraction + summarization +
  suggestions in one call.

## Notes & limitations

- Max upload size is 20MB (configurable in `backend/app.py`).
- OCR accuracy depends on scan quality; a light grayscale/contrast/sharpen
  preprocessing step is applied automatically to improve results.
- The summarizer is extractive (selects real sentences from the source),
  which keeps facts grounded in the original text — it does not paraphrase
  or hallucinate new content, unlike LLM-based summarizers.
- Summary "length" controls roughly what % of the original sentences are
  kept (short ≈15%, medium ≈30%, long ≈50%, with sensible min/max bounds).
