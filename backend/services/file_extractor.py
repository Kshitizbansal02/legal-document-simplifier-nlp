"""
file_extractor.py
-----------------
OCR + Multi-Format File Extraction Layer
Supports: Digital PDFs, Scanned PDFs, Images (PNG, JPG, TIFF, BMP)

Plug into your existing pipeline by calling extract_text_from_file(file_bytes, filename)
which returns a plain string ready for your /api/v1/analyze endpoint.
"""

import io
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF — for digital PDFs
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# If Tesseract is not on your PATH, set it explicitly here:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Minimum characters extracted from a PDF page before we treat it as scanned
DIGITAL_TEXT_THRESHOLD = 30

# OCR config — PSM 6 = assume uniform block of text (good for legal docs)
TESSERACT_CONFIG = "--psm 6 --oem 3"

SUPPORTED_IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
SUPPORTED_PDF_TYPE = {".pdf"}


# ─────────────────────────────────────────────
# IMAGE PREPROCESSING
# ─────────────────────────────────────────────

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Enhance image quality before OCR.
    Steps: grayscale → contrast boost → sharpen → binarize
    These steps significantly improve Tesseract accuracy on scanned legal docs.
    """
    # Convert to grayscale
    image = image.convert("L")

    # Boost contrast (helps with faded scans)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Sharpen edges (helps with blurry scans)
    image = image.filter(ImageFilter.SHARPEN)

    # Binarize using threshold (black/white — best for Tesseract)
    image = image.point(lambda x: 0 if x < 140 else 255, "1")

    return image


# ─────────────────────────────────────────────
# EXTRACTORS
# ─────────────────────────────────────────────

def extract_from_image(file_bytes: bytes) -> str:
    """
    Run OCR on a raw image file (PNG, JPG, TIFF, etc.)
    Returns extracted text string.
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        processed = preprocess_image_for_ocr(image)
        text = pytesseract.image_to_string(processed, config=TESSERACT_CONFIG)
        text = text.strip()
        if not text:
            raise ValueError("OCR returned empty text — image may be too low quality.")
        logger.info(f"Image OCR extracted {len(text)} characters.")
        return text
    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        raise


def extract_from_pdf(file_bytes: bytes) -> str:
    """
    Smart PDF extractor:
    - First tries direct digital text extraction (PyMuPDF)
    - Falls back to OCR page-by-page if the page appears scanned
    Returns full document text as a single string.
    """
    full_text = []

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        logger.info(f"PDF opened: {total_pages} pages.")

        for page_num, page in enumerate(doc):

            # ── Attempt 1: Direct digital text ──
            digital_text = page.get_text("text").strip()

            if len(digital_text) >= DIGITAL_TEXT_THRESHOLD:
                logger.debug(f"Page {page_num + 1}: digital text ({len(digital_text)} chars).")
                full_text.append(digital_text)

            # ── Attempt 2: Page looks scanned → OCR ──
            else:
                logger.debug(f"Page {page_num + 1}: sparse text, switching to OCR.")
                try:
                    # Render page to image at 300 DPI (optimal for OCR)
                    mat = fitz.Matrix(300 / 72, 300 / 72)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img_bytes = pix.tobytes("png")

                    image = Image.open(io.BytesIO(img_bytes))
                    processed = preprocess_image_for_ocr(image)
                    ocr_text = pytesseract.image_to_string(processed, config=TESSERACT_CONFIG).strip()

                    if ocr_text:
                        full_text.append(ocr_text)
                    else:
                        logger.warning(f"Page {page_num + 1}: OCR also returned empty.")

                except Exception as ocr_err:
                    logger.error(f"Page {page_num + 1} OCR failed: {ocr_err}")

        doc.close()

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise

    combined = "\n\n".join(full_text).strip()

    if not combined:
        raise ValueError("No text could be extracted from the PDF.")

    logger.info(f"PDF extraction complete: {len(combined)} total characters.")
    return combined


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Master dispatcher — detects file type and routes to correct extractor.

    Args:
        file_bytes : raw bytes of the uploaded file
        filename   : original filename with extension (used for type detection)

    Returns:
        Extracted plain text string, ready for the NLP pipeline.

    Raises:
        ValueError : if file type is unsupported or extraction fails
    """
    suffix = Path(filename).suffix.lower()

    if suffix in SUPPORTED_PDF_TYPE:
        logger.info(f"Routing '{filename}' → PDF extractor.")
        return extract_from_pdf(file_bytes)

    elif suffix in SUPPORTED_IMAGE_TYPES:
        logger.info(f"Routing '{filename}' → Image OCR extractor.")
        return extract_from_image(file_bytes)

    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Supported: PDF ({', '.join(SUPPORTED_PDF_TYPE)}) "
            f"and Images ({', '.join(SUPPORTED_IMAGE_TYPES)})"
        )
