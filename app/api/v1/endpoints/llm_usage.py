"""
LLM Usage API Endpoints — for viewing usage stats and triggering reports.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.integrations.llm_usage import get_usage_tracker, send_daily_usage_email

router = APIRouter(prefix="/llm-usage", tags=["LLM Usage"])


class UsageSummaryResponse(BaseModel):
    """Usage summary response."""
    date: str
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: float
    free_model_calls: int
    paid_model_calls: int
    errors: int
    by_provider: dict
    by_model: dict


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary():
    """Get today's LLM usage summary."""
    tracker = get_usage_tracker()
    summary = tracker.get_daily_summary()
    return UsageSummaryResponse(
        date=summary.date,
        total_calls=summary.total_calls,
        total_input_tokens=summary.total_input_tokens,
        total_output_tokens=summary.total_output_tokens,
        total_tokens=summary.total_tokens,
        total_cost_usd=summary.total_cost_usd,
        free_model_calls=summary.free_model_calls,
        paid_model_calls=summary.paid_model_calls,
        errors=summary.errors,
        by_provider=summary.by_provider,
        by_model=summary.by_model,
    )


@router.get("/summary/monthly")
async def get_monthly_usage_summary():
    """Get current month's LLM usage summary."""
    from datetime import datetime
    tracker = get_usage_tracker()
    now = datetime.now()
    summary = tracker.get_monthly_summary(now.year, now.month)
    return {
        "period": summary.date,
        "total_calls": summary.total_calls,
        "total_tokens": summary.total_tokens,
        "total_cost_usd": summary.total_cost_usd,
        "free_model_calls": summary.free_model_calls,
        "paid_model_calls": summary.paid_model_calls,
        "errors": summary.errors,
        "by_provider": summary.by_provider,
        "by_model": summary.by_model,
    }


@router.post("/send-daily-email")
async def trigger_daily_email(email: str = "nishantha.priyadarshana@gmail.com"):
    """Manually trigger daily usage email."""
    success = await send_daily_usage_email()
    if success:
        return {"message": f"Daily usage email sent to {email}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email - check logs"
        )


@router.get("/provider-pool/status")
async def get_provider_pool_status():
    """Get current provider pool status (for debugging)."""
    from app.integrations.llm_chat import get_engine
    engine = get_engine()
    return engine.provider_pool.status()