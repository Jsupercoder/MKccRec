
import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="CC Reconciliation", layout="wide")
st.title("📊 Credit Card Reconciliation Tool")

# Define known vendor keywords mapped to labels
known_vendors = {
    "autozone": "Autozone",
    "o'reilly": "O'Reilly",
    "advance": "Advance",
    "chevron": "Chevron",
    "shell": "Shell",
    "walmart": "Walmart",
    "uber": "Uber",
    "planet ford": "Dealership",
    "shipley": "Shipley",
    "xl parts": "XL Parts",
    "wm": "Walmart",
    "pizza": "Food",
    "repairpal": "Office Expenses",
    "food mart": "Food Mart",
    "e&l tools": "Fixed Assets",
    "online payment": "Payment",
    "moving iron": "Sublet",
    "brenntag": "Brenntag",
    "1-800 radiator": "1-800 Radiator",
    "rob's hardware": "Office Expenses",
    "sterling mccall": "Dealership",
    "tom peacock": "Dealership",
    "gexa": "Office Expenses",
    "a-1 auto electric": "A-1 Auto Electric",
    "audi": "Dealership",
    "lmc complete": "Sublet",
    "discount-tire": "Sublet",
    "papa john's": "Food",
    "locksmiths": "Sublet",
    "family dollar": "Office Expenses",
    "republic services": "Office Expenses",
    "texan gmc": "Dealership",
    "amazon": "Amazon",
    "an cdjr": "Dealership",
    "chevron": "Gas",
    "shell": "Gas",
    "lawn": "Office Expenses",
    "youtube tv": "Office Expenses",
    "mercedes-benz": "Dealership"
}

def extract_vendor(description):
    if not isinstance(description, str):
        return "Unknown"
    desc = description.lower()
    for keyword, label in known_vendors.items():
        if keyword in desc:
            return label
    return "Other"

def clean_and_format(df, last4):
    # Show original preview for debugging
    st.write("🔍 Raw CSV preview before cleaning:")
    st.dataframe(df.head())

    # Drop completely empty columns
    df = df.dropna(axis=1, how="all")

    # Drop any column that is exactly "*"
    df = df.loc[:, ~df.apply(lambda col: col.astype(str).str.fullmatch(r"\*").all())]

    # Trim to first 3 columns if more
    if df.shape[1] > 3:
        df = df.iloc[:, :3]

    # Assign expected column names
    df.columns = ["Date", "Amount", "Description"]

    # Add Last 4 column
    df["Last 4"] = last4

    # Clean date format to date only (no time)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    # Extract vendor from description
    df["Vendor"] = df["Description"].apply(extract_vendor)

    # Reorder columns
    df = df[["Date", "Amount", "Vendor", "Last 4", "Description"]]
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

        st.success(f"✅ CSVs processed successfully — total rows: {len(combined_df)}")
        st.write("🧾 Preview of Combined Data:")
        st.dataframe(combined_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Failed to process files: {e}")
