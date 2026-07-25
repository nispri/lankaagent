"""
Ceyloria Holidays — Database Seed Script
Run: docker compose exec api python data/seed.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta

from app.core.database import Base, async_session_factory, engine
from app.core.models import (
    Booking,
    Conversation,
    Itinerary,
    Lead,
    Message,
    Tenant,
    User,
    WellnessProtocol,
)
from data.tour_data import ATTRACTIONS, HOTELS, ITINERARY, SAMPLE_INQUIRY, TOUR_PRICING


async def seed() -> None:
    """Seed database with Ceyloria Holidays data"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # 1. Create Ceyloria Holidays tenant
        tenant = Tenant(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            name="Ceyloria Holidays",
            slug="ceyloria-holidays",
            plan="enterprise",
            settings={
                "brand_name": "Ceyloria Holidays",
                "tagline": "Glimpses of Ceylon",
                "currency": "USD",
                "languages": ["en", "ru", "de", "fr", "zh", "si", "ta"],
                "whatsapp_number": "+94 77 123 4567",
                "website": "https://ceyloriaholidays.com",
                "tours": TOUR_PRICING,
                "hotels": HOTELS,
                "attractions": ATTRACTIONS,
                "itinerary": ITINERARY,
            },
        )
        session.add(tenant)
        await session.flush()

        # 2. Create admin user
        user = User(
            id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            tenant_id=tenant.id,
            email="nishantha.priyadarshana@gmail.com",
            password_hash="",
            full_name="Nishantha Priyadarshana",
            role="owner",
        )
        session.add(user)
        await session.flush()

        # 3. Create a sample lead (inquiry)
        lead = Lead(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            tenant_id=tenant.id,
            source=SAMPLE_INQUIRY["source"],
            contact_name=SAMPLE_INQUIRY["contact_name"],
            contact_phone=SAMPLE_INQUIRY["contact_phone"],
            contact_email=SAMPLE_INQUIRY["contact_email"],
            language=SAMPLE_INQUIRY["language"],
            status="new",
            intent=SAMPLE_INQUIRY["intent"],
        )
        session.add(lead)
        await session.flush()

        # 4. Create conversation with sample messages
        conversation = Conversation(
            id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
            tenant_id=tenant.id,
            lead_id=lead.id,
            channel="whatsapp",
            external_thread_id="whatsapp_thread_001",
            language="ru",
        )
        session.add(conversation)
        await session.flush()

        messages = [
            Message(
                conversation_id=conversation.id,
                role="user",
                content=SAMPLE_INQUIRY["intent"]["message"],
                created_at=datetime.utcnow() - timedelta(minutes=5),
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content="Привет! 🇱🇰 Спасибо за ваш запрос. Я подготовлю для вас индивидуальный маршрут по Шри-Ланке на 10-12 дней. У вас отличный выбор! Дикая природа, культурное наследие и пляжный отдых — идеальное сочетание.",  # noqa: RUF001
                created_at=datetime.utcnow() - timedelta(minutes=4),
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content="Я предлагаю вам наш тур \"Проблески Цейлона\" (14 дней/13 ночей) с возможностью сократить до 12 дней. Ориентировочная стоимость: $4,990 за двоих (все включено). Хотите увидеть детальный маршрут?",  # noqa: RUF001
                created_at=datetime.utcnow() - timedelta(minutes=3),
            ),
        ]
        for msg in messages:
            session.add(msg)
        await session.flush()

        # 5. Create an itinerary (quote)
        itinerary = Itinerary(
            id=uuid.UUID("55555555-5555-5555-5555-555555555555"),
            tenant_id=tenant.id,
            lead_id=lead.id,
            version=1,
            title="Glimpses of Ceylon — 14 Days Premium Tour",
            days=ITINERARY,
            total_price_usd=4990.00,
            currency="USD",
            status="draft",
            valid_until=datetime.utcnow() + timedelta(days=14),
            created_by=user.id,
        )
        session.add(itinerary)
        await session.flush()

        # 6. Create a confirmed booking
        booking = Booking(
            id=uuid.UUID("66666666-6666-6666-6666-666666666666"),
            tenant_id=tenant.id,
            lead_id=lead.id,
            itinerary_id=itinerary.id,
            booking_reference="CH-2026-0001",
            status="confirmed",
            travelers=[
                {"name": "Alexei Petrov", "passport": "72XXXXXX", "nationality": "RU", "dob": "1985-03-15"},
                {"name": "Elena Petrova", "passport": "72XXXXXX", "nationality": "RU", "dob": "1987-08-22"},
            ],
            payment_status="paid",
            payment_intent_id="pi_test_demo_001",
            commission_usd=748.50,
            starts_at=datetime(2026, 12, 15).date(),
            ends_at=datetime(2026, 12, 28).date(),
        )
        session.add(booking)
        await session.flush()

        # 7. Create a wellness protocol (Ayurveda add-on)
        wellness = WellnessProtocol(
            id=uuid.UUID("77777777-7777-7777-7777-777777777777"),
            tenant_id=tenant.id,
            lead_id=lead.id,
            health_intake={
                "conditions": ["stress", "fatigue"],
                "goals": ["relaxation", "detox"],
                "dietary_preferences": "vegetarian",
                "allergies": ["pollen"],
            },
            recommended_treatments=[
                {"name": "Abhyanga (Oil Massage)", "sessions": 3, "price_usd": 180},
                {"name": "Shirodhara", "sessions": 2, "price_usd": 160},
                {"name": "Yoga & Meditation", "sessions": 5, "price_usd": 150},
                {"name": "Herbal Steam Bath", "sessions": 3, "price_usd": 90},
            ],
            assigned_doctor_id=uuid.UUID("88888888-8888-8888-8888-888888888888"),
            status="accepted",
            total_price_usd=580.00,
        )
        session.add(wellness)
        await session.flush()

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
