# Acceptance Criteria Checklist

This document tracks major milestones and feature completeness for `fraud-anomaly-lab`.  
When implementing new features, update this checklist accordingly.

---

## 0. Repository and Tooling Scaffold

- [x] Monorepo structure created with:
  - `backend/`, `dashboard/`, `ml/`, `shared/`, `notebooks/`, `context/`, `scripts/`, `reports/`.
- [x] Root `README.md` with quickstart, deployment targets, and repo map.
- [x] `.gitignore` configured to exclude data, artifacts, environments, and generated reports.
- [x] `.env.example` added.
- [x] Minimal CI via GitHub Actions (`.github/workflows/ci.yml`).
- [x] Dockerfiles for backend and dashboard plus `docker-compose.yml`.
- [x] Makefile with targets: `setup`, `test`, `api`, `dashboard`, `compose-up`, `compose-down`, `download-data`.

---

## 1. Data Acquisition and Management

- [x] Kaggle setup instructions documented (`scripts/kaggle_setup.md`).
- [x] Shell script to download Kaggle dataset to `data/raw/` (`scripts/download_kaggle.sh`).
- [x] Python helper `ml/download_data.py` to check/download data and guide the user.
- [x] Ensure raw data and artifacts are excluded from git (`.gitignore`).

---

## 2. EDA and Decision Documentation

- [x] EDA decisions notebook template created (`notebooks/01_eda_decisions.ipynb`).
- [x] Notebook README with conventions and usage.
- [x] Context docs populated:
  - [x] `GOAL.md`
  - [x] `COMPONENTS.md`
  - [x] `DECISIONS.md`
  - [x] `METRICS.md`
  - [x] `COSINE_GROUNDING_TEMPLATE.md`
  - [x] `ACCEPTANCE_CRITERIA.md` (this file)

---

## 3. ML Pipeline (Placeholders)

- [x] `ml/preprocess.py` with placeholder but structured functions.
- [x] `ml/train_all.py` with placeholder training orchestrator.
- [x] `ml/evaluate.py` with placeholder evaluation logic.
- [x] `ml/ensemble.py` with placeholder ensemble interface.
- [x] `ml/requirements.txt` listing core dependencies (`pandas`, `numpy`, `scikit-learn`, `pyod`, `joblib`).
- [ ] Implement full preprocessing (including time-based split and scaling).
- [ ] Train six models and persist artifacts.
- [ ] Implement ensemble logic and store configuration/metadata.

---

## 4. Backend API

- [x] FastAPI app scaffold:
  - [x] `GET /health` endpoint.
  - [x] Placeholder `POST /predict` endpoint.
- [x] Structured logging configuration in `backend/app/core/logging.py`.
- [x] Basic configuration in `backend/app/core/config.py`.
- [x] Placeholder services:
  - [x] `model_registry.py`
  - [x] `scorer.py`
- [x] Pydantic schemas in `backend/app/schemas/transactions.py`.
- [x] Backend tests:
  - [x] `tests/test_health.py` using `TestClient`.
- [ ] Wire real model artifacts into the API (loading via model registry).
- [ ] Implement full `/predict` behavior (including preprocessing and ensemble scoring).
- [ ] Add additional API endpoints if needed (e.g., metrics).

---

## 5. Dashboard

- [x] Streamlit app scaffold in `dashboard/app.py`.
- [x] Reads API base URL from environment and pings `/health`.
- [x] `dashboard/requirements.txt` with minimal dependencies.
- [ ] Add views for:
  - [ ] Threshold tuning and performance trade-offs.
  - [ ] Example transactions and model explanations.
  - [ ] Historical monitoring (if data available).

---

## 6. Reporting and Explainability

- [x] `reports/model_comparison.md` template created.
- [ ] Populate comparison report with model metrics (PR-AUC, ROC-AUC, etc.).
- [ ] Implement feature importance / explainability analysis (per `notebooks/01_eda_decisions.ipynb` plan).
- [ ] Surface key results in dashboard and/or API.

---

## 7. Deployment Readiness

- [ ] Verified backend Docker image runs locally and on Hugging Face Spaces.
- [ ] Verified dashboard runs locally and on Streamlit Community Cloud.
- [ ] Documented deployment workflows in `README.md` or separate docs.
- [ ] Confirmed all external services used are free-tier compatible.

---

## 8. Quality and Maintenance

- [ ] Test coverage for critical components (preprocessing, scoring, API).
- [ ] Logging coverage sufficient for debugging in production-like environments.
- [ ] Code style consistent and passes basic linting (if introduced later).
- [ ] Context docs updated when architectural or modeling decisions change.

When you implement a new feature or complete a milestone, **update this file** to reflect the current state.