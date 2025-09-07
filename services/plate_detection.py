import numpy as np
import cv2
import streamlit as st
from PIL import Image, ImageOps
from datetime import datetime

from models.yolo_loader import load_yolo_model
from models.ocr_loader import load_ocr_reader
from utils.preprocessing import preprocess_text
from utils.db_utils import get_residents_collection, get_logs_collection
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, OCR_LANGUAGES


def process_image(image_file):
    """Pipeline: detect → OCR → verify with MongoDB → log results"""

    # --- Load models ---
    yolo = load_yolo_model(MODEL_PATH)
    ocr = load_ocr_reader(OCR_LANGUAGES)

    if not yolo or not ocr:
        st.warning("⚠️ Failed to load YOLO or OCR models.")
        return

    # --- Load DB collections ---
    residents = get_residents_collection()
    logs = get_logs_collection()

    # --- Prepare image ---
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)  # fix orientation
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # --- Detect plates ---
    results = yolo(img_cv)[0]

    # Draw bounding boxes on original image
    annotated_img = results.plot()

    # --- Show uploaded + annotated side by side ---
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="📷 Uploaded Vehicle Image", width=350)
    with col2:
        st.image(annotated_img, caption="🔲 Detected Plates", channels="BGR", width=350)

    # 👇 Debugging: show raw YOLO detections
    st.write("Raw YOLO detections:", results.boxes.data)

    plate_detected = False
    crops = []  # store all cropped plates

    for x1, y1, x2, y2, score, _ in results.boxes.data.tolist():
        if score > CONFIDENCE_THRESHOLD:
            plate_detected = True

            # Crop detected plate
            crop = img_cv[int(y1):int(y2), int(x1):int(x2)]
            crops.append(crop)

            # OCR
            ocr_text = " ".join([res[1] for res in ocr.readtext(crop)])
            plate_number = preprocess_text(ocr_text)

            # OCR results styled
            st.markdown(
                f"**🔍 OCR Raw:** <span style='font-size:18px; color:lime;'>{ocr_text}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"**📌 Processed Plate:** <span style='font-size:20px; color:yellow;'>{plate_number}</span>",
                unsafe_allow_html=True,
            )

            # --- Verification ---
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
                    "timestamp": datetime.now(),
                    "status": status
                })
            else:
                st.warning("⚠️ No valid plate extracted.")
            break

    # --- Show all cropped plates side by side ---
    if crops:
        st.markdown("### 🎯 Detected Plate Crops")
        crop_cols = st.columns(len(crops))
        for idx, crop in enumerate(crops):
            with crop_cols[idx]:
                st.image(crop, caption=f"Plate {idx+1}", channels="BGR", width=200)

    if not plate_detected:
        st.warning("⚠️ No plate detected with sufficient confidence.")
