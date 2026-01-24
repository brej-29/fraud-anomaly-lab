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
   - `ml/ensemble.py` – combine model outputs into an ensemble score and/or decision rule.

3. **Model artifacts (`ml/artifacts/`)**
   - Serialized model files (e.g., `.pkl`, `.joblib`) and associated metadata.
   - Ignored by git by default; only small, intentional demo artifacts may be committed later if needed.

4. **Inference API (`backend/`)**
   - FastAPI application exposing:
     - `GET /health` – health check endpoint.
     - `POST /predict` – per-transaction scoring endpoint (to be implemented).
   - Uses:
     - `backend/app/services/model_registry.py` – to load/register the trained models and ensemble.
     - `backend/app/services/scorer.py` – to apply preprocessing and scoring logic.
     - `backend/app/schemas/transactions.py` – pydantic schemas for request/response.
   - Containerized via `backend/Dockerfile` and can be deployed on **Hugging Face Spaces**.

5. **Monitoring & Exploration Dashboard (`dashboard/`)**
   - Streamlit app in `dashboard/app.py`:
     - Reads API base URL from environment.
     - Pings `/health` and, later, sends sample transactions to `/predict`.
     - Can display aggregate statistics, threshold analysis, and comparison plots.
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
   - `.github/workflows/ci.yml` – minimal GitHub Actions workflow:
     - Installs dependencies.
     - Runs backend tests (`pytest`).
     - Optionally verifies that `ml/` module imports successfully.
   - `docker-compose.yml` – local composition of backend + dashboard.
   - `Makefile` – convenience targets for setup, testing, running services, and downloading data.

---

## Component Interactions

- **ML → Backend**:
  - ML pipeline outputs model artifacts and potentially a configuration/metadata file describing:
    - Model types and file paths.
    - Preprocessing parameters (e.g., scalers).
    - Thresholds used for classification.
  - Backend loads these artifacts at startup via the model registry.

- **Backend → Dashboard**:
  - Dashboard sends HTTP requests to the FastAPI service:
    - `GET /health` to validate connectivity.
    - `POST /predict` to score single or batched transactions.
  - Later, the dashboard may request aggregated metrics from new API endpoints (e.g., `/metrics`).

- **Shared configuration**:
  - `.env` / environment variables plus `shared/constants.py` coordinate default ports, URLs, paths, and other lightweight configuration.

This architecture is intentionally **simple and modular** so that each layer can be evolved independently while preserving clear handoffs (data → models → API → dashboard).