"""
LankaAgent — SQLAlchemy Models (Multi-Tenant via RLS)
"""
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tenant(Base):
    """Operator (multi-tenant)"""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="starter", nullable=False)
    settings = Column(JSON, default=dict)
    stripe_customer_id = Column(String(255))
    payhere_merchant_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    """Operator staff user"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="agent", nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="users")


class Lead(Base):
    """Inbound inquiry"""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False)
    external_id = Column(String(255))
    contact_name = Column(String(255))
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    language = Column(String(10), default="en")
    status = Column(String(50), default="new", nullable=False)
    intent = Column(JSON, default=dict)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="leads")


class Conversation(Base):
    """WhatsApp/Web chat session"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    channel = Column(String(50), nullable=False)
    external_thread_id = Column(String(255))
    language = Column(String(10), default="en")
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Message(Base):
    """Individual message within a conversation"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True),
                             ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON)
    tool_results = Column(JSON)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Itinerary(Base):
    """Generated travel itinerary/quote"""
    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    version = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    days = Column(JSON, nullable=False)
    total_price_usd = Column(Float(precision=2))
    total_price_lkr = Column(Float(precision=2))
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="draft")
    valid_until = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Booking(Base):
    """Confirmed booking"""
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="SET NULL"))
    booking_reference = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), default="confirmed")
    travelers = Column(JSON, nullable=False)
    special_requests = Column(Text)
    payment_status = Column(String(50), default="pending")
    payment_intent_id = Column(String(255))
    commission_usd = Column(Float(precision=2))
    commission_lkr = Column(Float(precision=2))
    starts_at = Column(Date, nullable=False)
    ends_at = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Payment(Base):
    """Payment transaction"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"))
    amount_usd = Column(Float(precision=2))
    amount_lkr = Column(Float(precision=2))
    currency = Column(String(3), nullable=False)
    gateway = Column(String(50), nullable=False)
    gateway_payment_id = Column(String(255))
    gateway_response = Column(JSON)
    status = Column(String(50), default="pending")
    fee_usd = Column(Float(precision=2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WellnessProtocol(Base):
    """Ayurveda/wellness protocol for a lead"""
    __tablename__ = "wellness_protocols"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    health_intake = Column(JSON, nullable=False)
    recommended_treatments = Column(JSON, nullable=False)
    assigned_doctor_id = Column(UUID(as_uuid=True))
    status = Column(String(50), default="proposed")
    total_price_usd = Column(Float(precision=2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnalyticsEvent(Base):
    """Product analytics event"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(UUID(as_uuid=True),
                       ForeignKey("tenants.id", ondelete="CASCADE"))
    event_name = Column(String(255), nullable=False)
    properties = Column(JSON, default=dict)
    user_id = Column(UUID(as_uuid=True))
    session_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
