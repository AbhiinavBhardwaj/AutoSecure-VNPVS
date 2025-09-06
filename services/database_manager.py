import streamlit as st
import pandas as pd
import re
from utils.database import load_database
from config import DATABASE_PATH


def normalize_plate(text: str) -> str:
    return re.sub(r'[^A-Z0-9]', '', (text or "").upper())


def manage_database():
    """UI for viewing, adding, editing, and deleting vehicle records."""
    vehicle_db = load_database(DATABASE_PATH)

    # --- Show database ---
    if st.checkbox("Show Vehicle Database", value=True):
        st.dataframe(vehicle_db)

    # --- Add new record ---
    if st.checkbox("Add New Vehicle Record"):
        with st.form("add_vehicle_form", clear_on_submit=True):
            plate_input = st.text_input("Number Plate (e.g. MH12EM8473)")
            owner_input = st.text_input("Owner Name")
            brand_input = st.text_input("Brand")
            color_input = st.text_input("Color")
            submitted = st.form_submit_button("Save")

            if submitted:
                plate = normalize_plate(plate_input)
                owner = (owner_input or "").strip()
                brand = (brand_input or "").strip()
                color = (color_input or "").strip()

                if not plate or not owner or not brand or not color:
                    st.error("⚠️ All fields are required.")
                    return

                if not vehicle_db.empty and plate in vehicle_db["NumberPlate"].values:
                    st.warning(f"Plate `{plate}` already exists.")
                    return

                new_row = {
                    "NumberPlate": plate,
                    "OwnerName": owner,
                    "Brand": brand,
                    "Color": color,
                }

                vehicle_db = pd.concat([vehicle_db, pd.DataFrame([new_row])], ignore_index=True)
                vehicle_db.to_csv(DATABASE_PATH, index=False)
                st.success(f"✅ New record for `{plate}` added successfully.")
                st.dataframe(vehicle_db)

    # --- Edit / Delete record ---
    if st.checkbox("Edit or Delete Records"):
        if vehicle_db.empty:
            st.info("📂 Database is empty. Add a record first.")
            return

        selected_plate = st.selectbox(
            "Select Vehicle by Number Plate", vehicle_db["NumberPlate"].tolist()
        )

        if selected_plate:
            record = vehicle_db.loc[vehicle_db["NumberPlate"] == selected_plate].iloc[0]

            with st.form("edit_vehicle_form"):
                owner_edit = st.text_input("Owner Name", value=record["OwnerName"])
                brand_edit = st.text_input("Brand", value=record["Brand"])
                color_edit = st.text_input("Color", value=record["Color"])

                col1, col2 = st.columns(2)
                update_btn = col1.form_submit_button("💾 Update Record")
                delete_btn = col2.form_submit_button("🗑️ Delete Record")

                if update_btn:
                    vehicle_db.loc[
                        vehicle_db["NumberPlate"] == selected_plate,
                        ["OwnerName", "Brand", "Color"],
                    ] = [owner_edit.strip(), brand_edit.strip(), color_edit.strip()]

                    vehicle_db.to_csv(DATABASE_PATH, index=False)
                    st.success(f"✅ Record for `{selected_plate}` updated.")
                    st.dataframe(vehicle_db)

                if delete_btn:
                    vehicle_db = vehicle_db[vehicle_db["NumberPlate"] != selected_plate]
                    vehicle_db.to_csv(DATABASE_PATH, index=False)
                    st.success(f"🗑️ Record for `{selected_plate}` deleted.")
                    st.dataframe(vehicle_db)
