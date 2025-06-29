import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(page_title="CC Reconciliation Tool", layout="wide")
st.title("💳 Credit Card Reconciliation Tool")

label_map = {
    "1-800 radiator": "1-800 RADIATOR",
    "a-1 auto": "A-1 AUTO ELECTRIC",
    "advance auto": "ADVANCE",
    "autozone": "AUTOZONE",
    "brenntag": "BRENNTAG",
    "o'reilly": "O'REILLY",
    "xl parts": "XL PARTS",
    "amazon": "AMAZON",
    "walmart": "WALMART",
    "cdjr": "DEALERSHIP",
    "mercedes-benz": "DEALERSHIP",
    "tom peacock": "DEALERSHIP",
    "planet ford": "DEALERSHIP",
    "chevron": "GAS",
    "shell": "GAS",
    "exxon": "GAS",
    "mobil": "GAS",
    "fixed asset": "FIXED ASSET",
    "sublet": "SUBLET",
    "office depot": "OFFICE EXP",
    "staples": "OFFICE EXP",
}

cog_labels = [
    "1-800 RADIATOR", "A-1 AUTO ELECTRIC", "ADVANCE", "AUTOZONE",
    "BRENNTAG", "DEALERSHIP", "O'REILLY", "XL PARTS", "OTHER COG"
]
other_labels = [
    "AMAZON", "FIXED ASSET", "GAS", "SUBLET", "OFFICE EXP", "WALMART"
]

def label_expense(description):
    desc = str(description).lower()
    if "online payment thank you" in desc:
        return "Payment"
    for keyword, label in label_map.items():
        if keyword in desc:
            return label
    return "OTHER COG"

def get_expense_group(label):
    if label in cog_labels:
        return "COG"
    elif label in other_labels:
        return "Other Expenses"
    elif label == "Payment":
        return "Payment"
    else:
        return "Uncategorized"

def process_file(uploaded_file, last4):
    df = pd.read_csv(uploaded_file, header=None)
    df.dropna(axis=1, how="all", inplace=True)
    df = df.loc[:, ~df.apply(lambda col: col.astype(str).str.fullmatch(r"\*").all())]

    st.write(f"🔍 Preview of card ending in {last4}:")
    st.dataframe(df.head())
    st.write("📋 Detected columns:", df.columns.tolist())

    if df.shape[1] == 3:
        df.columns = ["Post Date", "Amount", "Description"]
    elif df.shape[1] == 4:
        df.columns = ["Post Date", "Amount", "Description", "Memo"]
    elif df.shape[1] == 5:
        df = df.drop(df.columns[2], axis=1)
        df.columns = ["Post Date", "Amount", "Description", "Memo"]
    else:
        st.error("❌ Unrecognized column layout.")
        return pd.DataFrame()

    df.insert(0, "Card Last 4", last4)
    return df[["Card Last 4", "Post Date", "Amount", "Description"]]

st.subheader("Upload Your Credit Card CSVs")
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload CreditCard6.csv (Last 4: 0078)", type="csv")
with col2:
    file2 = st.file_uploader("Upload CreditCard7.csv (Last 4: 3896)", type="csv")

parts_file = st.file_uploader("Upload POS Parts Report", type="csv")

if file1 and file2:
    cc6 = process_file(file1, "0078")
    cc7 = process_file(file2, "3896")

    if not cc6.empty and not cc7.empty:
        combined = pd.concat([cc6, cc7], ignore_index=True)

        combined["Post Date"] = pd.to_datetime(combined["Post Date"], errors="coerce")
        combined["Amount"] = pd.to_numeric(combined["Amount"], errors="coerce")
        combined["Label"] = combined["Description"].apply(label_expense)
        combined["Group"] = combined["Label"].apply(get_expense_group)
        combined.drop_duplicates(subset=["Card Last 4", "Post Date", "Amount", "Description"], inplace=True)

        if parts_file:
            parts_df = pd.read_csv(parts_file)
            parts_df.columns = [col.strip() for col in parts_df.columns]
            parts_df["Date"] = pd.to_datetime(parts_df["Date"], errors="coerce")
            parts_df["Amount"] = pd.to_numeric(parts_df["Amount"], errors="coerce")

            def is_fuzzy_matched(row):
                date_range = (parts_df["Date"] >= row["Post Date"] - timedelta(days=1)) & \
                             (parts_df["Date"] <= row["Post Date"] + timedelta(days=1))
                amount_match = abs(parts_df["Amount"] - row["Amount"]) < 0.01
                return (date_range & amount_match).any()

            combined["Matched"] = combined.apply(is_fuzzy_matched, axis=1)
        else:
            combined["Matched"] = False

        report1 = combined.sort_values(by="Post Date")
        report2 = combined.sort_values(by=["Label", "Post Date"])

