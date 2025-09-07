import streamlit as st
from utils.db_utils import get_residents_collection

def normalize_plate(text: str) -> str:
    import re
    return re.sub(r'[^A-Z0-9]', '', (text or "").upper())


def manage_database():
    """UI for viewing, adding, editing, and deleting vehicle records (MongoDB)."""
    residents = get_residents_collection()

    # --- Show database ---
    if st.checkbox("Show Vehicle Database", value=True):
        data = list(residents.find({}, {"_id": 0}))
        if data:
            st.dataframe(data)
        else:
            st.info("📂 Database is empty. Add a record first.")

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

                if residents.find_one({"plate": plate}):
                    st.warning(f"Plate `{plate}` already exists.")
                    return

                residents.insert_one({
                    "plate": plate,
                    "owner": owner,
                    "brand": brand,
                    "color": color
                })
                st.success(f"✅ New record for `{plate}` added successfully.")

    # --- Edit / Delete record ---
    if st.checkbox("Edit or Delete Records"):
        data = list(residents.find({}, {"_id": 0}))
        if not data:
            st.info("📂 Database is empty. Add a record first.")
            return

        plates = [d["plate"] for d in data]
        selected_plate = st.selectbox("Select Vehicle by Number Plate", plates)

        if selected_plate:
            record = residents.find_one({"plate": selected_plate}, {"_id": 0})

            with st.form("edit_vehicle_form"):
                owner_edit = st.text_input("Owner Name", value=record["owner"])
                brand_edit = st.text_input("Brand", value=record["brand"])
                color_edit = st.text_input("Color", value=record["color"])

                col1, col2 = st.columns(2)
                update_btn = col1.form_submit_button("💾 Update Record")
                delete_btn = col2.form_submit_button("🗑️ Delete Record")

                if update_btn:
                    residents.update_one(
                        {"plate": selected_plate},
                        {"$set": {
                            "owner": owner_edit.strip(),
                            "brand": brand_edit.strip(),
                            "color": color_edit.strip()
                        }}
                    )
                    st.success(f"✅ Record for `{selected_plate}` updated.")

                if delete_btn:
                    residents.delete_one({"plate": selected_plate})
                    st.success(f"🗑️ Record for `{selected_plate}` deleted.")
