from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from app.utils.monitoring import record_error
from app.utils.logger import logger

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
    def _base_error_content(
        *,
        request_id: str,
        status_code: int,
        message: str,
        error_type: str,
        details: dict | None = None,
    ) -> dict:
        payload = {
            "success": False,
            "status_code": status_code,
            "message": message,
            "error_type": error_type,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }
        if details:
            payload["details"] = details
        return payload
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", "unknown")
        record_error(
            error_type=exc.error_type,
            path=request.url.path,
            status_code=exc.status_code,
            request_id=request_id,
        )
        logger.warning(
            f"event=app_exception request_id={request_id} path={request.url.path} "
            f"status={exc.status_code} error_type={exc.error_type} message={exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_base_error_content(
                request_id=request_id,
                status_code=exc.status_code,
                message=exc.message,
                error_type=exc.error_type,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "unknown")
        record_error(
            error_type="ValidationError",
            path=request.url.path,
            status_code=422,
            request_id=request_id,
        )
        logger.warning(
            f"event=validation_error request_id={request_id} path={request.url.path} "
            f"status=422 errors={len(exc.errors())}"
        )
        normalized = []
        for err in exc.errors():
            normalized.append(
                {
                    "field": ".".join(str(x) for x in err.get("loc", [])[1:]) if err.get("loc") else "unknown",
                    "message": err.get("msg"),
                    "type": err.get("type"),
                }
            )
        return JSONResponse(
            status_code=422,
            content=_base_error_content(
                request_id=request_id,
                status_code=422,
                message="Validation error",
                error_type="ValidationError",
                details={"errors": normalized},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", "unknown")
        record_error(
            error_type="HTTPException",
            path=request.url.path,
            status_code=exc.status_code,
            request_id=request_id,
        )
        logger.warning(
            f"event=http_exception request_id={request_id} path={request.url.path} "
            f"status={exc.status_code} message={exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_base_error_content(
                request_id=request_id,
                status_code=exc.status_code,
                message=str(exc.detail),
                error_type="HTTPException",
            ),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        record_error(
            error_type=type(exc).__name__,
            path=request.url.path,
            status_code=500,
            request_id=request_id,
        )
        logger.exception(
            f"event=unhandled_exception request_id={request_id} path={request.url.path} "
            f"status=500 error_type={type(exc).__name__}"
        )
        # In production, we don't want to expose internal error details
        return JSONResponse(
            status_code=500,
            content=_base_error_content(
                request_id=request_id,
                status_code=500,
                message="An unexpected server error occurred",
                error_type="InternalServerError",
            ),
        )
