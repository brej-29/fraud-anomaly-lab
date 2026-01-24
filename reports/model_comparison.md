# Model Comparison Report

This report summarizes the performance of the anomaly detection models trained on the **Credit Card Fraud Detection** dataset.

> **Note**: This file is generated from `ml/artifacts/metadata.json` by `ml.evaluate.generate_model_comparison_report`.  
> Run `make train` followed by `make report` to refresh the contents after retraining.

## 1. Overview

- Dataset: Kaggle `mlg-ulb/creditcardfraud`.
- Objective: Detect fraudulent credit card transactions (anomaly detection / binary classification).
- Current models included in this step:
  - Isolation Forest (sklearn)
  - Local Outlier Factor (LOF, sklearn with `novelty=True`)
  - One-Class SVM (sklearn)
  - COPOD (PyOD)
- Metrics:
  - Primary: PR-AUC (Precision–Recall AUC)
  - Secondary: ROC-AUC
  - Threshold-based: Precision, Recall, F1, confusion matrices

## 2. Per-Model Metrics (Validation and Test)

After running the full pipeline, this section is populated with a table of metrics per model, per split (validation and test):

- ROC-AUC
- PR-AUC
- Precision
- Recall
- F1 score
- Decision threshold on anomaly scores
- Whether precision/recall constraints were satisfied during threshold calibration

The table is written automatically by `ml/evaluate.py` based on `metadata.json`.

## 3. Threshold Selection and Trade-offs

Thresholds are calibrated on the **validation** split according to the strategy defined in `context/METRICS.md` and implemented in `ml.evaluate.choose_threshold`:

- Prefer thresholds that satisfy **both**:
  - Precision ≥ 0.90
  - Recall ≥ 0.75
- Among those, pick the threshold with the highest F1 score.
- If no threshold satisfies both constraints, pick the threshold with the best F1 and mark that constraints were not met.

This ensures a clear trade-off between catching fraud (recall) and controlling false alarms (precision).

## 4. Notes on Training Setup

- Models are trained using **normal-only** transactions from the training split.
- Data is split using a **time-based 60/20/20** rule on the `Time` column:
  - Train: earliest 60% of transactions
  - Validation: next 20%
  - Test: final 20%
- Preprocessing:
  - Robust scaling for `Amount` and `Time`
  - PCA components (`V1`–`V28`) passed through unchanged

## 5. Explainability and Insights

Explainability in this project relies on:

- A **supervised proxy model** (LogisticRegression with `class_weight="balanced"`) trained on labeled data.
- **Permutation importance** on the validation set to identify influential transformed features (`Time`, `Amount`, `V1`–`V28`).
- Careful communication that PCA components are not directly interpretable as original business features.

Key findings and top influential components should be summarized here after analysis.

## 6. Best Model and Next Steps

Once metrics are populated:

- Identify which model offers the best balance of PR-AUC, recall, and precision on both validation and test splits.
- Document:
  - The chosen model and operating threshold.
  - Whether precision/recall constraints were met.
  - Any notable weaknesses (e.g., sensitivity to particular feature distributions).

Future steps (beyond this report):

- Add additional models (e.g., autoencoder-based) and an ensemble.
- Integrate metrics and explanations into the Streamlit dashboard and FastAPI API.
- Extend monitoring to include data drift and performance drift in production.