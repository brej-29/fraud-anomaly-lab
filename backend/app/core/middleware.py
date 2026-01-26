from __future__ import annotations

import time
import uuid
from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .metrics import METRICS


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches a per-request ID for logging and tracing.

    - If the incoming request has an `X-Request-ID` header, it is propagated.
    - Otherwise, a new UUID4 is generated.
    - The request id is stored on `request.state.request_id` and added to the response
      headers as `X-Request-ID`.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records basic HTTP request metrics.

    It measures per-request latency and updates the global METRICS singleton.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - start
            METRICS.record_request(
                path=request.url.path,
                method=request.method,
                status_code=500,
                latency_s=duration,
            )
            raise

        duration = time.perf_counter() - start
        METRICS.record_request(
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency_s=duration,
        )
        return response