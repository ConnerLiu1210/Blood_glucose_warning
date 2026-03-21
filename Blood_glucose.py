from pathlib import Path
import pandas as pd


# File paths
DATA_DIR = Path("data")

FULL_REDCAP_PATH = DATA_DIR / "Full REDCap Data Intervention for Dexcom FINAL.xlsx"
MASTER_CLARITY_PATH = DATA_DIR / "Master Clarity log 1-101 for Dexcom FINAL.xlsx"
SECONDARY_CGM_PATH = DATA_DIR / "Final Seconary CGM cohort pull_uncleaned.xlsx"


# Load Excel files
def load_excel_files():
    print("Loading Excel files...")

    full_redcap = pd.read_excel(FULL_REDCAP_PATH)
    master_clarity = pd.read_excel(MASTER_CLARITY_PATH)
    secondary_cgm = pd.read_excel(SECONDARY_CGM_PATH, sheet_name=None)

    # strip column names to avoid hidden spaces
    full_redcap.columns = full_redcap.columns.str.strip()
    master_clarity.columns = master_clarity.columns.str.strip()

    print("Loaded successfully.")
    return full_redcap, master_clarity, secondary_cgm


# Clean Master Clarity
def clean_master_clarity(master_clarity):
    df = master_clarity.copy()

    # rename damaged timestamp column
    for col in df.columns:
        if "imes" in str(col):
            df = df.rename(columns={col: "Timestamp"})
            break

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df[df["Sub ID"].notna()].copy()
    df = df[df["Timestamp"].notna()].copy()

    df["Glucose_raw"] = df["Glucose Value (mg/dL)"].astype(str).str.strip()
    df["Glucose_text_upper"] = df["Glucose_raw"].str.upper()
    df["Glucose_numeric"] = pd.to_numeric(df["Glucose_raw"], errors="coerce")

    df["Is_High"] = (
        (df["Glucose_text_upper"] == "HIGH") |
        (df["Glucose_numeric"] > 400)
    ).astype(int)

    df = df.sort_values(["Sub ID", "Timestamp"]).reset_index(drop=True)

    print("Cleaned Master Clarity shape:", df.shape)
    print("High count:", df["Is_High"].sum())

    return df


# Filter validated ongoing CGM/POC pairs from Full REDCap
def filter_validated_pairs(full_redcap):
    df = full_redcap.copy()

    # keep only ongoing CGM/POC pair rows
    df = df[df["Repeat Instrument"] == "Daily Ongoing CGM/POC Pairs"].copy()

    # normalize Yes/No columns
    time_match_col = "Were ongoing CGM/POC value within 5 minutes?"
    validation_col = "Was ongoing validation criteria met?"

    df[time_match_col] = df[time_match_col].astype(str).str.strip()
    df[validation_col] = df[validation_col].astype(str).str.strip()

    # keep only time-matched and validation-passed rows
    df = df[
        (df[time_match_col] == "Yes") &
        (df[validation_col] == "Yes")
    ].copy()

    # rename key columns
    df = df.rename(columns={
        "Unique Study ID": "Study_ID",
        "Date .4": "Pair_Date",
        "Ongoing CGM value": "CGM_value",
        "Time of ongoing CGM value": "CGM_time",
        "Ongoing POC value": "POC_value",
        "Time of ongoing POC value": "POC_time",
    })

    print("Validated CGM/POC pairs shape:", df.shape)
    print(df[
        ["Study_ID", "Pair_Date", "CGM_value", "CGM_time", "POC_value", "POC_time"]
    ].head())

    return df


# Main
if __name__ == "__main__":
    full_redcap_df, master_clarity_df, secondary_cgm_dict = load_excel_files()

    clarity_clean_df = clean_master_clarity(master_clarity_df)
    validated_pairs_df = filter_validated_pairs(full_redcap_df)