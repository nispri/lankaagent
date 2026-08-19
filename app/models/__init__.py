"""LankaAgent Models Package.

This module provides ONLY helper functions to avoid double-registration of SQLAlchemy models.
Model classes MUST be imported directly from app.models.tenant
"""

from app.models.tenant import (
    get_tenant_by_slug,
    get_tenant_by_domain,
    get_user_by_clerk_id,
    create_tenant,
    create_user,
)

__all__ = [
    "get_tenant_by_slug",
    "get_tenant_by_domain",
    "get_user_by_clerk_id",
    "create_tenant",
    "create_user",
]