import sys, os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database.connection import SessionLocal
from app.models.attendance import Attendance
from app.models.student import Student
from app.services.attendance_service import _compute_status_from_time
from app.services.class_timing_service import resolve_timing

db = SessionLocal()
attendances = db.query(Attendance).all()
for att in attendances:
    student = db.query(Student).filter(Student.id == att.student_id).first()
    if student:
        _, _, present_cutoff, late_cutoff = resolve_timing(db, student.department, student.semester)
        new_status = _compute_status_from_time(att.time, present_cutoff=present_cutoff, late_cutoff=late_cutoff)
        if new_status != att.status:
            print(f"Updating {student.first_name} {student.last_name} from {att.status} to {new_status}")
            att.status = new_status
            
db.commit()
print("Done reevaluating.")
