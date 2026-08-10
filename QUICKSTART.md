# LankaAgent - Quick Start Guide for New Session

> **⚡ REVENUE-FIRST:** this project earns money. See [REVENUE-PLAN.md](REVENUE-PLAN.md) for the full money model (9 streams, costs, projections, targets) — every feature must pass the Revenue Filter (DEC-20260810-001). **Money-linked milestones:** first booking this week → 3 pilots / $3K MRR by M2 → $70K MRR by M12.

## 🚀 Quick Start (5 minutes)

### 1. Start Services
```bash
cd /c/Users/nishanthap/lankaagent
docker compose up -d api postgres redis
```

### 2. Verify Services
```bash
# Check API health
curl https://cycling-handwash-oversweet.ngrok-free.dev/health/ready

# Check widget
open https://cycling-handwash-oversweet.ngrok-free.dev/widget/embed

# Test widget chat API
curl -X POST "https://cycling-handwash-oversweet.ngrok-free.dev/widget/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "language": "en", "session_id": "test_123"}'
```

### 3. Run Tests
```bash
docker exec lankaagent-api python -m pytest tests/test_api.py tests/test_tour_pricing.py -v --tb=no
```

---

## 🌐 Live Endpoints (ngrok)

| Service | URL | Status |
|---------|-----|--------|
| **Widget Embed** | `https://cycling-handwash-oversweet.ngrok-free.dev/widget/embed` | ✅ Live |
| **Widget Chat API** | `POST https://cycling-handwash-oversweet.ngrok-free.dev/widget/chat` | ✅ Working |
| **Voice TTS** | `GET https://cycling-handwash-oversweet.ngrok-free.dev/widget/tts?text=...&language=en` | ✅ Edge neural voices |
| **Voice STT** | `POST https://cycling-handwash-oversweet.ngrok-free.dev/widget/stt?language=en` (raw audio body) | ✅ Whisper |
| **WhatsApp Webhook** | `https://cycling-handwash-oversweet.ngrok-free.dev/webhook/whatsapp` | ✅ Twilio verified |
| **API Docs** | `https://cycling-handwash-oversweet.ngrok-free.dev/docs` | ✅ Live |
| **Health Check** | `https://cycling-handwash-oversweet.ngrok-free.dev/health/ready` | ✅ Healthy |

---

## 🤖 AI Provider (OpenCode Zen — primary)

The concierge runs on **OpenCode Zen** free models (same as Hermes chat), with OpenRouter as automatic fallback.

| Setting | Value |
|---------|-------|
| Provider | `ZEN_BASE_URL=https://opencode.ai/zen/v1` |
| Model | `ZEN_MODEL=deepseek-v4-flash-free` (free tier) |
| Fallback | `OPENROUTER_MODEL=deepseek-v4-flash-free` via OpenRouter |
| Reply format | Strict JSON `{"reply": "..."}` — internal reasoning stripped server-side |

**Env vars** (in `.env`, passed via docker-compose):
```
ZEN_API_KEY=sk-...          # from ~/AppData/Local/hermes/.env (OPENCODE_ZEN_API_KEY)
ZEN_BASE_URL=https://opencode.ai/zen/v1
ZEN_MODEL=deepseek-v4-flash-free
OPENROUTER_API_KEY=sk-or-...
```

**Why:** OpenRouter free tier has a daily rate limit (50 free requests/day). Zen free tier is more generous and powers this very chat session.

---

## 📱 WhatsApp Testing (Critical)

### Twilio Sandbox Setup
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-sandbox
2. Set webhook URL: `https://cycling-handwash-oversweet.ngrok-free.dev/webhook/whatsapp`
3. Method: POST
4. Click **Save**

### Test WhatsApp
1. Send join code (e.g., `join liquid-mix`) to `+1 415 523 8886` on WhatsApp
2. Wait for confirmation
3. Send `hello` → Get AI response
4. Send `привет` → Get Russian response

---

## 🤖 AI Chat Endpoints

### Widget Chat API
```
POST https://cycling-handwash-oversweet.ngrok-free.dev/widget/chat
Content-Type: application/json

{
  "message": "I want to book a tour",
  "language": "en",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "response": "Our signature tour is 'Glimpses of Ceylon'...",
  "language": "en"
}
```

**Supported Languages:** `en`, `ru`, `de`, `fr`, `zh`, `si`, `ta`

---

## 🎙 Voice Endpoints

### Text-to-Speech (Anuki speaks)
```
GET https://cycling-handwash-oversweet.ngrok-free.dev/widget/tts?text=Hello&language=en
```
Returns MP3 audio (Microsoft Edge neural voices: EN=Jenny, RU=Svetlana, DE=Katja, FR=Denise, ZH=Xiaoxiao, SI=Sameera, TA=Pallavi).

### Speech-to-Text (guest speaks)
```
POST https://cycling-handwash-oversweet.ngrok-free.dev/widget/stt?language=en
Content-Type: audio/webm   (raw bytes, NOT multipart!)
```
Body: raw audio bytes (webm/mp3/wav). Response: `{"text": "...", "confidence": ..., "clear": true}`.

> ⚠️ **STT contract:** send RAW audio bytes in the request body. Multipart FormData fails with "Invalid data". First call downloads ~75MB Whisper model, then cached.

---

## 🧮 Custom Tour Pricing

Anuki quotes **custom-length tours** (5/7/10/14 days) with exact USD prices computed by `app/integrations/tour_pricing.py` from real hotel data:

| Days | 2 pax | 4 pax | 6 pax |
|------|-------|-------|-------|
| 5 | $901 | $662 | $613 |
| 7 | $1,261 | $934 | $869 |
| 10 | $1,830 | $1,370 | $1,279 |
| 14 | $2,491 | $1,855 | $1,731 |

- 14-day/2-pax calibrated to exactly match the catalog $2,490/pp
- Other durations/pax: LLM offers "let me prepare an exact quote" (team confirms)
- Test: `python3 -c "from app.integrations.tour_pricing import quote_table; print(quote_table())"`

---

## 📱 Widget Embed Code

Add to any website:
```html
<script>
  (function() {
    var script = document.createElement('script');
    script.src = 'https://cycling-handwash-oversweet.ngrok-free.dev/widget/embed.js';
    script.async = true;
    document.head.appendChild(script);
  })();
</script>
```

Or embed directly:
```html
<iframe src="https://cycling-handwash-oversweet.ngrok-free.dev/widget/embed" 
        style="width:100%; height:600px; border:none;"></iframe>
```

---

## 🧪 Testing Commands

```bash
# Run all tests
docker exec lankaagent-api python -m pytest tests/test_api.py -v --tb=no

# Test specific endpoint
curl -X POST "https://cycling-handwash-oversweet.ngrok-free.dev/widget/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "language": "en", "session_id": "test_123"}'

# Test WhatsApp webhook
curl -X POST "https://cycling-handwash-oversweet.ngrok-free.dev/webhook/whatsapp" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+19379152975&Body=hello&ProfileName=TestUser"

# Check health
curl https://cycling-handwash-oversweet.ngrok-free.dev/health/ready
```

---

## 🔧 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Widget shows "undefined" | Check `apiBase` in widget JS is `/widget` not `/api/v1/widget` |
| ngrok tunnel down | Restart ngrok: `python3 -c "from pyngrok import ngrok; conf.get_default().auth_token = '...'; ngrok.connect(8000, bind_tls=True)"` |
| Twilio webhook fails | Verify webhook URL in Twilio Console matches ngrok URL |
| Tests fail | Run `docker cp /c/Users/nishanthap/lankaagent/tests lankaagent-api:/app/tests` then `docker exec lankaagent-api python -m pytest tests/test_api.py tests/test_tour_pricing.py -v` |
| Database errors | `docker compose down -v && docker compose up -d postgres redis` then `docker exec lankaagent-api python -m data.seed` |
| STT returns "Invalid data" | Client sent multipart — must send RAW audio bytes as body |
| Voice input: "Microphone access denied" | Test in Chrome/Edge (not embedded preview). Click 🔒 in address bar → Site settings → Microphone → Allow → reload |
| LLM rate-limited | Check ZEN_API_KEY is set; Zen is primary, OpenRouter fallback only |
| Chat replies show thinking text | Shouldn't happen — `_strip_reasoning` + JSON extraction in llm_chat.py; if it recurs, check model in use |

---

## 📋 Pilot Launch Checklist

- [ ] Send 3 outreach messages (BIMARI, SLTDA, Ceyloria Partner)
- [ ] Confirm Twilio sandbox webhook URL saved
- [ ] Test WhatsApp from personal phone
- [ ] Test widget embed on test page
- [ ] Verify Russian/English responses work
- [ ] Schedule pilot onboarding calls

---

## 📞 Key Contacts

| Role | Contact | Purpose |
|------|---------|---------|
| **Chairman** | Nishantha Priyadarshana | Business decisions, approvals |
| **Wife (BIMARI)** | Ayurveda network | Wellness pilot contacts |
| **SLTDA Contact** | ICT Department | Operator registry, licensing |
| **Twilio Support** | Console > Support | Webhook issues |
| **ngrok Dashboard** | https://dashboard.ngrok.com | Tunnel management |

---

## 📂 Key Files Reference

| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup, architecture |
| `SPEC.md` | Product specification, pricing, roadmap |
| `ARCHITECTURE.md` | Technical architecture, ADRs |
| `GOVERNANCE.md` | Operating model, roles, decisions |
| `SPEC.md` | Product spec, pricing, ICP |
| `PILOT-OUTREACH.md` | Outreach templates for pilots |
| `SPEC.md` | Product specification |
| `SPEC.md` | Product specification |
| `docker-compose.yml` | Local development stack |
| `.env.example` | Environment template |
| `Makefile` | Common commands |
| `.env.example` | Environment template |

---

## 🚀 Tomorrow's Quick Start (Copy-Paste)

```bash
# 1. Navigate to project
cd /c/Users/nishanthap/lankaagent

# 2. Start services
docker compose up -d api postgres redis

# 2. Start ngrok (in separate terminal)
python3 -c "
from pyngrok import ngrok, conf
conf.get_default().auth_token = '<NGROK_AUTH_TOKEN_FROM_DASHBOARD>'
tunnel = ngrok.connect(8000, bind_tls=True)
print('NGROK_URL:', tunnel.public_url)
import time
while True: time.sleep(60)
"

# 3. Update Twilio webhook to new ngrok URL
# 2. Test widget: open https://<ngrok-url>/widget/embed
# 3. Send outreach messages
```

---

**Last Updated:** 2026-08-10  
**Status:** ✅ All systems operational (Zen LLM + voice + custom pricing live)  
**Next Session:** Pilot outreach & onboarding