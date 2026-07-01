"""Health endpoint tests."""

from fastapi.testclient import TestClient


def test_liveness_returns_200_with_envelope(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "alive"
    assert set(body.keys()) == {"success", "message", "data", "error"}


def test_readiness_reports_per_dependency_status(client: TestClient) -> None:
    # No real Postgres in the unit test env, so readiness is degraded (503),
    # while faked Redis/Qdrant report ok.
    response = client.get("/health/readiness")

    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    checks = body["data"]["checks"]
    assert checks["redis"] == "ok"
    assert checks["qdrant"] == "ok"
    assert checks["database"].startswith("error")
    assert body["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
