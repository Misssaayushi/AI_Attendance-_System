from typing import Any, Optional
from fastapi.responses import JSONResponse
from datetime import datetime

def success_response(
    data: Any = None, 
    message: str = "Request successful", 
    status_code: int = 200
) -> JSONResponse:
    """Standard success JSON response formatter."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    )

def error_response(
    message: str = "An error occurred", 
    status_code: int = 400, 
    error_type: str = "BadRequest"
) -> JSONResponse:
    """Standard error JSON response formatter."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status_code": status_code,
            "message": message,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        }
    )

def success(data: Any, message: str = "OK") -> JSONResponse:
    """Returns a success response standardizing format to {status, message, data}."""
    return success_response(data=data, message=message, status_code=200)

def error(detail: str, status_code: int = 400) -> JSONResponse:
    """Returns an error response standardizing format to {status, detail}."""
    return error_response(message=detail, status_code=status_code)

