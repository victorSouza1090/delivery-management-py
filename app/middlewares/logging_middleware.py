import logging
import time
from fastapi import Request

logger = logging.getLogger("api")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info({
            "event": "request_start",
            "method": request.method,
            "path": request.url.path
        })
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info({
            "event": "request_end",
            "status_code": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "duration": duration
        })
    return response