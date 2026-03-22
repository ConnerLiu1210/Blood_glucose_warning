from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
)


# File paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_PATH = OUTPUT_DIR / "train.log"
METRICS_PATH = OUTPUT_DIR / "metrics.txt"

FULL_REDCAP_PATH = DATA_DIR / "Full REDCap Data Intervention for Dexcom FINAL.xlsx"
MASTER_CLARITY_PATH = DATA_DIR / "Master Clarity log 1-101 for Dexcom FINAL.xlsx"
SECONDARY_CGM_PATH = DATA_DIR / "Final Seconary CGM cohort pull_uncleaned.xlsx"



# Logging helper
def log_message(message, log_path=LOG_PATH):
    print(message)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


# Load Excel files
def load_excel_files():
    log_message("Loading Excel files...")

    full_redcap = pd.read_excel(FULL_REDCAP_PATH)
    master_clarity = pd.read_excel(MASTER_CLARITY_PATH)
    secondary_cgm = pd.read_excel(SECONDARY_CGM_PATH, sheet_name=None)

    full_redcap.columns = full_redcap.columns.str.strip()
    master_clarity.columns = master_clarity.columns.str.strip()

    log_message("Loaded successfully.")
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

    log_message(f"Cleaned Master Clarity shape: {df.shape}")
    log_message(f"High count: {df['Is_High'].sum()}")

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

    log_message(f"Validated CGM/POC pairs shape: {df.shape}")
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

    log_message(f"Timestamp-ready validated pairs shape: {df.shape}")
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

    log_message(f"Clean pair glucose values shape: {df.shape}")
    log_message(f"CGM range: {df['CGM_value'].min()} to {df['CGM_value'].max()}")
    log_message(f"POC range: {df['POC_value'].min()} to {df['POC_value'].max()}")

    return df


# Build transformer input sequences
def build_transformer_sequences(clarity_clean, seq_len=36):
    log_message("Building transformer sequences...")

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

    log_message(f"Transformer sequence shape: {X.shape}")
    log_message(f"Transformer label shape: {y.shape}")
    if len(y) > 0:
        unique, counts = np.unique(y, return_counts=True)
        log_message(f"Label counts: {dict(zip(unique, counts))}")

    return X, y


# Dataset
class GlucoseDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# Transformer model
class GlucoseTransformer(nn.Module):
    def __init__(
        self,
        input_dim=2,
        d_model=32,
        nhead=4,
        num_layers=2,
        dim_feedforward=64,
        dropout=0.1
    ):
        super().__init__()

        self.input_proj = nn.Linear(input_dim, d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.classifier = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        x = self.input_proj(x)
        x = self.encoder(x)
        x = x[:, -1, :]
        out = self.classifier(x)
        return out


# Train and evaluate
def train_transformer_model(X, y, epochs=5, batch_size=64, lr=1e-3):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    train_dataset = GlucoseDataset(X_train, y_train)
    test_dataset = GlucoseDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GlucoseTransformer().to(device)

    class_counts = np.bincount(y_train)
    class_weights = len(y_train) / (2.0 * class_counts)
    class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    log_message(f"Training on device: {device}")

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0

        for batch_X, batch_y in train_loader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            logits = model(batch_X)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        log_message(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

    model.eval()
    all_preds = []
    all_true = []
    all_probs = []

    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X = batch_X.to(device)

            logits = model(batch_X)
            probs = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()
            preds = torch.argmax(logits, dim=1).cpu().numpy()

            all_probs.extend(probs)
            all_preds.extend(preds)
            all_true.extend(batch_y.numpy())

    cm = confusion_matrix(all_true, all_preds)
    tn, fp, fn, tp = cm.ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    auroc = roc_auc_score(all_true, all_probs)
    auprc = average_precision_score(all_true, all_probs)
    report = classification_report(all_true, all_preds, digits=4)

    log_message("\n===== TRANSFORMER RESULTS =====")
    log_message("Confusion Matrix:")
    log_message(cm)

    log_message("\nClassification Report:")
    log_message(report)

    log_message("\nAdditional Metrics:")
    log_message(f"Sensitivity (Recall): {sensitivity:.4f}")
    log_message(f"Specificity: {specificity:.4f}")
    log_message(f"AUROC: {auroc:.4f}")
    log_message(f"AUPRC: {auprc:.4f}")

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        f.write("===== TRANSFORMER RESULTS =====\n")
        f.write("Confusion Matrix:\n")
        f.write(str(cm) + "\n\n")
        f.write("Classification Report:\n")
        f.write(report + "\n")
        f.write(f"Sensitivity (Recall): {sensitivity:.4f}\n")
        f.write(f"Specificity: {specificity:.4f}\n")
        f.write(f"AUROC: {auroc:.4f}\n")
        f.write(f"AUPRC: {auprc:.4f}\n")

    return model


# Main
if __name__ == "__main__":
    # clear old log at the start of each run
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("Training log\n")

    full_redcap_df, master_clarity_df, secondary_cgm_dict = load_excel_files()

    clarity_clean_df = clean_master_clarity(master_clarity_df)

    validated_pairs_df = filter_validated_pairs(full_redcap_df)
    validated_pairs_ready_df = build_pair_timestamps(validated_pairs_df)
    validated_pairs_clean_df = clean_pair_glucose_values(validated_pairs_ready_df)

    X_seq, y_seq = build_transformer_sequences(clarity_clean_df, seq_len=36)

    transformer_model = train_transformer_model(
        X_seq, y_seq,
        epochs=5,
        batch_size=64,
        lr=1e-3
    )