import pytest
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine
from app.models import Student, Attendance, Admin
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Creates all tables once per test session."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """Provides a clean database session for each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_student_creation(db_session: Session):
    """Verifies that a student record can be created with all fields."""
    # 1. Clear existing test data if any
    db_session.query(Student).filter(Student.roll_number == "TEST101").delete()
    db_session.commit()

    # 2. Create new student
    new_student = Student(
        full_name="Test Student",
        roll_number="TEST101",
        email_address="test@example.com",
        department="Computer Science",
        course="B.Tech",
        year_batch="2024",
        semester=6,
        gender="Male",
        face_encoding="[0.1, -0.2, 0.5...]" # Dummy encoding
    )
    db_session.add(new_student)
    db_session.commit()

    # 3. Verify
    db_student = db_session.query(Student).filter(Student.roll_number == "TEST101").first()
    assert db_student is not None
    assert db_student.full_name == "Test Student"
    assert db_student.department == "Computer Science"

def test_attendance_relationship(db_session: Session):
    """Verifies that attendance records can be linked to a student."""
    # 1. Get the test student
    student = db_session.query(Student).filter(Student.roll_number == "TEST101").first()
    assert student is not None

    # 2. Create attendance record
    new_attendance = Attendance(
        student_id=student.id,
        status="Present"
    )
    db_session.add(new_attendance)
    db_session.commit()

    # 3. Verify relationship (Back-reference)
    # This proves Step 2 (Relationships) is working!
    db_student = db_session.query(Student).filter(Student.roll_number == "TEST101").first()
    assert len(db_student.attendance_records) > 0
    assert db_student.attendance_records[0].status == "Present"

def test_duplicate_roll_number_fails(db_session: Session):
    """Verifies that the unique constraint on roll_number is working."""
    duplicate_student = Student(
        full_name="Duplicate Student",
        roll_number="TEST101", # Already exists from previous test
        email_address="other@example.com",
        department="IT",
        course="B.Tech",
        year_batch="2024",
        semester=4,
        gender="Female"
    )
    
    with pytest.raises(Exception): # Should raise IntegrityError
        db_session.add(duplicate_student)
        db_session.commit()
    db_session.rollback()

def test_admin_creation(db_session: Session):
    """Verifies that admin records can be created."""
    # Clear test admin
    db_session.query(Admin).filter(Admin.username == "testadmin").delete()
    db_session.commit()

    admin = Admin(username="testadmin", password="hashed_password")
    db_session.add(admin)
    db_session.commit()

    db_admin = db_session.query(Admin).filter(Admin.username == "testadmin").first()
    assert db_admin is not None
    assert db_admin.username == "testadmin"
