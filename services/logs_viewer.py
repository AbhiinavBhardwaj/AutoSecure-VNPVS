import streamlit as st
from utils.db_utils import get_logs_collection

def view_logs():
    st.subheader("📜 Detection Logs")
    logs = list(get_logs_collection().find({}, {"_id": 0}))
    if logs:
        st.dataframe(logs)
    else:
        st.info("No logs yet.")
