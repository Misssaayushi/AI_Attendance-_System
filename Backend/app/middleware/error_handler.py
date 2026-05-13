from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

# --- Custom Exception Classes ---

class AppException(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message: str, status_code: int = 500, error_type: str = "AppException"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_type="NotFoundException")

class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400, error_type="BadRequestException")

class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500, error_type="DatabaseException")

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401, error_type="UnauthorizedException")

# --- Global Exception Handlers ---

def register_error_handlers(app: FastAPI):
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "error_type": exc.error_type,
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status_code": 422,
                "message": "Validation error",
                "errors": exc.errors(),
                "error_type": "ValidationError",
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.detail,
                "error_type": "HTTPException",
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # In production, we don't want to expose internal error details
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "An unexpected server error occurred",
                "error_type": "InternalServerError",
                "timestamp": datetime.now().isoformat()
            }
        )
