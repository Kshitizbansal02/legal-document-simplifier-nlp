"""
services/risk.py
================
Risk level prediction for a legal clause.

TWO-TIER APPROACH
-----------------
Tier 1 (preferred): Trained LogisticRegression classifier on top of
    MiniLM embeddings. Gives a predicted label + confidence score.
    Train it with: python scripts/train_risk_clf.py

Tier 2 (fallback): KNN majority vote via similarity search.
    Used automatically if the classifier model file doesn't exist yet.
    Less accurate but requires no training step.

WHY NOT JUST USE KNN?
---------------------
The old risk.py was KNN-only, which has two problems:
  1. No confidence score — you can't tell "barely medium" from "clearly high"
  2. Sensitive to whatever happens to be in the top-5 similar clauses
     (if your DB is imbalanced, you'll always predict "low")

A trained classifier fixes both: it learns decision boundaries across
the full dataset and gives calibrated probability scores.

RISK LEVELS
-----------
  low    → Standard boilerplate, no unusual obligations
  medium → Some restrictions or obligations worth reviewing
  high   → Significant legal/financial risk, lawyer review recommended
"""

from __future__ import annotations
import logging
import numpy as np
from services.model_registry import registry
from services.similarity import get_similar

logger = logging.getLogger(__name__)

# Maps predicted label to a human-readable explanation shown in the UI
RISK_DESCRIPTIONS: dict[str, str] = {
    "low":    "Standard clause — no unusual obligations detected.",
    "medium": "Contains notable restrictions or obligations. Review recommended.",
    "high":   "Significant legal or financial risk. Legal counsel strongly advised.",
}


def predict_risk(text: str) -> dict:
    """
    Predict the risk level of a legal clause.

    Returns
    -------
    dict with keys:
        level       : str   — "low" | "medium" | "high"
        confidence  : float — 0.0–1.0 (how certain the model is)
        description : str   — plain-English explanation
        method      : str   — "classifier" | "knn_fallback"

    Example
    -------
    >>> predict_risk("The licensee shall not sublicense or transfer any rights.")
    {
        "level": "high",
        "confidence": 0.87,
        "description": "Significant legal or financial risk...",
        "method": "classifier"
    }
    """
    vec = registry.embedder.encode([text], normalize_embeddings=True)

    # ── Tier 1: trained classifier ───────────────────────────────────────────
    if registry.risk_clf is not None:
        label: str = registry.risk_clf.predict(vec)[0]
        # predict_proba gives confidence per class; take the winning class prob
        proba: np.ndarray = registry.risk_clf.predict_proba(vec)[0]
        confidence = float(proba.max())

        return {
            "level":       label,
            "confidence":  round(confidence, 3),
            "description": RISK_DESCRIPTIONS.get(label, ""),
            "method":      "classifier",
        }

    # ── Tier 2: KNN fallback ─────────────────────────────────────────────────
    logger.warning("Risk classifier not available — using KNN fallback.")
    similar = get_similar(text, top_k=7)

    if not similar:
        return {
            "level":       "unknown",
            "confidence":  0.0,
            "description": "Could not determine risk — no similar clauses found.",
            "method":      "knn_fallback",
        }

    # Weighted vote: weight each neighbour's vote by its similarity score
    vote_weights: dict[str, float] = {}
    for item in similar:
        lvl = item["risk_level"]
        vote_weights[lvl] = vote_weights.get(lvl, 0.0) + item["score"]

    winner = max(vote_weights, key=vote_weights.__getitem__)
    total  = sum(vote_weights.values())
    confidence = round(vote_weights[winner] / total, 3)

    return {
        "level":       winner,
        "confidence":  confidence,
        "description": RISK_DESCRIPTIONS.get(winner, ""),
        "method":      "knn_fallback",
    } 