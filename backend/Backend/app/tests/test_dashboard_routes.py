import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database.connection import SessionLocal
from app.main import app
from app.models.admin import Admin
from app.services import dashboard_analytics_service
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_dashboard_admin").delete()
    admin = Admin(
        username="test_dashboard_admin",
        password=get_password_hash("password123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    login = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_dashboard_admin", "password": "password123"},
    )
    token = login.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_dashboard_admin").delete()
    db.commit()
    db.close()


def test_dashboard_summary_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_dashboard_summary",
        lambda db, target_date=None, department=None: {
            "date": "2026-05-29",
            "department": department,
            "total_students": 120,
            "present_today": 102,
            "absent_today": 18,
            "attendance_percentage": 85.0,
        },
    )

    response = client.get(
        f"{settings.API_PREFIX}/dashboard/summary",
        params={"target_date": "2026-05-29", "department": "Computer Science"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Analytics Retrieved Successfully"
    assert payload["data"]["total_students"] == 120
    assert payload["data"]["attendance_percentage"] == 85.0


def test_dashboard_daily_stats_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_daily_attendance_stats",
        lambda db, target_date=None, department=None: {
            "date": "2026-05-29",
            "department": department,
            "total_students": 100,
            "present_students": 88,
            "absent_students": 12,
            "attendance_percentage": 88.0,
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/stats/daily",
        params={"target_date": "2026-05-29", "department": "IT"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Daily Analytics Retrieved Successfully"
    assert payload["data"]["present_students"] == 88


def test_dashboard_monthly_stats_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_monthly_attendance_stats",
        lambda db, year, month, department=None: {
            "year": year,
            "month": month,
            "department": department,
            "days_in_month": 31,
            "total_students": 120,
            "present_records": 3000,
            "absent_records": 720,
            "attendance_percentage": 80.65,
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/stats/monthly",
        params={"year": 2026, "month": 5, "department": "Computer Science"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Monthly Analytics Retrieved Successfully"
    assert payload["data"]["days_in_month"] == 31


def test_dashboard_department_stats_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_department_attendance_stats",
        lambda db, target_date=None: [
            {
                "department": "CSE",
                "total_students": 60,
                "present_students": 51,
                "absent_students": 9,
                "attendance_percentage": 85.0,
            },
            {
                "department": "IT",
                "total_students": 40,
                "present_students": 32,
                "absent_students": 8,
                "attendance_percentage": 80.0,
            },
        ],
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/stats/department",
        params={"target_date": "2026-05-29"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Department Analytics Retrieved Successfully"
    assert payload["data"]["count"] == 2


def test_dashboard_weekly_graph_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_weekly_trend_graph",
        lambda db, end_date=None, days=7, department=None: {
            "range": {"from_date": "2026-05-23", "to_date": "2026-05-29"},
            "department": department,
            "labels": ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"],
            "data": [75.0, 72.0, 84.0, 85.0, 88.0, 86.0, 90.0],
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/graphs/weekly",
        params={"end_date": "2026-05-29", "days": 7, "department": "CSE"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Weekly Trend Retrieved Successfully"
    assert payload["data"]["labels"][0] == "Sat"


def test_dashboard_monthly_graph_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_monthly_trend_graph",
        lambda db, year, month, department=None: {
            "range": {"year": year, "month": month},
            "department": department,
            "labels": ["01", "02", "03"],
            "data": [80.0, 82.5, 79.0],
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/graphs/monthly",
        params={"year": 2026, "month": 5, "department": "IT"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Monthly Trend Retrieved Successfully"
    assert payload["data"]["data"][1] == 82.5


def test_dashboard_department_graph_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_department_comparison_graph",
        lambda db, target_date=None: {
            "date": "2026-05-29",
            "labels": ["CSE", "IT", "ECE"],
            "data": [88.0, 82.0, 79.0],
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/graphs/department",
        params={"target_date": "2026-05-29"},
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Department Comparison Retrieved Successfully"
    assert payload["data"]["labels"][2] == "ECE"


def test_dashboard_monitoring_summary_route(auth_header, monkeypatch):
    monkeypatch.setattr(
        dashboard_analytics_service,
        "get_analytics_monitoring_summary",
        lambda db: {
            "total_students": 220,
            "total_attendance_records": 5100,
            "latest_attendance_date": "2026-05-29",
            "analytics_default_trend_days": 7,
            "analytics_max_trend_days": 31,
        },
    )
    response = client.get(
        f"{settings.API_PREFIX}/dashboard/monitoring/summary",
        headers=auth_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Analytics Monitoring Retrieved Successfully"
    assert payload["data"]["total_students"] == 220
