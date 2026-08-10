"""
LankaAgent — API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, health, leads, real_itinerary

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(real_itinerary.router, prefix="/itinerary", tags=["Real Itinerary"])
