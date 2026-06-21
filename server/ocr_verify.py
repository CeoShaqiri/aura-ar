"""
Aura Legacy Grant — OCR Name Extraction Endpoint
Hosted on the Hetzner CAX31 node alongside the main FastAPI server.

Endpoint: POST /api/v1/ocr-verify
Input:    multipart/form-data with field  id_document  (image or PDF)
Output:   JSON  { "extracted_name": "John Doe" }

Dependencies (add to requirements.txt):
    pytesseract>=0.3.10
    Pillow>=10.0.0
    pdf2image>=1.17.0
    python-Levenshtein>=0.23.0

System packages (add to Dockerfile):
    tesseract-ocr tesseract-ocr-eng poppler-utils

Add this router to main.py:
    from ocr_verify import router as ocr_router
    app.include_router(ocr_router)
"""

import io
import re
import os
import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract

# pdf2image is optional — only imported if a PDF is submitted
try:
    from pdf2image import convert_from_bytes
    _PDF_SUPPORT = True
except ImportError:
    _PDF_SUPPORT = False

logger = logging.getLogger("aura.ocr")

router = APIRouter()

# ── Config ────────────────────────────────────────────────────────────────────
MAX_BYTES     = 8 * 1024 * 1024  # 8 MB
ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

# Tesseract PSM 4  = assume a single column of text of variable sizes
# OEM 3            = use default OCR engine (LSTM + legacy)
TESS_CONFIG = "--psm 4 --oem 3"

# ── Name patterns to try against OCR output ───────────────────────────────────
# Tries common ID layout keywords before resorting to heuristics
_NAME_PREFIXES = [
    r"(?:name|surname|last\s*name|first\s*name|full\s*name|given\s*name)\s*[:\-]?\s*([A-Za-z\s\-\'\.]{3,40})",
    r"(?:nom|vorname|nachname|cognome|nombre)\s*[:\-]?\s*([A-Za-z\s\-\'\.]{3,40})",
]
# Fallback: first capitalised multi-word token on its own line
_FALLBACK_RE = re.compile(r"^([A-Z][a-z]+(?: [A-Z][a-z]+)+)$", re.MULTILINE)


def _preprocess(img: Image.Image) -> Image.Image:
    """Convert to greyscale and sharpen — improves OCR accuracy on IDs."""
    from PIL import ImageFilter, ImageEnhance
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    return img


def _extract_name_from_text(text: str) -> Optional[str]:
    """
    Try labelled patterns first, then a capitalised two-word fallback.
    Returns the best candidate or None.
    """
    for pattern in _NAME_PREFIXES:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            # Filter out obvious non-names (single words, or too long)
            tokens = candidate.split()
            if 2 <= len(tokens) <= 5:
                return " ".join(t.capitalize() for t in tokens)

    # Fallback: first line that looks like "Firstname Lastname"
    m = _FALLBACK_RE.search(text)
    if m:
        return m.group(1).strip()

    return None


def _ocr_image(img: Image.Image) -> str:
    img = _preprocess(img)
    return pytesseract.image_to_string(img, config=TESS_CONFIG)


def _ocr_pdf(data: bytes) -> str:
    if not _PDF_SUPPORT:
        raise HTTPException(
            status_code=422,
            detail="PDF processing not available on this node. Please upload an image.",
        )
    pages = convert_from_bytes(data, dpi=200, first_page=1, last_page=2)
    texts = []
    for page in pages:
        texts.append(_ocr_image(page))
    return "\n".join(texts)


# ── Endpoint ──────────────────────────────────────────────────────────────────
@router.post("/api/v1/ocr-verify")
async def ocr_verify(id_document: UploadFile = File(...)):
    """
    Accept a government ID image or PDF, run Tesseract OCR, extract the
    applicant's name, and return it for the Identity Lock check.
    """
    # Validate content type
    content_type = (id_document.content_type or "").lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Allowed: {', '.join(sorted(ALLOWED_TYPES))}",
        )

    # Read + size-check
    data = await id_document.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 8 MB limit.")

    # OCR
    try:
        if content_type == "application/pdf":
            raw_text = _ocr_pdf(data)
        else:
            img = Image.open(io.BytesIO(data))
            raw_text = _ocr_image(img)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("OCR failed: %s", exc)
        raise HTTPException(status_code=500, detail="OCR processing failed.")

    # Extract name
    extracted_name = _extract_name_from_text(raw_text) or ""
    logger.info("OCR extracted name: %r", extracted_name)

    return JSONResponse({"extracted_name": extracted_name})
