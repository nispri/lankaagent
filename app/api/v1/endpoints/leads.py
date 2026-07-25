"""Leads endpoints"""
from uuid import UUID

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("")
async def list_leads() -> list[dict]:
    """List all leads (placeholder)"""
    return []


@router.get("/{lead_id}")
async def get_lead(lead_id: UUID) -> dict:
    """Get lead by ID (placeholder)"""
    return {"id": str(lead_id), "message": "Lead detail endpoint - not yet implemented"}


@router.post("")
async def create_lead() -> dict:
    """Create a new lead (placeholder)"""
    return {"message": "Create lead endpoint - not yet implemented"}