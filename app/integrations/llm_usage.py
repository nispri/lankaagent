"""
LLM Usage Tracker — tracks token usage across providers, logs costs, and sends daily email reports.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """Single LLM call usage record."""
    timestamp: datetime
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    success: bool
    error: str | None = None


@dataclass
class DailyUsageSummary:
    """Aggregated daily usage by provider/model."""
    date: str
    total_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    by_provider: dict = field(default_factory=dict)
    by_model: dict = field(default_factory=dict)
    errors: int = 0
    free_model_calls: int = 0
    paid_model_calls: int = 0


# Cost estimates per 1K tokens (USD) - update as pricing changes
MODEL_COSTS = {
    # Free models
    "deepseek-v4-flash-free": {"input": 0.0, "output": 0.0},
    "meta-llama/llama-3.1-8b-instruct:free": {"input": 0.0, "output": 0.0},
    "google/gemma-2-9b-it:free": {"input": 0.0, "output": 0.0},
    "microsoft/phi-3-mini-128k-instruct:free": {"input": 0.0, "output": 0.0},
    "meta-llama/llama-3.2-3b-instruct:free": {"input": 0.0, "output": 0.0},
    "google/gemma-2-27b-it:free": {"input": 0.0, "output": 0.0},
    "deepseek/deepseek-chat-v3-0324": {"input": 0.0, "output": 0.0},
    # Cost-effective paid models
    "deepseek/deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.00059, "output": 0.00079},
    "anthropic/claude-3.5-haiku": {"input": 0.0008, "output": 0.004},
    "google/gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "anthropic/claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "openai/gpt-4o": {"input": 0.0025, "output": 0.01},
    "google/gemini-pro": {"input": 0.000125, "output": 0.0005},
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.00059, "output": 0.00079},
}


def is_free_model(model: str) -> bool:
    """Check if a model is free (cost = $0)."""
    costs = MODEL_COSTS.get(model, {"input": 0, "output": 0})
    return costs.get("input", 0) == 0 and costs.get("output", 0) == 0


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for a model call."""
    costs = MODEL_COSTS.get(model, {"input": 0.0005, "output": 0.0015})
    input_cost = (input_tokens / 1000) * costs.get("input", 0.0005)
    output_cost = (output_tokens / 1000) * costs.get("output", 0.0015)
    return round(input_cost + output_cost, 6)


class UsageTracker:
    """Tracks LLM usage, persists to disk, and sends daily email reports."""

    def __init__(self, storage_path: str = "/app/data/llm_usage.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[UsageRecord] = []
        self._load()

    def _load(self) -> None:
        """Load existing records from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                self._records = [
                    UsageRecord(
                        timestamp=datetime.fromisoformat(r["timestamp"]),
                        provider=r["provider"],
                        model=r["model"],
                        input_tokens=r["input_tokens"],
                        output_tokens=r["output_tokens"],
                        total_tokens=r["total_tokens"],
                        estimated_cost_usd=r["estimated_cost_usd"],
                        success=r["success"],
                        error=r.get("error"),
                    )
                    for r in data
                ]
            except Exception as e:
                logger.warning(f"Failed to load usage records: {e}")
                self._records = []

    def _save(self) -> None:
        """Save records to disk."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump([
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "provider": r.provider,
                        "model": r.model,
                        "input_tokens": r.input_tokens,
                        "output_tokens": r.output_tokens,
                        "total_tokens": r.total_tokens,
                        "estimated_cost_usd": r.estimated_cost_usd,
                        "success": r.success,
                        "error": r.error,
                    }
                    for r in self._records
                ], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage records: {e}")

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        success: bool = True,
        error: str | None = None,
    ) -> UsageRecord:
        """Record a single LLM call."""
        total = input_tokens + output_tokens
        cost = estimate_cost(model, input_tokens, output_tokens)
        record = UsageRecord(
            timestamp=datetime.now(timezone.utc),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
            success=success,
            error=error,
        )
        self._records.append(record)
        self._save()
        logger.info(
            f"LLM usage: {provider}/{model} — "
            f"in:{input_tokens} out:{output_tokens} cost:${cost:.6f} "
            f"{'✓' if success else '✗'}"
        )
        return record

    def get_daily_summary(self, date: datetime | None = None) -> DailyUsageSummary:
        """Get aggregated summary for a specific date (UTC)."""
        if date is None:
            date = datetime.now(timezone.utc)
        date_str = date.strftime("%Y-%m-%d")
        start = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        day_records = [r for r in self._records if start <= r.timestamp < end]

        summary = DailyUsageSummary(date=date_str)
        for r in day_records:
            summary.total_calls += 1
            summary.total_input_tokens += r.input_tokens
            summary.total_output_tokens += r.output_tokens
            summary.total_tokens += r.total_tokens
            summary.total_cost_usd += r.estimated_cost_usd
            if not r.success:
                summary.errors += 1

            # By provider
            p = summary.by_provider.setdefault(r.provider, {
                "calls": 0, "tokens": 0, "cost": 0.0, "models": {}
            })
            p["calls"] += 1
            p["tokens"] += r.total_tokens
            p["cost"] += r.estimated_cost_usd
            m = p["models"].setdefault(r.model, {"calls": 0, "tokens": 0, "cost": 0.0})
            m["calls"] += 1
            m["tokens"] += r.total_tokens
            m["cost"] += r.estimated_cost_usd

            # By model
            m2 = summary.by_model.setdefault(r.model, {
                "calls": 0, "tokens": 0, "cost": 0.0, "provider": r.provider
            })
            m2["calls"] += 1
            m2["tokens"] += r.total_tokens
            m2["cost"] += r.estimated_cost_usd

            # Free vs paid
            if is_free_model(r.model):
                summary.free_model_calls += 1
            else:
                summary.paid_model_calls += 1

        # Round costs
        summary.total_cost_usd = round(summary.total_cost_usd, 6)
        for p in summary.by_provider.values():
            p["cost"] = round(p["cost"], 6)
            for m in p["models"].values():
                m["cost"] = round(m["cost"], 6)
        for m in summary.by_model.values():
            m["cost"] = round(m["cost"], 6)

        return summary

    def get_monthly_summary(self, year: int, month: int) -> DailyUsageSummary:
        """Get aggregated summary for a month."""
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        month_records = [r for r in self._records if start <= r.timestamp < end]

        summary = DailyUsageSummary(date=f"{year}-{month:02d}")
        for r in month_records:
            summary.total_calls += 1
            summary.total_input_tokens += r.input_tokens
            summary.total_output_tokens += r.output_tokens
            summary.total_tokens += r.total_tokens
            summary.total_cost_usd += r.estimated_cost_usd
            if not r.success:
                summary.errors += 1

            p = summary.by_provider.setdefault(r.provider, {
                "calls": 0, "tokens": 0, "cost": 0.0, "models": {}
            })
            p["calls"] += 1
            p["tokens"] += r.total_tokens
            p["cost"] += r.estimated_cost_usd

            m = summary.by_model.setdefault(r.model, {
                "calls": 0, "tokens": 0, "cost": 0.0, "provider": r.provider
            })
            m["calls"] += 1
            m["tokens"] += r.total_tokens
            m["cost"] += r.estimated_cost_usd

            if is_free_model(r.model):
                summary.free_model_calls += 1
            else:
                summary.paid_model_calls += 1

        summary.total_cost_usd = round(summary.total_cost_usd, 6)
        for p in summary.by_provider.values():
            p["cost"] = round(p["cost"], 6)
        for m in summary.by_model.values():
            m["cost"] = round(m["cost"], 6)

        return summary

    def format_daily_email(self, summary: DailyUsageSummary) -> str:
        """Format daily usage summary as HTML email."""
        free_pct = 0
        if summary.total_calls > 0:
            free_pct = round(summary.free_model_calls / summary.total_calls * 100, 1)

        lines = [
            f"<h2>📊 LLM Usage Report — {summary.date}</h2>",
            f"<p><strong>Total Calls:</strong> {summary.total_calls} | "
            f"<strong>Total Tokens:</strong> {summary.total_tokens:,} | "
            f"<strong>Est. Cost:</strong> ${summary.total_cost_usd:.6f} | "
            f"<strong>Free Model %:</strong> {free_pct}%</p>",
            f"<p><strong>Free Model Calls:</strong> {summary.free_model_calls} | "
            f"<strong>Paid Model Calls:</strong> {summary.paid_model_calls} | "
            f"<strong>Errors:</strong> {summary.errors}</p>",
            "<h3>By Provider</h3>",
            "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse'>",
            "<tr><th>Provider</th><th>Calls</th><th>Tokens</th><th>Cost (USD)</th><th>Models</th></tr>",
        ]

        for provider, data in sorted(summary.by_provider.items(), key=lambda x: -x[1]["cost"]):
            models_str = ", ".join(
                f"{m}({d['calls']}, ${d['cost']:.6f})"
                for m, d in data["models"].items()
            )
            lines.append(
                f"<tr><td>{provider}</td><td>{data['calls']}</td>"
                f"<td>{data['tokens']:,}</td><td>${data['cost']:.6f}</td>"
                f"<td>{models_str}</td></tr>"
            )

        lines.append("</table>")
        lines.append("<h3>By Model</h3>")
        lines.append(
            "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse'>"
            "<tr><th>Model</th><th>Provider</th><th>Calls</th><th>Tokens</th>"
            "<th>Cost (USD)</th><th>Type</th></tr>"
        )

        for model, data in sorted(summary.by_model.items(), key=lambda x: -x[1]["cost"]):
            model_type = "🆓 Free" if is_free_model(model) else "💰 Paid"
            lines.append(
                f"<tr><td>{model}</td><td>{data['provider']}</td>"
                f"<td>{data['calls']}</td><td>{data['tokens']:,}</td>"
                f"<td>${data['cost']:.6f}</td><td>{model_type}</td></tr>"
            )

        lines.append("</table>")
        lines.append("<hr>")
        lines.append(
            f"<p><small>Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
            f"Costs are estimates based on public pricing.</small></p>"
        )
        return "\n".join(lines)

    async def send_daily_email(self, email: str = "nishantha.priyadarshana@gmail.com") -> bool:
        """Send daily usage email via Postmark."""
        try:
            from app.core.config import settings
            import httpx

            if not settings.POSTMARK_SERVER_TOKEN:
                logger.warning("POSTMARK_SERVER_TOKEN not configured, skipping email")
                return False

            summary = self.get_daily_summary()
            html = self.format_daily_email(summary)

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.postmarkapp.com/email",
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Postmark-Server-Token": settings.POSTMARK_SERVER_TOKEN,
                    },
                    json={
                        "From": settings.POSTMARK_FROM_EMAIL,
                        "To": email,
                        "Subject": f"📊 LankaAgent LLM Daily Usage — {summary.date}",
                        "HtmlBody": html,
                        "Tag": "llm-usage-daily",
                    },
                )
                if resp.status_code == 200:
                    logger.info(f"Daily usage email sent to {email}")
                    return True
                else:
                    logger.error(f"Postmark error: {resp.status_code} {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to send daily usage email: {e}")
            return False


# Global tracker instance
_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get or create the global usage tracker."""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker


async def send_daily_usage_email() -> bool:
    """Scheduled job: send daily usage email at end of day UTC."""
    tracker = get_usage_tracker()
    return await tracker.send_daily_email()