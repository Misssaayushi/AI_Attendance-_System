import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()
from app.database.connection import SessionLocal
from app.models.student import Student

db = SessionLocal()
students = db.query(Student).all()
for s in students:
    print(s.id, s.first_name, s.last_name, s.roll_number)
db.close()
