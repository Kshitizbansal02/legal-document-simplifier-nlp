"""
app/routes.py
=============
API route definitions.

DESIGN DECISIONS
----------------
1. The route is async but the heavy work (model inference) is synchronous.
   For a demo/academic project this is fine. In production you'd run
   CPU-bound inference in a thread pool:
       result = await asyncio.get_event_loop().run_in_executor(None, analyze_sync, req.text)

2. We return HTTP 503 if models aren't loaded yet (race condition on startup)
   rather than a cryptic 500 error.

3. Error handling is explicit — we distinguish between:
   - Input problems (400 Bad Request)
   - Model not ready (503 Service Unavailable)
   - Internal failures (500 Internal Server Error)
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import AnalyzeRequest, AnalyzeResponse
from services.model_registry import registry
from services.anonymizer import anonymize, deanonymize
from services.similarity import get_similar
from services.risk import predict_risk
from services.llm import analyze_clause

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

    # ── Step 1: Anonymize ─────────────────────────────────────────────────────
    # Replace named entities with placeholders BEFORE sending to external LLM.
    # This is the privacy-preserving layer — real names, organisations, and
    # amounts never leave your infrastructure in plaintext.
    anon_text, entity_map = anonymize(req.text)
    logger.debug(f"Anonymized {len(entity_map)} entities")

    # ── Step 2: Risk prediction ───────────────────────────────────────────────
    # Run against ORIGINAL text so entity names don't confuse the classifier.
    # The risk model uses embeddings, not LLM — so privacy isn't a concern here.
    risk_result = predict_risk(req.text)

    # ── Step 3: LLM analysis (single call) ───────────────────────────────────
    # One API call returns both simplification AND risk explanation.
    # The anonymized text is sent — the LLM never sees real entity names.
    try:
        llm_output = analyze_clause(anon_text)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM analysis failed: {exc}",
        )

    # ── Step 4: Deanonymize LLM outputs ──────────────────────────────────────
    # Restore original entity names in the LLM's text before returning.
    simplified       = deanonymize(llm_output["simplified"],       entity_map)
    risk_explanation = deanonymize(llm_output["risk_explanation"],  entity_map)

    # ── Step 5: Retrieve similar clauses ─────────────────────────────────────
    # Search the clause database for semantically similar examples.
    # This grounds the response in real contract data — not LLM imagination.
    similar = get_similar(req.text, top_k=5)

    return AnalyzeResponse(
        anonymized_text  = anon_text,
        simplified       = simplified,
        risk_explanation = risk_explanation,
        risk             = risk_result,
        similar_clauses  = similar,
    )