"""
LankaAgent — API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, health, leads, llm_usage, real_itinerary, tenants

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(real_itinerary.router, prefix="/itinerary", tags=["Real Itinerary"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(llm_usage.router, prefix="/llm-usage", tags=["LLM Usage"])
