"""
services/similarity.py
======================
Semantic similarity search over the clause database.

This is the core RAG (Retrieval-Augmented Generation) component.
It answers: "What real contract clauses are most similar to this input?"

HOW IT WORKS
------------
1. Embed the query clause using the same MiniLM model used to build the DB
2. Compute cosine similarity between query vector and all stored embeddings
3. Return top-K results with their clause text, type, risk level, and score

WHY THIS BEATS CHATGPT FOR THIS TASK
-------------------------------------
A generic LLM has no access to your specific clause database.
It can only guess from training data. This retrieval step grounds
every response in real, labeled legal examples — dramatically reducing
hallucination risk in a domain where accuracy is critical.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from services.model_registry import registry


def get_similar(
    query: str,
    top_k: int = 5,
    min_score: float = 0.3,
) -> list[dict]:
    """
    Find the most semantically similar clauses to a query string.

    Parameters
    ----------
    query     : The clause text to search for
    top_k     : Maximum number of results to return
    min_score : Minimum cosine similarity threshold (0–1).
                Results below this are excluded — prevents returning
                unrelated clauses just because nothing better exists.

    Returns
    -------
    List of dicts, each containing:
        clause_text  : str
        clause_type  : str   (e.g. "Exclusivity", "Governing Law")
        risk_level   : str   (e.g. "low", "medium", "high")
        score        : float (cosine similarity, higher = more similar)

    Raises
    ------
    RuntimeError if models are not loaded yet (registry not ready).
    """
    if not registry.is_ready:
        raise RuntimeError("Models not loaded. Did startup complete?")

    # Embed the query — registry.embedder is the shared SentenceTransformer
    q_vec = registry.embedder.encode([query], normalize_embeddings=True)

    # Cosine similarity against all stored clause embeddings
    scores: np.ndarray = cosine_similarity(q_vec, registry.clause_embeddings)[0]

    # Get indices sorted by score descending, filtered by threshold
    ranked_idx = np.argsort(scores)[::-1]
    results = []

    for idx in ranked_idx:
        score = float(scores[idx])
        if score < min_score:
            break  # results are sorted — nothing after this beats threshold
        row = registry.clauses_df.iloc[idx]
        results.append({
            "clause_text" : row["clause_text"],
            "clause_type" : row.get("clause_type", "Unknown"),
            "risk_level"  : row.get("risk_level",  "unknown"),
            "score"       : round(score, 4),
        })
        if len(results) >= top_k:
            break

    return results