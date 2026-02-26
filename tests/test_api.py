from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_get_random_endpoint_schema():
    res = client.get("/get_random?n_bytes=16&mode=hybrid_mix")
    assert res.status_code == 200
    data = res.json()

    assert "random_number" in data
    assert "health_score" in data
    assert "source" in data
    assert "latency_ms" in data

    # 16 bytes => 32 hex chars
    assert len(data["random_number"]) == 32

def test_stats_endpoint():
    res = client.get("/stats?last_n=50")
    assert res.status_code == 200
    data = res.json()
    assert "by_source" in data
