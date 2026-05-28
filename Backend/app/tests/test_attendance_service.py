from datetime import datetime, timezone

import pytest

from app.database.connection import SessionLocal
from app.exceptions import DuplicateAttendanceException, StudentNotFoundException
from app.models.attendance import Attendance
from app.models.student import Student
from app.schemas.attendance import AttendanceMarkRequest
from app.services import attendance_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    session.query(Attendance).filter(Attendance.student_id.in_(
        session.query(Student.id).filter(Student.roll_number.like("TEST_ATT_SRV%"))
    )).delete(synchronize_session=False)
    session.query(Student).filter(Student.roll_number.like("TEST_ATT_SRV%")).delete()
    session.commit()
    try:
        yield session
    finally:
        session.query(Attendance).filter(Attendance.student_id.in_(
            session.query(Student.id).filter(Student.roll_number.like("TEST_ATT_SRV%"))
        )).delete(synchronize_session=False)
        session.query(Student).filter(Student.roll_number.like("TEST_ATT_SRV%")).delete()
        session.commit()
        session.close()


def _create_student(session, idx: int) -> Student:
    student = Student(
        first_name="Test",
        last_name=f"Service{idx}",
        roll_number=f"TEST_ATT_SRV{idx}",
        email_address=f"test_att_srv{idx}@example.com",
        department="Computer Science",
        course="B.Tech",
        year_batch="2026",
        semester=6,
        gender="Female",
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def test_mark_attendance_success(db_session):
    student = _create_student(db_session, 1)
    payload = AttendanceMarkRequest(
        student_id=student.id,
        attendance_date=datetime.now(timezone.utc).date(),
        status="Present",
        confidence_score=0.92,
    )
    record = attendance_service.mark_attendance(db_session, payload)
    assert record.id is not None
    assert record.student_id == student.id
    assert record.status == "Present"


def test_mark_attendance_duplicate_rejected(db_session):
    student = _create_student(db_session, 2)
    payload = AttendanceMarkRequest(
        student_id=student.id,
        attendance_date=datetime.now(timezone.utc).date(),
        status="Present",
        confidence_score=0.95,
    )
    attendance_service.mark_attendance(db_session, payload)
    with pytest.raises(DuplicateAttendanceException):
        attendance_service.mark_attendance(db_session, payload)


def test_mark_attendance_student_not_found(db_session):
    payload = AttendanceMarkRequest(
        student_id=999999,
        attendance_date=datetime.now(timezone.utc).date(),
        status="Present",
        confidence_score=0.99,
    )
    with pytest.raises(StudentNotFoundException):
        attendance_service.mark_attendance(db_session, payload)

