"""
LankaAgent API — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import LankaAgentException, lankaagent_exception_handler
from app.core.middleware import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    TenantMiddleware,
)
from app.core.redis import redis_client
from app.integrations.chat_widget.router import router as chat_widget_router
from app.integrations.whatsapp import router as whatsapp_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan events"""
    # Startup
    logger.info("Starting LankaAgent API", version=settings.APP_VERSION)

    # Initialize database (create tables if not exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.exception("Redis connection failed", error=str(e))

    logger.info("LankaAgent API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down LankaAgent API")
    await redis_client.close()
    await engine.dispose()
    logger.info("LankaAgent API shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="LankaAgent — AI Travel Concierge for Sri Lanka Tour Operators",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # Middleware (order matters - last added = first executed)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Exception handlers
    app.add_exception_handler(LankaAgentException, lankaagent_exception_handler)

    # Health endpoints (no auth, no tenant)
    @app.get("/health", tags=["Health"])
    async def health_liveness() -> dict:
        """Liveness probe - always returns 200 if app is running"""
        return {"status": "alive", "version": settings.APP_VERSION}

    @app.get("/health/ready", tags=["Health"])
    async def health_readiness(request: Request) -> JSONResponse:  # noqa: ARG001
        """Readiness probe - checks dependencies"""
        checks = {
            "database": False,
            "redis": False,
        }

        # Check database
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception:
            pass

        # Check Redis
        try:
            await redis_client.ping()
            checks["redis"] = True
        except Exception:
            pass

        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if all_ready else "not_ready",
                "checks": checks,
                "version": settings.APP_VERSION,
            }
        )

    # API Router
    app.include_router(api_router, prefix="/api/v1")

    # Webhook endpoints (no auth)
    app.include_router(whatsapp_router, prefix="/webhook", tags=["Webhooks"])

    # Chat widget embed
    app.include_router(chat_widget_router, prefix="/widget", tags=["Chat Widget"])

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "AI Travel Concierge for Sri Lanka Tour Operators",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,
    )
