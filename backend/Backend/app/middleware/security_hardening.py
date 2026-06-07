from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import settings


async def security_hardening_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > settings.REQUEST_MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "success": False,
                        "status_code": 413,
                        "message": "Request body too large",
                        "error_type": "PayloadTooLarge",
                    },
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "status_code": 400,
                    "message": "Invalid Content-Length header",
                    "error_type": "BadRequestException",
                },
            )

    response = await call_next(request)
    if settings.SECURITY_HEADERS_ENABLED:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

