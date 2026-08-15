import json
import streamlit as st

from extractors.pdf_extractor import extract_pdf
from extractors.docx_extractor import extract_docx
from utils.json_builder import build_structured_json

st.set_page_config(page_title="Book → JSON Converter", page_icon="📚", layout="centered")

st.title("📚 Book / Textbook → Structured JSON")
st.caption("Upload a PDF or Word file. Get back a structured JSON with detected chapters and page-level text.")

with st.expander("⚠️ Personal use note", expanded=False):
    st.write(
        "This tool is meant for converting books you personally own or have "
        "legal access to, for your own study/reference. It doesn't include "
        "any feature to publish or share the generated JSON with other users."
    )

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx"])
ocr_enabled = st.checkbox("Enable OCR fallback for scanned pages", value=True)
size_ratio = st.slider(
    "Heading sensitivity (higher = fewer, bigger headings detected)",
    min_value=1.05, max_value=2.0, value=1.25, step=0.05,
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.name.split(".")[-1].lower()
    title = uploaded_file.name.rsplit(".", 1)[0]

    if st.button("Convert to JSON", type="primary"):
        progress_bar = st.progress(0, text="Starting extraction...")

        def progress_callback(current, total):
            progress_bar.progress(current / total, text=f"Processing page {current}/{total}")

        with st.spinner("Extracting text..."):
            if file_type == "pdf":
                pages = extract_pdf(file_bytes, ocr_enabled=ocr_enabled, progress_callback=progress_callback)
            elif file_type == "docx":
                pages = extract_docx(file_bytes)
            else:
                st.error("Unsupported file type.")
                st.stop()

        progress_bar.progress(1.0, text="Building structured JSON...")
        result = build_structured_json(pages, title=title, size_ratio=size_ratio)
        progress_bar.empty()

        st.success(f"Done. Detected {result['chapter_count']} chapter(s) across {len(pages)} page unit(s).")

        st.subheader("Preview")
        st.json(result, expanded=False)

        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_str,
            file_name=f"{title}.json",
            mime="application/json",
        )
else:
    st.info("Upload a PDF or DOCX file to begin.")
  
