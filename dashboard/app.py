import json
import os
from typing import Any, Dict, Tuple

import pandas as pd
import requests
import streamlit as st


def get_api_base_url() -> str:
    """Resolve the API base URL from environment or fallback."""
    return os.getenv("DASHBOARD_API_BASE_URL", "http://localhost:8000")


def call_api(path: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Tuple[bool, Any]:
    """
    Call the backend API and return (ok, data_or_error_message).
    """
    base_url = st.session_state.get("api_base_url", get_api_base_url())
    url = f"{base_url.rstrip('/')}{path}"
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True, resp.json()
    except Exception as exc:  # noqa: BLE001 - broad for UI display
        return False, str(exc)


def _render_health_tab() -> None:
    st.subheader("API Health and Configuration")

    # Health
    ok, data = call_api("/health")
    if ok:
        st.success("Backend /health is reachable.")
        st.json(data)
    else:
        st.error(f"Failed to reach /health: {data}")
        return

    # Metrics
    ok, metrics = call_api("/metrics")
    st.markdown("### Runtime Metrics")
    if ok:
        st.json(metrics)
    else:
        st.warning(f"Could not fetch /metrics: {metrics}")


def _render_models_tab() -> None:
    st.subheader("Model Comparison (Validation/Test)")

    ok, data = call_api("/models")
    if not ok:
        st.error(f"Failed to fetch /models: {data}")
        return

    models = data.get("models", {})
    if not models:
        st.info(
            "No models found in metadata. "
            "Run the training pipeline (`make train-all`) and restart the API."
        )
        return

    rows = []
    for model_name, info in models.items():
        metrics = info.get("metrics", {})
        threshold = info.get("threshold")
        constraints_met = info.get("constraints_met")
        for split in ("val", "test"):
            m = metrics.get(split, {})
            rows.append(
                {
                    "model": model_name,
                    "split": split,
                    "roc_auc": m.get("roc_auc"),
                    "pr_auc": m.get("pr_auc"),
                    "precision": m.get("precision"),
                    "recall": m.get("recall"),
                    "f1": m.get("f1"),
                    "threshold": threshold if split == "val" else "",
                    "constraints_met": constraints_met if split == "val" else "",
                }
            )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.markdown(
        """
        **Notes**

        - Metrics are computed using a time-based split (train/val/test).
        - Thresholds are calibrated on the validation set with precision & recall constraints.
        - The ensemble model aggregates min–max normalized scores from all base models.
        """
    )


def _render_predict_tab() -> None:
    st.subheader("Score a Transaction")

    st.markdown(
        """
        Paste a JSON payload representing a single transaction with fields
        `Time`, `Amount`, and `V1`–`V28`. Example:
        """
    )

    example_payload = {
        "Time": 0.0,
        "Amount": 1.0,
        **{f"V{i}": 0.0 for i in range(1, 29)},
    }
    default_json = json.dumps(example_payload, indent=2)
    payload_text = st.text_area("Transaction JSON", value=default_json, height=260)

    if st.button("Score Transaction"):
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
            return

        ok, data = call_api("/predict", method="POST", payload=payload)
        if not ok:
            st.error(f"Prediction failed: {data}")
            return

        st.success("Prediction received.")
        st.json(data)


def _render_monitor_tab() -> None:
    st.subheader("Monitoring and Drift")

    st.markdown("### Recent Predictions")
    limit = st.slider("Number of recent predictions", min_value=10, max_value=500, value=100, step=10)
    ok, recent = call_api(f"/monitor/recent?limit={limit}")
    if ok and recent.get("records"):
        df = pd.DataFrame(recent["records"])
        st.dataframe(df, use_container_width=True)
    elif ok:
        st.info("No predictions have been recorded yet.")
    else:
        st.warning(f"Could not fetch recent predictions: {recent}")

    st.markdown("### Drift (PSI on Ensemble Scores)")
    window_size = st.slider("Window size for drift computation", min_value=50, max_value=1000, value=500, step=50)
    ok, drift_info = call_api(f"/drift?window_size={window_size}")
    if ok:
        st.json(drift_info)
    else:
        st.warning(f"Could not fetch drift metrics: {drift_info}")


def main() -> None:
    """Main entrypoint for the Streamlit dashboard."""
    st.set_page_config(page_title="Fraud Anomaly Lab Dashboard", layout="wide")

    st.title("Fraud Anomaly Lab – Dashboard")
    st.write(
        "Monitoring and interactive analysis for the credit card fraud "
        "anomaly detection models."
    )

    api_base_url = get_api_base_url()
    st.sidebar.header("Configuration")
    st.sidebar.text_input("API Base URL", value=api_base_url, key="api_base_url")

    tab_health, tab_models, tab_predict, tab_monitor = st.tabs(
        ["API Health", "Models", "Predict", "Monitoring"]
    )

    with tab_health:
        _render_health_tab()
    with tab_models:
        _render_models_tab()
    with tab_predict:
        _render_predict_tab()
    with tab_monitor:
        _render_monitor_tab()


if __name__ == "__main__":
    main()