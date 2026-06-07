import time
from fastapi import Request
from app.utils.logger import logger

async def log_requests_middleware(request: Request, call_next):
    """
    Middleware to log every incoming request and its processing time.
    Format: [METHOD] [PATH] | [STATUS] | [TIME]ms
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration in milliseconds
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {formatted_process_time}ms"
    )
    
    return response
