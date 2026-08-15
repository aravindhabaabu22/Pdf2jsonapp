"""
DOCX extraction: pulls paragraphs with style-based font-size metadata,
so the same heading-detection logic in json_builder can be reused.

Word documents don't have "pages" in the file format itself (pagination is
a rendering-time concept), so we treat each paragraph as its own pseudo-page
unit, numbered sequentially. This keeps the JSON shape consistent with the
PDF extractor's output.
"""

import io
from typing import List, Dict, Any
from docx import Document


def _style_font_size(paragraph) -> float:
    """Best-effort font size lookup: run-level size, else style-level size, else default 12."""
    for run in paragraph.runs:
        if run.font and run.font.size:
            return run.font.size.pt
    if paragraph.style and paragraph.style.font and paragraph.style.font.size:
        return paragraph.style.font.size.pt
    # Heading styles in docx often carry size only via the style hierarchy;
    # fall back to inferring from style name.
    name = (paragraph.style.name or "").lower()
    if "heading 1" in name or "title" in name:
        return 20.0
    if "heading 2" in name:
        return 17.0
    if "heading" in name:
        return 15.0
    return 12.0


def extract_docx(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Returns a list of pseudo-page dicts, one per paragraph, matching the
    PDF extractor's shape so json_builder can process either source:
        {"page_num": int, "blocks": [{"text": str, "font_size": float}], "ocr_used": False}
    """
    doc = Document(io.BytesIO(file_bytes))
    pages_out = []

    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        font_size = _style_font_size(paragraph)
        pages_out.append({
            "page_num": i + 1,
            "blocks": [{"text": text, "font_size": font_size}],
            "ocr_used": False,
        })

    return pages_out
  
