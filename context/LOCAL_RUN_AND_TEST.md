# Local Run &amp; Test Guide

This guide explains **exactly** how to run and test the full fraud anomaly lab system locally on Windows, including backend API, ML training, and Streamlit dashboard.

---

## 1. Before You Start

### 1.1 Software you need installed

On your Windows machine, ensure you have:

1. **Python 3.10+**
   - Check:
     - CMD / PowerShell:
       ```bash
       python --version
       ```
   - If missing, install from: https://www.python.org/downloads/

2. **Git**
   - Check:
     ```bash
     git --version
     ```
   - If missing, install from: https://git-scm.com/downloads

3. **Make (optional but recommended)**
   - Many commands are wrapped in the `Makefile`.
   - On Windows one easy option is **Git Bash** (installed with Git) + a basic `make`:
     - Option A – via Chocolatey (from an *elevated* PowerShell):
       ```powershell
       choco install make
       ```
     - Option B – use **Git Bash** and install `make` via your package manager (if available).
   - If you do not have `make`, you can still run everything using the raw Python commands listed below.

4. **Virtual environment support**
   - Python 3.10+ includes `venv` by default.
   - Verify:
     ```bash
     python -m venv --help
     ```

5. **(Optional) Docker Desktop**
   - Only required if you want to run the services via Docker or mimic deployment.
   - Download from: https://www.docker.com/products/docker-desktop

---

### 1.2 Files to read (recommended context)

Before running everything, skim these project docs (already in the repo):

- `README.md` – high-level overview and quickstart.
- `context/COMPONENTS.md` – architecture of ML pipeline, API, monitoring, and dashboard.
- `context/DECISIONS.md` – key design decisions (including the six models and ensemble).
- `docs/RETRAINING_AND_OPERATIONS.md` – how retraining, thresholds, and drift monitoring work.

These are not strictly required to *run* the system, but they help you understand what each command is doing.

---

## 2. Get the Code &amp; Create a Virtual Environment (Windows)

You can do this in **CMD**, **PowerShell**, or **Git Bash**. Choose one shell and stay consistent.

### 2.1 Clone the repository

**CMD / PowerShell / Git Bash** (all the same):

```bash
git clone &lt;YOUR_REPO_URL&gt; fraud-anomaly-lab
cd fraud-anomaly-lab
```

Replace `&lt;YOUR_REPO_URL&gt;` with your actual Git URL (HTTPS or SSH).

---

### 2.2 Create and activate a virtual environment

Below are shell-specific commands.

#### 2.2.1 CMD

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

To confirm you are in the venv:

```cmd
python --version
pip --version
```

#### 2.2.2 PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run (once, in an elevated PowerShell):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry activation.

#### 2.2.3 Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Check:

```bash
python --version
pip --version
```

---

## 3. Install Dependencies

You can either use **Make** (recommended if available) or run raw pip commands.

### 3.1 Using Make (Windows with `make` installed)

From the repo root (venv activated):

```bash
make setup
```

This will:

- Install backend, ML, and shared dependencies.
- Install `ruff` and test dependencies.

### 3.2 Without Make: Manual installation (CMD / PowerShell / Git Bash)

From the repo root (venv activated):

```bash
pip install -r ml/requirements.txt
pip install -r backend/requirements.txt
pip install -r dashboard/requirements.txt
pip install -r shared/requirements.txt
pip install ruff
pip install pytest
```

(If the project uses editable installs or extra `setup.cfg`/`pyproject.toml`, `make setup` is still preferred. Use the Makefile as the source of truth if in doubt.)

---

## 4. Prepare Data and Train Models Locally

### 4.1 Download the dataset

If `make` is available:

```bash
make download-data
```

Without `make`, refer to the `Makefile` target `download-data` to see the exact script or commands used (typically something like `python scripts/download_data.py`).

Example (if applicable):

```bash
python scripts/download_data.py
```

### 4.2 Preprocess the data

With Make:

```bash
make preprocess
```

Without Make (check Makefile for exact script name):

```bash
python ml/preprocess.py
```

### 4.3 Train all models (6 base models + ensemble)

With Make:

```bash
make train-all
```

This:

- Trains IsolationForest, LOF, One-Class SVM, COPOD, Autoencoder, and the score-based ensemble.
- Saves artifacts to `ml/artifacts/` including:
  - `preprocessor.joblib`
  - model files (`*.joblib`, `autoencoder.keras`)
  - `metadata.json`
  - `thresholds.json`

Without Make (equivalent):

```bash
python ml/train_all.py
```

### 4.4 Generate the model comparison report (optional but recommended)

With Make:

```bash
make report
```

Without Make (check the Makefile; typically):

```bash
python ml/evaluate.py
```

This will generate a markdown report under `reports/` summarizing all six models and the ensemble.

---

## 5. Run the Backend API Locally

You can run the backend using **Make** or directly via **uvicorn**.

> Make sure the training step has produced `ml/artifacts/` before starting the API, otherwise the model registry cannot load.

### 5.1 Using Make

From the repo root (venv activated):

```bash
make api
```

By default this will run the FastAPI app (e.g. on `http://localhost:8000`), respecting the `PORT` environment variable if set.

### 5.2 Without Make: using uvicorn directly

#### 5.2.1 CMD

```cmd
set PORT=8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port %PORT% --reload
```

#### 5.2.2 PowerShell

```powershell
$env:PORT = 8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $env:PORT --reload
```

#### 5.2.3 Git Bash

```bash
export PORT=8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --reload
```

Once running, check:

- **Health**: http://localhost:8000/health
- **Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

---

## 6. Run the Streamlit Dashboard Locally

The dashboard connects to the backend API (URL configurable via environment or UI).

### 6.1 Using Make

From the repo root (venv activated):

```bash
make dashboard
```

By default this will start Streamlit on `http://localhost:8501`.

### 6.2 Without Make: `streamlit run`

Ensure the backend is already running (step 5).

#### 6.2.1 CMD

```cmd
set API_BASE_URL=http://localhost:8000
streamlit run dashboard/app.py --server.port 8501
```

#### 6.2.2 PowerShell

```powershell
$env:API_BASE_URL = "http://localhost:8000"
streamlit run dashboard/app.py --server.port 8501
```

#### 6.2.3 Git Bash

```bash
export API_BASE_URL=http://localhost:8000
streamlit run dashboard/app.py --server.port 8501
```

Then open: http://localhost:8501

In the UI:

- **API Health** tab → verify connectivity.
- **Models** tab → view metrics from `metadata.json`.
- **Predict** tab → send sample transactions.
- **Monitoring** tab → inspect recent predictions and drift.

---

## 7. Run Tests Locally

### 7.1 Run all tests via Make

With `make`:

```bash
make test
```

(If the Makefile separates backend and ML tests, follow those targets, e.g. `make test-backend`, `make test-ml`.)

TensorFlow-heavy tests are usually marked with `tf_heavy` and skipped by default in CI; you can selectively include or exclude them as needed.

### 7.2 Run ML tests manually

From repo root, venv activated:

#### 7.2.1 All ML tests (excluding heavy ones by default)

```bash
pytest ml
```

#### 7.2.2 Explicitly run or skip TensorFlow-heavy tests

- Run **only** TensorFlow-heavy tests:

  ```bash
  pytest ml -m tf_heavy
  ```

- Run **everything except** TensorFlow-heavy tests:

  ```bash
  pytest ml -m "not tf_heavy"
  ```

### 7.3 Run backend tests

```bash
pytest backend
```

You can also run a single test file or test class, e.g.:

```bash
pytest backend/tests/test_api_health.py
```

### 7.4 Lint the code with Ruff

With Make:

```bash
make lint
```

Without Make:

```bash
ruff backend ml shared
```

---

## 8. (Optional) Run Everything via Docker on Windows

If you have **Docker Desktop** and want to use the provided `docker-compose.yml`:

### 8.1 Start services

#### 8.1.1 PowerShell / CMD

From the repo root:

```bash
docker-compose up --build
```

This will:

- Build and run the backend container.
- Build and run the dashboard container.
- Use network settings defined in `docker-compose.yml`.

Once running:

- Backend: typically at `http://localhost:8000` (or configured port).
- Dashboard: typically at `http://localhost:8501`.

### 8.2 Stop services

```bash
docker-compose down
```

---

## 9. Summary: Quick Command Cheat Sheet (Windows)

### 9.1 One-time setup

```bash
git clone &lt;YOUR_REPO_URL&gt; fraud-anomaly-lab
cd fraud-anomaly-lab
python -m venv .venv
# CMD
.\.venv\Scripts\activate
# PowerShell
.\.venv\Scripts\Activate.ps1
# Git Bash
source .venv/Scripts/activate

make setup           # or use manual pip installs
make download-data
make preprocess
make train-all
make report          # optional
```

### 9.2 Daily development loop

Terminal 1 (backend):

```bash
make api
# or uvicorn as shown above for your shell
```

Terminal 2 (dashboard):

```bash
make dashboard
# or streamlit run dashboard/app.py
```

### 9.3 Testing and linting

```bash
make test            # if available
pytest ml -m "not tf_heavy"
pytest backend
ruff backend ml shared
```

This file is the canonical step-by-step reference for running and testing the system locally on Windows (CMD, PowerShell, or Git Bash). For deeper architectural context, refer back to the other files in the `context/` folder.