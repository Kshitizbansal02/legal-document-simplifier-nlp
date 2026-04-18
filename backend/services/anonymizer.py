"""
services/anonymizer.py
======================
Privacy-preserving anonymization before sending text to external LLMs.

WHY THE OLD VERSION WAS BROKEN
--------------------------------
The old regex approach matched ANY two capitalized words as a PERSON:
    "This Agreement" → [PERSON_1]
    "The Distributor" → [PERSON_2]
    "Unless Earlier"  → [PERSON_3]

This corrupted the text before it reached the LLM, producing nonsense output.

NEW APPROACH
------------
We use spaCy's en_core_web_sm model for NER, which understands context.
"The Distributor" is correctly identified as ORG, not PERSON.
"This Agreement" is not an entity at all.

Regex is kept ONLY as a fallback for patterns spaCy misses in legal text:
  - Indian/formatted money  (₹1,00,000)
  - Structured dates spaCy sometimes skips

ANONYMIZATION CONTRACT
----------------------
anonymize(text) → (anonymized_text, mapping)
deanonymize(text, mapping) → original_text

The mapping is a plain dict {placeholder: original_value}.
Both functions are pure — no side effects, safe to call from threads.
"""

from __future__ import annotations
import re
import spacy

# Load once at module level — spaCy models are small (~12 MB), safe to do here.
# If you need to avoid this, pass the nlp object in instead.
try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )

# Entity labels we want to anonymize before sending to external LLM
_ANONYMIZE_LABELS = {"PERSON", "ORG", "GPE", "DATE", "MONEY", "CARDINAL"}

# Regex patterns for things spaCy misses in dense legal text
_FALLBACK_PATTERNS: list[tuple[str, str]] = [
    ("MONEY", r"₹\s?\d+(?:,\d+)*(?:\.\d+)?"),          # ₹1,00,000
    ("DATE",  r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),          # 01/04/2024
]


def anonymize(text: str) -> tuple[str, dict[str, str]]:
    """
    Replace named entities with stable placeholders.

    Returns
    -------
    anonymized_text : str
        Text with entities replaced, e.g. "John Smith" → "[PERSON_1]"
    mapping : dict
        {placeholder → original_value} for deanonymization later.

    Example
    -------
    >>> txt, m = anonymize("Acme Ltd must pay ₹50,000 to John Doe by 01/01/2025.")
    >>> txt
    '[ORG_1] must pay [MONEY_1] to [PERSON_1] by [DATE_1].'
    >>> m
    {'[ORG_1]': 'Acme Ltd', '[MONEY_1]': '₹50,000', ...}
    """
    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}

    # ── Stage 1: spaCy NER ───────────────────────────────────────────────────
    doc = _nlp(text)

    # Process longest spans first to avoid partial replacements
    # e.g. replace "Acme Corp Ltd" before "Acme Corp"
    entities = sorted(doc.ents, key=lambda e: len(e.text), reverse=True)

    for ent in entities:
        if ent.label_ not in _ANONYMIZE_LABELS:
            continue
        original = ent.text.strip()
        if not original or original in mapping.values():
            # Already mapped under a different span (overlap) — skip
            continue

        label = ent.label_
        counters[label] = counters.get(label, 0) + 1
        placeholder = f"[{label}_{counters[label]}]"
        mapping[placeholder] = original
        # Replace all occurrences of this exact string in the text
        text = text.replace(original, placeholder)

    # ── Stage 2: Regex fallback ──────────────────────────────────────────────
    for label, pattern in _FALLBACK_PATTERNS:
        for match in re.findall(pattern, text):
            if match in mapping.values():
                continue  # already caught by spaCy
            counters[label] = counters.get(label, 0) + 1
            placeholder = f"[{label}_{counters[label]}]"
            mapping[placeholder] = match
            text = text.replace(match, placeholder)

    return text, mapping


def deanonymize(text: str, mapping: dict[str, str]) -> str:
    """
    Restore original values from placeholders.

    Always call this on LLM output before returning to the user.
    The LLM may reorder words but should preserve placeholders verbatim.

    Example
    -------
    >>> deanonymize("[PERSON_1] signed on [DATE_1].", {"[PERSON_1]": "John", "[DATE_1]": "Monday"})
    'John signed on Monday.'
    """
    for placeholder, original in mapping.items():
        text = text.replace(placeholder, original)
    return text