"""
Real LLM Chat Engine — powers the Ceyloria widget with genuine AI via OpenRouter free models.
Knowledge base: real tour data from data/tour_data.py
"""

import asyncio

import httpx
from app.core.config import settings
from app.integrations.tour_pricing import quote_table
from data.tour_data import ATTRACTIONS, HOTELS, ITINERARY, TOUR_PRICING


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE — built from real tour data
# ─────────────────────────────────────────────────────────────
def build_knowledge_base() -> str:
    """Serialize real tour data into a compact prompt block."""
    lines = []
    lines.append(f"TOUR: {TOUR_PRICING['name']} — {TOUR_PRICING['duration']} (valid until {TOUR_PRICING['valid_until']})")
    lines.append(f"MEAL PLAN: {TOUR_PRICING['meal_plan']}")
    lines.append("PRICING (USD per person, double occupancy):")
    for pax, rate in sorted(TOUR_PRICING["rates"]["per_person_double"].items()):
        lines.append(f"  - {pax} travelers: ${rate:,}")
    lines.append(f"  - Single supplement: ${TOUR_PRICING['rates']['single_supplement']:,}")
    lines.append(f"  - Child with bed: ${TOUR_PRICING['rates']['child_with_bed']:,}")
    lines.append(f"  - Child no bed: ${TOUR_PRICING['rates']['child_no_bed']:,}")
    lines.append(f"PEAK SUPPLEMENT: +${TOUR_PRICING['peak_season_supplement_per_night']}/night (Dec 15 - Jan 15)")
    lines.append(f"SHOULDER SUPPLEMENT: +${TOUR_PRICING['shoulder_season_supplement_per_night']}/night (Jan 16 - Mar 31)")
    lines.append("INCLUDED: " + "; ".join(TOUR_PRICING["inclusions"]))
    lines.append("NOT INCLUDED: " + "; ".join(TOUR_PRICING["exclusions"]))
    lines.append("")
    lines.append("ITINERARY (day by day):")
    for day in ITINERARY:
        hotel_name = HOTELS[day["hotel"]]["name"] if day["hotel"] else "Departure"
        highlights = ", ".join(day["highlights"])
        attrs = ""
        if "attractions" in day:
            names = [ATTRACTIONS[a]["name"] for a in day["attractions"] if a in ATTRACTIONS]
            fees = sum(ATTRACTIONS[a]["fee_usd"] for a in day["attractions"] if a in ATTRACTIONS)
            if names:
                attrs = f" | Attractions: {', '.join(names)} (est. fees ${fees}/pp)"
        lines.append(f"  Day {day['day']}: {day['location']} — {hotel_name} ({day['meal']}) — {highlights}{attrs}")
    lines.append("")
    lines.append("HOTELS:")
    for _key, h in HOTELS.items():
        lines.append(
            f"  {h['name']} ({h['category']}, {h['location']}): "
            f"standard ${h['room_types']['standard']}/night, deluxe ${h['room_types']['deluxe']}/night, "
            f"HB +${h['meal_rates']['hb']}, FB +${h['meal_rates']['fb']}, AI +${h['meal_rates']['ai']}"
        )
    lines.append("")
    lines.append("ATTRACTIONS & ENTRANCE FEES (USD):")
    for _key, a in ATTRACTIONS.items():
        lines.append(f"  {a['name']}: ${a['fee_usd']} ({a['category']})")
    lines.append("")
    lines.append("AYURVEDA WELLNESS (BIMARI Naviina partnership):")
    lines.append("  Abhyanga massage $180 | Shirodhara $160 | Yoga & meditation $150 | Herbal steam bath $90 | Complete package $580/pp (incl. doctor consultation)")
    lines.append("")
    lines.append(quote_table())
    lines.append("")
    lines.append("CONTACT: WhatsApp +94 77 123 4567, email hello@ceyloriaholidays.com")
    return "\n".join(lines)


SYSTEM_PROMPT = """You are Anuki, the Front Office Concierge of Ceyloria Holidays — a premium Sri Lanka tour operator based in Colombo. You are the warm, professional first point of contact for every traveler who reaches out.

YOUR PERSONA:
- You are a real, warm human professional — a well-trained front office executive who has welcomed hundreds of travelers to Sri Lanka.
- You speak like a person: natural, gracious, and genuinely helpful. You use polite hospitality language ("We'd be delighted to...", "May I suggest...", "Certainly!").
- You NEVER sound robotic, scripted, or corporate. No bullet-point dumps unless the guest explicitly asks for a breakdown.
- You are proud of Sri Lanka and Ceyloria Holidays, and it shows — subtly, warmly.
- You handle upset or confused guests with calm, gracious professionalism.

ABSOLUTE RULES:
- NEVER reveal internal thoughts, analysis, or reasoning. NEVER narrate the conversation ("the user is asking...", "let me unpack...", "first, looking at the history..."). Speak ONLY the words you would say aloud to a guest standing in front of you.
- If a guest's message is garbled, confusing, or unclear — STOP and ask a small clarifying question in plain, friendly words. NEVER guess or assume what they meant.
- One short reply at a time. Never lecture, never repeat, never dump information.
- OUTPUT FORMAT — STRICT JSON: Respond with ONLY a single JSON object, nothing else: {{"reply": "your spoken words here"}}. The "reply" value is exactly what you would say aloud to the guest — no analysis, no notes, no labels, no thinking. Example: {{"reply": "Good afternoon! How many travelers shall I plan for?"}}

HOW TO CONVERSE:
1. Greet warmly and personally. If it's the first message, welcome them to Ceyloria Holidays.
2. Use ONLY the tour knowledge provided below. Never invent prices, hotels, or attractions not listed. If unsure, say you'll confirm with the team and follow up.
3. Answer in the SAME LANGUAGE the guest uses (Russian → Russian, German → German, etc.). Keep the same warmth in any language.
4. For group sizes not listed (e.g. 3 or 5), use the nearest tier and offer a custom quote — "I'll have our team prepare a tailored rate for your group."
5. Mention peak/shoulder supplements when a date is discussed — gently, as a helpful tip, not a warning.
6. For booking/quote requests, collect details naturally — travel dates, number of travelers, room preference, special occasions — one or two questions at a time, like a real conversation. Note honeymoons, anniversaries, birthdays and respond warmly.
7. CRITICAL — BE CONCISE: reply in 2-4 short sentences (max ~70 words) unless the guest explicitly asks for a full day-by-day itinerary or a complete breakdown. Never start a list you cannot finish. Never repeat what was already said. Ask ONE clear question at a time to move the conversation forward.
8. CLARIFY WHEN UNCLEAR — ALWAYS: whenever the guest's message is unclear, incomplete, ambiguous, garbled, very short, or missing key details (dates, number of travelers, preferences), STOP and ask ONE small clarifying question first. Never guess, never dump details prematurely. Examples: "I'd love to help! How many travelers should I plan for?" · "Could you tell me your preferred travel dates?" · "I didn't quite catch that — could you say it once more?" · "Just to make sure — are you thinking of the 14-day tour?" If you cannot understand at all, apologise warmly and ask them to repeat.
9. Never mention that you are an AI, a bot, or that you follow rules.
10. CUSTOM TOURS — IMPORTANT: If the guest asks for a tour of a different length (e.g. 7 days, 10 days, 5 days) or a customized itinerary, DO NOT invent prices. Use the CUSTOM TOUR QUOTES table below (exact USD per person for 5/7/10/14 days x 2/4/6 pax). Quote the closest match with confidence: "A 7-day version would be $1,261 per person for two travelers (double occupancy, HB)." For other durations or group sizes, say: "I can certainly tailor that for you — allow me a moment to prepare an exact quote," and offer to have the team confirm. You may suggest the popular 7-day highlights (Sigiriya, Kandy, Ella, beach) or 10-day version.

TOUR KNOWLEDGE:
{knowledge}"""


# In-process conversation memory per session lives in chat_widget/router.py


# ─────────────────────────────────────────────────────────────
# REASONING STRIPPER — removes any internal monologue the model
# leaks (e.g. "Okay, the user is asking...", "Let me unpack...")
# so the guest only ever sees the spoken reply.
# ─────────────────────────────────────────────────────────────
_REASONING_MARKERS = (
    "the user is asking", "the user just asked", "let me unpack", "looking back",
    "looking at the history", "looking at the context", "okay, the user", "okay, the guest",
    "hmm, this seems", "hmm, this looks", "first, looking", "unpack this", "their core need",
    "the guest seems", "the user seems", "constraints from my persona", "important constraints",
    "based on the history", "now it's clearer", "now they're asking", "they might be trying",
    "their earlier", "as per protocol", "i need to follow", "i should", "i must",
    "probably meant", "maybe autocorrect", "likely a typo", "might be a typo",
    "the user probably", "the guest probably", "my persona", "the rules", "the context,",
    "i'm anuki", "i am anuki", "let me think", "i'll ask", "i will ask", "so i",
    "this seems like", "that doesn't make sense in", "in the context of",
    "looking at this", "after that confusing", "now it's clearer", "their core",
    "the tour knowledge", "the knowledge provided", "given the history",
)


def _strip_reasoning(text: str) -> str:
    """Remove internal-reasoning monologue so only the spoken reply reaches the guest.

    Strategy: reasoning blocks come FIRST, the real reply LAST. We split into
    paragraphs/lines, drop anything that reads like analysis, and keep the tail.
    """
    if not text:
        return text

    # Normalize: split on blank lines (paragraphs) first, then lines
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return text

    def looks_like_reasoning(block: str) -> bool:
        low = block.lower()
        return (
            any(m in low for m in _REASONING_MARKERS)
            or low.startswith(("okay,", "hmm,", "now,", "first,", "so,", "looking", "the user", "the guest", "i need", "i should", "based on"))
        )

    # Find the LAST paragraph that does NOT look like reasoning
    kept = [p for p in paragraphs if not looks_like_reasoning(p)]
    if kept:
        return "\n".join(kept).strip()[:600]

    # All paragraphs look like reasoning — take the final sentence fragment
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    return (sentences[-1] if sentences else text)[:600]


def _extract_reply(text: str) -> str:
    """Extract the spoken reply. Priority: JSON {"reply": ...} → <reply> tags → stripper."""
    if not text:
        return text
    import json
    import re

    # 1) Try strict JSON object with "reply" key
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get("reply"):
            return str(obj["reply"]).strip()[:600]
    except Exception:
        pass

    # 2) Truncated JSON (model ran out of tokens): find "reply": "..." even without closing brace
    m = re.search(r'"reply"\s*:\s*"((?:[^"\\]|\\.)*)', text, re.DOTALL)
    if m:
        return m.group(1).strip()[:600]

    # 3) Some models wrap JSON in code fences or add prose around it — find the object
    m = re.search(r"\{[^{}]*\"reply\"\s*:\s*\"(.*?)\"[^{}]*\}", text, re.DOTALL)
    if m:
        return m.group(1).strip()[:600]

    # 4) Try <reply> tags
    m = re.search(r"<reply>(.*?)</reply>", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()[:600]

    # 5) Fallback: remove reasoning monologue
    return _strip_reasoning(text)


# ─────────────────────────────────────────────────────────────
# LLM ENGINE
# ─────────────────────────────────────────────────────────────
class LLMChatEngine:
    """Chat engine backed by OpenCode Zen (primary) with OpenRouter fallback."""

    def __init__(self):
        self.zen_url = settings.ZEN_BASE_URL or "https://opencode.ai/zen/v1"
        self.zen_model = settings.ZEN_MODEL or "deepseek-v4-flash-free"
        self.or_url = settings.OPENROUTER_BASE_URL or "https://openrouter.ai/api/v1"
        self.or_model = settings.OPENROUTER_MODEL or "deepseek-v4-flash-free"
        self.knowledge = build_knowledge_base()
        self.system = SYSTEM_PROMPT.format(knowledge=self.knowledge)

    async def chat(
        self,
        message: str,
        _language: str = "en",
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Send message to the LLM with tour knowledge + conversation history.

        Primary: OpenCode Zen (free deepseek-v4-flash-free).
        Fallback: OpenRouter (same model family). Returns a clean spoken reply.
        """
        # Build conversation messages: system + history + current
        messages = [{"role": "system", "content": self.system}]
        if history:
            for turn in history[-6:]:  # keep last 6 turns of context
                if turn.get("role") in ("user", "assistant") and turn.get("content"):
                    messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.zen_model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 2000,
            "top_p": 0.9,
            # NOTE: no response_format — Zen's json_object mode causes ~25% empty
            # replies on reasoning models; the system prompt demands JSON and
            # _extract_reply() parses it robustly (incl. truncated JSON).
        }

        # 1) Primary: OpenCode Zen — retry on empty/failed replies (free tier is flaky)
        if settings.ZEN_API_KEY:
            for attempt in range(3):
                result = await self._call_provider(
                    f"{self.zen_url}/chat/completions",
                    payload,
                    settings.ZEN_API_KEY,
                )
                if result and result.strip():
                    return result
                await asyncio.sleep(0.8 * (attempt + 1))

        # 2) Fallback: OpenRouter
        if settings.OPENROUTER_API_KEY:
            or_payload = {**payload, "model": self.or_model}
            result = await self._call_provider(
                f"{self.or_url}/chat/completions",
                or_payload,
                settings.OPENROUTER_API_KEY,
                extra_headers={
                    "HTTP-Referer": "https://ceyloria-site.vercel.app",
                    "X-Title": "Ceyloria Holidays Concierge",
                },
            )
            if result and result.strip():
                return result

        return "Sorry, I'm having trouble connecting right now. Please try again."

    async def _call_provider(
        self,
        url: str,
        payload: dict,
        api_key: str,
        extra_headers: dict | None = None,
    ) -> str | None:
        """POST to a provider; return the extracted reply or None on any failure."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    raw = data["choices"][0]["message"]["content"].strip()
                    return _extract_reply(raw)
                return None
        except Exception:
            return None


# Singleton engine (lazy init to avoid building KB at import)
_ENGINES: dict[str, "LLMChatEngine"] = {}


def get_engine() -> "LLMChatEngine":
    if "default" not in _ENGINES:
        _ENGINES["default"] = LLMChatEngine()
    return _ENGINES["default"]
