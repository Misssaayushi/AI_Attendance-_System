from app.schemas.auth import LoginRequest, TokenResponse, LogoutResponse, TokenData
from app.schemas.attendance import (
    AttendanceFilterParams,
    AttendanceListResponse,
    AttendanceMarkRequest,
    AttendanceMarkResponse,
    AttendanceRecordResponse,
    AttendanceStatus,
    AttendanceSummaryResponse,
)

# Export schemas for easy import
__all__ = [
    "LoginRequest",
    "TokenResponse",
    "LogoutResponse",
    "TokenData",
    "AttendanceStatus",
    "AttendanceMarkRequest",
    "AttendanceMarkResponse",
    "AttendanceRecordResponse",
    "AttendanceFilterParams",
    "AttendanceListResponse",
    "AttendanceSummaryResponse",
]
