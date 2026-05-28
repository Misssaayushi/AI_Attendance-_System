from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.student import router as student_router
from app.routes.attendance import router as attendance_router

# Initialize the master API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, prefix="/health", tags=["System Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(student_router, prefix="/students", tags=["Student Management"])
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance Management"])
