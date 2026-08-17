"""Tenant Context Middleware for Row Level Security."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.tenant import Tenant
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

# Paths that don't require tenant context
PUBLIC_PATHS = {
    "/health",
    "/health/ready",
    "/metrics",
    "/widget/embed",
    "/widget/chat",
    "/widget/config",
    "/widget/tts",
    "/widget/stt",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}

# Path prefixes that are public
PUBLIC_PREFIXES = (
    "/static/",
    "/assets/",
)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract tenant context and set PostgreSQL RLS session variable."""

    def __init__(self, app, excluded_paths: set = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or PUBLIC_PATHS

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip middleware for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Extract tenant identifier
        tenant_identifier = self._extract_tenant_identifier(request)
        
        if not tenant_identifier:
            # No tenant context - let auth middleware handle or continue without tenant
            return await call_next(request)

        # Resolve tenant and set RLS context
        async with async_session_maker() as db:
            try:
                tenant = await self._resolve_tenant(db, tenant_identifier)
                
                if tenant:
                    # Set tenant context in request state
                    request.state.tenant = tenant
                    request.state.tenant_id = str(tenant.id)
                    
                    # Set PostgreSQL session variable for RLS
                    await db.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant.id}'"))
                    await db.commit()
                    
                    logger.debug(f"Set tenant context: {tenant.slug} ({tenant.id})")
                else:
                    logger.warning(f"Tenant not found: {tenant_identifier}")
                    
            except Exception as e:
                logger.error(f"Error setting tenant context: {e}")
                # Don't block request on tenant context errors

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """Check if path should skip tenant context."""
        if path in self.excluded_paths:
            return True
        for prefix in PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    def _extract_tenant_identifier(self, request: Request) -> Optional[str]:
        """Extract tenant identifier from request."""
        # 1. Check X-Tenant-ID header (for API clients)
        if tenant_id := request.headers.get("X-Tenant-ID"):
            return tenant_id
        
        if tenant_slug := request.headers.get("X-Tenant-Slug"):
            return tenant_slug

        # 2. Check subdomain (tenant.api.ceyloria.com or tenant.lankaagent.com)
        host = request.headers.get("host", "").lower()
        
        # Handle custom domains (api.ceyloria.com, tenant.ceyloria.com)
        if "ceyloria.com" in host:
            parts = host.split(".")
            if len(parts) >= 3:
                # tenant.ceyloria.com or tenant.api.ceyloria.com
                return parts[0]
        
        # Handle lankaagent subdomains
        if "lankaagent" in host:
            parts = host.split(".")
            if len(parts) >= 3:
                return parts[0]

        # 3. Check query parameter (for testing)
        if tenant_slug := request.query_params.get("tenant_slug"):
            return tenant_slug

        return None

    async def _resolve_tenant(self, db: AsyncSession, identifier: str) -> Optional[Tenant]:
        """Resolve tenant by ID, slug, or domain."""
        import uuid
        
        # Try UUID first
        try:
            uuid_obj = uuid.UUID(identifier)
            result = await db.execute(
                select(Tenant).where(Tenant.id == uuid_obj, Tenant.is_active == True)
            )
            return result.scalar_one_or_none()
        except ValueError:
            pass
        
        # Try slug
        result = await db.execute(
            select(Tenant).where(Tenant.slug == identifier, Tenant.is_active == True)
        )
        tenant = result.scalar_one_or_none()
        if tenant:
            return tenant
        
        # Try domain
        result = await db.execute(
            select(Tenant).where(Tenant.domain == identifier, Tenant.is_active == True)
        )
        return result.scalar_one_or_none()


# ─────────────────────────────────────────────────────────────
# Dependency for getting current tenant in route handlers
# ─────────────────────────────────────────────────────────────

from fastapi import Request, HTTPException, Depends
from typing import Optional

async def get_current_tenant(request: Request) -> Tenant:
    """FastAPI dependency to get current tenant from request state."""
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant context not found. Provide X-Tenant-ID header or use tenant subdomain."
        )
    return tenant


async def get_tenant_id(request: Request) -> str:
    """FastAPI dependency to get current tenant ID."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant context not found."
        )
    return tenant_id


# Optional: For routes that work with or without tenant
async def get_optional_tenant(request: Request) -> Optional[Tenant]:
    """Get tenant if available, otherwise None."""
    return getattr(request.state, "tenant", None)