"""Health check endpoints"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter

router = APIRouter()

# Track app state
app_started_at: str | None = None


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    """Health module lifespan"""
    global app_started_at  # noqa: PLW0603
    from datetime import datetime, timezone  # noqa: PLC0415
    app_started_at = datetime.now(timezone.utc).isoformat()
    yield


@router.get("")
async def get_health() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "started_at": app_started_at or "unknown",
    }