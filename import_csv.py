import pandas as pd
from utils.db_utils import get_residents_collection

# --- Load CSV ---
csv_path = "data/vehicle_database.csv"
df = pd.read_csv(csv_path)

# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower()  # remove spaces & lowercase all

# --- MongoDB collection ---
residents = get_residents_collection()

# --- Helper to safely convert values to strings ---
def safe_str(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

# --- Column mapping from CSV to DB fields ---
COLUMN_MAP = {
    "numberplate": "plate",
    "ownername": "owner",
    "brand": "brand",
    "color": "color"
}

# --- Insert rows into MongoDB ---
for _, row in df.iterrows():
    # Prepare the document
    doc = {}
    for csv_col, db_field in COLUMN_MAP.items():
        if csv_col in row:
            doc[db_field] = safe_str(row[csv_col])
        else:
            doc[db_field] = ""  # fallback if column missing

    # Uppercase the plate
    doc["plate"] = doc["plate"].upper()

    # Avoid duplicates
    if not residents.find_one({"plate": doc["plate"]}):
        residents.insert_one(doc)

print("✅ CSV imported into MongoDB successfully!")
