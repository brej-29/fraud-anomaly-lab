# Key Design Decisions

This document captures important architectural and modeling choices. It should be updated as the project evolves.

---

## Model Suite and Autoencoder Choice

We implement **six models** in total for fraud/anomaly detection, followed by an **ensemble**:

- IsolationForest (sklearn)
- Local Outlier Factor (LOF, sklearn)
- One-Class SVM (sklearn)
- COPOD (Copula-Based Outlier Detection, via PyOD)
- An MLP autoencoder trained on tabular features
- A simple score-based ensemble over the above models

We explicitly **do not** use an LSTM-based autoencoder, because the dataset is not truly sequential.

### Why not LSTM-AE?

The Kaggle credit card dataset (`mlg-ulb/creditcardfraud`) does **not** provide a true sequence or customer-level session identifier:

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
- Provides a complementary inductive bias to the MLP autoencoder (nonparametric vs neural).

This aligns with our goals:

- Keep methods **simple, interpretable, and robust** for a first iteration.
- Favor models that **do not depend on unavailable structure** (like sequences or IDs).
- Use architectures that match the data: MLP autoencoders for tabular PCA features instead of sequence models.

---

## Ensemble and Score Normalization

- We combine the five base models using a **score-based ensemble**:
  - Each model produces anomaly scores where higher = more anomalous.
  - For every model we compute anomaly scores on the **training split** and store
    `score_min_train` and `score_max_train` in `ml/artifacts/metadata.json`.
  - At prediction time we apply **min–max normalization** to map scores into `[0, 1]`
    using these stored ranges so that models contribute on a comparable scale.
- The ensemble score is the **simple average** of normalized scores across all available models.

Rationale:

- The ensemble is cheap to compute and easy to reason about.
- Min–max normalization is **monotonic**, so each base model's ranking of transactions
  is preserved.
- We avoid training an extra supervised meta-model, which would require labels and
  more infrastructure.

Limitations and future options:

- Min–max normalization can be sensitive to extreme outliers in the training split.
- In the future we may consider **rank-based** normalization or robust scaling using
  quantiles.
- We store validation-time ensemble score histograms to support simple drift monitoring
  via PSI.

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

## Autoencoder Training and Reproducibility

- The autoencoder is a **fully connected (MLP) autoencoder** implemented in TensorFlow/Keras.
- It is trained **only on normal transactions** from the time-based training split.
- Training setup:
  - `Adam` optimizer with MSE reconstruction loss.
  - Early stopping on validation loss with a small `patience`.
  - A small hidden architecture `[64, 32]` by default to keep training fast on CPU.
- We call `shared.utils.set_global_seed` and `tf.random.set_seed` to make runs as reproducible
  as practical on CPU-only environments.

Limitations:

- Some low-level TensorFlow and BLAS operations can still be non-deterministic across
  hardware/OS combinations.
- Exact floating-point metrics may differ slightly between runs, but **relative rankings**
  and qualitative behavior should remain stable.

---

## Deployment and Tooling Choices

- **FastAPI** for the backend API:
  - Modern, async-ready, with strong typing via pydantic.
  - Good fit for Dockerized deployments (Hugging Face Spaces).
- **Streamlit** for the dashboard:
  - Faster iteration on UI.
  - Native support on Streamlit Community Cloud (free tier).
- **SQLite** for lightweight persistence:
  - Stores predictions and feedback with minimal operational overhead.
  - Sufficient for demo-scale workloads and free-tier hosting.
- **Single monorepo**:
  - Easier local development with shared utilities.
  - Easier to keep ML, API, and dashboard in sync.
- **Shared ML utilities**:
  - `ml/preprocess.py` centralizes loading, validation, time-based splitting, and scaling.
  - `ml/models.py` standardizes anomaly model interfaces and score direction (higher = more anomalous).
  - `ml/evaluate.py` centralizes threshold calibration and metric computation, ensuring consistency across models.
  - `ml/ensemble.py` defines score-based ensembling with reusable normalization logic.

---

## Feature Importance and Explainability Strategy

- Use a **supervised proxy model** (e.g., `LogisticRegression` with `class_weight="balanced"`) on the time-based train/validation splits to derive feature importance.
- Apply **permutation importance** on the validation split (see `notebooks/01_eda_decisions.ipynb`) to understand which transformed features (Time, Amount, V1–V28) drive predictive performance.
- For the autoencoder, interpretability comes primarily from:
  - The distribution of reconstruction errors over time and across cohorts.
  - The same supervised proxy model (rather than per-layer autoencoder weights), since PCA features are hard to map back to raw business features.
- Clearly communicate limitations:
  - PCA components are not directly interpretable as original features.
  - Importance rankings are useful for monitoring and sanity checks, not for direct causal claims.
- Record findings in:
  - `notebooks/01_eda_decisions.ipynb` (EDA details, including autoencoder and proxy feature importance),
  - `reports/model_comparison.md` (high-level narrative once models are trained).

---

## Future Decision Log

When adding new features or models, please:

1. Update this document with:
   - What changed.
   - Why it changed.
   - Alternatives considered.
2. Update `context/ACCEPTANCE_CRITERIA.md` with new checklist items or mark existing ones as completed as appropriate.