import pytest
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.services import student_service
from app.exceptions import (
    StudentNotFoundException,
    DuplicateRollNumberException,
    DuplicateEmailException,
)

@pytest.fixture
def db_session():
    """Provides a clean database session for each test and handles cleanup."""
    session = SessionLocal()
    # Clean up test student data before running test
    session.query(Student).filter(Student.roll_number.like("TEST_SRV%")).delete()
    session.commit()
    try:
        yield session
    finally:
        session.query(Student).filter(Student.roll_number.like("TEST_SRV%")).delete()
        session.commit()
        session.close()

def test_create_student_success(db_session: Session):
    payload = StudentCreate(
        first_name="John",
        last_name="Doe",
        email="test_srv_john@example.com",
        roll_number="TEST_SRV001",
        department="Computer Science",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Male"
    )
    student = student_service.create_student(db_session, payload)
    assert student.id is not None
    assert student.first_name == "John"
    assert student.email_address == "test_srv_john@example.com"
    assert student.roll_number == "TEST_SRV001"

def test_create_student_duplicate_email(db_session: Session):
    payload = StudentCreate(
        first_name="John",
        last_name="Doe",
        email="test_srv_duplicate@example.com",
        roll_number="TEST_SRV002",
        department="Computer Science",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Male"
    )
    student_service.create_student(db_session, payload)
    
    payload2 = StudentCreate(
        first_name="Jane",
        last_name="Doe",
        email="test_srv_duplicate@example.com",
        roll_number="TEST_SRV003",
        department="IT",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Female"
    )
    with pytest.raises(DuplicateEmailException):
        student_service.create_student(db_session, payload2)

def test_create_student_duplicate_roll(db_session: Session):
    payload = StudentCreate(
        first_name="John",
        last_name="Doe",
        email="test_srv_john2@example.com",
        roll_number="TEST_SRV004",
        department="Computer Science",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Male"
    )
    student_service.create_student(db_session, payload)
    
    payload2 = StudentCreate(
        first_name="Jane",
        last_name="Doe",
        email="test_srv_jane2@example.com",
        roll_number="TEST_SRV004",
        department="IT",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Female"
    )
    with pytest.raises(DuplicateRollNumberException):
        student_service.create_student(db_session, payload2)

def test_get_student_success(db_session: Session):
    payload = StudentCreate(
        first_name="Alice",
        last_name="Smith",
        email="test_srv_alice@example.com",
        roll_number="TEST_SRV005",
        department="Computer Science",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Female"
    )
    created = student_service.create_student(db_session, payload)
    
    fetched = student_service.get_student(db_session, created.id)
    assert fetched.id == created.id
    assert fetched.first_name == "Alice"

def test_get_student_not_found(db_session: Session):
    with pytest.raises(StudentNotFoundException):
        student_service.get_student(db_session, 999999)

def test_list_students(db_session: Session):
    payload1 = StudentCreate(
        first_name="Alice",
        last_name="Smith",
        email="test_srv_list1@example.com",
        roll_number="TEST_SRV101",
        department="CS",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Female"
    )
    payload2 = StudentCreate(
        first_name="Bob",
        last_name="Jones",
        email="test_srv_list2@example.com",
        roll_number="TEST_SRV102",
        department="IT",
        course="B.Tech",
        year_batch="2026",
        semester=1,
        gender="Male"
    )
    student_service.create_student(db_session, payload1)
    student_service.create_student(db_session, payload2)
    
    # List filtered by department
    students, total = student_service.list_students(db_session, department="CS")
    assert len(students) >= 1
    assert any(s.roll_number == "TEST_SRV101" for s in students)
    
    # List filtered by year_batch
    students2, total2 = student_service.list_students(db_session, year=2026)
    assert len(students2) >= 1
    assert any(s.roll_number == "TEST_SRV102" for s in students2)

def test_update_student_success(db_session: Session):
    payload = StudentCreate(
        first_name="Bob",
        last_name="Jones",
        email="test_srv_update@example.com",
        roll_number="TEST_SRV006",
        department="IT",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Male"
    )
    created = student_service.create_student(db_session, payload)
    
    update_payload = StudentUpdate(first_name="Bobby", semester=2)
    updated = student_service.update_student(db_session, created.id, update_payload)
    assert updated.first_name == "Bobby"
    assert updated.semester == 2

def test_delete_student_success(db_session: Session):
    payload = StudentCreate(
        first_name="Delete",
        last_name="Me",
        email="test_srv_delete@example.com",
        roll_number="TEST_SRV007",
        department="IT",
        course="B.Tech",
        year_batch="2025",
        semester=1,
        gender="Male"
    )
    created = student_service.create_student(db_session, payload)
    
    student_service.delete_student(db_session, created.id)
    with pytest.raises(StudentNotFoundException):
        student_service.get_student(db_session, created.id)
