"""
PDF extraction: pulls text blocks with font-size metadata (for heading
detection) from each page, using OCR fallback for scanned/image pages.
"""

import fitz  # PyMuPDF
from typing import List, Dict, Any, Callable, Optional

from utils.ocr_fallback import ocr_page, needs_ocr


def extract_pdf(
    file_bytes: bytes,
    ocr_enabled: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[Dict[str, Any]]:
    """
    Returns a list of page dicts:
        {"page_num": int, "blocks": [{"text": str, "font_size": float}], "ocr_used": bool}

    progress_callback(current_page, total_pages) is called after each page,
    useful for driving a Streamlit progress bar.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_out = []
    total = len(doc)

    for i, page in enumerate(doc):
        page_dict = page.get_text("dict")
        blocks_out = []
        native_text_chars = 0

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # 0 = text block, 1 = image block
                continue
            for line in block.get("lines", []):
                line_text = "".join(span["text"] for span in line.get("spans", []))
                if not line_text.strip():
                    continue
                # use the font size of the first span as representative
                font_size = line["spans"][0]["size"] if line.get("spans") else 12.0
                blocks_out.append({"text": line_text.strip(), "font_size": round(font_size, 1)})
                native_text_chars += len(line_text.strip())

        ocr_used = False
        if ocr_enabled and needs_ocr("".join(b["text"] for b in blocks_out)):
            ocr_text = ocr_page(page)
            if ocr_text:
                blocks_out = [{"text": ocr_text, "font_size": 12.0}]
                ocr_used = True

        pages_out.append({
            "page_num": i + 1,
            "blocks": blocks_out,
            "ocr_used": ocr_used,
        })

        if progress_callback:
            progress_callback(i + 1, total)

    doc.close()
    return pages_out
                  
