"""
=============================================================
  AI-Powered Legal Document Simplification & Explanation System
  Author  : [Your Name]
  Version : 1.0
  Description:
      Converts complex government/legal text into plain,
      accessible language using NLP techniques:
        - Abstractive Summarization  (BART / T5)
        - Named Entity Recognition   (spaCy)
        - Readability Scoring        (textstat – Flesch Reading Ease)
        - Paraphrasing               (T5 paraphrase model)
=============================================================
"""

import re
import warnings
warnings.filterwarnings("ignore")

# ── third-party ────────────────────────────────────────────
import spacy
import textstat
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# ── constants ──────────────────────────────────────────────
SUMMARIZER_MODEL   = "facebook/bart-large-cnn"
PARAPHRASE_MODEL   = "Vamsi/T5_Paraphrase_Paws"   # lightweight T5 paraphraser
MAX_CHUNK_TOKENS   = 900   # BART max is 1024; leave headroom
SUMMARY_MAX_NEW    = 180
SUMMARY_MIN_NEW    = 60


# ══════════════════════════════════════════════════════════
#  1.  MODEL LOADING  (cached – called once)
# ══════════════════════════════════════════════════════════

def load_models() -> dict:
    """
    Load and return all NLP models.
    Call once at startup and reuse throughout the session.
    """
    print("[INFO] Loading NLP models – this may take a moment on first run …")

    summarizer = pipeline(
        "summarization",
        model=SUMMARIZER_MODEL,
        device=-1          # CPU; change to 0 for GPU
    )

    para_tokenizer = AutoTokenizer.from_pretrained(PARAPHRASE_MODEL)
    para_model     = AutoModelForSeq2SeqLM.from_pretrained(PARAPHRASE_MODEL)

    nlp_spacy = spacy.load("en_core_web_sm")

    print("[INFO] All models loaded successfully.\n")

    return {
        "summarizer"     : summarizer,
        "para_tokenizer" : para_tokenizer,
        "para_model"     : para_model,
        "spacy"          : nlp_spacy,
    }


# ══════════════════════════════════════════════════════════
#  2.  TEXT PRE-PROCESSING
# ══════════════════════════════════════════════════════════

def preprocess(text: str) -> str:
    """
    Clean raw legal text:
      • Collapse excess whitespace
      • Remove page-break artefacts
      • Normalise smart quotes / dashes
    """
    text = re.sub(r"\s+", " ", text)              # collapse whitespace
    text = re.sub(r"[''`]", "'", text)            # normalise apostrophes
    text = re.sub(r"[""«»]", '"', text)           # normalise quotes
    text = re.sub(r"[–—]", "-", text)             # normalise dashes
    text = re.sub(r"\b(Ibid|Id\.|Op\.cit\.)\b",  # strip legal citations
                  "", text, flags=re.IGNORECASE)
    return text.strip()


def chunk_text(text: str, max_words: int = 400) -> list[str]:
    """
    Split long documents into sentence-aware chunks
    so the summarizer never exceeds its token limit.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current, count = [], [], 0

    for sent in sentences:
        word_len = len(sent.split())
        if count + word_len > max_words and current:
            chunks.append(" ".join(current))
            current, count = [sent], word_len
        else:
            current.append(sent)
            count += word_len

    if current:
        chunks.append(" ".join(current))

    return chunks


# ══════════════════════════════════════════════════════════
#  3.  NAMED ENTITY RECOGNITION  (spaCy)
# ══════════════════════════════════════════════════════════

LEGAL_ENTITY_LABELS = {
    "PERSON"   : "Person / Party",
    "ORG"      : "Organisation / Institution",
    "GPE"      : "Country / State / City",
    "LAW"      : "Law / Act / Statute",
    "DATE"     : "Date / Time Period",
    "MONEY"    : "Monetary Value",
    "CARDINAL" : "Section / Clause Number",
    "ORDINAL"  : "Order / Rank",
    "PERCENT"  : "Percentage",
    "NORP"     : "Nationality / Group",
}

def extract_entities(text: str, nlp) -> list[dict]:
    """
    Run spaCy NER and return a structured list of entities
    relevant to legal documents.

    Returns:
        [{"entity": str, "label": str, "description": str}, …]
    """
    doc = nlp(text)
    seen = set()
    entities = []

    for ent in doc.ents:
        key = (ent.text.strip(), ent.label_)
        if key in seen or ent.label_ not in LEGAL_ENTITY_LABELS:
            continue
        seen.add(key)
        entities.append({
            "entity"      : ent.text.strip(),
            "label"       : ent.label_,
            "description" : LEGAL_ENTITY_LABELS[ent.label_],
        })

    return entities


# ══════════════════════════════════════════════════════════
#  4.  ABSTRACTIVE SUMMARIZATION  (BART)
# ══════════════════════════════════════════════════════════

def summarize(text: str, summarizer) -> str:
    """
    Summarise legal text using BART.
    Handles long documents by chunking and concatenating summaries.
    """
    cleaned = preprocess(text)
    chunks  = chunk_text(cleaned, max_words=400)

    partial_summaries = []
    for i, chunk in enumerate(chunks):
        # Skip very short chunks (likely headings / artefacts)
        if len(chunk.split()) < 30:
            partial_summaries.append(chunk)
            continue

        result = summarizer(
            chunk,
            max_new_tokens = SUMMARY_MAX_NEW,
            min_new_tokens = SUMMARY_MIN_NEW,
            do_sample      = False,
            truncation     = True,
        )
        partial_summaries.append(result[0]["summary_text"])

    return " ".join(partial_summaries).strip()


# ══════════════════════════════════════════════════════════
#  5.  PARAPHRASING  (T5)
# ══════════════════════════════════════════════════════════

def paraphrase(text: str, tokenizer, model, num_beams: int = 5) -> str:
    """
    Paraphrase the summarised text using a T5-based model
    to further simplify vocabulary and sentence structure.
    """
    input_text = f"paraphrase: {text} </s>"
    inputs = tokenizer.encode(
        input_text,
        return_tensors = "pt",
        max_length     = 512,
        truncation     = True,
    )

    outputs = model.generate(
        inputs,
        max_new_tokens   = 256,
        num_beams        = num_beams,
        num_return_sequences = 1,
        early_stopping   = True,
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# ══════════════════════════════════════════════════════════
#  6.  READABILITY SCORING  (Flesch Reading Ease)
# ══════════════════════════════════════════════════════════

FLESCH_LABELS = [
    (90,  "Very Easy  – understood by 11-year-old"),
    (80,  "Easy       – conversational English"),
    (70,  "Fairly Easy"),
    (60,  "Standard   – 13–15 year old level"),
    (50,  "Fairly Difficult"),
    (30,  "Difficult  – college-educated reader"),
    (0,   "Very Confusing – professional / academic"),
]

def readability_label(score: float) -> str:
    for threshold, label in FLESCH_LABELS:
        if score >= threshold:
            return label
    return "Very Confusing"

def readability_scores(original: str, simplified: str) -> dict:
    """
    Compute Flesch Reading Ease and Flesch-Kincaid Grade Level
    for both the original and simplified texts.

    Flesch Reading Ease: 0–100 (higher = easier to read)
    FK Grade Level: school-grade equivalent (lower = simpler)
    """
    def safe_score(fn, txt):
        try:
            return round(fn(txt), 1)
        except Exception:
            return 0.0

    orig_fre  = safe_score(textstat.flesch_reading_ease,         original)
    simp_fre  = safe_score(textstat.flesch_reading_ease,         simplified)
    orig_fkg  = safe_score(textstat.flesch_kincaid_grade,        original)
    simp_fkg  = safe_score(textstat.flesch_kincaid_grade,        simplified)
    orig_dcr  = safe_score(textstat.dale_chall_readability_score, original)
    simp_dcr  = safe_score(textstat.dale_chall_readability_score, simplified)

    return {
        "original" : {
            "flesch_reading_ease"  : orig_fre,
            "flesch_kincaid_grade" : orig_fkg,
            "dale_chall"           : orig_dcr,
            "label"                : readability_label(orig_fre),
        },
        "simplified" : {
            "flesch_reading_ease"  : simp_fre,
            "flesch_kincaid_grade" : simp_fkg,
            "dale_chall"           : simp_dcr,
            "label"                : readability_label(simp_fre),
        },
        "improvement" : round(simp_fre - orig_fre, 1),
    }


# ══════════════════════════════════════════════════════════
#  7.  MAIN PIPELINE
# ══════════════════════════════════════════════════════════

def simplify_legal_document(text: str, models: dict) -> dict:
    """
    Full pipeline:
        Input → Preprocess → NER → Summarize → Paraphrase
             → Readability Score → Structured Output

    Args:
        text   : Raw legal / government document text
        models : Dict returned by load_models()

    Returns:
        result dict with keys:
            original_text, preprocessed_text, summary,
            simplified_text, entities, readability
    """
    # ── Stage 1 : Preprocess ──────────────────────────────
    preprocessed = preprocess(text)

    # ── Stage 2 : Named Entity Recognition ───────────────
    entities = extract_entities(preprocessed, models["spacy"])

    # ── Stage 3 : Abstractive Summarization ──────────────
    summary = summarize(preprocessed, models["summarizer"])

    # ── Stage 4 : Paraphrase (simplify vocabulary) ───────
    simplified = paraphrase(
        summary,
        models["para_tokenizer"],
        models["para_model"],
    )

    # ── Stage 5 : Readability Scores ─────────────────────
    scores = readability_scores(text, simplified)

    return {
        "original_text"    : text,
        "preprocessed_text": preprocessed,
        "summary"          : summary,
        "simplified_text"  : simplified,
        "entities"         : entities,
        "readability"      : scores,
    }


# ══════════════════════════════════════════════════════════
#  8.  OUTPUT FORMATTING
# ══════════════════════════════════════════════════════════

def format_output(result: dict) -> str:
    """
    Pretty-print the pipeline output to the console.
    """
    sep = "=" * 65
    lines = [
        sep,
        "  AI-POWERED LEGAL DOCUMENT SIMPLIFICATION SYSTEM",
        sep,
        "",
        "📄  ORIGINAL TEXT (first 300 chars):",
        result["original_text"][:300] + " …",
        "",
        "─" * 65,
        "✅  SIMPLIFIED TEXT:",
        result["simplified_text"],
        "",
        "─" * 65,
        "🏷️   EXTRACTED ENTITIES:",
    ]

    if result["entities"]:
        for ent in result["entities"]:
            lines.append(f"   • {ent['entity']:30s}  [{ent['description']}]")
    else:
        lines.append("   No named entities detected.")

    rd = result["readability"]
    lines += [
        "",
        "─" * 65,
        "📊  READABILITY SCORES:",
        f"   Flesch Reading Ease  │ Before: {rd['original']['flesch_reading_ease']:5.1f}"
        f"  →  After: {rd['simplified']['flesch_reading_ease']:5.1f}"
        f"  (+{rd['improvement']:.1f})",
        f"   FK Grade Level       │ Before: {rd['original']['flesch_kincaid_grade']:5.1f}"
        f"  →  After: {rd['simplified']['flesch_kincaid_grade']:5.1f}",
        f"   Original Label  : {rd['original']['label']}",
        f"   Simplified Label: {rd['simplified']['label']}",
        "",
        sep,
    ]

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
#  9.  DEMO  (run as standalone script)
# ══════════════════════════════════════════════════════════

SAMPLE_LEGAL_TEXT = """
WHEREAS, the Party of the First Part (hereinafter referred to as the "Licensor")
is the owner of certain intellectual property rights, including but not limited to
patents, trademarks, and copyrights, pertaining to the Software (as defined herein),
and WHEREAS, the Party of the Second Part (hereinafter referred to as the "Licensee")
desires to obtain a non-exclusive, non-transferable, limited license to use the
Software solely for internal business purposes, subject to the terms and conditions
set forth herein; NOW, THEREFORE, in consideration of the mutual covenants and
agreements contained herein, and for other good and valuable consideration, the
receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:
1. LICENSE GRANT. Subject to the terms and conditions of this Agreement, Licensor
hereby grants to Licensee a non-exclusive, non-transferable, revocable license to
use the Software in object code form only, solely for Licensee's internal business
operations. This license does not include the right to sublicense, modify, adapt,
translate, reverse engineer, decompile, disassemble, or create derivative works
based on the Software.
"""

if __name__ == "__main__":
    models = load_models()
    result = simplify_legal_document(SAMPLE_LEGAL_TEXT, models)
    print(format_output(result))
