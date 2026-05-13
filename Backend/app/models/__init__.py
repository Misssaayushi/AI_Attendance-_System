from app.models.student import Base, Student
from app.models.attendance import Attendance
from app.models.admin import Admin

# This makes it easy to import all models from app.models
__all__ = ["Base", "Student", "Attendance", "Admin"]