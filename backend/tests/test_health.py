from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("component") == "api"