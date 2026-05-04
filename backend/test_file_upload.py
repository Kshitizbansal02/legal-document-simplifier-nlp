"""
test_file_upload.py
-------------------
pytest tests for the OCR + file upload layer.
Add to your existing tests/ folder and run with: python -m pytest tests/ -v
"""

import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

# ── adjust import if your app entry point is named differently ──
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_png_bytes(text: str = "The licensee shall not assign any rights.") -> bytes:
    """Create a minimal PNG image with text burned in — simulates a scanned doc."""
    img = Image.new("RGB", (600, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_pdf_bytes_digital() -> bytes:
    """Create a minimal single-page digital PDF using PyMuPDF."""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "The licensee shall not assign or sublicense any rights.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ─────────────────────────────────────────────
# FILE EXTRACTOR UNIT TESTS
# ─────────────────────────────────────────────

class TestFileExtractor:

    def test_extract_from_digital_pdf(self):
        """Digital PDF should extract text without OCR."""
        from file_extractor import extract_from_pdf
        pdf_bytes = make_pdf_bytes_digital()
        result = extract_from_pdf(pdf_bytes)
        assert isinstance(result, str)
        assert len(result) > 10
        assert "licensee" in result.lower()

    def test_extract_from_image_png(self):
        """PNG image should go through OCR and return text."""
        from file_extractor import extract_from_image
        png_bytes = make_png_bytes("The party shall not disclose confidential information.")
        result = extract_from_image(png_bytes)
        assert isinstance(result, str)
        assert len(result) > 5

    def test_unsupported_file_type_raises(self):
        """Unsupported extension should raise ValueError."""
        from file_extractor import extract_text_from_file
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_file(b"dummy content", "contract.docx")

    def test_empty_image_raises(self):
        """Blank white image should raise ValueError (no OCR text)."""
        from file_extractor import extract_from_image
        blank = Image.new("RGB", (200, 200), color="white")
        buf = io.BytesIO()
        blank.save(buf, format="PNG")
        with pytest.raises(ValueError, match="empty"):
            extract_from_image(buf.getvalue())

    def test_dispatcher_routes_pdf(self):
        """extract_text_from_file should route .pdf to pdf extractor."""
        from file_extractor import extract_text_from_file
        pdf_bytes = make_pdf_bytes_digital()
        result = extract_text_from_file(pdf_bytes, "contract.pdf")
        assert len(result) > 10

    def test_dispatcher_routes_image(self):
        """extract_text_from_file should route .png to image extractor."""
        from file_extractor import extract_text_from_file
        png_bytes = make_png_bytes()
        result = extract_text_from_file(png_bytes, "scan.png")
        assert isinstance(result, str)


# ─────────────────────────────────────────────
# UPLOAD ENDPOINT INTEGRATION TESTS
# ─────────────────────────────────────────────

class TestUploadEndpoint:

    def test_upload_digital_pdf_success(self):
        """Digital PDF upload should return 200 with analysis + extraction_meta."""
        pdf_bytes = make_pdf_bytes_digital()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "simplified" in data
        assert "risk" in data
        assert "extraction_meta" in data
        assert data["extraction_meta"]["file_type"] == ".pdf"

    def test_upload_png_image_success(self):
        """PNG image upload should go through OCR and return analysis."""
        png_bytes = make_png_bytes()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("scan.png", png_bytes, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "simplified" in data
        assert data["extraction_meta"]["extraction_method"] == "ocr"

    def test_upload_unsupported_type_returns_415(self):
        """Uploading a .docx should return 415 Unsupported Media Type."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("contract.docx", b"dummy", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert response.status_code == 415

    def test_upload_empty_file_returns_400(self):
        """Empty file should return 400."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400

    def test_upload_oversized_file_returns_413(self):
        """File exceeding 10MB should return 413."""
        big_file = b"x" * (11 * 1024 * 1024)  # 11 MB
        response = client.post(
            "/api/v1/upload",
            files={"file": ("big.pdf", big_file, "application/pdf")},
        )
        assert response.status_code == 413

    def test_extraction_meta_fields_present(self):
        """Response must include all extraction_meta fields."""
        pdf_bytes = make_pdf_bytes_digital()
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.pdf", pdf_bytes, "application/pdf")},
        )
        meta = response.json().get("extraction_meta", {})
        assert "filename" in meta
        assert "file_type" in meta
        assert "characters_extracted" in meta
        assert "extraction_method" in meta
        assert meta["characters_extracted"] > 0
