"""
services/validator.py
=====================
Pre-pipeline validation layer.

Rejects input that is clearly not a legal clause or contract text
BEFORE it hits the expensive NLP pipeline (embedder, LLM, classifier).

DESIGN
------
Three-stage check, fastest to slowest:

  1. Length & character sanity   — instant, no imports needed
  2. Legal keyword heuristics    — fast set lookup
  3. spaCy entity/structure check — uses already-loaded spaCy model

Any stage can reject. All three must pass to proceed.

WHY NOT USE THE LLM TO VALIDATE?
---------------------------------
That would cost an API call for every invalid input — expensive and slow.
These heuristics catch 99% of junk (chat messages, code, random text, 
emojis, single words) in microseconds.
"""

from __future__ import annotations
import re
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# LEGAL KEYWORD SETS
# ─────────────────────────────────────────────

# Must contain at least MIN_KEYWORD_HITS of these to pass
LEGAL_KEYWORDS = {
    # Parties & roles
    "party", "parties", "licensee", "licensor", "licensors", "licensees",
    "licensor's", "licensee's", "employer", "employee", "contractor",
    "subcontractor", "vendor", "client", "customer", "supplier", "assignee",
    "assignor", "indemnitor", "indemnitee", "obligor", "obligee",

    # Agreement types
    "agreement", "contract", "clause", "provision", "terms", "conditions",
    "amendment", "addendum", "schedule", "exhibit", "annex", "appendix",
    "memorandum", "undertaking", "covenant", "deed", "instrument",

    # Legal actions & obligations
    "shall", "must", "hereby", "herein", "hereof", "hereto", "hereunder",
    "thereof", "thereto", "thereunder", "wherein", "whereby", "whereas",
    "notwithstanding", "pursuant", "subject to", "in accordance with",
    "assign", "sublicense", "transfer", "terminate", "indemnify",
    "warrant", "represent", "covenant", "disclose", "execute", "enforce",

    # Legal concepts
    "liability", "indemnification", "confidential", "proprietary",
    "intellectual property", "copyright", "trademark", "patent",
    "jurisdiction", "governing law", "arbitration", "dispute",
    "breach", "default", "remedy", "damages", "injunction",
    "force majeure", "waiver", "severability", "entire agreement",
    "consent", "approval", "notice", "obligation", "right", "rights",
    "license", "sublicense", "royalty", "fee", "payment", "term",
    "termination", "renewal", "expiration", "effective date",

    # Structural markers
    "section", "article", "subsection", "paragraph", "clause",
    "exhibit", "schedule", "recital", "whereas", "now therefore",
}

# Instant-reject patterns — if text matches these it's clearly not legal
REJECT_PATTERNS = [
    r"^\s*[\U00010000-\U0010ffff\u2600-\u27BF\uFE00-\uFE0F]+\s*$",  # emoji only
    r"^(hi|hello|hey|yo|sup|what'?s up|how are you)[.!?\s]*$",        # greetings
    r"^https?://\S+$",                                                  # just a URL
    r"^[\d\s\+\-\*\/\(\)\.]+$",                                        # only numbers/math
    r"^(select|insert|update|delete|drop|create|alter)\s+",            # SQL
    r"^(def |class |import |from |#|//).*",                            # code
]

# Thresholds
MIN_CHARS         = 20
MAX_CHARS         = 50_000
MIN_KEYWORD_HITS  = 1     # at least 1 legal keyword required
MIN_WORD_COUNT    = 5


# ─────────────────────────────────────────────
# VALIDATION RESULT
# ─────────────────────────────────────────────

class ValidationResult:
    def __init__(self, valid: bool, reason: str = ""):
        self.valid  = valid
        self.reason = reason

    def __bool__(self):
        return self.valid

    def __repr__(self):
        return f"ValidationResult(valid={self.valid}, reason={self.reason!r})"


# ─────────────────────────────────────────────
# MAIN VALIDATOR
# ─────────────────────────────────────────────

def validate_legal_text(text: str) -> ValidationResult:
    """
    Validate that input text is likely a legal clause or contract excerpt.

    Parameters
    ----------
    text : Raw input text (before anonymization)

    Returns
    -------
    ValidationResult with .valid (bool) and .reason (str) if invalid
    """

    # ── Stage 1: Basic sanity ─────────────────────────────────────────────────
    if not text or not text.strip():
        return ValidationResult(False, "Input is empty.")

    text_stripped = text.strip()

    if len(text_stripped) < MIN_CHARS:
        return ValidationResult(
            False,
            f"Input is too short ({len(text_stripped)} characters). "
            f"Please provide a complete legal clause."
        )

    if len(text_stripped) > MAX_CHARS:
        return ValidationResult(
            False,
            f"Input is too long ({len(text_stripped):,} characters). "
            f"Maximum allowed is {MAX_CHARS:,} characters."
        )

    word_count = len(text_stripped.split())
    if word_count < MIN_WORD_COUNT:
        return ValidationResult(
            False,
            f"Input has only {word_count} words. Please provide a complete clause."
        )

    # ── Stage 2: Instant-reject patterns ─────────────────────────────────────
    text_lower = text_stripped.lower()

    for pattern in REJECT_PATTERNS:
        if re.match(pattern, text_stripped, re.IGNORECASE):
            return ValidationResult(
                False,
                "Input does not appear to be a legal document or clause. "
                "Please paste a contract clause or upload a legal document."
            )

    # ── Stage 3: Legal keyword check ─────────────────────────────────────────
    hits = sum(1 for kw in LEGAL_KEYWORDS if kw in text_lower)

    if hits < MIN_KEYWORD_HITS:
        return ValidationResult(
            False,
            "Input does not appear to contain legal language. "
            "Please provide a contract clause or legal document excerpt. "
            "Examples: assignment clauses, confidentiality clauses, "
            "termination provisions, etc."
        )

    logger.debug(f"Validation passed: {len(text_stripped)} chars, {hits} legal keyword hits")
    return ValidationResult(True)


# ─────────────────────────────────────────────
# CONVENIENCE WRAPPER — raises HTTP exception directly
# ─────────────────────────────────────────────

def validate_or_raise(text: str) -> None:
    """
    Validate text and raise FastAPI HTTPException if invalid.
    Import and call this at the top of your route handlers.

    Usage:
        from services.validator import validate_or_raise
        validate_or_raise(req.text)
    """
    from fastapi import HTTPException, status

    result = validate_legal_text(text)
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input: {result.reason}",
        )
