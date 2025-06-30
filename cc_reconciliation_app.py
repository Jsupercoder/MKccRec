import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.set_page_config(page_title="CC Reconciliation - Google Sheets", layout="wide")
st.title("📊 Credit Card Reconciliation to Google Sheets")

def extract_vendor(description):
    if not isinstance(description, str):
        return "Unknown"
    known_vendors = ["Autozone", "O'Reilly", "Advance", "Chevron", "Shell", "Walmart", "Amazon"]
    for vendor in known_vendors:
        if re.search(vendor, description, re.IGNORECASE):
            return vendor
    return "Other"

def clean_and_format(df, last4):
    df.columns = ["Date", "Amount", "Description"]
    df["Last 4"] = last4
    df["Vendor"] = df["Description"].apply(extract_vendor)
    df = df[["Date", "Amount", "Vendor", "Last 4", "Description"]]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

st.subheader("Step 1: Upload Your Credit Card CSVs")

col1, col2 = st.columns(2)
with col1:
    cc6_file = st.file_uploader("Upload CreditCard6.csv", type="csv")
with col2:
    cc7_file = st.file_uploader("Upload CreditCard7.csv", type="csv")

if cc6_file and cc7_file:
    try:
    df6 = pd.read_csv(cc6_file, header=None)
    df7 = pd.read_csv(cc7_file, header=None)
    df6_cleaned = clean_and_format(df6, "0078")
    df7_cleaned = clean_and_format(df7, "3896")

    combined_df = pd.concat([df6_cleaned, df7_cleaned], ignore_index=True)
    combined_df = combined_df.sort_values("Date")

    st.success("✅ CSVs processed successfully.")
    st.write("🧾 Preview of Combined Data:")
    st.dataframe(combined_df.head())

except Exception as e:
    st.error(f"❌ Failed to process files: {e}")
