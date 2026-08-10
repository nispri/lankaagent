"""
Real Itinerary Chat Endpoint — Uses actual tour data from tour_data.py
"""
from typing import Any

from data.tour_data import (
    ATTRACTIONS,
    HOTELS,
    ITINERARY,
    TOUR_PRICING,
)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Real Itinerary Chat"])


class ChatMessage(BaseModel):
    message: str
    session_id: str
    language: str = "en"
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    language: str
    data_used: list[str] = []


@router.post("/chat", response_model=ChatResponse)
async def real_itinerary_chat(message: ChatMessage) -> ChatResponse:  # noqa: PLR0912, PLR0915 — keyword-router branch table (legacy endpoint, superseded by LLM widget)
    """
    Chat endpoint using REAL itinerary data from tour_data.py
    """
    user_msg = message.message.lower().strip()
    lang = message.language

    # Build context from session
    session_context = message.context or {}
    pax = session_context.get("pax", 2)
    # travel_dates intentionally parsed from session context (reserved)

    response_text = ""
    data_used = []

    # === PRICING QUERIES ===
    if any(k in user_msg for k in ["price", "cost", "how much", "pricing", "rate", "expensive", "budget"]):
        rates = TOUR_PRICING["rates"]["per_person_double"]
        # pax_rate reserved for per-group pricing display
        response_text = "Our 14-day 'Glimpses of Ceylon' tour:\n\n"
        response_text += "**Pricing (per person, all-inclusive):**\n"
        for pax_count, rate in sorted(rates.items()):
            marker = "← YOUR GROUP" if pax_count == pax else ""
            response_text += f"• {pax_count} travelers: ${rate:,}/pp {marker}\n"
        response_text += f"\n• Single supplement: ${TOUR_PRICING['rates']['single_supplement']:,}\n"
        response_text += f"• Child (with bed): ${TOUR_PRICING['rates']['child_with_bed']:,}\n"
        response_text += f"• Child (no bed): ${TOUR_PRICING['rates']['child_no_bed']:,}\n"
        response_text += "\n**Includes:** 13 nights HB, private AC vehicle, chauffeur guide, all transfers, guide, taxes, water.\n"
        response_text += "**Excludes:** Entrance fees, safari jeeps, alcohol, visa, insurance, tips.\n"
        data_used.append("TOUR_PRICING")

    # === DAY-BY-DAY ITINERARY ===
    elif any(k in user_msg for k in ["day by day", "daily", "day wise", "detailed itinerary", "itinerary", "day 1", "day 2", "schedule"]):
        response_text = "**Glimpses of Ceylon — 14 Day Itinerary:**\n\n"
        for day in ITINERARY:
            hotel_name = HOTELS[day["hotel"]]["name"] if day["hotel"] else "Departure"
            highlights = ", ".join(day["highlights"])
            response_text += f"**Day {day['day']}: {day['location']}** — {hotel_name} ({day['meal']})\n"
            response_text += f"  {highlights}\n\n"
        data_used.extend(["ITINERARY", "HOTELS"])

    # === SPECIFIC DAY QUERY ===
    elif "day" in user_msg and any(d.isdigit() for d in user_msg.split()):
        # Extract day number
        import re
        day_match = re.search(r"day\s*(\d+)", user_msg)
        if day_match:
            day_num = int(day_match.group(1))
            day_info = next((d for d in ITINERARY if d["day"] == day_num), None)
            if day_info:
                hotel_name = HOTELS[day_info["hotel"]]["name"] if day_info["hotel"] else "Departure"
                response_text = f"**Day {day_info['day']}: {day_info['location']}**\n"
                response_text += f"**Hotel:** {hotel_name} ({day_info['meal']})\n"
                response_text += f"**Highlights:** {', '.join(day_info['highlights'])}\n"
                if "attractions" in day_info:
                    attr_names = [ATTRACTIONS[a]["name"] for a in day_info["attractions"] if a in ATTRACTIONS]
                    response_text += f"**Attractions:** {', '.join(attr_names)}\n"
                    fees = sum(ATTRACTIONS[a]["fee_usd"] for a in day_info["attractions"] if a in ATTRACTIONS)
                    response_text += f"**Entrance fees (est.):** ${fees}/person\n"
                data_used.extend(["ITINERARY", "HOTELS", "ATTRACTIONS"])
            else:
                response_text = "Invalid day number. Our tour is 14 days (Day 1-14)."

    # === ATTRACTIONS/FEES === (Moved BEFORE location check for specificity)
    elif any(k in user_msg for k in ["entrance", "fee", "ticket", "attraction", "park", "safari", "museum", "temple"]):
        response_text = "**Major Attractions & Entrance Fees (2026 est.):**\\n\\n"
        for _key, attr in ATTRACTIONS.items():
            response_text += f"• **{attr['name']}** — ${attr['fee_usd']} ({attr['category']})\\n"
        response_text += f"\n**Total entrance fees (est.):** ~${sum(a['fee_usd'] for a in ATTRACTIONS.values())}/person\n"
        response_text += "**Safari jeep charges extra** (~$40-60/jeep, shared)."
        data_used.extend(["ATTRACTIONS"])

    # === SPECIFIC LOCATION/HOTEL ===
    elif any(loc in user_msg for loc in ["negombo", "anuradhapura", "habarana", "sigiriya", "kandy", "ella", "yala", "beruwala", "colombo"]):
        for day in ITINERARY:
            if day["location"].lower() in user_msg:
                hotel_name = HOTELS[day["hotel"]]["name"] if day["hotel"] else "Departure"
                hotel_data = HOTELS.get(day["hotel"], {})
                response_text = f"**{day['location']} (Day {day['day']})**\n"
                response_text += f"**Hotel:** {hotel_name} ({hotel_data.get('category', 'N/A')})\n"
                response_text += f"**Meal Plan:** {day['meal']}\n"
                response_text += f"**Highlights:** {', '.join(day['highlights'])}\n"
                if "attractions" in day:
                    attr_names = [ATTRACTIONS[a]["name"] for a in day["attractions"] if a in ATTRACTIONS]
                    fees = sum(ATTRACTIONS[a]["fee_usd"] for a in day["attractions"] if a in ATTRACTIONS)
                    response_text += f"**Attractions:** {', '.join(attr_names)}\n"
                    response_text += f"**Entrance fees (est.):** ${fees}/person\n"
                if hotel_data:
                    response_text += f"\n**Hotel Rates (est. per night):** Standard ${hotel_data['room_types']['standard']}, Deluxe ${hotel_data['room_types']['deluxe']}\n"
                    if "peak_supplement" in hotel_data:
                        response_text += f"Peak supplement: +${hotel_data['peak_supplement']}/night (Dec 15-Jan 15)\n"
                data_used.extend(["ITINERARY", "HOTELS", "ATTRACTIONS"])
                break

    # === HOTEL DETAILS ===
    elif any(k in user_msg for k in ["hotel", "accommodation", "stay", "room", "hotels"]):
        response_text = "**Accommodation (13 Nights):**\n\n"
        for day in ITINERARY:
            if day["hotel"]:
                hotel = HOTELS[day["hotel"]]
                response_text += f"**Day {day['day']} - {day['location']}:** {hotel['name']} ({hotel['category']})\n"
                response_text += f"  Standard: ${hotel['room_types']['standard']}/night | Deluxe: ${hotel['room_types']['deluxe']}/night\n"
                if "peak_supplement" in hotel:
                    response_text += f"  Peak supplement (Dec 15-Jan 15): +${hotel['peak_supplement']}/night\n"
                response_text += f"  Meal supplements: HB +${hotel['meal_rates']['hb']}, FB +${hotel['meal_rates']['fb']}, AI +${hotel['meal_rates']['ai']}\n\n"
        data_used.extend(["HOTELS", "ITINERARY"])

    # === AYURVEDA/WELLNESS ===
    elif any(k in user_msg for k in ["ayurveda", "wellness", "spa", "massage", "shirodhara", "yoga", "ayurvedic"]):
        response_text = "**Ayurveda Wellness Add-on (BIMARI Naviina Partnership):**\n\n"
        response_text += "• **Abhyanga Massage** — $180 (full body herbal oil massage)\n"
        response_text += "• **Shirodhara** — $160 (continuous oil stream on forehead)\n"
        response_text += "• **Yoga & Meditation** — $150/session\n"
        response_text += "• **Herbal Steam Bath** — $90\n"
        response_text += "• **Complete Package** — $580/person (all above + consultation)\n\n"
        response_text += "Available at partner centers in Kandy, Ella, Beruwala. Can be added to any tour day."
        data_used.append("TOUR_PRICING")

    # === AVAILABILITY/DATES ===
    elif any(k in user_msg for k in ["available", "availability", "date", "when", "december", "january", "2026"]):
        response_text = "We have availability for most 2026 dates.\n\n"
        response_text += "**Peak Season (Dec 15 - Jan 15):** +$45/night supplement\n"
        response_text += "**Shoulder Season (Jan 16 - Mar 31):** +$25/night supplement\n\n"
        response_text += "For exact availability, please share:\n"
        response_text += "• Preferred start date\n"
        response_text += "• Number of travelers\n"
        response_text += "• Any flexibility (±3 days)"
        data_used.append("TOUR_PRICING")

    # === BOOKING/QUOTE ===
    elif any(k in user_msg for k in ["book", "booking", "reserve", "quote", "proceed", "confirm", "sign up"]):
        response_text = "I'd be happy to prepare a detailed quote!\n\n"
        response_text += "I need:\n"
        response_text += "1. **Travel dates** (preferred start date ±3 days flexibility)\n"
        response_text += "2. **Exact number of travelers** (adults/children)\n"
        response_text += "3. **Room preference** (Standard/Deluxe, Twin/Double)\n"
        response_text += "4. **Special requirements** (dietary, mobility, celebrations)\n\n"
        response_text += "Once I have these, I'll send a formal quote with day-by-day breakdown and payment schedule."
        data_used.append("TOUR_PRICING")

    # === HELP/CAPABILITIES ===
    elif any(k in user_msg for k in ["help", "what can you do", "what can you help", "how can you help", "capabilities"]):
        response_text = "I'm your Ceyloria Holidays AI concierge with **full access to real tour data**. I can:\n\n"
        response_text += "🏨 **Hotels** — Rates, categories, meal plans for all 8 hotels\n"
        response_text += "🗓️ **Itinerary** — Day-by-day, specific day, or location details\n"
        response_text += "💰 **Pricing** — Per person rates for 2/4/6/10 pax, supplements\n"
        response_text += "🏛️ **Attractions** — Entrance fees for all 18 sites\n"
        response_text += "🌿 **Ayurveda** — Wellness packages, treatments, pricing\n"
        response_text += "📅 **Availability** — 2026 dates, peak/shoulder supplements\n"
        response_text += "📋 **Booking** — Quotes, payment schedules, requirements\n\n"
        response_text += "**Try asking:** \"Day 3 details\", \"Sigiriya entrance fee\", \"Hotel in Kandy\", \"Price for 4 people\", \"Ayurveda package\""
        data_used.append("ALL")

    # === DEFAULT ===
    else:
        response_text = "I have full access to our real tour data! Try asking:\n\n"
        response_text += "• **\"Day 3 details\"** — Specific day activities & hotel\n"
        response_text += "• **\"Sigiriya entrance fee\"** — Exact fee for any attraction\n"
        response_text += "• **\"Hotel in Kandy\"** — Room rates, meal plans, category\n"
        response_text += "• **\"Price for 4 people\"** — Exact per-person rate\n"
        response_text += "• **\"Day by day itinerary\"** — Full 14-day breakdown\n"
        response_text += "• **\"Ayurveda package\"** — Wellness treatments & pricing\n"
        response_text += "• **\"Availability December\"** — Peak season supplements\n"
        response_text += "• **\"Book for 2 people\"** — Start a quote\n\n"
        response_text += "What would you like to know?"
        data_used = []

    # Add context hint
    if pax != 2:
        response_text += f"\n\n*Context: Showing rates for {pax} travelers*"

    return ChatResponse(
        response=response_text,
        session_id=message.session_id,
        language=lang,
        data_used=data_used
    )


@router.get("/data/summary")
async def get_data_summary():
    """Summary of all available tour data"""
    return {
        "tour_name": TOUR_PRICING["name"],
        "duration": TOUR_PRICING["duration"],
        "total_days": len(ITINERARY),
        "hotels": len(HOTELS),
        "attractions": len(ATTRACTIONS),
        "destinations": {d["location"] for d in ITINERARY},
        "pricing_tiers": list(TOUR_PRICING["rates"]["per_person_double"].keys()),
        "price_range": {
            "min": min(TOUR_PRICING["rates"]["per_person_double"].values()),
            "max": max(TOUR_PRICING["rates"]["per_person_double"].values())
        }
    }


@router.get("/itinerary/full")
async def get_full_itinerary():
    """Complete day-by-day itinerary with all data"""
    full = []
    for day in ITINERARY:
        hotel = HOTELS.get(day["hotel"], {}) if day["hotel"] else None
        attractions = []
        if "attractions" in day:
            for a in day["attractions"]:
                if a in ATTRACTIONS:
                    attractions.append({"key": a, **ATTRACTIONS[a]})
        full.append({
            **day,
            "hotel_details": hotel,
            "attractions": attractions
        })
    return {"itinerary": full, "pricing": TOUR_PRICING}
