from app.services.auth_service import authenticate_admin
from app.services import student_service
from app.services import attendance_service

# Export services for easy import
__all__ = ["authenticate_admin", "student_service", "attendance_service"]
