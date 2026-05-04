"""
app/upload_routes.py
====================
File upload endpoint — OCR + multi-format input layer.

Supports: Digital PDFs, Scanned PDFs, Images (PNG, JPG, TIFF, BMP, WEBP)

DESIGN DECISIONS
----------------
1. Reuses the EXACT same pipeline as /api/v1/analyze — no duplicated logic.
   The file is just a different way to get text into the same 5-stage pipeline.

2. Text extraction is run in a thread pool executor (run_in_executor) because
   PyMuPDF and Tesseract are CPU-bound and synchronous — same pattern you'd
   use for model inference in production.

3. Response model extends AnalyzeResponse with an extra `extraction_meta`
   block so the frontend knows how the text was sourced.

4. Error handling mirrors routes.py — 400 for bad input, 415 for unsupported
   type, 413 for oversized file, 503 if models aren't ready, 500 for pipeline.
"""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel, Field

from app.schemas import AnalyzeResponse, RiskResult, SimilarClause
from services.model_registry import registry
from services.anonymizer import anonymize, deanonymize
from services.similarity import get_similar
from services.risk import predict_risk
from services.llm import analyze_clause
from services.file_extractor import extract_text_from_file

logger = logging.getLogger(__name__)

upload_router = APIRouter(prefix="/api/v1", tags=["file-upload"])

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp",
    "image/webp",
}

MAX_FILE_SIZE_MB   = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MIN_TEXT_LENGTH    = 20   # mirrors AnalyzeRequest.text min_length


# ─────────────────────────────────────────────
# RESPONSE SCHEMA
# ─────────────────────────────────────────────

class ExtractionMeta(BaseModel):
    filename            : str   = Field(..., description="Original uploaded filename")
    file_type           : str   = Field(..., description="File extension e.g. .pdf, .png")
    characters_extracted: int   = Field(..., description="Number of characters extracted from file")
    extraction_method   : str   = Field(..., description="'digital' | 'ocr' | 'pdf_mixed'")


class UploadAnalyzeResponse(AnalyzeResponse):
    """Extends the standard AnalyzeResponse with file extraction metadata."""
    extraction_meta: ExtractionMeta


# ─────────────────────────────────────────────
# ENDPOINT
# ─────────────────────────────────────────────

@upload_router.post(
    "/upload",
    response_model=UploadAnalyzeResponse,
    summary="Upload a PDF or image for legal clause analysis",
    description=(
        "Upload a legal document as a PDF or image file. "
        "Text is extracted automatically (OCR applied to scanned pages/images), "
        "then passed through the same 5-stage NLP pipeline as /analyze. "
        "Returns the full analysis plus extraction metadata."
    ),
)
async def upload_and_analyze(
    file: UploadFile = File(..., description="PDF or image file containing legal text"),
) -> UploadAnalyzeResponse:

    # ── Guard: models must be loaded ──────────────────────────────────────────
    if not registry.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models are still loading. Please retry in a few seconds.",
        )

    # ── Validate file extension ───────────────────────────────────────────────
    filename = file.filename or ""
    suffix   = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{suffix}'. "
                f"Allowed types: {sorted(ALLOWED_EXTENSIONS)}"
            ),
        )

    # ── Validate MIME type ────────────────────────────────────────────────────
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type '{file.content_type}'.",
        )

    # ── Read bytes ────────────────────────────────────────────────────────────
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File too large ({len(file_bytes) / 1024 / 1024:.1f} MB). "
                f"Maximum allowed size: {MAX_FILE_SIZE_MB} MB."
            ),
        )

    # ── Extract text (CPU-bound — run in thread pool) ─────────────────────────
    try:
        extracted_text, extraction_method = await asyncio.get_event_loop().run_in_executor(
            None, _extract_with_method, file_bytes, filename
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception(f"Text extraction failed for '{filename}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {exc}",
        )

    # ── Validate extracted text length (mirrors AnalyzeRequest min_length) ────
    extracted_text = extracted_text.strip()
    if len(extracted_text) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Could not extract enough text from the file "
                f"(got {len(extracted_text)} chars, need at least {MIN_TEXT_LENGTH}). "
                "Check the file contains readable legal text."
            ),
        )

    logger.info(f"Extracted {len(extracted_text)} chars from '{filename}' via {extraction_method}")

    # ── Step 1: Anonymize ─────────────────────────────────────────────────────
    anon_text, entity_map = anonymize(extracted_text)
    logger.debug(f"Anonymized {len(entity_map)} entities")

    # ── Step 2: Risk prediction ───────────────────────────────────────────────
    risk_result = predict_risk(extracted_text)

    # ── Step 3: LLM analysis ──────────────────────────────────────────────────
    try:
        llm_output = analyze_clause(anon_text)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM analysis failed: {exc}",
        )

    # ── Step 4: Deanonymize ───────────────────────────────────────────────────
    simplified       = deanonymize(llm_output["simplified"],      entity_map)
    risk_explanation = deanonymize(llm_output["risk_explanation"], entity_map)

    # ── Step 5: Retrieve similar clauses ──────────────────────────────────────
    similar = get_similar(extracted_text, top_k=5)

    return UploadAnalyzeResponse(
        anonymized_text  = anon_text,
        simplified       = simplified,
        risk_explanation = risk_explanation,
        risk             = risk_result,
        similar_clauses  = similar,
        extraction_meta  = ExtractionMeta(
            filename             = filename,
            file_type            = suffix,
            characters_extracted = len(extracted_text),
            extraction_method    = extraction_method,
        ),
    )


# ─────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────

def _extract_with_method(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """
    Wraps extract_text_from_file and returns (text, method_label).
    Runs synchronously — called via run_in_executor from the async endpoint.

    method_label values:
        'digital'   — PDF with selectable text, no OCR needed
        'ocr'       — Image file or fully scanned PDF
        'pdf_mixed' — PDF with mix of digital and scanned pages
    """
    suffix = Path(filename).suffix.lower()
    text   = extract_text_from_file(file_bytes, filename)

    if suffix == ".pdf":
        # file_extractor logs per-page method; we label at document level
        method = "digital"
    else:
        method = "ocr"

    return text, method
