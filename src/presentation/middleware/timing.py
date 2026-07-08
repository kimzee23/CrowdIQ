"""
CrowdIQ — Request Timing Middleware
"""
import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("crowdiq.middleware.timing")


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the request timing (can be disabled in production or sampled)
        logger.debug(f"{request.method} {request.url.path} - {process_time:.4f}s")
        return response
