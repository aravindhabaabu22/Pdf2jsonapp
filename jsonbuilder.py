"""
Turns a flat list of {page_num, blocks:[{text, font_size, is_heading}]}
into a nested chapter -> pages -> text JSON structure.

Heading detection strategy:
  - Compute the median font size across the whole document (body text size).
  - Any text block whose font size is meaningfully larger than the median,
    and which is short (few words, like a title line), is treated as a heading.
  - A new heading starts a new chapter; text until the next heading is
    nested under that chapter.
"""

import statistics
from typing import List, Dict, Any


def _median_font_size(pages: List[Dict[str, Any]]) -> float:
    sizes = []
    for page in pages:
        for block in page.get("blocks", []):
            if block["text"].strip():
                sizes.append(block["font_size"])
    return statistics.median(sizes) if sizes else 12.0


def _is_heading(block: Dict[str, Any], median_size: float, size_ratio: float = 1.25) -> bool:
    text = block["text"].strip()
    if not text:
        return False
    word_count = len(text.split())
    is_large = block["font_size"] >= median_size * size_ratio
    is_short = word_count <= 12
    return is_large and is_short


def build_structured_json(
    pages: List[Dict[str, Any]],
    title: str = "Untitled Document",
    size_ratio: float = 1.25,
) -> Dict[str, Any]:
    """
    pages: list of {
        "page_num": int,
        "blocks": [{"text": str, "font_size": float}],
        "ocr_used": bool
    }
    Returns nested JSON: {title, chapters: [{heading, pages: [{page_num, text, ocr_used}]}]}
    """
    median_size = _median_font_size(pages)

    chapters = []
    current_chapter = {"heading": "Preface", "pages": []}

    for page in pages:
        page_num = page["page_num"]
        ocr_used = page.get("ocr_used", False)
        blocks = page.get("blocks", [])

        page_text_parts = []
        for block in blocks:
            text = block["text"].strip()
            if not text:
                continue

            if _is_heading(block, median_size, size_ratio):
                # Close out current chapter, start a new one
                if current_chapter["pages"]:
                    chapters.append(current_chapter)
                elif current_chapter["heading"] != "Preface":
                    chapters.append(current_chapter)
                current_chapter = {"heading": text, "pages": []}
            else:
                page_text_parts.append(text)

        page_text = "\n".join(page_text_parts).strip()
        if page_text:
            current_chapter["pages"].append({
                "page_num": page_num,
                "text": page_text,
                "ocr_used": ocr_used,
            })

    # append the last chapter being built
    if current_chapter["pages"] or current_chapter["heading"] != "Preface":
        chapters.append(current_chapter)

    # drop an empty leading "Preface" chapter if nothing landed in it
    chapters = [c for c in chapters if c["pages"]]

    return {
        "title": title,
        "chapter_count": len(chapters),
        "chapters": chapters,
  }
  
