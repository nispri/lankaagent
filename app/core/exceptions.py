"""
LankaAgent — Custom Exceptions
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class LankaAgentException(Exception):
    """Base exception for LankaAgent"""
    status_code: int = 500
    detail: str = "Internal server error"
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code


class NotFoundException(LankaAgentException):
    status_code = 404
    error_code = "NOT_FOUND"
    detail = "Resource not found"


class UnauthorizedException(LankaAgentException):
    status_code = 401
    error_code = "UNAUTHORIZED"
    detail = "Not authenticated"


class ForbiddenException(LankaAgentException):
    status_code = 403
    error_code = "FORBIDDEN"
    detail = "Not authorized"


class BadRequestException(LankaAgentException):
    status_code = 400
    error_code = "BAD_REQUEST"
    detail = "Bad request"


class TenantRequiredException(LankaAgentException):
    status_code = 400
    error_code = "TENANT_REQUIRED"
    detail = "X-Tenant-ID header is required"


class RateLimitExceededException(LankaAgentException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    detail = "Rate limit exceeded. Try again later."


class PaymentRequiredException(LankaAgentException):
    status_code = 402
    error_code = "PAYMENT_REQUIRED"
    detail = "Subscription payment required"


async def lankaagent_exception_handler(request: Request, exc: LankaAgentException) -> JSONResponse:
    """Global exception handler for LankaAgent exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )