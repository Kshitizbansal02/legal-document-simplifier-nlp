import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from dotenv import load_dotenv
    load_dotenv()
    from main import app
    with TestClient(app) as c:
        yield c

def make_png_bytes(text: str = "The licensee shall not assign any rights without prior written consent.") -> bytes:
    """Burn text onto a white PNG — simulates a scanned legal document."""
    img  = Image.new("RGB", (700, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 35), text, fill="black")
    buf  = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_digital_pdf_bytes(text: str = "The licensee shall not assign or sublicense any rights.") -> bytes:
    """Create a minimal single-page digital PDF with selectable text."""
    import fitz
    doc  = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf  = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ─────────────────────────────────────────────
# FILE EXTRACTOR UNIT TESTS
# ─────────────────────────────────────────────

class TestFileExtractor:

    def test_digital_pdf_extracts_text(self):
        from services.file_extractor import extract_from_pdf
        result = extract_from_pdf(make_digital_pdf_bytes())
        assert isinstance(result, str)
        assert len(result) > 10
        assert "licensee" in result.lower()

    def test_image_png_extracts_via_ocr(self):
        from services.file_extractor import extract_from_image
        result = extract_from_image(make_png_bytes())
        assert isinstance(result, str)
        assert len(result) > 5

    def test_unsupported_extension_raises_value_error(self):
        from services.file_extractor import extract_text_from_file
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_file(b"dummy", "contract.docx")

    def test_blank_image_raises_value_error(self):
        from services.file_extractor import extract_from_image
        blank = Image.new("RGB", (200, 200), color="white")
        buf   = io.BytesIO()
        blank.save(buf, format="PNG")
        with pytest.raises(ValueError, match="empty"):
            extract_from_image(buf.getvalue())

    def test_dispatcher_routes_pdf_correctly(self):
        from services.file_extractor import extract_text_from_file
        result = extract_text_from_file(make_digital_pdf_bytes(), "contract.pdf")
        assert len(result) > 10

    def test_dispatcher_routes_image_correctly(self):
        from services.file_extractor import extract_text_from_file
        result = extract_text_from_file(make_png_bytes(), "scan.png")
        assert isinstance(result, str)


# ─────────────────────────────────────────────
# UPLOAD ENDPOINT INTEGRATION TESTS
# ─────────────────────────────────────────────

class TestUploadEndpoint:
    """Uses the TestClient fixture from your existing conftest.py"""

    def test_digital_pdf_returns_200(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.pdf", make_digital_pdf_bytes(), "application/pdf")},
        )
        assert response.status_code == 200

    def test_response_has_all_analyze_fields(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.pdf", make_digital_pdf_bytes(), "application/pdf")},
        )
        data = response.json()
        assert "simplified"       in data
        assert "risk"             in data
        assert "similar_clauses"  in data
        assert "anonymized_text"  in data
        assert "risk_explanation" in data

    def test_response_has_extraction_meta(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.pdf", make_digital_pdf_bytes(), "application/pdf")},
        )
        meta = response.json()["extraction_meta"]
        assert meta["filename"]             == "contract.pdf"
        assert meta["file_type"]            == ".pdf"
        assert meta["characters_extracted"]  > 0
        assert meta["extraction_method"]    in ("digital", "ocr", "pdf_mixed")

    def test_png_image_upload_returns_200(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("scan.png", make_png_bytes(), "image/png")},
        )
        assert response.status_code == 200
        assert response.json()["extraction_meta"]["extraction_method"] == "ocr"

    def test_unsupported_type_returns_415(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.docx", b"dummy content here", "application/vnd.openxmlformats")},
        )
        assert response.status_code == 415

    def test_empty_file_returns_400(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400

    def test_oversized_file_returns_413(self, client: TestClient):
        big = b"x" * (11 * 1024 * 1024)  # 11 MB
        response = client.post(
            "/api/v1/upload",
            files={"file": ("big.pdf", big, "application/pdf")},
        )
        assert response.status_code == 413

    def test_risk_fields_present(self, client: TestClient):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.pdf", make_digital_pdf_bytes(), "application/pdf")},
        )
        risk = response.json()["risk"]
        assert risk["level"]      in ("low", "medium", "high")
        assert 0.0 <= risk["confidence"] <= 1.0
        assert "description"      in risk
        assert "method"           in risk
