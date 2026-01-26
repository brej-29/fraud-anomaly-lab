# System Components and Architecture

This repository is organized as a **monorepo** with clear boundaries between ML, API, dashboard, and shared utilities.

---

## High-Level Flow

1. **Data acquisition (Kaggle)**
   - `scripts/download_kaggle.sh` and `ml/download_data.py` download the **Credit Card Fraud Detection** dataset from Kaggle (mlg-ulb/creditcardfraud) into `data/raw/`.
   - Raw data stays **local only** and is excluded from git.

2. **ML pipeline (`ml/`)**
   - `ml/preprocess.py` – load raw data, apply leak-safe splitting (time-based), preprocessing, and feature transformations.
   - `ml/train_all.py` – train a suite of anomaly detection / fraud detection models and save artifacts under `ml/artifacts/`.
   - `ml/evaluate.py` – compute metrics (PR-AUC, ROC-AUC, precision, recall, F1, etc.) and dump evaluation summaries.
   - `ml/ensemble.py` – implement a score-based ensemble that averages min–max normalized anomaly scores from all base models.

3. **Model artifacts (`ml/artifacts/`)**
   - Serialized model files (e.g., `.joblib` for classical models, `.keras` for the autoencoder) and associated metadata.
   - `metadata.json` contains:
     - Feature order and split information.
     - Per-model hyperparameters, thresholds, and evaluation metrics.
     - Ensemble configuration (base models, normalization parameters).
     - Baseline ensemble score histogram for drift monitoring.
   - `thresholds.json` provides per-model and ensemble thresholds.
   - `preprocessor.joblib` stores the fitted preprocessing pipeline.
   - Ignored by git by default; only small, intentional demo artifacts may be committed later if needed.

4. **Inference API (`backend/`)**
   - FastAPI application exposing:
     - `GET /health` and `GET /api/health` – health check endpoints.
     - `GET /models` – inspect models, thresholds, and evaluation metadata.
     - `GET /metrics` – lightweight in-memory runtime metrics.
     - `POST /predict` – per-transaction scoring endpoint (ensemble + per-model scores).
     - `POST /predict/batch` – batch scoring for multiple transactions.
     - `GET /monitor/recent` – recent prediction records (from SQLite).
     - `POST /feedback` – attach labels/notes to past predictions.
     - `GET /drift` – drift signal based on PSI of ensemble scores.
   - Uses:
     - `backend/app/services/model_registry.py` – to load/register the trained models and ensemble configuration from `ml/artifacts/`.
     - `backend/app/services/scorer.py` – to apply preprocessing, model scoring, ensemble aggregation, and persistence.
     - `backend/app/services/storage.py` – SQLite persistence for predictions and feedback.
     - `backend/app/schemas/transactions.py` – pydantic schemas for request/response payloads.
     - `backend/app/core/logging.py`, `backend/app/core/metrics.py`, `backend/app/core/middleware.py` – structured logging, request ids, and runtime metrics.
   - Containerized via `backend/Dockerfile` and deployable on **Hugging Face Spaces**.

5. **Monitoring & Exploration Dashboard (`dashboard/`)**
   - Streamlit app in `dashboard/app.py`:
     - Reads API base URL from environment (`DASHBOARD_API_BASE_URL`).
     - **API Health** tab – pings `/health` and `/metrics`.
     - **Models** tab – renders a table of validation/test metrics for all models and the ensemble via `/models`.
     - **Predict** tab – lets users paste a JSON transaction and calls `/predict`.
     - **Monitoring** tab – shows recent predictions and ensemble drift information via `/monitor/recent` and `/drift`.
   - Containerized via `dashboard/Dockerfile` and deployable to **Streamlit Community Cloud** (using repo and requirements).

6. **Shared utilities (`shared/`)**
   - `shared/constants.py` – common constants (paths, default thresholds, model names, etc.).
   - `shared/utils.py` – small utility helpers (e.g., seed setting, common logging helpers).
   - Imported by `ml/`, `backend/`, and `dashboard/` as needed.

7. **Notebooks (`notebooks/`)**
   - `notebooks/01_eda_decisions.ipynb` – structured EDA and decisions notebook template:
     - Problem framing, class imbalance analysis.
     - Leakage-safe split strategy.
     - Preprocessing and modeling plans.
     - Feature importance / explainability strategies.
   - `notebooks/README.md` – overview of notebook conventions and how to run them.

8. **Context and governance (`context/`)**
   - `GOAL.md`, `COMPONENTS.md`, `DECISIONS.md`, `METRICS.md` – grounding docs for why and how the system is built.
   - `COSINE_GROUNDING_TEMPLATE.md` – instructions that future tasks must follow.
   - `ACCEPTANCE_CRITERIA.md` – checklist to track progress and ensure consistency as features are added.

9. **CI / Tooling**
   - `.github/workflows/ci.yml` – GitHub Actions workflow:
     - Installs backend and ML dependencies.
     - Runs `ruff` for basic linting on `backend/`, `ml/`, and `shared/`.
     - Runs backend tests (`pytest backend`).
     - Runs ML tests excluding TensorFlow-heavy ones (`pytest ml -m "not tf_heavy"`).
   - `docker-compose.yml` – local composition of backend + dashboard.
   - `Makefile` – convenience targets for setup, linting, testing, running services, Docker builds, and downloading data.

---

## Component Interactions

- **ML → Backend**:
  - ML pipeline outputs model artifacts and a rich `metadata.json` describing:
    - Model types, file paths, and hyperparameters.
    - Preprocessing parameters (e.g., scalers) and feature order.
    - Per-model and ensemble thresholds, normalization ranges, and metrics.
    - Baseline ensemble score distributions for drift monitoring.
  - Backend loads these artifacts at startup via the model registry.

- **Backend ↔ SQLite**:
  - Backend persists prediction results (per-model scores + ensemble decision) and feedback into a lightweight SQLite database.
  - Monitoring endpoints (`/monitor/recent`, `/drift`) and future retraining scripts can read from this store.

- **Backend → Dashboard**:
  - Dashboard sends HTTP requests to the FastAPI service:
    - `GET /health` and `GET /metrics` to validate connectivity and runtime status.
    - `GET /models` to visualize model metrics and configuration.
    - `POST /predict` and `POST /predict/batch` to score transactions.
    - `GET /monitor/recent` and `GET /drift` for monitoring views.
  - This separation keeps the dashboard stateless and focused on visualization.

- **Shared configuration**:
  - `.env` / environment variables plus `shared/constants.py` coordinate default ports, URLs, paths, and other lightweight configuration.

This architecture is intentionally **simple and modular** so that each layer can be evolved independently while preserving clear handoffs (data → models → API → dashboard).