# Deploying the Dashboard to Streamlit Community Cloud

This guide explains how to deploy the Streamlit dashboard (`dashboard/app.py`) to **Streamlit Community Cloud**.

The dashboard is a thin UI layer: it talks to the backend API via HTTP and does not contain any model weights.

---

## 1. Prepare the Repository

1. Ensure your repository is on GitHub (public is easiest for Streamlit Community Cloud).
2. Confirm that the dashboard works locally:

   ```bash
   make setup           # installs backend + ml + dashboard deps
   make api             # in a separate terminal
   make dashboard       # runs on http://localhost:8501
   ```

3. Verify that the dashboard can reach the API when `DASHBOARD_API_BASE_URL` is set appropriately (e.g. `http://localhost:8000` locally or your Hugging Face Space URL in production).

---

## 2. Create a Streamlit App

1. Go to https://share.streamlit.io.
2. Click **New app**.
3. Select the GitHub repo and branch.
4. Set the entrypoint to:

   - **File**: `dashboard/app.py`

5. Click **Deploy**.

---

## 3. Configure Environment Variables

In the app settings on Streamlit Cloud, configure:

- `DASHBOARD_API_BASE_URL`:
  - Point this to your backend API base URL, for example:
    - Local tunneling (during testing): `https://<your-ngrok-subdomain>.ngrok.io`
    - Hugging Face Space: `https://fraud-anomaly-lab-api.hf.space`
  - The dashboard’s API calls will be of the form:
    - `GET {DASHBOARD_API_BASE_URL}/health`
    - `POST {DASHBOARD_API_BASE_URL}/predict`
    - `GET {DASHBOARD_API_BASE_URL}/models`, etc.

No other environment variables are strictly required for the dashboard.

---

## 4. Dependencies

`dashboard/requirements.txt` already lists the minimal dependencies:

```txt
streamlit
requests
pandas
```

Streamlit Community Cloud will install these automatically during deployment.

---

## 5. Verifying the Deployment

Once the app is live:

1. Open the Streamlit app URL.
2. In the sidebar, confirm that the **API Base URL** matches your backend:

   - You can override it interactively for experimentation.
   - The value is stored in `st.session_state["api_base_url"]`.

3. Use the tabs to verify functionality:

   - **API Health**:
     - Should show `/health` and `/metrics` responses from the backend.
   - **Models**:
     - Should list model metrics if artifacts are present.
   - **Predict**:
     - Paste a sample transaction JSON and verify that a prediction is returned.
   - **Monitoring**:
     - If the backend has processed some predictions, you should see recent records and drift information.

If the dashboard shows connectivity errors, double-check:

- The `DASHBOARD_API_BASE_URL` value.
- That the backend is reachable from the public internet (Hugging Face Space or other hosting).
- CORS/proxy settings where applicable (Hugging Face Spaces handle CORS automatically for simple use cases).