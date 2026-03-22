from pathlib import Path
import pandas as pd
import numpy as np


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

    full_redcap.columns = full_redcap.columns.str.strip()
    master_clarity.columns = master_clarity.columns.str.strip()

    print("Loaded successfully.")
    return full_redcap, master_clarity, secondary_cgm


# Clean Master Clarity
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


# Filter validated ongoing CGM/POC pairs from Full REDCap
def filter_validated_pairs(full_redcap):
    df = full_redcap.copy()

    df = df[df["Repeat Instrument"] == "Daily Ongoing CGM/POC Pairs"].copy()

    time_match_col = "Were ongoing CGM/POC value within 5 minutes?"
    validation_col = "Was ongoing validation criteria met?"

    df[time_match_col] = df[time_match_col].astype(str).str.strip()
    df[validation_col] = df[validation_col].astype(str).str.strip()

    df = df[
        (df[time_match_col] == "Yes") &
        (df[validation_col] == "Yes")
    ].copy()

    df = df.rename(columns={
        "Unique Study ID": "Study_ID",
        "Date .4": "Pair_Date",
        "Ongoing CGM value": "CGM_value",
        "Time of ongoing CGM value": "CGM_time",
        "Ongoing POC value": "POC_value",
        "Time of ongoing POC value": "POC_time",
    })

    print("Validated CGM/POC pairs shape:", df.shape)
    return df


# Build usable timestamps for validated CGM/POC pairs
def build_pair_timestamps(validated_pairs):
    df = validated_pairs.copy()

    df["Pair_Date"] = pd.to_datetime(df["Pair_Date"], errors="coerce").dt.date
    df["CGM_time"] = pd.to_datetime(df["CGM_time"], errors="coerce").dt.time
    df["POC_time"] = pd.to_datetime(df["POC_time"], errors="coerce").dt.time

    df["CGM_timestamp"] = pd.to_datetime(
        df["Pair_Date"].astype(str) + " " + df["CGM_time"].astype(str),
        errors="coerce"
    )
    df["POC_timestamp"] = pd.to_datetime(
        df["Pair_Date"].astype(str) + " " + df["POC_time"].astype(str),
        errors="coerce"
    )

    df["CGM_value"] = pd.to_numeric(df["CGM_value"], errors="coerce")
    df["POC_value"] = pd.to_numeric(df["POC_value"], errors="coerce")

    df = df[df["CGM_timestamp"].notna()].copy()
    df = df[df["POC_timestamp"].notna()].copy()
    df = df[df["CGM_value"].notna()].copy()
    df = df[df["POC_value"].notna()].copy()

    df["CGM_POC_diff"] = df["CGM_value"] - df["POC_value"]
    df["CGM_POC_abs_diff"] = (df["CGM_value"] - df["POC_value"]).abs()

    print("Timestamp-ready validated pairs shape:", df.shape)
    return df


# Clean validated pair glucose values
def clean_pair_glucose_values(validated_pairs_ready):
    df = validated_pairs_ready.copy()

    df = df[
        (df["CGM_value"] >= 20) & (df["CGM_value"] <= 500) &
        (df["POC_value"] >= 20) & (df["POC_value"] <= 500)
    ].copy()

    df["CGM_POC_diff"] = df["CGM_value"] - df["POC_value"]
    df["CGM_POC_abs_diff"] = (df["CGM_value"] - df["POC_value"]).abs()

    print("Clean pair glucose values shape:", df.shape)
    print("CGM range:", df["CGM_value"].min(), "to", df["CGM_value"].max())
    print("POC range:", df["POC_value"].min(), "to", df["POC_value"].max())

    return df


# Build transformer input sequences
def build_transformer_sequences(clarity_clean, seq_len=36):
    print("Building transformer sequences...")

    df = clarity_clean.copy()
    df = df[df["Event Type"] == "EGV"].copy()
    df = df.sort_values(["Sub ID", "Timestamp"]).reset_index(drop=True)

    sequences = []
    labels = []

    history_window = pd.Timedelta(hours=3)
    future_window = pd.Timedelta(hours=1)

    for subject_id, group in df.groupby("Sub ID"):
        group = group.sort_values("Timestamp").reset_index(drop=True)

        for i in range(len(group)):
            if pd.isna(group.loc[i, "Glucose_numeric"]):
                continue

            current_time = group.loc[i, "Timestamp"]
            history_start = current_time - history_window
            future_end = current_time + future_window

            history_df = group[
                (group["Timestamp"] >= history_start) &
                (group["Timestamp"] <= current_time) &
                (group["Glucose_numeric"].notna())
            ].copy()

            future_df = group[
                (group["Timestamp"] > current_time) &
                (group["Timestamp"] <= future_end)
            ].copy()

            if len(history_df) < 6 or len(future_df) < 1:
                continue

            future_high = (
                (future_df["Glucose_text_upper"] == "HIGH") |
                (future_df["Glucose_numeric"] > 400)
            ).any()

            glucose_seq = history_df["Glucose_numeric"].values.astype(float)
            time_seq = history_df["Timestamp"]

            if len(glucose_seq) > seq_len:
                glucose_seq = glucose_seq[-seq_len:]
                time_seq = time_seq.iloc[-seq_len:]

            padded_seq = np.zeros(seq_len, dtype=np.float32)
            time_gap = np.zeros(seq_len, dtype=np.float32)

            padded_seq[-len(glucose_seq):] = glucose_seq

            if len(time_seq) > 1:
                deltas = time_seq.diff().dt.total_seconds().fillna(0).values / 60.0
                time_gap[-len(glucose_seq):] = deltas.astype(np.float32)

            seq_features = np.stack([padded_seq, time_gap], axis=1)

            sequences.append(seq_features)
            labels.append(int(future_high))

    X = np.array(sequences, dtype=np.float32)
    y = np.array(labels, dtype=np.int64)

    print("Transformer sequence shape:", X.shape)
    print("Transformer label shape:", y.shape)
    if len(y) > 0:
        unique, counts = np.unique(y, return_counts=True)
        print("Label counts:", dict(zip(unique, counts)))

    return X, y


# Main
if __name__ == "__main__":
    full_redcap_df, master_clarity_df, secondary_cgm_dict = load_excel_files()

    clarity_clean_df = clean_master_clarity(master_clarity_df)

    validated_pairs_df = filter_validated_pairs(full_redcap_df)
    validated_pairs_ready_df = build_pair_timestamps(validated_pairs_df)
    validated_pairs_clean_df = clean_pair_glucose_values(validated_pairs_ready_df)

    X_seq, y_seq = build_transformer_sequences(clarity_clean_df, seq_len=36)