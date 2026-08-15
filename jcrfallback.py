"""
OCR fallback for scanned / image-only PDF pages.
Used when a page yields little or no extractable text via PyMuPDF.
"""

import pytesseract
from PIL import Image
import fitz  # PyMuPDF


def page_to_image(page: "fitz.Page", zoom: float = 2.0) -> Image.Image:
    """Render a PDF page to a PIL Image at a given zoom factor (higher = better OCR accuracy)."""
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def ocr_page(page: "fitz.Page", lang: str = "eng") -> str:
    """Run OCR on a single PDF page and return extracted text."""
    img = page_to_image(page)
    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def needs_ocr(extracted_text: str, min_chars: int = 20) -> bool:
    """Heuristic: if a page's native text extraction is near-empty, treat it as scanned."""
    return len(extracted_text.strip()) < min_chars
  
