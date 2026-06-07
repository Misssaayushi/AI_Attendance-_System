import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database.connection import SessionLocal
from app.main import app
from app.models.admin import Admin
from app.services import diagnostics_service
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_diag_admin").delete()
    admin = Admin(
        username="test_diag_admin",
        password=get_password_hash("password123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    login = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_diag_admin", "password": "password123"},
    )
    token = login.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_diag_admin").delete()
    db.commit()
    db.close()


def test_diagnostics_readiness_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        diagnostics_service,
        "get_backend_readiness_snapshot",
        lambda: {
            "timestamp": "2026-05-29T10:00:00+00:00",
            "database": {"connected": True},
            "scheduler": {"enabled": True, "running": True, "timezone": "Asia/Kolkata"},
            "overall_status": "ready",
        },
    )
    response = client.get(f"{settings.API_PREFIX}/diagnostics/readiness", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Backend Readiness Retrieved Successfully"
    assert payload["data"]["overall_status"] == "ready"


def test_diagnostics_api_coverage_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        diagnostics_service,
        "get_api_coverage_matrix",
        lambda: {
            "coverage": {"authentication": ["POST /auth/login"]},
            "totals": {"groups": 1, "endpoints": 1},
        },
    )
    response = client.get(f"{settings.API_PREFIX}/diagnostics/api-coverage", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "API Coverage Matrix Retrieved Successfully"
    assert payload["data"]["totals"]["endpoints"] == 1


def test_diagnostics_runtime_metrics_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        diagnostics_service,
        "get_api_coverage_matrix",
        lambda: {"coverage": {}, "totals": {"groups": 0, "endpoints": 0}},
    )
    response = client.get(f"{settings.API_PREFIX}/diagnostics/metrics", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Runtime Metrics Retrieved Successfully"
    assert "request_count" in payload["data"]


def test_diagnostics_stability_route(auth_header):
    response = client.get(f"{settings.API_PREFIX}/diagnostics/stability", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Stability Snapshot Retrieved Successfully"
    assert "status" in payload["data"]
