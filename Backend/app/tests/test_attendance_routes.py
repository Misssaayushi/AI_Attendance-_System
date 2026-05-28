from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database.connection import SessionLocal
from app.main import app
from app.models.admin import Admin
from app.models.attendance import Attendance
from app.models.student import Student
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_header():
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_attendance_route_admin").delete()
    admin = Admin(
        username="test_attendance_route_admin",
        password=get_password_hash("password123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    login = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_attendance_route_admin", "password": "password123"},
    )
    token = login.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    test_students = db.query(Student).filter(Student.roll_number.like("TEST_ATT_RTE%")).all()
    ids = [s.id for s in test_students]
    if ids:
        db.query(Attendance).filter(Attendance.student_id.in_(ids)).delete(synchronize_session=False)
    db.query(Student).filter(Student.roll_number.like("TEST_ATT_RTE%")).delete()
    db.query(Admin).filter(Admin.username == "test_attendance_route_admin").delete()
    db.commit()
    db.close()


def _create_student_for_routes() -> Student:
    db = SessionLocal()
    student = Student(
        first_name="Route",
        last_name="Tester",
        roll_number="TEST_ATT_RTE001",
        email_address="test_att_rte001@example.com",
        department="Computer Science",
        course="B.Tech",
        year_batch="2026",
        semester=6,
        gender="Male",
    )
    db.query(Attendance).filter(Attendance.student_id.in_(
        db.query(Student.id).filter(Student.roll_number == "TEST_ATT_RTE001")
    )).delete(synchronize_session=False)
    db.query(Student).filter(Student.roll_number == "TEST_ATT_RTE001").delete()
    db.add(student)
    db.commit()
    db.refresh(student)
    db.close()
    return student


def test_mark_attendance_route(auth_header):
    student = _create_student_for_routes()
    payload = {
        "student_id": student.id,
        "attendance_date": str(datetime.now(timezone.utc).date()),
        "status": "Present",
        "confidence_score": 0.98,
        "source": "ai_recognition",
    }
    response = client.post(f"{settings.API_PREFIX}/attendance/mark", json=payload, headers=auth_header)
    assert response.status_code == 201
    assert response.json()["success"] is True


def test_mark_attendance_duplicate_route(auth_header):
    db = SessionLocal()
    student = db.query(Student).filter(Student.roll_number == "TEST_ATT_RTE001").first()
    db.close()
    payload = {
        "student_id": student.id,
        "attendance_date": str(datetime.now(timezone.utc).date()),
        "status": "Present",
        "confidence_score": 0.98,
        "source": "ai_recognition",
    }
    response = client.post(f"{settings.API_PREFIX}/attendance/mark", json=payload, headers=auth_header)
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_list_attendance_route(auth_header):
    response = client.get(f"{settings.API_PREFIX}/attendance/", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "items" in response.json()["data"]


def test_daily_summary_route(auth_header):
    response = client.get(f"{settings.API_PREFIX}/attendance/summary/daily", headers=auth_header)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_students" in data
    assert "attendance_percentage" in data


def test_export_preview_route(auth_header):
    response = client.get(f"{settings.API_PREFIX}/attendance/export/preview", headers=auth_header)
    assert response.status_code == 200
    assert "rows" in response.json()["data"]

