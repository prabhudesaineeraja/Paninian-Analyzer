from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_endpoint() -> None:
    resp = client.post("/analyze", json={"text": "rama gacchati vanam", "top_k": 3})
    assert resp.status_code == 200
    data = resp.json()

    assert "top_analysis" in data
    assert len(data["top_analysis"]["tokens"]) >= 1
    assert data["top_analysis"]["rank"] == 1
