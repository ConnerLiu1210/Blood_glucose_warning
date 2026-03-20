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

    print("Loaded successfully.")
    return full_redcap, master_clarity, secondary_cgm

# clean Master_clarity
def clean_master_clarity(master_clarity):
    df = master_clarity.copy()

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


# Main
if __name__ == "__main__":
    full_redcap_df, master_clarity_df, secondary_cgm_dict = load_excel_files()
