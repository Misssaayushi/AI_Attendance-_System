import time
import uuid
from fastapi import Request
from app.utils.logger import logger

async def log_requests_middleware(request: Request, call_next):
    """
    Middleware to log every incoming request and its processing time.
    Format: [METHOD] [PATH] | [STATUS] | [TIME]ms
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration in milliseconds
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    
    # Log request details
    logger.info(
        f"event=request_completed request_id={request_id} method={request.method} "
        f"path={request.url.path} status={response.status_code} duration_ms={formatted_process_time}"
    )
    response.headers["X-Request-ID"] = request_id
    
    return response
