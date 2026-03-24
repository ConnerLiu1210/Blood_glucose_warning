# Glucose High Prediction Model

## Overview
This project builds a transformer-based model to predict whether glucose will enter a High state within the next 1 hour.

## Prediction Target
A sample is labeled as High if, within the next 1 hour:
- glucose value is greater than 400 mg/dL, or
- the record is explicitly labeled as `High`

## Data Sources
- `Full REDCap Data Intervention for Dexcom FINAL.xlsx`
- `Master Clarity log 1-101 for Dexcom FINAL.xlsx`
- `Final Seconary CGM cohort pull_uncleaned.xlsx`

## Input Features
The model uses a 3-hour historical CGM window and daily clinical features.

### CGM sequence features
- glucose value
- time gap between measurements
- glucose delta
- glucose slope
- rolling mean
- rolling standard deviation

### Daily insulin features
- IV insulin flag
- subQ insulin flag
- subQ bolus units
- basal insulin units
- NPH units

### Daily nutrition features
- enteral nutrition flag
- enteral feed duration
- TPN flag
- TPN duration

## Model
- Transformer encoder
- input dimension: 15
- hidden dimension: 32
- 2 encoder layers
- 4 attention heads

## Threshold
Final classification threshold:
- `0.9`

## Evaluation Metrics
- Precision
- Recall
- Specificity
- F1-score
- AUROC
- AUPRC
- Confusion Matrix

## Output
Each run creates a timestamped folder under `output/` containing:
- `train.log`
- `metrics.txt`

## Notes
- The model uses patient-level splitting to reduce data leakage.
- Dynamic glucose features are included to capture short-term trends.
- Insulin and nutrition features provide additional clinical context.