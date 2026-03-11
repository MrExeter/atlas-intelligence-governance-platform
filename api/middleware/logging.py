import uuid
import time
import logging
from fastapi import Request

logger = logging.getLogger("atlas")

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start) * 1000

    logger.info(
        {
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
    )

    return response
