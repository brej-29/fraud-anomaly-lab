# Retraining, Thresholds, and Operations

This document describes how to retrain models, regenerate artifacts, and operate the system over time.

The key principle: **training runs in `ml/`**, then the **backend API** and **dashboard** consume the resulting artifacts and metrics.

---

## 1. When to Retrain

You might choose to retrain when:

- You collect **new labeled data** (more confirmed fraud/non-fraud cases).
- Drift monitoring (`GET /drift`) shows a **high PSI** (e.g. > 0.25).
- Business requirements change (new fraud patterns, latency or precision/recall targets).
- You modify preprocessing or model configurations.

Retraining is cheap relative to serving predictions and should be done regularly during experimentation.

---

## 2. End-to-End Retraining Pipeline

From the project root:

```bash
# 1. Acquire or refresh data (if needed)
make download-data

# 2. Rebuild processed data cache (time-based split, scaling)
make preprocess

# 3. Train all models + ensemble and export artifacts
make train-all

# 4. Regenerate the model comparison report
make report
```

What happens:

1. `ml/preprocess.py`:
   - Validates schema and target.
   - Applies the **time-based 60/20/20 split**.
   - Fits the preprocessing pipeline.
   - Caches processed data for reuse.

2. `ml/train_all.py`:
   - Trains six models on **normal-only training data**:
     - IsolationForest, LOF, One-Class SVM, COPOD, MLP autoencoder, and a score-based ensemble.
   - Computes **validation/test metrics**.
   - Calibrates **per-model and ensemble thresholds** on the validation set using precision/recall constraints.
   - Writes:
     - `preprocessor.joblib`
     - Individual model artifacts
     - `thresholds.json`
     - `metadata.json` (with metrics, thresholds, normalization ranges, baseline histograms).

3. `ml/evaluate.py`:
   - Reads `metadata.json`.
   - Generates `reports/model_comparison.md` with tables of validation/test metrics.

After this pipeline completes, restart the backend API so that it reloads the updated artifacts.

---

## 3. Thresholds and Constraints

Thresholds are chosen via `ml.evaluate.choose_threshold`:

- Sweeps potential thresholds across the range of validation scores.
- Prefers thresholds that satisfy:
  - Minimum **precision**, e.g. ≥ 0.90.
  - Minimum **recall**, e.g. ≥ 0.75.
- If no threshold satisfies both, selects the best F1 and records that constraints were not met.

Thresholds are stored in two places:

- `ml/artifacts/thresholds.json` – simple mapping `model_name -> threshold`.
- `ml/artifacts/metadata.json` – inside each model entry (`models[model_name]["threshold"]`).

The backend uses these thresholds for:

- Per-model decisions (optional).
- The ensemble decision rule.

You can adjust the precision/recall targets by editing `choose_threshold` parameters and rerunning training.

---

## 4. Drift Monitoring with PSI

The ML pipeline stores a **baseline ensemble score distribution** in `metadata.json`:

- Based on the **validation** ensemble scores.
- Stored as:
  - `models["ensemble"]["baseline"]["histogram"]["bin_edges"]`
  - `models["ensemble"]["baseline"]["histogram"]["counts"]`
  - Plus the sample count (`n_samples`).

The backend:

- Logs each prediction to SQLite (`backend/app/services/storage.py`).
- Exposes `GET /drift`:
  - Fetches the most recent ensemble scores (window size configurable).
  - Computes **Population Stability Index (PSI)** using `shared.drift.compute_psi`.
  - Returns a drift level:
    - `< 0.1` → `"low"`
    - `0.1–0.25` → `"medium"`
    - `> 0.25` → `"high"`

Operational guidance:

- **Low**: no immediate action.
- **Medium**: monitor closely; consider retraining in the near future.
- **High**: investigate causes; retrain and/or adjust thresholds.

---

## 5. Feedback Loop

The system supports a simple feedback loop:

1. Predictions are stored in SQLite with:
   - Per-model scores and decisions.
   - Ensemble score and final flag.
2. Users can attach feedback via `POST /feedback`:
   - Use labels such as `"fraud"` / `"not_fraud"`.
   - Optional free-text notes.
3. Future scripts (not yet implemented) can:
   - Export recent predictions + feedback.
   - Build new training sets or evaluation slices.

This structure provides a foundation for active learning, periodic retraining, and human-in-the-loop evaluation.

---

## 6. Operational Checklist

For each new deployment or major retraining:

1. **Run the ML pipeline** (`make preprocess`, `make train-all`, `make report`).
2. **Inspect the report** (`reports/model_comparison.md`) for:
   - PR-AUC / ROC-AUC.
   - Precision/recall at the chosen thresholds.
   - Ensemble vs. single-model performance.
3. **Restart the backend API** so it reloads artifacts.
4. **Smoke test the API**:
   - `GET /health`, `GET /models`, `GET /metrics`.
   - `POST /predict` with a sample payload.
5. **Verify the dashboard**:
   - Health tab.
   - Models tab.
   - Predict and Monitoring views.

Keeping this loop tight will help maintain a robust and interpretable fraud detection system as data and requirements evolve.