# 🇮🇳 Vehicle Number Plate Verification

This project is a **Streamlit web app** that detects and verifies Indian vehicle number plates.  
It uses **YOLOv8** for license plate detection and **EasyOCR** for text extraction. The extracted plate number is then checked against a database (`vehicle_database.csv`).

---

## 🚀 Features
- Upload vehicle images (`.jpg`, `.jpeg`, `.png`).
- Detect license plates using YOLOv8.
- Extract text (plate numbers) using EasyOCR.
- Preprocess and validate number plate format (e.g., `MH12EM8473`).
- Verify against a local database of registered vehicles.
- Show results with owner details, brand, and color.

---

## 📂 Project Structure
```
.
├── app.py                  # Main Streamlit app
├── yolov8n-license-plate.pt # YOLO model file (must be downloaded separately)
├── vehicle_database.csv    # Vehicle database (CSV format)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## ⚙️ Installation

1. **Clone this repository**  
```bash
git clone https://github.com/your-username/vehicle-number-plate-verification.git
cd vehicle-number-plate-verification
```

2. **Create a virtual environment (recommended)**  
```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. **Install dependencies**  
```bash
pip install -r requirements.txt
```

4. **Download YOLOv8 license plate model**  
Make sure you have the file `yolov8n-license-plate.pt` in the project root directory.  
(You can train your own or download a pre-trained model.)

5. **Prepare Vehicle Database**  
Create a file named `vehicle_database.csv` with the following structure:
```csv
NumberPlate,OwnerName,Brand,Color
MH12EM8473,Rahul Sharma,Maruti Suzuki,White
DL5C1234,Amit Verma,Hyundai,Red
KA01AB1234,Pooja Nair,Honda,Black
```

---

## ▶️ Usage
Run the app with:
```bash
streamlit run app.py
```

Upload a vehicle image and click **Analyze Vehicle**.  
You’ll see:
- Uploaded vehicle image
- Detected license plate
- Extracted text from OCR
- Verification result against database

---

## 📌 Example Output
- ✅ Verified Vehicle → Shows owner, brand, and color.  
- ❌ Unverified Vehicle → Number plate not found in database.  
- ⚠️ Warning if OCR or YOLO fails.

---

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) – UI Framework
- [YOLOv8 (Ultralytics)](https://github.com/ultralytics/ultralytics) – License Plate Detection
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) – Text Recognition
- [OpenCV](https://opencv.org/) – Image Processing
- [Pandas](https://pandas.pydata.org/) – Database Handling

---

## 📜 License
This project is for educational purposes only.  
Make sure to comply with your country’s data privacy and surveillance laws.
