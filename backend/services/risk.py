"""
services/risk.py
================
Risk classification for legal clauses.

HOW IT WORKS
------------
1. Embed the input clause using the shared MiniLM embedder (same as similarity.py)
2. Pass the embedding to the trained LogisticRegression classifier (risk_clf.pkl)
3. Return level (low/medium/high), confidence score, description, and method label

WHY THE CLASSIFIER NOT THE LLM
--------------------------------
The risk classifier runs locally on embeddings — fast, deterministic, no API call.
The LLM is used separately for explanation text only. Keeping risk scoring local
means it works even if the Groq API is down, and produces consistent confidence %.

REGISTRY PATTERN
-----------------
Follows the same pattern as similarity.py — all heavy objects (embedder, classifier)
come from registry, which loads them once at startup. risk.py never loads models itself.
"""

from __future__ import annotations
import numpy as np
from services.model_registry import registry


# ─────────────────────────────────────────────
# RISK LEVEL METADATA
# ─────────────────────────────────────────────

RISK_DESCRIPTIONS = {
    "low": (
        "Low risk. This clause is standard and unlikely to create "
        "significant legal or financial obligations."
    ),
    "medium": (
        "Moderate risk. This clause may have implications worth reviewing. "
        "Consider consulting legal counsel if unsure."
    ),
    "high": (
        "Significant legal or financial risk. This clause could limit your "
        "rights or expose you to liability. Legal counsel strongly advised."
    ),
}

# Fallback if classifier returns an unexpected label
FALLBACK_DESCRIPTION = "Risk level could not be determined with confidence."


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────

def predict_risk(text: str) -> dict:
    """
    Predict the risk level of a legal clause.

    Parameters
    ----------
    text : Raw clause text (NOT anonymized — entity names don't affect embeddings
           and keeping them improves classifier accuracy on named-party clauses).

    Returns
    -------
    dict with keys:
        level       : str   — "low" | "medium" | "high"
        confidence  : float — model confidence in prediction (0–1)
        description : str   — plain English description of the risk level
        method      : str   — "classifier" | "knn_fallback"

    Raises
    ------
    RuntimeError if models are not loaded yet.
    """
    if not registry.is_ready:
        raise RuntimeError("Models not loaded. Did startup complete?")

    # ── Embed the clause ──────────────────────────────────────────────────────
    # Use the shared embedder — same model used to build the clause DB
    embedding = registry.embedder.encode([text], normalize_embeddings=True)

    # ── Classify ──────────────────────────────────────────────────────────────
    try:
        clf        = registry.risk_clf
        prediction = clf.predict(embedding)[0]           # "low" / "medium" / "high"
        proba      = clf.predict_proba(embedding)[0]     # probability per class
        confidence = float(np.max(proba))
        method     = "classifier"

    except Exception:
        # ── KNN fallback: if classifier fails, use cosine similarity to
        #    nearest clause in DB and inherit its risk label ──────────────────
        prediction, confidence, method = _knn_fallback(embedding)

    # ── Normalise label ───────────────────────────────────────────────────────
    level = str(prediction).lower().strip()
    if level not in RISK_DESCRIPTIONS:
        level = "medium"   # safe default for unexpected labels

    return {
        "level"      : level,
        "confidence" : round(confidence, 4),
        "description": RISK_DESCRIPTIONS[level],
        "method"     : method,
    }


# ─────────────────────────────────────────────
# KNN FALLBACK
# ─────────────────────────────────────────────

def _knn_fallback(embedding: np.ndarray) -> tuple[str, float, str]:
    """
    Emergency fallback when the sklearn classifier fails.
    Finds the nearest clause in the DB by cosine similarity
    and inherits its risk label.

    Returns (level, confidence, method_label)
    """
    from sklearn.metrics.pairwise import cosine_similarity

    scores = cosine_similarity(embedding, registry.clause_embeddings)[0]
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])

    row = registry.clauses_df.iloc[best_idx]
    level = str(row.get("risk_level", "medium")).lower().strip()

    if level not in RISK_DESCRIPTIONS:
        level = "medium"

    return level, best_score, "knn_fallback"
