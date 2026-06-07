from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.student import router as student_router
from app.routes.attendance import router as attendance_router
from app.routes.attendance import ai_router as ai_attendance_router
from app.routes.dashboard import router as dashboard_router
from app.routes.diagnostics import router as diagnostics_router
from app.routes.websocket import router as ws_router
from app.routes.class_timing import router as class_timing_router

# Initialize the master API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, prefix="/health", tags=["System Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(student_router, prefix="/students", tags=["Student Management"])
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance Management"])
api_router.include_router(ai_attendance_router, prefix="/attendance", tags=["Attendance Management (Internal)"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard Analytics"])
api_router.include_router(diagnostics_router, prefix="/diagnostics", tags=["Diagnostics"])
api_router.include_router(ws_router, tags=["WebSocket"])
api_router.include_router(class_timing_router, prefix="/class-timings", tags=["Class Timings"])
