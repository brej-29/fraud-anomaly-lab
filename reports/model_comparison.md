# Model Comparison Report

This report was generated from `ml/artifacts/metadata.json`.

## 1. Overview

- Dataset: Kaggle `mlg-ulb/creditcardfraud`
- Objective: Detect fraudulent credit card transactions via anomaly detection.
- Metrics: PR-AUC (primary), ROC-AUC, and threshold-based precision, recall, and F1.

## 2. Per-Model Metrics

| Model | Split | ROC-AUC | PR-AUC | Precision | Recall | F1 | Threshold | Constraints Met |
|---|---|---|---|---|---|---|---|---|
| isolation_forest | val | 0.9294 | 0.0201 | 0.0300 | 0.3333 | 0.0551 | 0.5924 | no |
| isolation_forest | test | 0.9433 | 0.0354 | 0.0493 | 0.2800 | 0.0838 | 0.5924 | no |
| lof | val | 0.6432 | 0.0024 | 0.0010 | 1.0000 | 0.0020 | 0.9419 | no |
| lof | test | 0.4896 | 0.0014 | 0.0013 | 1.0000 | 0.0026 | 0.9419 | no |
| one_class_svm | val | 0.9363 | 0.0600 | 0.1006 | 0.5439 | 0.1699 | 6.1389 | no |
| one_class_svm | test | 0.9473 | 0.1303 | 0.2010 | 0.5467 | 0.2939 | 6.1389 | no |
| copod | val | 0.9404 | 0.0542 | 0.0909 | 0.3158 | 0.1412 | 93.3129 | no |
| copod | test | 0.9474 | 0.1076 | 0.2029 | 0.3733 | 0.2629 | 93.3129 | no |

## 3. Notes

- Models are trained on **normal-only** transactions from the training split.
- Splits are **time-based** (train: early, val/test: later) to reduce leakage.
- Thresholds are calibrated on the validation set using precision and recall constraints.
- This example table was generated before the autoencoder and ensemble were added; after rerunning
  `make train-all` and `make report` you will see rows for the autoencoder and the score-based ensemble as well.

## 4. Best Model (Summary)

Refer to the table above to identify the model with the best balance of PR-AUC, recall, and precision on the validation and test sets.