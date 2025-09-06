import streamlit as st
from services.plate_detection import process_image
from services.database_manager import manage_database

st.set_page_config(page_title="Vehicle Number Plate Verification", layout="wide")

st.title("🇮🇳 Vehicle Numberplate Verification")
st.markdown("Upload a vehicle image to detect and verify its license plate against the database.")

# Single uploader
image_file = st.file_uploader("Upload Vehicle Image", type=["jpg", "jpeg", "png"], key="vehicle_upload")

if image_file and st.button("Analyze Vehicle", key="analyze_vehicle"):
    with st.spinner("Processing..."):
        process_image(image_file)

# Database section
manage_database()
