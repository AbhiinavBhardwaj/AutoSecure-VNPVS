import streamlit as st
import cv2
import pandas as pd
import numpy as np
import re
from PIL import Image, ImageOps
from typing import Optional
import easyocr
import os
from ultralytics import YOLO

# --- CONFIGURATION ---
MODEL_PATH = "yolov8n-license-plate.pt"
DATABASE_PATH = "vehicle_database.csv"
CONFIDENCE_THRESHOLD = 0.5
OCR_LANGUAGES = ['en']

# --- HELPER FUNCTIONS ---

@st.cache_resource
def load_yolo_model(path):
    """Loads the YOLOv8 model from the specified path."""
    if not os.path.exists(path):
        st.error(f"Model file not found at: {path}. Please make sure the YOLO model is in the correct directory.")
        return None
    try:
        model = YOLO(path)
        return model
    except Exception as e:
        st.error(f"Error loading YOLO model: {e}")
        return None

@st.cache_resource
def load_ocr_reader(languages):
    """Loads the EasyOCR reader."""
    try:
        # gpu=False is safer for broader compatibility
        reader = easyocr.Reader(languages, gpu=False)
        return reader
    except Exception as e:
        st.error(f"Error loading EasyOCR model: {e}")
        return None

def load_database(path):
    """Loads the vehicle database from a CSV file."""
    if not os.path.exists(path):
        st.error(f"Database file not found at: {path}. Please create a 'vehicle_database.csv'.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        # Standardize number plate format in the database for reliable matching
        df['NumberPlate'] = df['NumberPlate'].str.replace(r'[^A-Z0-9]', '', regex=True).str.upper()

        return df.drop_duplicates(subset=['NumberPlate'], keep='first')
    except Exception as e:
        st.error(f"Error loading or processing database: {e}")
        return pd.DataFrame()

def preprocess_text(raw_text):
    """
    Extracts the most likely Indian license plate number from raw OCR text
    using a series of regular expressions.
    using a series of regular expressions, now returns Optional[str].
    """
    # Combine all parts of the text and convert to uppercase for consistent matching
    cleaned_text = re.sub(r'[^A-Z0-9]', '', raw_text.upper())

    # Most common modern format: XX00XX0000 (e.g., MH12EM8473)
    match = re.search(r'([A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4})', cleaned_text)
    if match:
        return match.group(1)

    # Common format with single letter series: XX00X0000 (e.g., HR26U5478)
    match = re.search(r'([A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4})', cleaned_text)
    if match:
        return match.group(1)
        
    # Format for some states: XX00[A-Z]0000 (e.g., DL5C1234)
    match = re.search(r'([A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4})', cleaned_text)
    if match:
        return match.group(1)

    # If no specific pattern is found, return None to indicate failure
    # If no pattern is found, return None to indicate failure
    return None


# --- MAIN APPLICATION LOGIC ---

def process_image(image_file):
    """Main function to process an uploaded image."""
    # Load models and database
    # Load models and the database
    yolo_model = load_yolo_model(MODEL_PATH)
    ocr_reader = load_ocr_reader(OCR_LANGUAGES)
    vehicle_db = load_database(DATABASE_PATH)

    if yolo_model is None or ocr_reader is None or vehicle_db.empty:
        st.warning("One or more essential components failed to load. Please check the setup and file paths.")
        return

    # Convert image to a format OpenCV can use
    img = Image.open(image_file)
    # Correct the orientation based on EXIF data
    img = ImageOps.exif_transpose(img)
   # img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB_BGR)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


    st.image(img, caption="Uploaded Vehicle Image", use_column_width=True)

    # 1. Number Plate Detection
    results = yolo_model(img_cv)[0]

    plate_detected = False
    plate_detected: bool = False
    for res in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = res

        if score > CONFIDENCE_THRESHOLD:
            plate_detected = True

            # Crop the detected plate region
            plate_crop = img_cv[int(y1):int(y2), int(x1):int(x2)]

            # Display detected plate
            st.image(plate_crop, caption="Detected License Plate", channels="BGR")

            # 2. OCR: Number Extraction
            ocr_results = ocr_reader.readtext(plate_crop)

            if not ocr_results:
                st.warning("OCR could not extract any text from the license plate.")
                continue

            # Combine OCR results and post-process text
            raw_text = " ".join([res[1] for res in ocr_results])
            plate_number = preprocess_text(raw_text)

            st.write(f"**Extracted Text (Raw):** `{raw_text}`")

            # 3. Database Verification
            if plate_number:
                st.write(f"**Processed Number Plate:** `{plate_number}`")
                db_record = vehicle_db[vehicle_db['NumberPlate'] == plate_number]

                # 4. Decision Logic
                if not db_record.empty:
                    # Case: Plate Found in DB
                    db_brand = db_record['Brand'].iloc[0]
                    db_color = db_record['Color'].iloc[0]
                    db_owner = db_record['OwnerName'].iloc[0]

                    st.info(f"**Database Record Found:** Owner: `{db_owner}`, Brand: `{db_brand}`, Color: `{db_color}`")
                    st.success("✅ **Verified Vehicle:** This number plate is present in the database.")
                else:
                    # Case: Plate Not Found in DB
                    st.error("❌ **Unverified Vehicle:** This number plate was NOT FOUND in the database.")
                    st.error("❌ **Unverified Vehicle:** This number plate was not found in the database.")
            else:
                st.warning("Could not extract a valid number plate from the OCR text.")

            # Stop after processing the first high-confidence detection
            break

    if not plate_detected:
        st.warning("No license plate was detected in the image with sufficient confidence.")


# --- STREAMLIT FRONTEND ---

st.set_page_config(page_title="Vehicle Number Plate Verification", layout="wide")

#st.title("🇮🇳 Vehicle Number Plate Verification")
st.title("🇮🇳 Vehicle Numberplate Verification")
st.markdown("Upload a vehicle image to detect the license plate and verify it against a database.")

image_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png"])

if image_file:
    # A button to trigger the analysis
    if st.button("Analyze Vehicle"):
        with st.spinner("Processing image... This may take a moment."):
            process_image(image_file)
