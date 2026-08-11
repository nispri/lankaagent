"""
Ceyloria Holidays — Tour Packages (2026 Updated Pricing)
"""

# ─────────────────────────────────────────────────────────────
# HOTEL DATA (2026 Estimated Rates)
# ─────────────────────────────────────────────────────────────
HOTELS = {
    "arie_lagoon": {
        "name": "Arie Lagoon",
        "location": "Negombo",
        "category": "4-star",
        "room_types": {"standard": 95, "deluxe": 130},
        "meal_rates": {"bb": 0, "hb": 25, "fb": 50, "ai": 90},
        "peak_supplement": 35,  # Dec 21 - Jan 10
        "shoulder_supplement": 18,  # Jan 11 - Mar 31
    },
    "alakamanda": {
        "name": "Alakamanda Hotel",
        "location": "Anuradhapura",
        "category": "4-star",
        "room_types": {"standard": 80, "deluxe": 110},
        "meal_rates": {"bb": 0, "hb": 20, "fb": 40, "ai": 75},
    },
    "cinnamon_village": {
        "name": "Cinnamon Village",
        "location": "Habarana",
        "category": "4-star",
        "room_types": {"standard": 120, "deluxe": 160},
        "meal_rates": {"bb": 0, "hb": 25, "fb": 50, "ai": 95},
        "peak_supplement": 38,
        "shoulder_supplement": 28,
    },
    "cinnamon_citadel": {
        "name": "Cinnamon Citadel",
        "location": "Kandy",
        "category": "4-star",
        "room_types": {"standard": 135, "deluxe": 180},
        "meal_rates": {"bb": 0, "hb": 25, "fb": 50, "ai": 95},
        "peak_supplement": 48,
        "shoulder_supplement": 25,
    },
    "ekho_ella": {
        "name": "EKHO Ella",
        "location": "Ella",
        "category": "4-star",
        "room_types": {"standard": 110, "deluxe": 150},
        "meal_rates": {"bb": 0, "hb": 22, "fb": 45, "ai": 85},
        "peak_supplement": 60,
        "shoulder_supplement": 28,
    },
    "cinnamon_wild": {
        "name": "Cinnamon Wild",
        "location": "Yala",
        "category": "4-star",
        "room_types": {"standard": 150, "deluxe": 200},
        "meal_rates": {"bb": 0, "hb": 25, "fb": 50, "ai": 95},
        "peak_supplement": 65,
        "shoulder_supplement": 42,
    },
    "cinnamon_bey": {
        "name": "Cinnamon Bey",
        "location": "Beruwala",
        "category": "5-star",
        "room_types": {"standard": 160, "deluxe": 220},
        "meal_rates": {"bb": 0, "hb": 25, "fb": 50, "ai": 95},
        "peak_supplement": 130,
        "shoulder_supplement": 28,
    },
    "ozo_colombo": {
        "name": "OZO Colombo",
        "location": "Colombo",
        "category": "4-star",
        "room_types": {"standard": 100, "deluxe": 140},
        "meal_rates": {"bb": 0, "hb": 20, "fb": 40, "ai": 80},
    },
}

# ─────────────────────────────────────────────────────────────
# ATTRACTIONS & ENTRANCE FEES (2026 Estimated)
# ─────────────────────────────────────────────────────────────
ATTRACTIONS = {
    "sigiriya": {"name": "Sigiriya Rock Fortress", "fee_usd": 42, "category": "heritage"},
    "sigiriya_museum": {"name": "Sigiriya Museum", "fee_usd": 6, "category": "heritage"},
    "pidurangala": {"name": "Pidurangala Rock", "fee_usd": 5, "category": "adventure"},
    "dambulla_cave": {"name": "Dambulla Cave Temple", "fee_usd": 10, "category": "heritage"},
    "anuradhapura": {"name": "Ancient City of Anuradhapura", "fee_usd": 35, "category": "heritage"},
    "mihintale": {"name": "Mihintale Temple", "fee_usd": 6, "category": "heritage"},
    "isurumuniya": {"name": "Isurumuniya Temple", "fee_usd": 4, "category": "heritage"},
    "polonnaruwa": {"name": "Polonnaruwa Ancient City", "fee_usd": 30, "category": "heritage"},
    "tooth_temple": {"name": "Temple of the Sacred Tooth Relic", "fee_usd": 12, "category": "heritage"},
    "cultural_show": {"name": "Kandyan Cultural Dance Show", "fee_usd": 6, "category": "culture"},
    "peradeniya": {"name": "Peradeniya Botanical Garden", "fee_usd": 10, "category": "nature"},
    "haggala": {"name": "Haggala Botanical Garden", "fee_usd": 10, "category": "nature"},
    "minneriya": {"name": "Minneriya National Park", "fee_usd": 18, "category": "wildlife"},
    "yala": {"name": "Yala National Park", "fee_usd": 18, "category": "wildlife"},
    "village_tour": {"name": "Traditional Village Tour", "fee_usd": 18, "category": "culture"},
}

# ─────────────────────────────────────────────────────────────
# TOUR ITINERARY — Glimpses of Ceylon (14 Days / 13 Nights)
# ─────────────────────────────────────────────────────────────
ITINERARY = [
    {"day": 1, "location": "Negombo", "hotel": "arie_lagoon", "highlights": ["Airport pickup", "Beach relaxation", "Sunset walk"], "meal": "HB"},
    {"day": 2, "location": "Anuradhapura", "hotel": "alakamanda", "highlights": ["Sri Maha Bodhi", "Ruwanwelisaya", "Samadhi Buddha", "Isurumuniya Temple"], "meal": "HB", "attractions": ["anuradhapura", "mihintale", "isurumuniya"]},
    {"day": 3, "location": "Habarana", "hotel": "cinnamon_village", "highlights": ["Sigiriya Rock Fortress", "Minneriya Safari"], "meal": "HB", "attractions": ["sigiriya", "minneriya"]},
    {"day": 4, "location": "Habarana", "hotel": "cinnamon_village", "highlights": ["Polonnaruwa Ancient City", "Village Tour"], "meal": "HB", "attractions": ["polonnaruwa", "village_tour"]},
    {"day": 5, "location": "Kandy", "hotel": "cinnamon_citadel", "highlights": ["Dambulla Cave Temple", "Spice Garden", "Kandy Lake"], "meal": "HB", "attractions": ["dambulla_cave"]},
    {"day": 6, "location": "Kandy", "hotel": "cinnamon_citadel", "highlights": ["Temple of Tooth Relic", "Kandy City Tour", "Cultural Dance Show"], "meal": "HB", "attractions": ["tooth_temple", "cultural_show", "peradeniya"]},
    {"day": 7, "location": "Ella", "hotel": "ekho_ella", "highlights": ["Tea Plantation Tour", "Haggala Garden", "Scenic Train Ride"], "meal": "HB", "attractions": ["haggala"]},
    {"day": 8, "location": "Ella", "hotel": "ekho_ella", "highlights": ["Little Adam's Peak", "Nine Arch Bridge", "Ella Rock", "Ravana Falls"], "meal": "HB"},
    {"day": 9, "location": "Yala", "hotel": "cinnamon_wild", "highlights": ["Yala Afternoon Safari"], "meal": "HB", "attractions": ["yala"]},
    {"day": 10, "location": "Yala", "hotel": "cinnamon_wild", "highlights": ["Yala Full Day Safari"], "meal": "HB", "attractions": ["yala"]},
    {"day": 11, "location": "Beruwala", "hotel": "cinnamon_bey", "highlights": ["Beach relaxation", "Sunset", "Seafood dinner"], "meal": "HB"},
    {"day": 12, "location": "Beruwala", "hotel": "cinnamon_bey", "highlights": ["Turtle Hatchery", "Madu River Safari", "Brief Garden"], "meal": "HB"},
    {"day": 13, "location": "Colombo", "hotel": "ozo_colombo", "highlights": ["Colombo City Tour", "Pettah Bazaar", "Galle Face Green"], "meal": "HB"},
    {"day": 14, "location": "Colombo", "hotel": None, "highlights": ["Airport transfer", "Departure"], "meal": "BB"},
]

# ─────────────────────────────────────────────────────────────
# 2026 PRICING (Estimated — adjust with real hotel rates)
# ─────────────────────────────────────────────────────────────
TOUR_PRICING = {
    "name": "Glimpses of Ceylon",
    "duration": "14 Days / 13 Nights",
    "valid_until": "2026-12-31",
    "meal_plan": "HB (Breakfast + Dinner)",
    "currency": "USD",
    "rates": {
        "per_person_double": {
            2: 2490,    # 2 pax
            4: 2190,    # 4 pax
            6: 2090,    # 6 pax
            10: 1990,   # 10 pax
        },
        "single_supplement": 1590,
        "triple_reduction": 190,
        "child_with_bed": 890,
        "child_no_bed": 550,
    },
    "peak_season_supplement_per_night": 45,  # Dec 15 - Jan 15
    "shoulder_season_supplement_per_night": 25,  # Jan 16 - Mar 31
    "inclusions": [
        "13 nights accommodation in standard rooms on HB basis",
        "Air-conditioned private vehicle throughout",
        "English-speaking chauffeur guide",
        "All airport transfers",
        "City tours as per itinerary",
        "500ml x 2 mineral water per person per day",
        "All applicable taxes",
    ],
    "exclusions": [
        "Entrance fees to monuments and national parks",
        "Safari jeep charges",
        "Alcoholic beverages",
        "Personal expenses (laundry, tips, phone)",
        "Visa fees",
        "Travel insurance",
    ],
}


# ─────────────────────────────────────────────────────────────
# SAMPLE INQUIRY FOR TEST RUN
# ─────────────────────────────────────────────────────────────
SAMPLE_INQUIRY = {
    "source": "whatsapp",
    "contact_name": "Alexei Petrov",
    "contact_phone": "+7 916 123-4567",
    "contact_email": "alexei.petrov@example.com",
    "language": "ru",
    "intent": {
        "pax": 2,
        "dates": ["2026-12-15", "2026-12-25"],
        "budget_usd": 5000,
        "interests": ["wildlife", "culture", "beach", "ayurveda"],
        "message": "Hi! We are a couple from Moscow looking for a 10-12 day tour of Sri Lanka in December. We love wildlife, culture, and beaches. Also interested in Ayurveda. Budget around $5000 for everything.",
    },
}
