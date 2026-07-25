"""Leads endpoints — real database queries"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.models import Booking, Itinerary, Lead, WellnessProtocol

router = APIRouter()


@router.get("")
async def list_leads(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """List all leads"""
    result = await session.execute(select(Lead).order_by(Lead.created_at.desc()).limit(50))
    leads = result.scalars().all()
    return [
        {
            "id": str(lead.id),
            "name": lead.contact_name,
            "phone": lead.contact_phone,
            "email": lead.contact_email,
            "language": lead.language,
            "source": lead.source,
            "status": lead.status,
            "intent": lead.intent,
            "created_at": str(lead.created_at),
        }
        for lead in leads
    ]


@router.get("/{lead_id}")
async def get_lead(lead_id: UUID, session: AsyncSession = Depends(get_session)) -> dict:
    """Get lead by ID with full details"""
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        return {"error": "Lead not found", "id": str(lead_id)}

    # Get related itinerary
    itin_result = await session.execute(
        select(Itinerary).where(Itinerary.lead_id == lead_id).order_by(Itinerary.version.desc())
    )
    itinerary = itin_result.scalar_one_or_none()

    # Get related booking
    booking_result = await session.execute(
        select(Booking).where(Booking.lead_id == lead_id)
    )
    booking = booking_result.scalar_one_or_none()

    # Get wellness protocol
    wellness_result = await session.execute(
        select(WellnessProtocol).where(WellnessProtocol.lead_id == lead_id)
    )
    wellness = wellness_result.scalar_one_or_none()

    return {
        "lead": {
            "id": str(lead.id),
            "name": lead.contact_name,
            "phone": lead.contact_phone,
            "email": lead.contact_email,
            "language": lead.language,
            "source": lead.source,
            "status": lead.status,
            "intent": lead.intent,
            "created_at": str(lead.created_at),
        },
        "itinerary": {
            "title": itinerary.title,
            "days_count": len(itinerary.days) if itinerary else 0,
            "total_price_usd": itinerary.total_price_usd,
            "status": itinerary.status,
            "valid_until": str(itinerary.valid_until) if itinerary else None,
        } if itinerary else None,
        "booking": {
            "reference": booking.booking_reference,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "travelers": booking.travelers,
            "total_nights": (booking.ends_at - booking.starts_at).days,
            "starts_at": str(booking.starts_at),
            "ends_at": str(booking.ends_at),
        } if booking else None,
        "wellness": {
            "treatments": wellness.recommended_treatments,
            "total_price_usd": wellness.total_price_usd,
            "status": wellness.status,
        } if wellness else None,
    }


@router.post("")
async def create_lead() -> dict:
    """Create a new lead (placeholder — will implement with agent)"""
    return {"message": "Create lead via agent — not yet available"}
