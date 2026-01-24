import os

import requests
import streamlit as st


def get_api_base_url() -> str:
    """Resolve the API base URL from environment or fallback."""
    return os.getenv("DASHBOARD_API_BASE_URL", "http://localhost:8000")


def ping_api(base_url: str) -> dict:
    """Ping the backend /health endpoint and return response or error."""
    url = f"{base_url.rstrip('/')}/health"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return {"ok": True, "data": response.json()}
    except Exception as exc:  # noqa: BLE001 - broad for UI display
        return {"ok": False, "error": str(exc)}


def main() -> None:
    """Main entrypoint for the Streamlit dashboard."""
    st.set_page_config(page_title="Fraud Anomaly Lab Dashboard", layout="wide")

    st.title("Fraud Anomaly Lab – Dashboard")
    st.write(
        "This Streamlit app will provide monitoring and interactive analysis for the "
        "credit card fraud anomaly detection models."
    )

    api_base_url = get_api_base_url()
    st.sidebar.header("Configuration")
    st.sidebar.text_input("API Base URL", value=api_base_url, key="api_base_url")

    if st.button("Ping API"):
        result = ping_api(st.session_state.get("api_base_url", api_base_url))
        if result["ok"]:
            st.success(f"API is reachable: {result['data']}")
        else:
            st.error(f"Failed to reach API: {result['error']}")

    st.markdown("---")
    st.subheader("Planned Features")
    st.markdown(
        """
        - Threshold tuning and precision–recall trade-off visualization.
        - Model comparison across six anomaly detection models and ensemble.
        - Example transaction scoring and explanation.
        - Monitoring views for recent predictions (if data is logged).
        """
    )


if __name__ == "__main__":
    main()