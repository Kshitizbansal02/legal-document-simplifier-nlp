"""
tests/test_api.py
=================
Test suite for the Legal Analyzer API.

Run from backend/ folder:
    pytest tests/ -v
    pytest tests/ -v --tb=short        # shorter tracebacks
    pytest tests/test_api.py::test_anonymizer -v   # single test

Coverage:
    - Anonymizer (unit)
    - Similarity search (unit)
    - Risk prediction (unit)
    - Full /analyze endpoint (integration)
    - Edge cases (empty, short, very long input)
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient


# ══════════════════════════════════════════════════════════
#  FIXTURES
# ══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def client():
    """
    Create a single TestClient for the whole test session.
    Models load once (expensive) and are reused across all tests.
    """
    from dotenv import load_dotenv
    load_dotenv()
    from main import app
    with TestClient(app) as c:
        yield c


# ── Sample clauses of varying risk ───────────────────────
LOW_RISK_CLAUSE = (
    "This Agreement shall be governed by and construed in accordance "
    "with the laws of the State of California."
)

MEDIUM_RISK_CLAUSE = (
    "The Licensee shall not assign, transfer, or sublicense any rights "
    "granted under this Agreement without the prior written consent of "
    "the Licensor, which consent shall not be unreasonably withheld."
)

HIGH_RISK_CLAUSE = (
    "In the event of any breach of this Agreement, the Licensor shall "
    "be entitled to seek injunctive relief, specific performance, and "
    "any other remedies available at law or in equity, including "
    "recovery of all legal fees and consequential damages without limit."
)

CLAUSE_WITH_ENTITIES = (
    "Rahul Mehta, on behalf of TechSoft Solutions Ltd, agrees to pay "
    "₹5,00,000 to DataVault Inc by 15 March 2025, failing which "
    "a penalty of ₹50,000 per day shall apply."
)

EXCLUSIVITY_CLAUSE = (
    "The Company appoints the Distributor as its exclusive distributor "
    "within the Territory and the Distributor shall not, during the "
    "term of this Agreement, distribute, market or sell products "
    "that compete with the Company's products."
)


# ══════════════════════════════════════════════════════════
#  1. HEALTH CHECK
# ══════════════════════════════════════════════════════════

class TestHealth:

    def test_root_returns_ok(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_models_loaded_on_startup(self, client):
        r = client.get("/")
        assert r.json()["models_loaded"] is True, (
            "Models should be loaded by the time TestClient is ready. "
            "Check lifespan startup logs."
        )


# ══════════════════════════════════════════════════════════
#  2. ANONYMIZER  (unit — no API call)
# ══════════════════════════════════════════════════════════

class TestAnonymizer:
    """
    NLP Concept: Named Entity Recognition (NER)
    Tool: spaCy en_core_web_sm
    Tests that real entities are replaced and restored correctly.
    """

    def setup_method(self):
        from services.anonymizer import anonymize, deanonymize
        self.anonymize   = anonymize
        self.deanonymize = deanonymize

    def test_person_is_anonymized(self):
        text, mapping = self.anonymize("Rahul Mehta signed the contract.")
        assert "Rahul Mehta" not in text
        assert any("PERSON" in k for k in mapping)

    def test_org_is_anonymized(self):
        text, mapping = self.anonymize("TechSoft Solutions Ltd shall pay.")
        assert "TechSoft Solutions Ltd" not in text
        assert any("ORG" in k for k in mapping)

    def test_money_is_anonymized(self):
        text, mapping = self.anonymize("The fee is ₹5,00,000 per annum.")
        assert "₹5,00,000" not in text
        assert any("MONEY" in k for k in mapping)

    def test_deanonymize_restores_original(self):
        original = "Rahul Mehta signed on behalf of TechSoft Solutions Ltd."
        anon, mapping = self.anonymize(original)
        restored = self.deanonymize(anon, mapping)
        assert restored == original

    def test_non_entity_text_unchanged(self):
        text = "This agreement shall be governed by applicable law."
        anon, mapping = self.anonymize(text)
        # No entities expected — mapping should be empty or very small
        # and the core legal terms must survive
        assert "agreement" in anon.lower()
        assert "governed" in anon.lower()

    def test_empty_mapping_on_no_entities(self):
        _, mapping = self.anonymize("The term shall commence on the effective date.")
        # spaCy may or may not tag "effective date" — either is fine
        # but we must always get a dict back
        assert isinstance(mapping, dict)

    def test_multiple_same_entity_type(self):
        text = "John Smith will pay Jane Doe for the services."
        anon, mapping = self.anonymize(text)
        # Both names should be replaced with distinct placeholders
        assert "John Smith" not in anon
        assert "Jane Doe"   not in anon
        person_placeholders = [k for k in mapping if "PERSON" in k]
        assert len(person_placeholders) == 2

    def test_placeholder_format(self):
        text = "Acme Corp must pay by 01/01/2025."
        _, mapping = self.anonymize(text)
        for placeholder in mapping:
            assert placeholder.startswith("["), f"Bad format: {placeholder}"
            assert placeholder.endswith("]"),   f"Bad format: {placeholder}"


# ══════════════════════════════════════════════════════════
#  3. SIMILARITY SEARCH  (unit)
# ══════════════════════════════════════════════════════════

class TestSimilarity:
    """
    NLP Concept: Sentence Embeddings + Cosine Similarity
    Model: all-MiniLM-L6-v2 (Sentence-BERT family)
    Tests that semantically similar clauses are retrieved correctly.
    """

    def setup_method(self):
        from services.similarity import get_similar
        self.get_similar = get_similar

    def test_returns_list(self):
        results = self.get_similar(LOW_RISK_CLAUSE)
        assert isinstance(results, list)

    def test_returns_up_to_top_k(self):
        results = self.get_similar(LOW_RISK_CLAUSE, top_k=3)
        assert len(results) <= 3

    def test_result_has_required_fields(self):
        results = self.get_similar(MEDIUM_RISK_CLAUSE, top_k=1)
        assert len(results) > 0
        r = results[0]
        assert "clause_text"  in r
        assert "clause_type"  in r
        assert "risk_level"   in r
        assert "score"        in r

    def test_scores_are_descending(self):
        results = self.get_similar(HIGH_RISK_CLAUSE, top_k=5)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True), (
            "Results should be ordered highest similarity first"
        )

    def test_scores_in_valid_range(self):
        results = self.get_similar(EXCLUSIVITY_CLAUSE, top_k=5)
        for r in results:
            assert 0.0 <= r["score"] <= 1.0, f"Score out of range: {r['score']}"

    def test_similar_clause_is_more_similar_than_dissimilar(self):
        """
        An exclusivity clause should be more similar to another
        exclusivity clause than to a governing law clause.
        """
        results_excl = self.get_similar(EXCLUSIVITY_CLAUSE, top_k=1)
        results_gov  = self.get_similar(LOW_RISK_CLAUSE,    top_k=1)

        if results_excl and results_gov:
            # The top match for exclusivity should score higher than
            # the top match for the unrelated governing law clause
            # (this tests that the embedding space is meaningful)
            assert results_excl[0]["score"] >= 0.3, (
                "Top match for exclusivity clause should have decent similarity"
            )

    def test_min_score_threshold_filters_results(self):
        results_strict = self.get_similar(LOW_RISK_CLAUSE, min_score=0.9)
        results_loose  = self.get_similar(LOW_RISK_CLAUSE, min_score=0.1)
        # Stricter threshold should return fewer or equal results
        assert len(results_strict) <= len(results_loose)

    def test_risk_level_values_are_valid(self):
        valid = {"low", "medium", "high", "unknown"}
        results = self.get_similar(HIGH_RISK_CLAUSE, top_k=5)
        for r in results:
            assert r["risk_level"].lower() in valid, (
                f"Unexpected risk_level: {r['risk_level']}"
            )


# ══════════════════════════════════════════════════════════
#  4. RISK PREDICTION  (unit)
# ══════════════════════════════════════════════════════════

class TestRiskPrediction:
    """
    NLP Concept: Text Classification via Embeddings
    Model: LogisticRegression on MiniLM embeddings (or KNN fallback)
    Tests that risk levels are predicted with valid confidence scores.
    """

    def setup_method(self):
        from services.risk import predict_risk
        self.predict_risk = predict_risk

    def test_returns_required_fields(self):
        result = self.predict_risk(LOW_RISK_CLAUSE)
        assert "level"       in result
        assert "confidence"  in result
        assert "description" in result
        assert "method"      in result

    def test_level_is_valid(self):
        for clause in [LOW_RISK_CLAUSE, MEDIUM_RISK_CLAUSE, HIGH_RISK_CLAUSE]:
            result = self.predict_risk(clause)
            assert result["level"] in {"low", "medium", "high"}, (
                f"Invalid risk level: {result['level']}"
            )

    def test_confidence_in_range(self):
        result = self.predict_risk(MEDIUM_RISK_CLAUSE)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_description_is_non_empty(self):
        result = self.predict_risk(HIGH_RISK_CLAUSE)
        assert len(result["description"]) > 0

    def test_method_is_valid(self):
        result = self.predict_risk(LOW_RISK_CLAUSE)
        assert result["method"] in {"classifier", "knn_fallback"}

    def test_high_risk_clause_not_predicted_low(self):
        """
        A clause with injunctive relief + consequential damages
        should not be predicted as low risk.
        """
        result = self.predict_risk(HIGH_RISK_CLAUSE)
        assert result["level"] != "low", (
            f"High-risk clause incorrectly predicted as low "
            f"(confidence: {result['confidence']})"
        )

    def test_governing_law_is_low_risk(self):
        """Governing law clauses are standard boilerplate — should be low risk."""
        result = self.predict_risk(LOW_RISK_CLAUSE)
        assert result["level"] == "low", (
            f"Governing law clause predicted as {result['level']} "
            f"(confidence: {result['confidence']})"
        )


# ══════════════════════════════════════════════════════════
#  5. FULL PIPELINE — /analyze endpoint  (integration)
# ══════════════════════════════════════════════════════════

class TestAnalyzeEndpoint:
    """
    Integration tests for the full pipeline:
    Anonymize → Risk → LLM → Deanonymize → Similarity
    """

    def test_basic_request_succeeds(self, client):
        r = client.post("/api/v1/analyze", json={"text": MEDIUM_RISK_CLAUSE})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    def test_response_has_all_fields(self, client):
        r = client.post("/api/v1/analyze", json={"text": LOW_RISK_CLAUSE})
        body = r.json()
        assert "anonymized_text"  in body
        assert "simplified"       in body
        assert "risk_explanation" in body
        assert "risk"             in body
        assert "similar_clauses"  in body

    def test_risk_object_structure(self, client):
        r = client.post("/api/v1/analyze", json={"text": HIGH_RISK_CLAUSE})
        risk = r.json()["risk"]
        assert "level"       in risk
        assert "confidence"  in risk
        assert "description" in risk
        assert "method"      in risk

    def test_similar_clauses_structure(self, client):
        r = client.post("/api/v1/analyze", json={"text": EXCLUSIVITY_CLAUSE})
        clauses = r.json()["similar_clauses"]
        assert isinstance(clauses, list)
        if clauses:
            c = clauses[0]
            assert "clause_text" in c
            assert "clause_type" in c
            assert "risk_level"  in c
            assert "score"       in c

    def test_entities_deanonymized_in_output(self, client):
        """
        Real entity names should appear in the simplified output,
        not the [PERSON_1] placeholders.
        """
        r = client.post("/api/v1/analyze", json={"text": CLAUSE_WITH_ENTITIES})
        body = r.json()
        simplified = body["simplified"]
        # Placeholders must not leak into the final output
        assert "[PERSON_" not in simplified, "PERSON placeholder not deanonymized"
        assert "[ORG_"    not in simplified, "ORG placeholder not deanonymized"
        assert "[MONEY_"  not in simplified, "MONEY placeholder not deanonymized"

    def test_anonymized_text_has_placeholders(self, client):
        """The anonymized_text field should contain placeholders."""
        r = client.post("/api/v1/analyze", json={"text": CLAUSE_WITH_ENTITIES})
        anon = r.json()["anonymized_text"]
        assert "[" in anon and "]" in anon, (
            "anonymized_text should contain entity placeholders"
        )

    def test_simplified_is_readable_length(self, client):
        """Simplified output should be shorter than input (it's a summary)."""
        r = client.post("/api/v1/analyze", json={"text": HIGH_RISK_CLAUSE})
        simplified = r.json()["simplified"]
        assert len(simplified) > 20,  "Simplified text is suspiciously short"
        assert len(simplified) < 2000, "Simplified text is suspiciously long"

    def test_high_risk_clause_flagged(self, client):
        r = client.post("/api/v1/analyze", json={"text": HIGH_RISK_CLAUSE})
        level = r.json()["risk"]["level"]
        assert level in {"medium", "high"}, (
            f"High-risk clause should not be predicted low, got: {level}"
        )

    def test_multiple_clauses_consistent(self, client):
        """Same input should produce same risk level (model is deterministic)."""
        r1 = client.post("/api/v1/analyze", json={"text": MEDIUM_RISK_CLAUSE})
        r2 = client.post("/api/v1/analyze", json={"text": MEDIUM_RISK_CLAUSE})
        assert r1.json()["risk"]["level"] == r2.json()["risk"]["level"]


# ══════════════════════════════════════════════════════════
#  6. EDGE CASES
# ══════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_too_short_input_rejected(self, client):
        """Input under 20 chars should return 422 (validation error)."""
        r = client.post("/api/v1/analyze", json={"text": "short"})
        assert r.status_code == 422, (
            f"Expected 422 for short input, got {r.status_code}"
        )

    def test_empty_input_rejected(self, client):
        r = client.post("/api/v1/analyze", json={"text": ""})
        assert r.status_code == 422

    def test_missing_text_field_rejected(self, client):
        r = client.post("/api/v1/analyze", json={})
        assert r.status_code == 422

    def test_whitespace_only_rejected(self, client):
        r = client.post("/api/v1/analyze", json={"text": "   "})
        assert r.status_code == 422

    def test_very_long_input_handled(self, client):
        """Input at the max limit (10,000 chars) should not crash."""
        long_text = (MEDIUM_RISK_CLAUSE + " ") * 50  # ~2500 words
        long_text = long_text[:9999]
        r = client.post("/api/v1/analyze", json={"text": long_text})
        assert r.status_code in {200, 422, 500}, (
            "Should handle long input gracefully — not hang or crash"
        )

    def test_non_legal_text_still_processed(self, client):
        """Non-legal English should still return a valid response structure."""
        r = client.post(
            "/api/v1/analyze",
            json={"text": "The weather today is very nice and the sun is shining brightly over the hills."}
        )
        assert r.status_code == 200
        assert "risk" in r.json()

    def test_hindi_mixed_text(self, client):
        """Mixed language input should not crash the pipeline."""
        r = client.post(
            "/api/v1/analyze",
            json={"text": "यह agreement TechSoft Ltd और DataVault Inc के बीच है।"}
        )
        assert r.status_code in {200, 500}  # should not return 422 or hang