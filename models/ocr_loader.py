import streamlit as st
import easyocr

@st.cache_resource
def load_ocr_reader(languages=["en"]):
    """Load EasyOCR reader safely without deprecated args."""
    try:
        # ✅ No character_whitelist (EasyOCR doesn’t support it)
        reader = easyocr.Reader(languages, gpu=False)
        return reader
    except Exception as e:
        st.error(f"Error loading EasyOCR: {e}")
        return None


def run_ocr(reader, image):
    """Run OCR and filter results for license plates only."""
    if reader is None:
        return []

    try:
        results = reader.readtext(image)
        # results → [ [bbox, text, confidence], ... ]

        # ✅ Keep only uppercase letters, numbers, and dots
        cleaned = []
        for _, text, conf in results:
            filtered = "".join([ch for ch in text if ch.isalnum() or ch in [".", "-"]])
            cleaned.append((filtered.upper(), conf))
        return cleaned
    except Exception as e:
        st.error(f"OCR failed: {e}")
        return []
