from __future__ import annotations
import json
import logging
import os
import re
from openai import OpenAI

logger = logging.getLogger(__name__)
_MODEL = "llama-3.1-8b-instant"

def _get_client() -> OpenAI:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = """You are a legal assistant helping non-lawyers understand contract clauses.

The text you receive may contain placeholders like [PERSON_1], [ORG_2], [DATE_1], [MONEY_1].
These represent anonymized real values. You MUST include every placeholder exactly as written
in BOTH your simplified and risk_explanation outputs. Never drop, skip, paraphrase, or remove
any placeholder — if the clause mentions [MONEY_1], your output must also contain [MONEY_1].

Respond ONLY with a valid JSON object in this exact format:
{
  "simplified": "<2-3 sentence plain English summary of what this clause means>",
  "risk_explanation": "<1-2 sentences on what risk this clause poses to the signing party, or 'No significant risk.' if low risk>"
}

Rules:
- Use simple language a 16-year-old can understand
- Do not use legal jargon
- Be specific about obligations, amounts, and deadlines — include all placeholders
- Every [PLACEHOLDER] from the input must appear in your output
- Do not add any text outside the JSON object
"""


def analyze_clause(anonymized_text: str) -> dict[str, str]:
    client = _get_client()   # ← get client here, not at module level
    try:
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": anonymized_text},
            ],
            temperature=0.2,
            max_tokens=512,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        return _parse_llm_response(raw)
    except Exception as exc:
        logger.error(f"LLM call failed: {exc}")
        raise RuntimeError(f"LLM analysis failed: {exc}") from exc


def _parse_llm_response(raw: str) -> dict[str, str]:
    """
    Safely parse the LLM JSON response.

    Handles common failure modes:
      - Model wraps JSON in markdown code fences (```json ... ```)
      - Model adds a preamble sentence before the JSON
      - Model returns malformed JSON

    Returns a fallback dict rather than crashing the whole request.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()

    try:
        data = json.loads(cleaned)
        return {
            "simplified":       str(data.get("simplified", "")).strip(),
            "risk_explanation": str(data.get("risk_explanation", "")).strip(),
        }
    except json.JSONDecodeError:
        logger.warning(f"LLM returned non-JSON output: {raw[:200]}")
        # Best-effort: return raw text as simplified, flag the explanation
        return {
            "simplified":       raw[:500],
            "risk_explanation": "Could not parse structured response.",
        }