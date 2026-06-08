import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database.connection import SessionLocal
from app.repositories import class_timing_repository

db = SessionLocal()
rule = class_timing_repository.get_by_dept_and_sem(db, None, None)
print(f"Global rule: {rule}")
