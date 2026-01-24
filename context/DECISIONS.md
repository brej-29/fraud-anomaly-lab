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
- Concrete implementation:
  - Sort all rows by `Time` ascending.
  - Use a **60/20/20** split on the sorted data:
    - Train: earliest 60% of transactions.
    - Validation: next 20%.
    - Test: final 20%.
  - Implemented in:
    - `ml/preprocess.py` (`time_based_split`),
    - and reused in `notebooks/01_eda_decisions.ipynb` for analysis and visualization.

---

## Preprocessing Choices (Initial)

- Scale `Amount` and `Time` using a **RobustScaler** to reduce sensitivity to outliers.
- Keep `V1`–`V28` as-is (already PCA-transformed numeric features).
- Implement preprocessing as a reusable **sklearn Pipeline** (see `ml/preprocess.build_preprocessor`), so:
  - The same transformation is used for training, evaluation, and (later) API inference.
  - The fitted preprocessor can be serialized and loaded alongside model artifacts.
- Handle class imbalance primarily via:
  - Threshold selection on anomaly scores.
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
- **Shared ML utilities**:
  - `ml/preprocess.py` centralizes loading, validation, time-based splitting, and scaling.
  - `ml/models.py` standardizes anomaly model interfaces and score direction (higher = more anomalous).
  - `ml/evaluate.py` centralizes threshold calibration and metric computation, ensuring consistency across models.

---

## Feature Importance and Explainability Strategy

- Use a **supervised proxy model** (e.g., `LogisticRegression` with `class_weight=\"balanced\"`) on the time-based train/validation splits to derive feature importance.
- Apply **permutation importance** on the validation split (see `notebooks/01_eda_decisions.ipynb`) to understand which transformed features (Time, Amount, V1–V28) drive predictive performance.
- Clearly communicate limitations:
  - PCA components are not directly interpretable as original features.
  - Importance rankings are useful for monitoring and sanity checks, not for direct causal claims.
- Record findings in:
  - `notebooks/01_eda_decisions.ipynb` (EDA details),
  - `reports/model_comparison.md` (high-level narrative once models are trained).

---

## Future Decision Log

When adding new features or models, please:

1. Update this document with:
   - What changed.
   - Why it changed.
   - Alternatives considered.
2. Update `context/ACCEPTANCE_CRITERIA.md` with new checklist items or mark existing ones as completed as appropriate.