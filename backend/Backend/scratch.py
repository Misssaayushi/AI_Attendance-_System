import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database.connection import SessionLocal
from app.models.student import Student
from app.models.class_timing import ClassTiming
from app.models.attendance import Attendance

db = SessionLocal()
students = db.query(Student).all()
for s in students:
    print(f"Student: id={s.id}, dept={s.department}, sem={s.semester}")

rules = db.query(ClassTiming).all()
for r in rules:
    print(f"Rule: id={r.id}, dept={r.department}, sem={r.semester}, start={r.class_start_time}, present={r.present_cutoff}, late={r.late_cutoff}")

att = db.query(Attendance).all()
for a in att:
    print(f"Attendance: student={a.student_id}, status={a.status}, time={a.time}")
