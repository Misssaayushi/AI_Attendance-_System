import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.config import settings
from app.main import app
from app.models.admin import Admin
from app.database.connection import SessionLocal
from app.services import email_service
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_email_route_admin").delete()
    admin = Admin(
        username="test_email_route_admin",
        password=get_password_hash("password123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    login = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_email_route_admin", "password": "password123"},
    )
    token = login.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_email_route_admin").delete()
    db.commit()
    db.close()


def test_send_monthly_report_email_invalid_recipient_group():
    with pytest.raises(Exception):
        email_service._resolve_recipient_group("invalid")


def test_send_daily_report_email_route(auth_header, monkeypatch):
    def _fake_send(db, *, target_date, recipient_group, force_send=False):
        return {
            "report_type": "daily",
            "recipients": ["admin@example.com"],
            "file_path": "fake.xlsx",
            "email_sent": True,
            "recipients_count": 1,
            "attachment_name": "fake.xlsx",
            "attempts": 1,
        }

    monkeypatch.setattr(email_service, "send_daily_report_email", _fake_send)
    response = client.post(
        f"{settings.API_PREFIX}/attendance/reports/email/daily",
        params={"target_date": "2026-05-29", "recipient_group": "admin"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["report_type"] == "daily"


def test_send_monthly_report_email_route(auth_header, monkeypatch):
    def _fake_send(db, *, year, month, recipient_group, department=None, student_id=None, force_send=False):
        return {
            "report_type": "monthly",
            "recipients": ["admin@example.com"],
            "file_path": "fake.xlsx",
            "email_sent": True,
            "recipients_count": 1,
            "attachment_name": "fake.xlsx",
            "attempts": 1,
        }

    monkeypatch.setattr(email_service, "send_monthly_report_email", _fake_send)
    response = client.post(
        f"{settings.API_PREFIX}/attendance/reports/email/monthly",
        params={"year": 2026, "month": 5, "recipient_group": "admin"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["report_type"] == "monthly"


def test_compute_email_delivery_summary_from_rows():
    rows = [
        SimpleNamespace(status="success", duration_ms=1200),
        SimpleNamespace(status="failed", duration_ms=2200),
        SimpleNamespace(status="success", duration_ms=1800),
        SimpleNamespace(status="skipped", duration_ms=800),
    ]
    summary = email_service.compute_email_delivery_summary_from_rows(rows)
    assert summary["runs"] == 4
    assert summary["success_runs"] == 2
    assert summary["failed_runs"] == 1
    assert summary["skipped_runs"] == 1
    assert summary["avg_duration_ms"] == 1500
    assert summary["success_rate_pct"] == 50.0


def test_email_deliveries_route(auth_header, monkeypatch):
    fake_rows = [
        SimpleNamespace(
            id=1,
            report_type="daily",
            report_date=SimpleNamespace(isoformat=lambda: "2026-05-29"),
            recipient_group="admin",
            report_label="all_students",
            status="success",
            attempts=1,
            recipients_count=2,
            attachment_name="attendance_2026_05.xlsx",
            duration_ms=1300,
            error_message=None,
            started_at=SimpleNamespace(isoformat=lambda: "2026-05-29T17:00:00+00:00"),
            finished_at=SimpleNamespace(isoformat=lambda: "2026-05-29T17:00:01+00:00"),
        )
    ]
    monkeypatch.setattr(email_service, "list_email_deliveries", lambda db, limit=50: fake_rows)
    response = client.get(f"{settings.API_PREFIX}/attendance/reports/email/deliveries?limit=10", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["count"] == 1


def test_email_delivery_summary_route(auth_header, monkeypatch):
    fake_summary = {
        "runs": 4,
        "success_runs": 3,
        "failed_runs": 1,
        "skipped_runs": 0,
        "avg_duration_ms": 1450,
        "success_rate_pct": 75.0,
    }
    monkeypatch.setattr(email_service, "get_email_delivery_summary", lambda db, last_n=50: fake_summary)
    response = client.get(f"{settings.API_PREFIX}/attendance/reports/email/summary?last_n=30", headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["success_rate_pct"] == 75.0
