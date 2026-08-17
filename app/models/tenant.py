"""Tenant and User models with Row Level Security."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


class Tenant(Base):
    """Tenant model with Row Level Security support."""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(200), nullable=True, unique=True)
    branding = Column(JSONB, nullable=True, default={})
    settings = Column(JSONB, nullable=True, default={})
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    tours = relationship("Tour", back_populates="tenant", cascade="all, delete-orphan")
    hotels = relationship("Hotel", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(slug='{self.slug}', name='{self.name}')>"


class User(Base):
    """User model with tenant association and Clerk integration."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(100), unique=True, nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    role = Column(String(50), default="agent", nullable=False)  # admin, agent, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    # Composite index for tenant + email lookups
    __table_args__ = (
        Index("ix_users_tenant_email", "tenant_id", "email"),
    )

    def __repr__(self):
        return f"<User(email='{self.email}', tenant_id='{self.tenant_id}', role='{self.role}')>"


# ─────────────────────────────────────────────────────────────
# Tenant-scoped models (Tours, Hotels, Leads, Conversations)
# ─────────────────────────────────────────────────────────────

class Tour(Base):
    """Tour model scoped to tenant."""
    __tablename__ = "tours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=False)
    min_pax = Column(Integer, default=2)
    max_pax = Column(Integer, default=20)
    base_price_usd = Column(Integer, nullable=False)  # per person
    currency = Column(String(3), default="USD")
    includes = Column(JSONB, nullable=True, default=[])
    excludes = Column(JSONB, nullable=True, default=[])
    images = Column(JSONB, nullable=True, default=[])
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="tours")

    __table_args__ = (
        Index("ix_tours_tenant_slug", "tenant_id", "slug", unique=True),
    )


class Hotel(Base):
    """Hotel model scoped to tenant."""
    __tablename__ = "hotels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    country = Column(String(100), default="Sri Lanka")
    address = Column(Text, nullable=True)
    star_rating = Column(Integer, nullable=True)
    price_per_night_usd = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    amenities = Column(JSONB, nullable=True, default=[])
    images = Column(JSONB, nullable=True, default=[])
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="hotels")

    __table_args__ = (
        Index("ix_hotels_tenant_slug", "tenant_id", "slug", unique=True),
    )


class Lead(Base):
    """Lead model scoped to tenant."""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    status = Column(String(50), default="new")  # new, contacted, qualified, booked, lost
    source = Column(String(50), default="widget")  # widget, whatsapp, email, referral
    tour_interest = Column(String(200), nullable=True)
    pax = Column(Integer, nullable=True)
    travel_dates = Column(JSONB, nullable=True)
    budget_usd = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_contact_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="leads")


class Conversation(Base):
    """Conversation model scoped to tenant."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    channel = Column(String(50), default="widget")  # widget, whatsapp, email
    language = Column(String(10), default="en")
    status = Column(String(50), default="active")  # active, closed, escalated
    messages = Column(JSONB, nullable=True, default=[])
    conversation_metadata = Column(JSONB, nullable=True, default={})  # renamed from metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="conversations")


# ─────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────

async def get_tenant_by_slug(db: AsyncSession, slug: str) -> Optional[Tenant]:
    """Get tenant by slug."""
    result = await db.execute(select(Tenant).where(Tenant.slug == slug, Tenant.is_active == True))
    return result.scalar_one_or_none()


async def get_tenant_by_domain(db: AsyncSession, domain: str) -> Optional[Tenant]:
    """Get tenant by custom domain."""
    result = await db.execute(select(Tenant).where(Tenant.domain == domain, Tenant.is_active == True))
    return result.scalar_one_or_none()


async def get_user_by_clerk_id(db: AsyncSession, clerk_id: str) -> Optional[User]:
    """Get user by Clerk ID."""
    result = await db.execute(select(User).where(User.clerk_id == clerk_id, User.is_active == True))
    return result.scalar_one_or_none()


async def create_tenant(
    db: AsyncSession,
    slug: str,
    name: str,
    domain: Optional[str] = None,
    branding: Optional[dict] = None,
    settings: Optional[dict] = None,
) -> Tenant:
    """Create a new tenant."""
    tenant = Tenant(
        slug=slug,
        name=name,
        domain=domain,
        branding=branding or {},
        settings=settings or {},
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


async def create_user(
    db: AsyncSession,
    clerk_id: str,
    tenant_id: uuid.UUID,
    email: str,
    full_name: Optional[str] = None,
    role: str = "agent",
) -> User:
    """Create a new user."""
    user = User(
        clerk_id=clerk_id,
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user