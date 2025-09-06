import os
import streamlit as st
from ultralytics import YOLO

@st.cache_resource
def load_yolo_model(path: str):
    """Loads YOLOv8 model from given path."""
    if not os.path.exists(path):
        st.error(f"Model not found at: {path}")
        return None
    try:
        return YOLO(path)
    except Exception as e:
        st.error(f"Error loading YOLO: {e}")
        return None
