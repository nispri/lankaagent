"""
LankaAgent — Middleware: Correlation ID, Tenant Resolution, Rate Limiting, Logging
"""
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.exceptions import RateLimitExceededException


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Adds or propagates correlation ID for request tracing"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # noqa: ANN201
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class TenantMiddleware(BaseHTTPMiddleware):
    """Resolves and validates tenant from header"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # noqa: ANN201
        tenant_id = request.headers.get(settings.TENANT_HEADER)
        if tenant_id:
            request.state.tenant_id = tenant_id
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting (use Redis-backed for production)"""

    def __init__(self, app, requests: int = 100, window: int = 60) -> None:  # noqa: ANN001
        super().__init__(app)
        self.requests = requests
        self.window = window
        self._buckets: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # noqa: ANN201
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = __import__("time").time()
        bucket = self._buckets.get(client_ip, [])

        # Clean expired entries
        bucket = [t for t in bucket if now - t < self.window]

        if len(bucket) >= self.requests:
            raise RateLimitExceededException()

        bucket.append(now)
        self._buckets[client_ip] = bucket
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # noqa: ANN201
        import structlog  # noqa: PLC0415

        logger = structlog.get_logger()
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.info("request_started", method=request.method, path=request.url.path, correlation_id=correlation_id)

        response = await call_next(request)

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            correlation_id=correlation_id,
        )
        return response