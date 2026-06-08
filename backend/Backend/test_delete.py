import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database.connection import SessionLocal
from app.models.student import Student
from app.services.student_service import delete_student

db = SessionLocal()
try:
    student = db.query(Student).filter(Student.roll_number == "2").first()
    if student:
        print(f"Deleting student ID: {student.id}")
        delete_student(db, student.id)
        print("Deleted successfully")
    else:
        print("Student not found by roll number 2")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
