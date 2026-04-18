"""
services/model_registry.py
===========================
Central registry for all heavy objects (models, dataframes, embeddings).

WHY THIS EXISTS
---------------
Previously every service file loaded its own model at import time:

    # similarity.py  ← loaded SentenceTransformer on import
    # risk.py        ← imported similarity.py, triggering the load again
    # routes.py      ← imported both, double-loading on startup

Now there is exactly ONE copy of each model, loaded once during the
FastAPI lifespan startup, and injected into every service via this registry.
Tests can call registry.load_mock() to skip heavy downloads entirely.
"""

from __future__ import annotations
import logging
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Holds references to all loaded models and data assets."""

    def __init__(self) -> None:
        self._ready = False
        self.embedder = None          # SentenceTransformer
        self.risk_clf = None          # sklearn classifier
        self.clauses_df: pd.DataFrame | None = None
        self.clause_embeddings: np.ndarray | None = None

    @property
    def is_ready(self) -> bool:
        return self._ready

    async def load(self) -> None:
        """Called once at startup by FastAPI lifespan."""
        logger.info("Loading NLP models…")

        # Import here so that tests can mock before calling load()
        from sentence_transformers import SentenceTransformer

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("  ✓ SentenceTransformer loaded")

        self.clauses_df = pd.read_csv("data/cleaned_clauses.csv")
        self.clause_embeddings = np.load("data/embeddings.npy")
        logger.info(f"  ✓ Clause DB loaded ({len(self.clauses_df)} rows)")

        try:
            self.risk_clf = joblib.load("models/risk_clf.pkl")
            logger.info("  ✓ Risk classifier loaded")
        except FileNotFoundError:
            logger.warning(
                "  ! models/risk_clf.pkl not found — "
                "run scripts/train_risk_clf.py first. "
                "Falling back to KNN majority vote."
            )
            self.risk_clf = None

        self._ready = True
        logger.info("All models ready.")

    def clear(self) -> None:
        """Called on shutdown."""
        self.embedder = None
        self.risk_clf = None
        self.clauses_df = None
        self.clause_embeddings = None
        self._ready = False


# Singleton — import this everywhere
registry = ModelRegistry()