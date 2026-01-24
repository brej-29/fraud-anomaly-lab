# Project Goal

Build an end-to-end **credit card fraud anomaly detection lab** that is:

- **Free to run and deploy**:
  - API served via FastAPI, containerized and deployable on **Hugging Face Spaces (Docker)**.
  - Monitoring and exploration dashboard built with **Streamlit**, deployable on **Streamlit Community Cloud**.
- **Transparent and decision-focused**:
  - All major modeling and engineering decisions are captured in `context/` and in EDA notebooks.
  - Metrics, thresholds, and trade-offs are documented and reproducible.
- **Extensible and testable**:
  - Clear boundaries between ML training, model artifacts, API, and dashboard.
  - Basic tests and CI from the start.

We use the Kaggle dataset:

> **Credit Card Fraud Detection** – https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Raw data is **never committed** to git. It must be downloaded via the Kaggle API into `data/raw/`.

---

## Constraints

- **Cost / licensing**
  - Only **free** services: Hugging Face Spaces (Docker) and Streamlit Community Cloud.
  - Use only open-source Python libraries that are free for commercial and academic use.
- **Runtime / environment**
  - Python **3.10+**.
  - Designed to run on modest CPU-only environments (no GPU assumed).
- **Data handling**
  - Raw Kaggle CSV is downloaded locally to `data/raw/` and ignored by git.
  - Derived artifacts (trained models) are stored under `ml/artifacts/` and ignored, except for small sample/demo artifacts if explicitly added later.
- **Simplicity first**
  - Favor simple, explainable pipelines and code structure over heavy orchestration.
  - Prefer a single repository with clear submodules (`backend/`, `dashboard/`, `ml/`, `shared/`).

---

## Success Metrics (High Level)

We treat this as a **highly imbalanced, binary classification / anomaly detection** problem. Fraud is rare and costly.

Primary objectives:

- **Detection quality**
  - Achieve **high recall on fraud cases** while keeping precision acceptable.
  - Focus on **PR-AUC** (Precision–Recall AUC) as a primary metric due to class imbalance.
- **Proposed initial targets** (subject to refinement after baseline runs):
  - **Validation PR-AUC**: > 0.80.
  - **Validation ROC-AUC**: > 0.97.
  - At a selected operating threshold:
    - **Recall (fraud)**: >= 0.80.
    - **Precision (fraud)**: >= 0.10 (starting point, to be refined with business context).
- **Operational quality**
  - API health endpoint always available.
  - Latency suitable for real-time per-transaction scoring on CPU (e.g., &lt; 50 ms per transaction for typical models).

These targets are **aspirational** and will be revisited as we run baselines.

---

## Dataset Facts (for grounding)

- Dataset: **Credit Card Fraud Detection** (European cardholder transactions, September 2013).
- Size: **284,807** transactions, **492** frauds (~0.172% fraud rate).
- Features:
  - `Time`: seconds elapsed between each transaction and the first transaction in the dataset.
  - `Amount`: transaction amount.
  - `Class`: binary target (1 = fraud, 0 = non-fraud).
  - `V1`–`V28`: numerical features obtained via **PCA** transformation for confidentiality.
- Key implications:
  - **Severe class imbalance** → accuracy is misleading; use PR-AUC, ROC-AUC, recall, precision.
  - **PCA components (V1–V28)** are not directly interpretable; feature importance must be handled via model-agnostic methods.
  - **Time field** enables leakage-aware splits (e.g., train on earlier timestamps, validate/test on later).

---

## High-Level Objective Statement

> Build a fully reproducible, free-to-deploy anomaly detection lab for credit card fraud using the Kaggle credit card dataset, delivering a FastAPI inference API, a Streamlit monitoring dashboard, and a suite of six anomaly detection models (including COPOD via PyOD) with an ensemble, all grounded in explicit, documented decisions and metrics.