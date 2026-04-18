"""
app/schemas.py
==============
Pydantic models for request/response validation.

These serve as the contract between frontend and backend.
Every field is typed and documented so the auto-generated
FastAPI docs (/docs) are useful to teammates.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=20,
        max_length=10_000,
        description="The legal clause or contract text to analyze.",
        examples=["The Licensee shall not sublicense or transfer any rights without prior written consent."]
    )

    @field_validator("text")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class SimilarClause(BaseModel):
    clause_text  : str   = Field(..., description="Text of the similar clause from the database")
    clause_type  : str   = Field(..., description="Category of the clause (e.g. Exclusivity)")
    risk_level   : str   = Field(..., description="Risk label of this database clause")
    score        : float = Field(..., description="Cosine similarity score (0–1, higher = more similar)")


class RiskResult(BaseModel):
    level       : str   = Field(..., description="Predicted risk level: low | medium | high")
    confidence  : float = Field(..., description="Model confidence in prediction (0–1)")
    description : str   = Field(..., description="Plain English description of the risk level")
    method      : str   = Field(..., description="How risk was determined: classifier | knn_fallback")


class AnalyzeResponse(BaseModel):
    anonymized_text  : str               = Field(..., description="Input text with entities replaced by placeholders")
    simplified       : str               = Field(..., description="Plain English explanation of the clause")
    risk_explanation : str               = Field(..., description="Why this clause may be risky")
    risk             : RiskResult
    similar_clauses  : List[SimilarClause]