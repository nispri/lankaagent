"""
Custom Tour Pricing Engine — Ceyloria Holidays
Builds a priced itinerary for ANY number of days from real hotel/attraction data.

Used by Anuki (the concierge LLM) when a guest asks for a customized tour
(shorter, longer, or rearranged). All arithmetic is done here in Python —
the LLM never computes prices itself.
"""

from data.tour_data import ATTRACTIONS, HOTELS, ITINERARY

# ─────────────────────────────────────────────────────────────
# COST PARAMETERS (calibrate with real supplier rates)
# ─────────────────────────────────────────────────────────────
VEHICLE_DAILY_RATE = 140      # USD/day — AC vehicle + chauffeur guide (1-4 pax)
VEHICLE_DAILY_RATE_GROUP = 170  # USD/day — van + guide (5+ pax)
AIRPORT_TRANSFER_TOTAL = 60   # USD — both airport transfers for the whole group
MARGIN = 0.2595              # 25.95% — calibrates 14-day/2-pax to exactly $2,490/pp
SINGLE_SUPPLEMENT_PER_NIGHT = 45  # USD/night when solo traveler


def _hotel_cost_per_night(hotel_key: str, meal: str = "HB") -> int:
    """Room (standard, double) + meal rate, in USD per night."""
    h = HOTELS[hotel_key]
    return h["room_types"]["standard"] + h["meal_rates"].get(meal.lower(), 0)


def quote_custom_tour(days: int, pax: int, start_day: int = 1) -> dict:
    """Price a custom tour of `days` nights starting from itinerary day `start_day`.

    Returns a dict with per-person price, total, breakdown, and the day list.
    """
    days = max(days, 2)
    days = min(days, 21)
    pax = max(1, int(pax))

    # Pick the requested slice of the itinerary (hotel nights = days, last day = departure)
    tour_days = ITINERARY[start_day - 1 : start_day - 1 + days]
    # Ensure we have a departure day: if slice ends mid-tour, add departure from last hotel
    if len(tour_days) < days:
        # Extend by repeating the last hotel (approximation for longer stays)
        last = tour_days[-1]
        while len(tour_days) < days:
            tour_days.append({**last, "day": tour_days[-1]["day"] + 1})
    if tour_days and tour_days[-1].get("hotel") is not None:
        tour_days.append({**tour_days[-1], "day": tour_days[-1]["day"] + 1, "hotel": None, "highlights": ["Airport transfer", "Departure"]})

    # Hotel nights: all days that have a hotel (excludes the departure day)
    hotel_nights = [d for d in tour_days if d.get("hotel")]
    hotel_total = sum(_hotel_cost_per_night(d["hotel"], d.get("meal", "HB")) for d in hotel_nights)

    # Transport: daily rate x travel days + airport transfers
    vehicle_rate = VEHICLE_DAILY_RATE_GROUP if pax >= 5 else VEHICLE_DAILY_RATE
    transport_total = vehicle_rate * days + AIRPORT_TRANSFER_TOTAL

    # Rooms needed for the group
    rooms = (pax + 1) // 2  # 2 pax per double room

    # Cost per person = (hotel rooms cost + transport) / pax
    hotel_for_group = hotel_total * rooms
    cost_per_person = (hotel_for_group + transport_total) / pax

    # Single supplement: if pax == 1, they pay the room alone
    if pax == 1:
        cost_per_person += SINGLE_SUPPLEMENT_PER_NIGHT * len(hotel_nights)

    price_per_person = round(cost_per_person * (1 + MARGIN))
    total = price_per_person * pax

    # Attraction fees estimate
    attraction_fees = 0
    attractions_seen = []
    for d in tour_days:
        for a_key in d.get("attractions", []):
            if a_key in ATTRACTIONS and a_key not in attractions_seen:
                attractions_seen.append(a_key)
                attraction_fees += ATTRACTIONS[a_key]["fee_usd"]

    # Build human-readable day list
    day_list = []
    for d in tour_days:
        hotel_name = HOTELS[d["hotel"]]["name"] if d.get("hotel") else "Departure"
        day_list.append(
            f"Day {d['day']}: {d['location']} — {hotel_name} ({d.get('meal', 'BB')}) — {', '.join(d['highlights'][:3])}"
        )

    return {
        "name": f"Custom {days}-day Sri Lanka Tour",
        "days": days,
        "nights": len(hotel_nights),
        "pax": pax,
        "rooms": rooms,
        "price_per_person_usd": price_per_person,
        "total_usd": total,
        "currency": "USD",
        "meal_plan": "HB (Breakfast + Dinner)",
        "breakdown": {
            "hotels_usd": hotel_for_group,
            "transport_usd": transport_total,
            "attraction_fees_est_pp": attraction_fees,
            "vehicle": "AC van + guide" if pax >= 5 else "AC car + chauffeur guide",
        },
        "day_list": day_list,
        "note": "Estimated pricing — final quote after confirming availability with hotels.",
    }


def quote_table() -> str:
    """Precompute a compact quote table for common durations/pax for the LLM prompt."""
    lines = ["CUSTOM TOUR QUOTES (USD per person, double occupancy, HB):"]
    for days in (5, 7, 10, 14):
        row = [f"  {days} days: "]
        for pax in (2, 4, 6):
            q = quote_custom_tour(days, pax)
            row.append(f"{pax} pax ${q['price_per_person_usd']:,}")
        lines.append("  |  ".join(row))
    lines.append("  (For other durations/pax: compute with the same engine; attraction fees and supplements extra.)")
    return "\n".join(lines)
