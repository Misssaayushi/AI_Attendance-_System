import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database.connection import SessionLocal
from app.models.admin import Admin
from app.models.student import Student
from app.utils.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header():
    """Setup a test admin, log in, and return headers containing Bearer token."""
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_student_route_admin").delete()
    
    # Create new test admin
    test_admin = Admin(
        username="test_student_route_admin",
        password=get_password_hash("password123")
    )
    db.add(test_admin)
    db.commit()
    db.close()
    
    # Log in
    response = client.post(
        f"{settings.API_PREFIX}/auth/login",
        json={"username": "test_student_route_admin", "password": "password123"}
    )
    token = response.json()["access_token"]
    
    # Clean up student test records
    db = SessionLocal()
    db.query(Student).filter(Student.roll_number.like("TEST_RTE%")).delete()
    db.commit()
    db.close()
    
    yield {"Authorization": f"Bearer {token}"}
    
    # Cleanup admin and student test records at end
    db = SessionLocal()
    db.query(Admin).filter(Admin.username == "test_student_route_admin").delete()
    db.query(Student).filter(Student.roll_number.like("TEST_RTE%")).delete()
    db.commit()
    db.close()

def test_unauthorized_access():
    """Verify that accessing endpoints without a valid token returns 401."""
    response = client.get(f"{settings.API_PREFIX}/students/")
    assert response.status_code == 401

def test_create_student_route(auth_header):
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "test_rte_jane@example.com",
        "roll_number": "TEST_RTE001",
        "department": "IT",
        "course": "B.Tech",
        "year_batch": "2025",
        "semester": 3,
        "gender": "Female"
    }
    response = client.post(
        f"{settings.API_PREFIX}/students/",
        json=payload,
        headers=auth_header
    )
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["email"] == "test_rte_jane@example.com"
    assert res_data["data"]["roll_number"] == "TEST_RTE001"

def test_create_student_duplicate_roll_route(auth_header):
    # Try creating student with existing roll number
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "test_rte_jane_unique@example.com",
        "roll_number": "TEST_RTE001", # Existing
        "department": "IT",
        "course": "B.Tech",
        "year_batch": "2025",
        "semester": 3,
        "gender": "Female"
    }
    response = client.post(
        f"{settings.API_PREFIX}/students/",
        json=payload,
        headers=auth_header
    )
    assert response.status_code == 400
    res_data = response.json()
    assert res_data["success"] is False
    assert "Roll number already registered" in res_data["message"]

def test_list_students_route(auth_header):
    response = client.get(
        f"{settings.API_PREFIX}/students/",
        params={"page": 1, "page_size": 10, "search": "Jane"},
        headers=auth_header
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["total"] >= 1
    assert any(s["roll_number"] == "TEST_RTE001" for s in res_data["data"]["items"])

def test_get_student_route(auth_header):
    # First find the student ID
    response = client.get(
        f"{settings.API_PREFIX}/students/",
        params={"search": "TEST_RTE001"},
        headers=auth_header
    )
    student_id = response.json()["data"]["items"][0]["id"]
    
    # Get by ID
    response = client.get(
        f"{settings.API_PREFIX}/students/{student_id}",
        headers=auth_header
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["roll_number"] == "TEST_RTE001"

def test_update_student_route(auth_header):
    # First find the student ID
    response = client.get(
        f"{settings.API_PREFIX}/students/",
        params={"search": "TEST_RTE001"},
        headers=auth_header
    )
    student_id = response.json()["data"]["items"][0]["id"]
    
    # Update first name
    response = client.put(
        f"{settings.API_PREFIX}/students/{student_id}",
        json={"first_name": "Janey"},
        headers=auth_header
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["first_name"] == "Janey"

def test_delete_student_route(auth_header):
    # First find the student ID
    response = client.get(
        f"{settings.API_PREFIX}/students/",
        params={"search": "TEST_RTE001"},
        headers=auth_header
    )
    student_id = response.json()["data"]["items"][0]["id"]
    
    # Delete student
    response = client.delete(
        f"{settings.API_PREFIX}/students/{student_id}",
        headers=auth_header
    )
    assert response.status_code == 200 # Since our endpoint returns standard success with status 200
    assert response.json()["success"] is True
    
    # Verify it is deleted
    response = client.get(
        f"{settings.API_PREFIX}/students/{student_id}",
        headers=auth_header
    )
    assert response.status_code == 404


def test_list_students_search_too_long(auth_header):
    long_search = "x" * (settings.API_MAX_SEARCH_LENGTH + 1)
    response = client.get(
        f"{settings.API_PREFIX}/students/",
        params={"search": long_search},
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
