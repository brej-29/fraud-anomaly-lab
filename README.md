# fraud-anomaly-lab

End-to-end, free-to-run credit card fraud anomaly detection lab. This monorepo contains data pipelines, model training, an inference API, and a monitoring dashboard built around the Kaggle *Credit Card Fraud Detection* dataset (`mlg-ulb/creditcardfraud`).

Key deliverables:
- FastAPI inference service (backend) containerizable for Hugging Face Spaces (Docker).
- Streamlit dashboard for monitoring and interactive what-if analysis, deployable on Streamlit Community Cloud.
- Six anomaly detection models (IsolationForest, LOF, One-Class SVM, COPOD, MLP autoencoder, and a score-based ensemble).
- Reproducible ML training pipeline with explicit decisions and metrics tracked in `context/` and `reports/`.
- Lightweight SQLite-based logging of predictions and feedback to support monitoring and future retraining.

## Free Deployment Targets

- **API**: Hugging Face Spaces using the `backend/` Dockerfile (see `docs/DEPLOY_HF_SPACES.md`).
- **Dashboard**: Streamlit Community Cloud using `dashboard/app.py` and `dashboard/requirements.txt` (see `docs/DEPLOY_STREAMLIT_CLOUD.md`).

## Local Quickstart

```bash
make setup           # install backend + ml + dashboard dependencies into your environment
make download-data   # download Kaggle data into data/raw (requires Kaggle API setup)
make preprocess      # run time-based split + preprocessing, cache splits under data/processed
make train-all       # train 6 models + ensemble and export artifacts under ml/artifacts/
make report          # generate reports/model_comparison.md from training metadata
make api             # run FastAPI dev server on http://localhost:8000
make dashboard       # run Streamlit app on http://localhost:8501
make test            # run backend + ml tests (pytest; TF-heavy tests skipped by default)
make e2e             # run download-data -> preprocess -> train-all -> report
```

## Repo Map (high level)

- `backend/` – FastAPI app, model loading, HTTP API, metrics, SQLite persistence, tests, and Dockerfile.
- `dashboard/` – Streamlit monitoring and exploration UI plus Dockerfile.
- `ml/` – Data download, preprocessing, training, evaluation, autoencoder, and ensemble logic.
- `shared/` – Cross-cutting utilities and constants (including drift metrics).
- `notebooks/` – EDA and decision notebooks.
- `context/` – Grounding docs, architecture, metrics, and acceptance criteria (read these first).
- `scripts/` – Kaggle setup and dataset download scripts.
- `docs/` – Deployment and operations guides.