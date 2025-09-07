import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from datetime import datetime
import re

from ultralytics import YOLO
from paddleocr import PaddleOCR

from utils.db_utils import get_residents_collection, get_logs_collection
from config import MODEL_PATH, CONFIDENCE_THRESHOLD

# ------------------------
# 1️⃣ Initialize OCR + YOLO
# ------------------------
ocr = PaddleOCR(use_angle_cls=True, lang="en")  # high-accuracy OCR
yolo = YOLO(MODEL_PATH)  # YOLOv8 custom model

# ------------------------
# 2️⃣ Preprocess OCR text
# ------------------------
def preprocess_text(ocr_text: str):
    """
    Clean OCR output to extract valid Indian license plate numbers.
    Format examples:
        MH43D9740, DL1CAB1234, GJ05AB6789
    """
    if not ocr_text:
        return None
    cleaned = re.sub(r"[^A-Z0-9]", "", ocr_text.upper())
    match = re.match(r"[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}", cleaned)
    return match.group() if match else None

# ------------------------
# 3️⃣ Main detection pipeline
# ------------------------
def process_image(image_file):
    """
    Full pipeline:
    1. Load image
    2. YOLO plate detection
    3. PaddleOCR recognition
    4. DB verification + logging
    5. Streamlit display
    """

    # --- Load DB ---
    residents = get_residents_collection()
    logs = get_logs_collection()

    # --- Load and prepare image ---
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)  # fix orientation
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # --- YOLO detection ---
    results = yolo.predict(img_cv, conf=CONFIDENCE_THRESHOLD)
    annotated_img = results[0].plot()

    # --- Display uploaded vs annotated ---
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="📷 Uploaded Vehicle Image", width=350)
    with col2:
        st.image(annotated_img, caption="🔲 Detected Plates", channels="BGR", width=350)

    # --- Debug raw YOLO detections ---
    st.write("Raw YOLO detections:", results[0].boxes.data)

    plate_number = None
    crops = []

    # --- Loop over YOLO detections ---
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        score = float(box.conf[0])

        if score < CONFIDENCE_THRESHOLD:
            continue

        # Crop plate
        crop = img_cv[y1:y2, x1:x2]
        crops.append(crop)

        # OCR via PaddleOCR
        ocr_result = ocr.ocr(crop, cls=True)
        #ocr_text = "".join([line[1][0] for line in ocr_result]) if ocr_result else ""
        ocr_text = "".join(
    item[1][0] if isinstance(item[1][0], str) else "".join(item[1][0])
    for line in ocr_result
    for item in line
)

        plate_number = preprocess_text(ocr_text)

        # Display OCR
        st.markdown(
            f"**🔍 OCR Raw:** <span style='font-size:18px; color:lime;'>{ocr_text}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**📌 Processed Plate:** <span style='font-size:20px; color:yellow;'>{plate_number}</span>",
            unsafe_allow_html=True,
        )

        # --- DB verification & logging ---
        if plate_number:
            match = residents.find_one({"plate": plate_number})
            status = "VERIFIED" if match else "UNREGISTERED"

            if match:
                st.success(
                    f"✅ Verified: {match['owner']} | {match['brand']} | {match['color']}"
                )
            else:
                st.error("❌ Plate not found in resident database.")

            logs.insert_one({
                "plate": plate_number,
                "timestamp": datetime.utcnow(),
                "status": status
            })
            break  # stop after first valid plate

    # --- Display all plate crops ---
    if crops:
        st.markdown("### 🎯 Detected Plate Crops")
        for idx, crop in enumerate(crops):
            st.image(crop, caption=f"Plate {idx+1}", channels="BGR", width=200)

    if not crops:
        st.warning("⚠️ No plate detected with sufficient confidence.")
    elif not plate_number:
        st.warning("⚠️ OCR could not extract a valid plate from detected crops.")
