"""
app/routes.py  (updated — validation layer added)
=============
Only change from original: validate_or_raise(req.text) added as Step 0.
Everything else is identical to your existing routes.py.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import AnalyzeRequest, AnalyzeResponse
from services.model_registry import registry
from services.anonymizer import anonymize, deanonymize
from services.similarity import get_similar
from services.risk import predict_risk
from services.llm import analyze_clause
from services.validator import validate_or_raise   # ← NEW

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze a legal clause",
    description=(
        "Accepts a legal clause and returns: plain-English simplification, "
        "risk assessment with confidence score, and semantically similar "
        "clauses retrieved from the database."
    ),
)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:

    # Guard: models must be loaded before we can do anything
    if not registry.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models are still loading. Please retry in a few seconds.",
        )

    # ── Step 0: Validate input is legal text ──────────────────────────────────
    validate_or_raise(req.text)

    # ── Step 1: Anonymize ─────────────────────────────────────────────────────
    anon_text, entity_map = anonymize(req.text)
    logger.debug(f"Anonymized {len(entity_map)} entities")

    # ── Step 2: Risk prediction ───────────────────────────────────────────────
    risk_result = predict_risk(req.text)

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
    similar = get_similar(req.text, top_k=5)

    return AnalyzeResponse(
        anonymized_text  = anon_text,
        simplified       = simplified,
        risk_explanation = risk_explanation,
        risk             = risk_result,
        similar_clauses  = similar,
    )