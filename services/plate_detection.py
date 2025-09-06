import cv2
import streamlit as st
from PIL import Image, ImageOps

from models.yolo_loader import load_yolo_model
from models.ocr_loader import load_ocr_reader
from utils.database import load_database
from utils.preprocessing import preprocess_text
from config import MODEL_PATH, DATABASE_PATH, CONFIDENCE_THRESHOLD, OCR_LANGUAGES

def process_image(image_file):
    """Pipeline: detect → OCR → verify with DB"""
    yolo = load_yolo_model(MODEL_PATH)
    ocr = load_ocr_reader(OCR_LANGUAGES)
    db = load_database(DATABASE_PATH)

    if not yolo or not ocr or db.empty:
        st.warning("One or more essential components failed to load.")
        return

    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    st.image(img, caption="Uploaded Vehicle Image", use_column_width=True)

    results = yolo(img_cv)[0]

    for x1, y1, x2, y2, score, _ in results.boxes.data.tolist():
        if score > CONFIDENCE_THRESHOLD:
            crop = img_cv[int(y1):int(y2), int(x1):int(x2)]
            st.image(crop, caption="Detected Plate", channels="BGR")

            ocr_text = " ".join([res[1] for res in ocr.readtext(crop)])
            plate_number = preprocess_text(ocr_text)
            st.write(f"**OCR Raw:** `{ocr_text}`")

            if plate_number:
                st.write(f"**Processed Plate:** `{plate_number}`")
                match = db[db["NumberPlate"] == plate_number]
                if not match.empty:
                    st.success(f"✅ Verified: {match.iloc[0]['OwnerName']} | {match.iloc[0]['Brand']} | {match.iloc[0]['Color']}")
                else:
                    st.error("❌ Plate not found in database.")
            else:
                st.warning("No valid plate extracted.")
            break
    else:
        st.warning("No plate detected with sufficient confidence.")
