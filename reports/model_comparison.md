# Model Comparison Report (Template)

This report will summarize the performance of all models and the ensemble on the **Credit Card Fraud Detection** dataset.

## 1. Overview

- Dataset: Kaggle `mlg-ulb/creditcardfraud`
- Objective: Detect fraudulent credit card transactions (anomaly detection / binary classification).
- Metrics:
  - Primary: PR-AUC (Precision–Recall AUC)
  - Secondary: ROC-AUC
  - Threshold-based: Precision, Recall, F1, confusion matrices

## 2. Candidate Models

List the six models (including COPOD) once finalized. For each model, capture:

- Type (supervised / unsupervised)
- Library / implementation
- Key hyperparameters
- Training time and inference cost considerations

## 3. Validation Results

Create a table (or multiple tables) including, at minimum:

- PR-AUC
- ROC-AUC
- Precision / Recall / F1 at chosen thresholds
- Threshold(s) used and rationale

## 4. Test Results

Mirror the validation section using the **held-out test set**. Highlight any overfitting or shifts.

## 5. Threshold Selection and Trade-offs

Explain how thresholds were chosen (per `context/METRICS.md`):

- Max-F1 threshold vs. recall-constrained thresholds.
- Business-inspired trade-offs between false positives and false negatives (if available).

## 6. Ensemble Performance

Describe the ensemble method (e.g., score averaging, stacking, rules) and compare:

- Ensemble vs. best single model.
- Where the ensemble helps or hurts (e.g., at certain recall levels).

## 7. Explainability and Insights

Summarize:

- Any feature importance or permutation importance results.
- Sensitivity analyses and their interpretations.
- Caveats due to PCA-based features (V1–V28).

## 8. Conclusions and Next Steps

Provide a concise conclusion, including:

- Recommended model/ensemble and operating threshold(s).
- Limitations of the current approach.
- Proposed improvements for future iterations (e.g., richer features, additional models, deployment refinements).