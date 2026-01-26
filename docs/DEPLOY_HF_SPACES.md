# Deploying the Backend API to Hugging Face Spaces

This guide explains how to deploy the FastAPI backend (`backend/`) to a **Hugging Face Space** using the provided Dockerfile.

The Space will expose the API under a URL of the form:

- `https://<space-name>.hf.space` (recommended for direct access), or
- `https://huggingface.co/spaces/<org>/<space-name>` (proxied).

> When calling the API from a browser or client, prefer the `*.hf.space` URL to avoid proxy-related 404s.

---

## 1. Prepare the Repository

1. Ensure the repo is pushed to GitHub (or hosted on Hugging Face directly).
2. Confirm that:

   - `backend/Dockerfile` exists and builds locally:

     ```bash
     docker build -t fraud-anomaly-backend -f backend/Dockerfile .
     ```

   - The ML pipeline has been run **at least once** so that `ml/artifacts/` contains:
     - `preprocessor.joblib`
     - `thresholds.json`
     - `metadata.json`
     - Model artifacts (`*.joblib`, `autoencoder.keras`)

   The Space will need these artifacts either baked into the image (by committing small demo artifacts) or mounted at runtime (e.g., by uploading them into the Space).

---

## 2. Create a Space

1. Go to https://huggingface.co/spaces.
2. Click **New Space**.
3. Choose:

   - **SDK**: `Docker`
   - **Hardware**: `CPU basic`
   - **Visibility**: `Public` or `Private` as desired.

4. Give the Space a name, e.g. `fraud-anomaly-lab-api`.

---

## 3. Configure the Space

In the Space settings:

1. Set the **Repository** contents to include this project, or push this repo directly to the Space.
2. Ensure the following files are present at the root of the Space repo:

   - `backend/Dockerfile`
   - `backend/requirements.txt`
   - `ml/requirements.txt`
   - `backend/app/main.py` and the rest of the backend code.
   - `shared/` and `ml/` packages.

3. Optionally add a `README.md` with a short description and an example API call.

---

## 4. Dockerfile Expectations

The provided `backend/Dockerfile`:

- Installs backend and ML dependencies:

  ```dockerfile
  COPY backend/requirements.txt /app/backend-requirements.txt
  COPY ml/requirements.txt /app/ml-requirements.txt

  RUN pip install --no-cache-dir -r /app/backend-requirements.txt \
      && pip install --no-cache-dir -r /app/ml-requirements.txt
  ```

- Copies the code:

  ```dockerfile
  COPY backend /app/backend
  COPY ml /app/ml
  COPY shared /app/shared
  ```

- Starts `uvicorn` using the `PORT` environment variable (which Hugging Face sets automatically):

  ```dockerfile
  CMD ["bash", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```

No further changes are required for basic deployment.

---

## 5. Environment Variables

You can configure environment variables in the Space settings:

- `ROOT_PATH` (optional):
  - Set this if the Space requires a prefix (e.g. when the API is reverse-proxied).
  - The FastAPI app is instantiated with `root_path=os.getenv("ROOT_PATH", "")`.
- `API_LOG_LEVEL` (optional): `info`, `debug`, etc.

For most Spaces, leaving `ROOT_PATH` unset (empty string) is sufficient.

---

## 6. Artifacts Strategy

The backend expects artifacts under `ml/artifacts/` at runtime. There are two common approaches:

1. **Bake small demo artifacts into the image**:
   - Run training locally:

     ```bash
     make download-data
     make preprocess
     make train-all
     ```

   - Commit the resulting small `ml/artifacts/` directory (minus large raw data files).
   - Rebuild the Docker image and push to the Space.

2. **Upload artifacts into the Space**:
   - Keep artifacts out of git locally.
   - In the Space, upload a pre-built `ml/artifacts/` folder via the web UI or `git-lfs` (if large).
   - Ensure the folder path matches `shared.constants.ARTIFACTS_DIR` (`ml/artifacts` at project root).

If artifacts are missing, `/predict` will return `503` with a clear error message indicating that the training pipeline needs to be run.

---

## 7. Smoke Test

Once the Space is built and running:

1. Open the Space’s URL, e.g. `https://fraud-anomaly-lab-api.hf.space`.
2. Visit `/docs` to see the interactive FastAPI documentation.
3. Call:

   - `GET /health` – should return `{ "status": "ok", "component": "api", "loaded_models": ... }`.
   - `GET /metrics` – should return a small JSON with request/latency counters.
   - `GET /models` – should list models and thresholds (if artifacts are present).

You can also use the **dashboard** (deployed separately) to point at the Space’s base URL via `DASHBOARD_API_BASE_URL`.