import os
import pandas as pd
import streamlit as st

def load_database(path: str) -> pd.DataFrame:
    """Load and clean vehicle database."""
    if not os.path.exists(path):
        st.error(f"Database file not found at {path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
        df["NumberPlate"] = df["NumberPlate"].str.replace(r"[^A-Z0-9]", "", regex=True).str.upper()
        return df.drop_duplicates(subset=["NumberPlate"], keep="first")
    except Exception as e:
        st.error(f"Error reading database: {e}")
        return pd.DataFrame()
