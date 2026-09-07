import json
import logging
import time
import uuid

from fastapi import Request, Response

logger = logging.getLogger("support_agent")
logging.basicConfig(level=logging.INFO, format="%(message)s")


async def request_observability(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
                ensure_ascii=False,
            )
        )
        if "response" in locals():
            response.headers["x-request-id"] = request_id
