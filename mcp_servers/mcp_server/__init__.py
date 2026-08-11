"""
LankaAgent MCP Server — Tourism Data Tools (FastMCP)

Real data wired from the Ceyloria tour knowledge base (hotels, attractions,
pricing, itinerary). Build context copies ../data/tour_data.py into ./data/
so the server runs self-contained.
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("LankaAgent Tourism Data")

# ── Data loading: prefer the copied repo data, fall back to embedded copies ──
try:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data import tour_data  # type: ignore[import-not-found]

    HOTELS: dict = tour_data.HOTELS
    ATTRACTIONS: dict = tour_data.ATTRACTIONS
    ITINERARY: list = tour_data.ITINERARY
    TOUR_PRICING: dict = tour_data.TOUR_PRICING
except Exception:  # pragma: no cover - fallback for standalone runs
    HOTELS = {}
    ATTRACTIONS = {}
    ITINERARY = []
    TOUR_PRICING = {}


# Attraction → province + description enrichment (kept here, not in tour data)
_PROVINCES = {
    "sigiriya": "Central", "sigiriya_museum": "Central", "pidurangala": "Central",
    "dambulla_cave": "Central", "anuradhapura": "North Central", "mihintale": "North Central",
    "isurumuniya": "North Central", "polonnaruwa": "North Central",
    "tooth_temple": "Central", "cultural_show": "Central", "peradeniya": "Central",
    "haggala": "Uva", "minneriya": "North Central", "yala": "Southern", "village_tour": "North Central",
}
_DESCRIPTIONS = {
    "sigiriya": "UNESCO-listed 5th-century rock fortress with frescoes and lion staircase.",
    "anuradhapura": "UNESCO ancient capital with Sri Maha Bodhi (2,300-year-old sacred fig tree).",
    "polonnaruwa": "UNESCO medieval capital with Gal Vihara rock-carved Buddha statues.",
    "tooth_temple": "UNESCO site housing the Sacred Tooth Relic in Kandy.",
    "yala": "Sri Lanka's most famous national park — leopards, elephants, sloth bears.",
    "minneriya": "Famous for the 'Gathering' — herds of elephants near the Minneriya tank.",
    "haggala": "Cool-climate botanical garden near Ella with 10,000+ plant species.",
    "dambulla_cave": "UNESCO cave temple complex with 150+ Buddha statues and murals.",
    "peradeniya": "Royal Botanical Garden — orchids, giant bamboo, 4,000+ species.",
}


@mcp.tool(name="search_attractions")
async def search_attractions(
    province: str | None = None, category: str | None = None, limit: int = 20
) -> list[dict]:
    """Search Sri Lanka attractions by province and category.

    Args:
        province: Optional province name (e.g. "Central", "North Central", "Uva", "Southern").
        category: Optional category (heritage, wildlife, nature, culture, adventure).
        limit: Max results (default 20).
    """
    results: list[dict] = []
    for aid, data in ATTRACTIONS.items():
        if category and data.get("category") != category:
            continue
        prov = _PROVINCES.get(aid)
        if province and prov and prov.lower() != province.lower():
            continue
        results.append({
            "id": aid,
            "name": data.get("name", aid),
            "category": data.get("category"),
            "province": prov,
            "fee_usd": data.get("fee_usd"),
        })
    return results[:limit]


@mcp.tool(name="get_attraction_details")
async def get_attraction_details(attraction_id: str) -> dict:
    """Get full attraction details including entrance fee and description."""
    data = ATTRACTIONS.get(attraction_id)
    if not data:
        return {"found": False, "attraction_id": attraction_id, "error": "Attraction not found"}
    return {
        "found": True,
        "id": attraction_id,
        "name": data.get("name"),
        "category": data.get("category"),
        "province": _PROVINCES.get(attraction_id),
        "fee_usd": data.get("fee_usd"),
        "description": _DESCRIPTIONS.get(attraction_id, "No description yet"),
        "in_tour": any(
            attraction_id in (day.get("attractions") or [])
            for day in ITINERARY
        ),
    }


@mcp.tool(name="get_seasonal_pricing")
async def get_seasonal_pricing(attraction_id: str, month: int) -> dict:
    """Get peak/shoulder/low pricing adjustment for an attraction by month (1-12).

    Peak: Dec 15 - Jan 15 (supplement per night). Shoulder: Jan 16 - Mar 31.
    """
    data = ATTRACTIONS.get(attraction_id)
    if not data:
        return {"attraction_id": attraction_id, "found": False}
    if not 1 <= month <= 12:
        return {"attraction_id": attraction_id, "found": False, "error": "month must be 1-12"}
    if month == 12:
        season = "peak"
    elif month == 1:
        season = "peak"  # Jan 1-15 peak; simplified
    elif month in (2, 3):
        season = "shoulder"
    else:
        season = "low"
    per_night = TOUR_PRICING.get("peak_season_supplement_per_night", 45) if season == "peak" else (
        TOUR_PRICING.get("shoulder_season_supplement_per_night", 25) if season == "shoulder" else 0
    )
    return {
        "attraction_id": attraction_id,
        "name": data.get("name"),
        "month": month,
        "season": season,
        "entrance_fee_usd": data.get("fee_usd"),
        "tour_supplement_per_night_usd": per_night,
    }


@mcp.tool(name="get_visa_requirements")
async def get_visa_requirements(nationality: str) -> dict:
    """Get visa requirements for Sri Lanka by nationality.

    Returns ETA eligibility and indicative fee for the main source markets.
    """
    # Indicative ETA fee bands (ETA system, 2026). Free for most arrivals.
    country = nationality.strip().lower()
    fee = 50
    visa_required = True
    eta_eligible = True
    exempt = {"maldives", "singapore", "seychelles"}
    if country in exempt:
        visa_required = False
        eta_eligible = False
        fee = 0
    return {
        "nationality": nationality,
        "visa_required": visa_required,
        "eta_eligible": eta_eligible,
        "fee_usd": fee,
        "note": "Electronic Travel Authorization (ETA) — apply online before arrival",
    }


@mcp.tool(name="get_tour_quote")
async def get_tour_quote(pax: int, days: int = 14) -> dict:
    """Get a Ceyloria tour quote (USD per person) for a party size and duration.

    Args:
        pax: Number of travelers (2, 4, 6, or 10).
        days: Tour length in days (5, 7, 10, or 14).
    """
    try:
        from app.integrations.tour_pricing import (
            quote_custom_tour,  # type: ignore[import-not-found]
        )

        return quote_custom_tour(pax=pax, days=days)
    except Exception:
        rates = TOUR_PRICING.get("rates", {}).get("per_person_double", {})
        per_person = rates.get(pax, rates.get(2, 2490))
        return {
            "tour": TOUR_PRICING.get("name", "Glimpses of Ceylon"),
            "pax": pax,
            "days": days,
            "per_person_usd": per_person,
            "note": "Estimated rate; exact quote from pricing engine",
        }


@mcp.tool(name="get_hotels")
async def get_hotels(location: str | None = None) -> list[dict]:
    """List hotels in the tour network, optionally filtered by location."""
    results: list[dict] = []
    for hid, data in HOTELS.items():
        if location and location.lower() not in (data.get("location") or "").lower():
            continue
        results.append({
            "id": hid,
            "name": data.get("name"),
            "location": data.get("location"),
            "category": data.get("category"),
            "standard_rate_usd": data.get("room_types", {}).get("standard"),
        })
    return results
