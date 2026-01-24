# Key Design Decisions

This document captures important architectural and modeling choices. It should be updated as the project evolves.

---

## Model Suite and LSTM-AE Swap

We plan to implement **six models** in total for fraud/anomaly detection, followed by an **ensemble**. Instead of using an LSTM-based autoencoder, we use **COPOD (Copula-Based Outlier Detection)** from **PyOD** as the fifth model.

### Why not LSTM-AE?

The Kaggle credit card dataset (mlg-ulb/creditcardfraud) does **not** provide a true sequence or customer-level session identifier:

- Features are largely **PCA components (V1–V28)**.
- `Time` is a monotonically increasing integer representing seconds since the first transaction, but:
  - It does not encode which transactions belong to the same cardholder.
  - We cannot reliably build sequences of transactions per customer without additional IDs.
- LSTM autoencoders are best suited for **sequential data** where order and grouping are meaningful (e.g., time series per account, clickstream sessions).

Using LSTM-AE here would require **inventing artificial sequences** (e.g., sliding windows over the global time series), which introduces:

- Ambiguity about what constitutes a "sequence".
- Risk of **data leakage** across train/validation/test when windows overlap.
- Additional complexity not justified for a first, free-to-run baseline.

### Why COPOD (PyOD)?

**COPOD** (Copula-Based Outlier Detection):

- Is implemented in **PyOD**, a widely used Python outlier detection library.
- Is **unsupervised**, fully compatible with the dataset’s numeric features.
- Scales to medium-sized tabular datasets efficiently (suitable for free CPU-only environments).
- Does not rely on sequence information, making it a better fit for our setting.

This aligns with our goals:

- Keep methods **simple, interpretable, and robust** for a first iteration.
- Favor models that **do not depend on unavailable structure** (like sequences or IDs).

---

## Data Splitting Strategy

- Use a **time-based split**:
  - Train on **earlier** transactions.
  - Validate/test on **later** transactions.
- Rationale:
  - Mirrors realistic deployment where models trained on past data are applied to future transactions.
  - Reduces the risk of temporal **data leakage** (information from the future bleeding into the past).
- Implementation details will be fleshed out in:
  - `notebooks/01_eda_decisions.ipynb`
  - `ml/preprocess.py`

---

## Preprocessing Choices (Initial)

- Scale `Amount` and potentially `Time` using a robust scaler (e.g., `StandardScaler` or `RobustScaler`).
- Keep `V1`–`V28` as-is (already PCA-transformed numeric features).
- Handle class imbalance primarily via:
  - Threshold selection.
  - Model choice.
  - Metric optimization (e.g., PR-AUC, recall at fixed precision), rather than heavy rebalancing techniques at first.

Further adjustments (e.g., SMOTE, class weights) may be considered after baseline evaluation.

---

## Deployment and Tooling Choices

- **FastAPI** for the backend API:
  - Modern, async-ready, with strong typing via pydantic.
  - Good fit for Dockerized deployments (Hugging Face Spaces).
- **Streamlit** for the dashboard:
  - Faster iteration on UI.
  - Native support on Streamlit Community Cloud (free tier).
- **Single monorepo**:
  - Easier local development with shared utilities.
  - Easier to keep ML, API, and dashboard in sync.

---

## Future Decision Log

When adding new features or models, please:

1. Update this document with:
   - What changed.
   - Why it changed.
   - Alternatives considered.
2. Update `context/ACCEPTANCE_CRITERIA.md` with new checklist items or mark existing ones as completed as appropriate.