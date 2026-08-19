"""
Tenant API Endpoints - Multi-tenant branding and configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_session
from app.models.tenant import Tenant, get_tenant_by_slug

router = APIRouter(prefix="", tags=["Tenants"])


class TenantBranding(BaseModel):
    """Tenant branding configuration."""
    primary_color: str = "#e94560"
    secondary_color: str = "#0F4C44"
    logo_url: str | None = None
    favicon_url: str | None = None
    company_name: str = "Ceyloria Holidays"
    welcome_message: str = "Hello! 🇱🇰 Welcome to Ceyloria Holidays! How can I help you plan your Sri Lanka trip?"
    subtitle: str = "AI Travel Concierge"
    placeholder: str = "Type your message... or use the mic"
    font_family: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    border_radius: str = "16px"
    chat_position: str = "bottom-right"  # bottom-right, bottom-left


@router.get("/{tenant_slug}/branding", tags=["Tenants"])
async def get_tenant_branding(
    tenant_slug: str,
    db: AsyncSession = Depends(get_session)
):
    """Get tenant branding configuration for widget customization."""
    tenant = await get_tenant_by_slug(db, tenant_slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_slug}' not found or inactive"
        )

    branding = tenant.branding or {}

    return {
        "primary_color": branding.get("primary_color", "#e94560"),
        "secondary_color": branding.get("secondary_color", "#0F4C44"),
        "logo_url": branding.get("logo_url"),
        "favicon_url": branding.get("favicon_url"),
        "company_name": tenant.name,
        "welcome_message": branding.get("welcome_message", f"Hello! 🇱🇰 Welcome to {tenant.name}! How can I help you plan your Sri Lanka trip?"),
        "subtitle": branding.get("subtitle", "AI Travel Concierge"),
        "placeholder": branding.get("placeholder", "Type your message... or use the mic"),
        "font_family": branding.get("font_family", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
        "border_radius": branding.get("border_radius", "16px"),
        "chat_position": branding.get("chat_position", "bottom-right"),
    }


@router.get("/{tenant_slug}/config", tags=["Tenants"])
async def get_tenant_config(
    tenant_slug: str,
    db: AsyncSession = Depends(get_session)
):
    """Get full tenant configuration for widget initialization."""
    from app.core.config import settings
    tenant = await get_tenant_by_slug(db, tenant_slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_slug}' not found or inactive"
        )

    branding = tenant.branding or {}
    settings = tenant.settings or {}

    return {
        "tenant_slug": tenant.slug,
        "tenant_name": tenant.name,
        "api_base": "/api/v1",
        "widget_endpoint": f"/widget/{tenant.slug}",
        "supported_languages": ["en", "ru", "de", "fr", "zh", "si", "ta"],
        "default_language": settings.get("default_language", "en"),
        "branding": {
            "primary_color": branding.get("primary_color", "#e94560"),
            "secondary_color": branding.get("secondary_color", "#0F4C44"),
            "logo_url": branding.get("logo_url"),
            "favicon_url": branding.get("favicon_url"),
            "company_name": tenant.name,
            "welcome_message": branding.get("welcome_message", f"Hello! 🇱🇰 Welcome to {tenant.name}! How can I help you plan your Sri Lanka trip?"),
            "subtitle": branding.get("subtitle", "AI Travel Concierge"),
            "placeholder": branding.get("placeholder", "Type your message... or use the mic"),
            "font_family": branding.get("font_family", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            "border_radius": branding.get("border_radius", "16px"),
            "chat_position": branding.get("chat_position", "bottom-right"),
        },
        "features": {
            "voice_enabled": settings.get("voice_enabled", True),
            "multilingual": settings.get("multilingual", True),
            "wellness_upsell": settings.get("wellness_upsell", True),
            "lead_capture": settings.get("lead_capture", True),
            "mcp_enabled": settings.get("mcp_enabled", True),
        }
    }


@router.put("/{tenant_slug}/branding", tags=["Tenants"])
async def update_tenant_branding(
    tenant_slug: str,
    branding: dict,
    db: AsyncSession = Depends(get_session)
):
    """Update tenant branding configuration (admin only)."""
    tenant = await get_tenant_by_slug(db, tenant_slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_slug}' not found"
        )

    tenant.branding = {
        "primary_color": branding.get("primary_color", "#e94560"),
        "secondary_color": branding.get("secondary_color", "#0F4C44"),
        "logo_url": branding.get("logo_url"),
        "favicon_url": branding.get("favicon_url"),
        "welcome_message": branding.get("welcome_message"),
        "subtitle": branding.get("subtitle"),
        "placeholder": branding.get("placeholder"),
        "font_family": branding.get("font_family"),
        "border_radius": branding.get("border_radius"),
        "chat_position": branding.get("chat_position"),
    }

    await db.commit()
    await db.refresh(tenant)

    return {"message": "Branding updated successfully", "branding": tenant.branding}


class TenantSettingsUpdate(BaseModel):
    """Tenant settings update."""
    voice_enabled: bool = True
    multilingual: bool = True
    wellness_upsell: bool = True
    lead_capture: bool = True
    mcp_enabled: bool = True
    default_language: str = "en"


@router.put("/{tenant_slug}/settings", tags=["Tenants"])
async def update_tenant_settings(
    tenant_slug: str,
    settings_update: dict,
    db: AsyncSession = Depends(get_session)
):
    """Update tenant settings (admin only)."""
    tenant = await get_tenant_by_slug(db, tenant_slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_slug}' not found"
        )

    tenant.settings = settings_update
    await db.commit()
    await db.refresh(tenant)

    return {"message": "Settings updated successfully", "settings": tenant.settings}