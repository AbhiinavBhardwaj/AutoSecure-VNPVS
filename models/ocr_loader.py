import streamlit as st
import easyocr

@st.cache_resource
def load_ocr_reader(languages):
    """Load EasyOCR reader safely."""
    try:
        return easyocr.Reader(languages, gpu=False)
    except Exception as e:
        st.error(f"Error loading EasyOCR: {e}")
        return None
