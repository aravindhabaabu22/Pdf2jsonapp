# Book → JSON Converter

Converts PDF or Word (.docx) textbooks into structured JSON with detected
chapters and page-level text. Includes OCR fallback for scanned pages.

## Output shape

```json
{
  "title": "My Book",
  "chapter_count": 5,
  "chapters": [
    {
      "heading": "Chapter 1: Introduction",
      "pages": [
        { "page_num": 3, "text": "...", "ocr_used": false }
      ]
    }
  ]
}
