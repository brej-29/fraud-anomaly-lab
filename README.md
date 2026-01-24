# fraud-anomaly-lab

End-to-end, free-to-run credit card fraud anomaly detection lab. This monorepo contains data pipelines, model training, an inference API, and a monitoring dashboard built around the Kaggle *Credit Card Fraud Detection* dataset (mlg-ulb/creditcardfraud).

Key deliverables:
- FastAPI inference service (backend) containerizable for Hugging Face Spaces (Docker).
- Streamlit dashboard for monitoring and interactive what-if analysis, deployable on Streamlit Community Cloud.
- Six anomaly detection models including COPOD (via PyOD) and an ensemble layer.
- Reproducible ML training pipeline with explicit decisions and metrics tracked in `context/` and `reports/`.

## Free Deployment Targets

- **API**: Hugging Face Spaces using the `backend/` Dockerfile.
- **Dashboard**: Streamlit Community Cloud using `dashboard/app.py` and `dashboard/requirements.txt`.

## Local Quickstart

```bash
make setup           # install backend + ml + dashboard dependencies into your environment
make download-data   # download Kaggle data into data/raw (requires Kaggle API setup)
make preprocess      # run time-based split + preprocessing, cache splits under data/processed
make train           # train 4 anomaly models (IsolationForest, LOF, One-Class SVM, COPOD) and export artifacts
make report          # generate reports/model_comparison.md from training metadata
make api             # run FastAPI dev server on http://localhost:8000
make dashboard       # run Streamlit app on http://localhost:8501
make test            # run backend + ml tests (pytest)
make e2e             # run download-data -> preprocess -> train -> report
```

## Repo Map (high level)

- `backend/` – FastAPI app, model loading, HTTP API, tests, and Dockerfile.
- `dashboard/` – Streamlit monitoring and exploration UI plus Dockerfile.
- `ml/` – Data download, preprocessing, training, evaluation, and ensemble logic.
- `shared/` – Cross-cutting utilities and constants.
- `notebooks/` – EDA and decision notebooks.
- `context/` – Grounding docs, architecture, metrics, and acceptance criteria (read these first).
- `scripts/` – Kaggle setup and dataset download scripts.