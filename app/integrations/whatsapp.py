"""
WhatsApp Webhook Handler — Twilio Integration
"""
from app.core.config import settings
from fastapi import APIRouter, Request
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

# In-memory conversation store (replace with Redis/DB in production)
conversations: dict[str, list[dict]] = {}

# Auto-replies for common inquiries
AUTO_REPLIES = {
    "en": {
        "hi": "Hello! 🇱🇰 Welcome to Ceyloria Holidays! I'm your AI travel concierge. How can I help you plan your Sri Lanka trip?",
        "hello": "Hello! 🇱🇰 Welcome to Ceyloria Holidays! I'm your AI travel concierge. How can I help you plan your Sri Lanka trip?",
        "price": "Our 14-day 'Glimpses of Ceylon' tour starts at $2,490 per person for 2 travelers (all-inclusive). Would you like a detailed itinerary?",
        "tour": "Our signature tour is 'Glimpses of Ceylon' — 14 days covering Negombo, Anuradhapura, Sigiriya, Kandy, Ella, Yala, Beruwala, and Colombo. Includes premium hotels, all transfers, and expert guides.",
        "ayurveda": "Yes! We offer personalized Ayurveda wellness add-ons in partnership with BIMARI Naviina. Treatments include Abhyanga massage ($180), Shirodhara ($160), Yoga ($150), and herbal steam baths ($90). Complete package: $580/person.",
        "default": "Thank you for your message! I can help you with:\n\n🏛️ Tour inquiries & itineraries\n💰 Pricing & availability\n🌿 Ayurveda wellness packages\n📋 Booking & payments\n\nWhat would you like to know?"
    },
    "ru": {
        "hi": "Здравствуйте! 🇱🇰 Добро пожаловать в Ceyloria Holidays! Я ваш AI-консьерж. Чем могу помочь в планировании поездки на Шри-Ланку?",
        "hello": "Здравствуйте! 🇱🇰 Добро пожаловать в Ceyloria Holidays! Я ваш AI-консьерж. Чем могу помочь в планировании поездки на Шри-Ланку?",
        "price": "Наш 14-дневный тур 'Проблески Цейлона' начинается от $2,490 на человека (для двоих). Желаете получить детальный маршрут?",
        "default": "Спасибо за ваше сообщение! Я могу помочь с:\n\n🏛️ Информация о турах\n💰 Цены и наличие\n🌿 Аюрведа оздоровление\n📋 Бронирование\n\nЧто вас интересует?"  # noqa: RUF001
    }
}


def get_auto_reply(message: str, lang: str = "en") -> str:
    """Simple keyword-based auto-reply"""
    msg_lower = message.lower().strip()
    replies = AUTO_REPLIES.get(lang, AUTO_REPLIES["en"])

    # Check keywords
    for keyword in ["hi", "hello", "привет", "здравствуйте"]:
        if keyword in msg_lower:
            return replies.get("hi", replies["default"])
    if any(w in msg_lower for w in ["price", "cost", "price", "сколько", "цена"]):
        return replies.get("price", replies["default"])
    if any(w in msg_lower for w in ["tour", "trip", "itinerary", "тур", "путешествие"]):
        return replies.get("tour", replies["default"])
    if any(w in msg_lower for w in ["ayurveda", "wellness", "massage", "аюрведа"]):
        return replies["ayurveda"]

    return replies["default"]


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> str:
    """Handle incoming WhatsApp messages from Twilio"""
    form = await request.form()
    form.get("From", "unknown")
    body = form.get("Body", "")
    form.get("ProfileName", "Traveler")

    # Detect language (use profile name or message content as hint)
    # Russian characters detected
    has_cyrillic = any(ord(c) > 1024 for c in body)
    lang = "ru" if has_cyrillic else "en"

    # Build response
    reply = get_auto_reply(body, lang)

    resp = MessagingResponse()
    resp.message(f"*Ceyloria Holidays* 🇱🇰\n\n{reply}")

    return str(resp)


@router.get("/whatsapp")
async def whatsapp_verify(request: Request) -> str:
    """Twilio webhook verification (GET request)"""
    query = request.query_params
    hub_mode = query.get("hub.mode")
    hub_challenge = query.get("hub.challenge")
    hub_token = query.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_token == settings.META_VERIFY_TOKEN:
        return hub_challenge
    return "Verification failed"
