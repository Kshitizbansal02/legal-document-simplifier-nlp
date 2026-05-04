"""
app/upload_routes.py  (updated — validation layer added)
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
from services.validator import validate_or_raise               # ← NEW

logger = logging.getLogger(__name__)

upload_router = APIRouter(prefix="/api/v1", tags=["file-upload"])

ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"
}
ALLOWED_MIME_TYPES = {
    "application/pdf", "image/png", "image/jpeg",
    "image/tiff", "image/bmp", "image/webp",
}
MAX_FILE_SIZE_MB    = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MIN_TEXT_LENGTH     = 20


class ExtractionMeta(BaseModel):
    filename            : str   = Field(...)
    file_type           : str   = Field(...)
    characters_extracted: int   = Field(...)
    extraction_method   : str   = Field(...)


class UploadAnalyzeResponse(AnalyzeResponse):
    extraction_meta: ExtractionMeta


@upload_router.post("/upload", response_model=UploadAnalyzeResponse)
async def upload_and_analyze(file: UploadFile = File(...)) -> UploadAnalyzeResponse:

    if not registry.is_ready:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Models are still loading.")

    filename = file.filename or ""
    suffix   = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=f"Unsupported file type '{suffix}'.")

    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=f"Unsupported content type '{file.content_type}'.")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Max: {MAX_FILE_SIZE_MB} MB.")

    try:
        extracted_text, extraction_method = await asyncio.get_event_loop().run_in_executor(
            None, _extract_with_method, file_bytes, filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Text extraction failed: {exc}")

    extracted_text = extracted_text.strip()

    if len(extracted_text) < MIN_TEXT_LENGTH:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Could not extract enough text ({len(extracted_text)} chars).")

    # ── Step 0.5: Validate extracted text is legal content ───────────────────
    validate_or_raise(extracted_text)

    anon_text, entity_map = anonymize(extracted_text)
    risk_result           = predict_risk(extracted_text)

    try:
        llm_output = analyze_clause(anon_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"LLM analysis failed: {exc}")

    simplified       = deanonymize(llm_output["simplified"],      entity_map)
    risk_explanation = deanonymize(llm_output["risk_explanation"], entity_map)
    similar          = get_similar(extracted_text, top_k=5)

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


def _extract_with_method(file_bytes: bytes, filename: str) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    text   = extract_text_from_file(file_bytes, filename)
    method = "digital" if suffix == ".pdf" else "ocr"
    return text, method