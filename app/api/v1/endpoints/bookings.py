"""Bookings endpoints"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Booking

router = APIRouter()


@router.get("")
async def list_bookings(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """List all bookings"""
    result = await session.execute(select(Booking).order_by(Booking.created_at.desc()).limit(50))
    bookings = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "reference": b.booking_reference,
            "status": b.status,
            "payment_status": b.payment_status,
            "travelers": len(b.travelers) if b.travelers else 0,
            "total_nights": (b.ends_at - b.starts_at).days,
            "starts_at": str(b.starts_at),
            "ends_at": str(b.ends_at),
            "created_at": str(b.created_at),
        }
        for b in bookings
    ]


@router.get("/{booking_id}")
async def get_booking(booking_id: UUID, session: AsyncSession = Depends(get_session)) -> dict:
    """Get booking by ID"""
    result = await session.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        return {"error": "Booking not found", "id": str(booking_id)}
    return {
        "id": str(booking.id),
        "reference": booking.booking_reference,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "travelers": booking.travelers,
        "special_requests": booking.special_requests,
        "commission_usd": booking.commission_usd,
        "starts_at": str(booking.starts_at),
        "ends_at": str(booking.ends_at),
        "created_at": str(booking.created_at),
    }
