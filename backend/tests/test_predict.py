from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _dummy_transaction_payload() -> dict:
    # Minimal valid transaction payload matching schemas.transactions.Transaction.
    base = {
        "Time": 0.0,
        "Amount": 1.0,
    }
    for i in range(1, 29):
        base[f"V{i}"] = 0.0
    return base


def test_predict_returns_503_when_artifacts_missing() -> None:
    """
    When no ML artifacts are present, the predict endpoint should respond with 503.

    This keeps failure modes explicit instead of silently returning dummy scores.
    """
    response = client.post("/predict", json=_dummy_transaction_payload())
    assert response.status_code == 503
    data = response.json()
    assert "Model artifacts not available" in data.get("detail", "")


def test_models_endpoint_available_without_artifacts() -> None:
    """
    The /models endpoint should still respond even if no artifacts have been trained yet.
    """
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "thresholds" in data


def test_drift_endpoint_reports_missing_baseline_without_artifacts() -> None:
    """
    The drift endpoint should explain that baseline histograms are missing when
    training has not yet been run.
    """
    response = client.get("/drift")
    assert response.status_code == 503
    data = response.json()
    assert "baseline histogram not available" in data.get("detail", "")