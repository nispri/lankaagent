"""Tenant and User models with Row Level Security - Single source of truth for all models."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Index, Float, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


# ─────────────────────────────────────────────────────────────
# Core Models
# ─────────────────────────────────────────────────────────────

class Tenant(Base):
    """Tenant model with Row Level Security support."""
    __tablename__ = "tenants"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(200), nullable=True, unique=True)
    branding = Column(JSONB, nullable=True, default={})
    settings = Column(JSONB, nullable=True, default={})
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships - use fully qualified paths matching the module where defined
    users = relationship("app.models.tenant.User", back_populates="tenant", cascade="all, delete-orphan")
    tours = relationship("app.models.tenant.Tour", back_populates="tenant", cascade="all, delete-orphan")
    hotels = relationship("app.models.tenant.Hotel", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("app.models.tenant.Lead", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("app.models.tenant.Conversation", back_populates="tenant", cascade="all, delete-orphan")
    itineraries = relationship("app.models.tenant.Itinerary", back_populates="tenant", cascade="all, delete-orphan")
    bookings = relationship("app.models.tenant.Booking", back_populates="tenant", cascade="all, delete-orphan")
    payments = relationship("app.models.tenant.Payment", back_populates="tenant", cascade="all, delete-orphan")
    wellness_protocols = relationship("app.models.tenant.WellnessProtocol", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(slug='{self.slug}', name='{self.name}')>"


class User(Base):
    """User model with tenant association and Clerk integration."""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_tenant_email", "tenant_id", "email"),
        {'extend_existing': True}
    )

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

    # Relationships - use fully qualified path
    tenant = relationship("app.models.tenant.Tenant", back_populates="users")

    def __repr__(self):
        return f"<User(email='{self.email}', tenant_id='{self.tenant_id}', role='{self.role}')>"


# ─────────────────────────────────────────────────────────────
# Tenant-scoped models (Tours, Hotels, Leads, Conversations)
# ─────────────────────────────────────────────────────────────

class Tour(Base):
    """Tour model scoped to tenant."""
    __tablename__ = "tours"
    __table_args__ = (
        Index("ix_tours_tenant_slug", "tenant_id", "slug", unique=True),
        {'extend_existing': True}
    )

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

    tenant = relationship("app.models.tenant.Tenant", back_populates="tours")


class Hotel(Base):
    """Hotel model scoped to tenant."""
    __tablename__ = "hotels"
    __table_args__ = (
        Index("ix_hotels_tenant_slug", "tenant_id", "slug", unique=True),
        {'extend_existing': True}
    )

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

    tenant = relationship("app.models.tenant.Tenant", back_populates="hotels")


class Lead(Base):
    """Lead model scoped to tenant."""
    __tablename__ = "leads"
    __table_args__ = {'extend_existing': True}

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

    tenant = relationship("app.models.tenant.Tenant", back_populates="leads")
    assigned_user = relationship("app.models.tenant.User", foreign_keys="app.models.tenant.Lead.assigned_to")
    itineraries = relationship("app.models.tenant.Itinerary", back_populates="lead")
    bookings = relationship("app.models.tenant.Booking", back_populates="lead")
    wellness_protocols = relationship("app.models.tenant.WellnessProtocol", back_populates="lead")


class Conversation(Base):
    """Conversation model scoped to tenant."""
    __tablename__ = "conversations"
    __table_args__ = {'extend_existing': True}

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

    tenant = relationship("app.models.tenant.Tenant", back_populates="conversations")


class Message(Base):
    """Individual message within a conversation"""
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSONB)
    tool_results = Column(JSONB)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Itinerary(Base):
    """Generated travel itinerary/quote"""
    __tablename__ = "itineraries"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    version = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    days = Column(JSONB, nullable=False)
    total_price_usd = Column(Float(precision=2))
    total_price_lkr = Column(Float(precision=2))
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="draft")
    valid_until = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("app.models.tenant.Tenant", back_populates="itineraries")
    lead = relationship("app.models.tenant.Lead", back_populates="itineraries")


class Booking(Base):
    """Confirmed booking"""
    __tablename__ = "bookings"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="SET NULL"))
    booking_reference = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), default="confirmed")
    travelers = Column(JSONB, nullable=False)
    special_requests = Column(Text)
    payment_status = Column(String(50), default="pending")
    payment_intent_id = Column(String(255))
    commission_usd = Column(Float(precision=2))
    commission_lkr = Column(Float(precision=2))
    starts_at = Column(Date, nullable=False)
    ends_at = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("app.models.tenant.Tenant", back_populates="bookings")
    lead = relationship("app.models.tenant.Lead", back_populates="bookings")


class Payment(Base):
    """Payment transaction"""
    __tablename__ = "payments"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"))
    amount_usd = Column(Float(precision=2))
    amount_lkr = Column(Float(precision=2))
    currency = Column(String(3), nullable=False)
    gateway = Column(String(50), nullable=False)
    gateway_payment_id = Column(String(255))
    gateway_response = Column(JSONB)
    status = Column(String(50), default="pending")
    fee_usd = Column(Float(precision=2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("app.models.tenant.Tenant", back_populates="payments")


class WellnessProtocol(Base):
    """Ayurveda/wellness protocol for a lead"""
    __tablename__ = "wellness_protocols"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    health_intake = Column(JSONB, nullable=False)
    recommended_treatments = Column(JSONB, nullable=False)
    assigned_doctor_id = Column(UUID(as_uuid=True))
    status = Column(String(50), default="proposed")
    total_price_usd = Column(Float(precision=2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("app.models.tenant.Tenant", back_populates="wellness_protocols")
    lead = relationship("app.models.tenant.Lead", back_populates="wellness_protocols")


class AnalyticsEvent(Base):
    """Product analytics event"""
    __tablename__ = "analytics_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    event_name = Column(String(255), nullable=False)
    properties = Column(JSONB, default={})
    user_id = Column(UUID(as_uuid=True))
    session_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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