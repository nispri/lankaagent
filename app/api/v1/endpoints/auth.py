"""Auth endpoints"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login() -> dict:
    """Login endpoint (placeholder)"""
    return {"message": "Login endpoint - not yet implemented"}


@router.post("/register")
async def register() -> dict:
    """Register endpoint (placeholder)"""
    return {"message": "Register endpoint - not yet implemented"}


@router.get("/me")
async def me() -> dict:
    """Current user endpoint (placeholder)"""
    return {"message": "Current user endpoint - not yet implemented"}