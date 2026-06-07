from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database.connection import SessionLocal
from app.main import app
from app.models.admin import Admin
from app.services import auto_absent_service
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_scheduler_route_admin").delete()
    admin = Admin(
        username="test_scheduler_route_admin",
        password=get_password_hash("password123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    login = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_scheduler_route_admin", "password": "password123"},
    )
    token = login.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_scheduler_route_admin").delete()
    db.commit()
    db.close()


def test_scheduler_executions_route(auth_header, monkeypatch):
    fake_rows = [
        SimpleNamespace(
            id=1,
            job_name="auto_absent_daily",
            run_date=SimpleNamespace(isoformat=lambda: "2026-05-29"),
            status="success",
            started_at=SimpleNamespace(isoformat=lambda: "2026-05-29T17:00:00+00:00"),
            finished_at=SimpleNamespace(isoformat=lambda: "2026-05-29T17:00:02+00:00"),
            total_students=100,
            already_marked=80,
            auto_absent_marked=20,
            duplicate_skipped=0,
            excel_synced=20,
            attempt_count=1,
            duration_ms=2000,
            error_message=None,
        )
    ]

    monkeypatch.setattr(auto_absent_service, "list_scheduler_executions", lambda db, limit=30: fake_rows)
    response = client.get(f"{settings.API_PREFIX}/attendance/automation/executions?limit=10", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["count"] == 1
    assert payload["data"]["items"][0]["status"] == "success"


def test_scheduler_summary_route(auth_header, monkeypatch):
    fake_summary = {
        "runs": 5,
        "success_runs": 4,
        "partial_runs": 1,
        "failed_runs": 0,
        "avg_duration_ms": 1400,
        "avg_auto_absent_marked": 18,
        "success_rate_pct": 80.0,
    }
    monkeypatch.setattr(auto_absent_service, "get_scheduler_summary", lambda db, last_n=30: fake_summary)
    response = client.get(f"{settings.API_PREFIX}/attendance/automation/summary?last_n=15", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["runs"] == 5
    assert payload["data"]["success_rate_pct"] == 80.0

