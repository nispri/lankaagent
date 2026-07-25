# LankaAgent — Product Specification (SPEC.md)

**Version:** 1.0  
**Status:** Draft — Pending Chairman Approval  
**Owner:** Hermes (Chief of Staff)  
**Review Cycle:** Sprint 0 → Sprint 1 refinement

---

## 1. Vision & Strategy

### 1.1 One-Liner
**AI-powered 24/7 travel concierge for Sri Lanka tour operators — turns WhatsApp inquiries into confirmed bookings while they sleep.**

### 1.2 Problem Statement
- **2,000+ SLTDA-registered operators** lose 40-60% of leads to slow response (avg 4-12 hours)
- **No 24/7 multilingual support** — key markets (Russia, Germany, China, India, UK) inquire outside SL business hours
- **Manual itinerary building** takes 30-60 min per inquiry — not scalable
- **No integrated payment/booking** — operators chase payments via bank transfer screenshots
- **Wellness/Ayurveda upsell** ignored — wife's BIMARI network + Venuki's medical background = unique supply

### 1.3 Solution
**LankaAgent = WhatsApp/Web Widget → AI Agent (LangGraph) → Operator CRM + Payment + Booking Engine**

| User | Pain | LankaAgent Value |
|------|------|------------------|
| **Tour Operator** | Missed leads, manual work, no payments | 24/7 auto-quote, instant itinerary, collect payment, sync calendar |
| **Traveler (End Customer)** | Slow replies, language barrier, no instant booking | Instant reply (12 langs), live quote, pay now, visa/packing docs auto-sent |
| **Ayurveda/Wellness Center** | Empty rooms, no direct channel | Integrated upsell in itinerary, verified operator network |

### 1.4 Strategic Moats
1. **Domain Data** — SLTDA operator registry + attraction database + seasonal pricing (proprietary MCP server)
2. **Ayurveda Supply** — Wife's BIMARI Naviina network + medical credibility (Venuki) = exclusive wellness inventory
3. **WhatsApp-First Architecture** — Sri Lanka is WhatsApp-native; Meta Business API + Twilio = distribution
4. **Regulatory Trust** — SLTDA-compliant, TDL-integrated, local payment (PayHere/LankaPay)

---

## 2. Target Market & ICP

### 2.1 Primary ICP: "Growth-Minded Tour Operators"
| Criteria | Detail |
|----------|--------|
| **Size** | 5-50 guides, 10-200 bookings/month |
| **Tech Maturity** | Use WhatsApp Business, maybe Google Sheets, no CRM |
| **Pain** | Turning away night inquiries, losing to faster competitors |
| **Budget** | $100-500/mo (see pricing below) |
| **Location** | Colombo, Galle, Kandy, Sigiriya, Ella, Mirissa |
| **Language Need** | English + Russian/German/Chinese/French |

**Count:** ~500 operators in SLTDA registry fit this profile

### 2.2 Secondary ICP: "Wellness Resorts & Ayurveda Centers"
- 50+ SLTDA-licensed Ayurveda hotels
- Need: Direct booking, pre-arrival health intake, post-stay follow-up
- Price tolerance: $300-1,000/mo

### 2.3 Tertiary: "Freelance Guides / Micro-Operators"
- 1-4 guides, WhatsApp only
- Price: $49/mo (Starter)

---

## 3. Product Architecture

### 3.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LANKAAGENT PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  WHATSAPP    │    │   WEB WIDGET │    │   EMAIL      │    │  SLTDA   │  │
│  │  BUSINESS API│    │   (Embed)    │    │   (Forward)  │    │  REGISTRY│  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └────┬─────┘  │
│         │                   │                   │                 │        │
│         └───────────────────┼───────────────────┼─────────────────┘        │
│                             ▼                   ▼                          │
│                    ┌─────────────────────────────────────────┐             │
│                    │         API GATEWAY (FastAPI)           │             │
│                    │  Auth │ Rate Limit │ Router │ Webhooks   │             │
│                    └────────────────────┬────────────────────┘             │
│                                         │                                   │
│              ┌──────────────────────────┼──────────────────────────┐       │
│              ▼                          ▼                          ▼       │
│     ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐  │
│     │  TRAVEL AGENT   │      │  OPERATOR CRM   │      │  WELLNESS ENGINE│  │
│     │  (LangGraph)    │◄────►│  (Multi-tenant) │      │  (Ayurveda Match)│  │
│     │                 │      │                 │      │                 │  │
│     │ • Intent Parse  │      │ • Leads         │      │ • Health Intake │  │
│     │ • Itinerary Gen │      │ • Bookings      │      │ • Protocol Match│  │
│     │ • Quote Builder │      │ • Calendar      │      │ • Doctor Assign │  │
│     │ • Payment Flow  │      │ • Commissions   │      │ • Post-Care     │  │
│     │ • Multilingual  │      │ • Analytics     │      │                 │  │
│     └────────┬────────┘      └────────┬────────┘      └────────┬────────┘  │
│              │                        │                        │            │
│              └────────────────────────┼────────────────────────┘            │
│                                       ▼                                     │
│                          ┌─────────────────────────┐                        │
│                          │      DATA LAYER         │                        │
│                          │  PostgreSQL + Redis     │                        │
│                          │  (Multi-tenant RLS)     │                        │
│                          └───────────┬─────────────┘                        │
│                                      │                                      │
│              ┌───────────────────────┼───────────────────────┐             │
│              ▼                       ▼                       ▼             │
│     ┌───────────────┐      ┌───────────────┐      ┌───────────────┐       │
│     │  PAYMENTS     │      │  EXTERNAL     │      │  MCP SERVER   │       │
│     │  Stripe +     │      │  INTEGRATIONS │      │  (Tourism Data)│       │
│     │  PayHere      │      │  • Google Cal │      │  • SLTDA Stats│       │
│     │  (LKR/USD)    │      │  • WhatsApp   │      │  • Attractions│       │
│     │
```

### 3.2 Core Services

| Service | Tech | Responsibility |
|---------|------|----------------|
| **API Gateway** | FastAPI + Pydantic v2 | Auth (JWT), Rate limit, Request routing, Webhook verification |
| **Travel Agent** | LangGraph + LangChain | Conversation state, Intent classification, Itinerary generation, Quote building, Payment orchestration |
| **Operator CRM** | FastAPI + SQLAlchemy | Multi-tenant operator workspace: Leads, Bookings, Calendar, Commissions, Settings |
| **Wellness Engine** | Python + Rule Engine | Health intake → Protocol matching → Doctor assignment → Post-care scheduling |
| **Payments** | Stripe (Intl) + PayHere (LK) | Multi-currency, Split payments (operator commission), Refunds, Invoicing |
| **MCP Tourism Server** | FastMCP + SQLite/Postgres | SLTDA statistics, Attraction data, Seasonal pricing, Visa rules, Transport options |
| **Notifications** | Twilio (WhatsApp/SMS) + SendGrid | Transactional: Booking confirm, Payment receipt, Reminders, Visa docs |

### 3.3 Data Models (Core Entities)

```python
# Operator (Tenant)
Operator:
  id, name, slug, sltda_license, contact_email, phone, whatsapp_biz_id
  settings: {languages, currencies, commission_rate, branding, webhook_urls}
  subscription: {tier, status, stripe_customer_id, payhere_merchant_id}
  created_at, updated_at

# Lead (Inbound Inquiry)
Lead:
  id, operator_id, source (whatsapp/web/email), contact: {name, phone, email, language}
  status: new → qualified → quoted → booked → lost
  intent: {dates, pax, budget, interests, wellness_flag}
  conversation_id (LangGraph thread_id)
  assigned_guide_id, created_at, updated_at

# Itinerary / Quote
Itinerary:
  id, lead_id, operator_id, version, status: draft → sent → accepted → expired
  days: [{date, activities[], accommodation, transport, meals, wellness_options[]}]
  pricing: {base_usd, base_lkr, commission, taxes, total_usd, total_lkr, currency}
  valid_until, created_at, accepted_at

# Booking (Confirmed)
Booking:
  id, itinerary_id, operator_id, lead_id, status: confirmed → paid → completed → cancelled
  payment: {provider, intent_id, amount, currency, status, paid_at}
  travelers: [{name, passport, dob, nationality, dietary, medical_notes}]
  documents: {visa_letter, voucher, packing_list, wellness_intake_form}
  calendar_events: [google_calendar_ids]

# Wellness Protocol
WellnessProtocol:
  id, booking_id, intake: {conditions, goals, medications, allergies, preferences}
  matched_doctor_id, protocol: {treatments[], diet, yoga, meditation, duration}
  pre_arrival_notes, post_departure_followup_schedule
```

---

## 4. Agent Architecture (LangGraph)

### 4.1 State Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAVEL AGENT GRAPH                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [ENTRY] ──► CLASSIFY_INTENT ──► EXTRACT_ENTITIES ──►          │
│                                     │                            │
│                    ┌────────────────┼────────────────┐          │
│                    ▼                ▼                ▼          │
│             ┌────────────┐   ┌────────────┐   ┌────────────┐   │
│             │  GREETING  │   │  INQUIRY   │   │  BOOKING   │   │
│             │  (Small    │   │  (Itinerary│   │  (Payment  │   │
│             │   Talk)    │   │   + Quote) │   │   Flow)    │   │
│             └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   │
│                   │                │                │            │
│                   └────────────────┼────────────────┘            │
│                                    ▼                              │
│                          ┌─────────────────────┐                 │
│                          │   BUILD_ITINERARY   │                 │
│                          │  (MCP Tools + LLM)  │                 │
│                          └──────────┬──────────┘                 │
│                                    │                              │
│                          ┌─────────┴─────────┐                   │
│                          ▼                   ▼                   │
│                   ┌────────────┐      ┌────────────┐            │
│                   │  PRESENT   │      │  WELLNESS   │            │
│                   │  QUOTE     │      │  UPSSELL    │            │
│                   └─────┬──────┘      └─────┬──────┘            │
│                         │                   │                    │
│                         └─────────┬─────────┘                    │
│                                   ▼                              │
│                          ┌─────────────────────┐                 │
│                          │   PAYMENT_FLOW      │                 │
│                          │ (Stripe/PayHere)    │                 │
│                          └──────────┬──────────┘                 │
│                                    │                              │
│                          ┌─────────┴─────────┐                   │
│                          ▼                   ▼                   │
│                   ┌────────────┐      ┌────────────┐            │
│                   │  CONFIRM   │      │  FOLLOW_UP  │            │
│                   │  BOOKING   │      │  (Docs,     │            │
│                   │  + SYNC    │      │   Visa,     │            │
│                   └────────────┘      │   Packing)  │            │
│                                       └────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Key Nodes & Tools

| Node | Tools Called | Output |
|------|--------------|--------|
| `CLASSIFY_INTENT` | LLM (structured output) | `IntentType: greeting \| inquiry \| booking \| support \| complaint` |
| `EXTRACT_ENTITIES` | LLM + Regex | `TravelDates, PaxCount, Budget, Interests[], Language, WellnessFlag` |
| `BUILD_ITINERARY` | `mcp_tourism.search_attractions`, `mcp_tourism.get_seasonal_pricing`, `mcp_tourism.get_transport_options`, `operator_crm.get_availability` | `ItineraryDraft` (validated Pydantic model) |
| `PRESENT_QUOTE` | Template renderer (Jinja2 + i18n) | `QuoteMessage` (WhatsApp template + Web HTML) |
| `WELLNESS_UPSELL` | `wellness_engine.match_protocol`, `operator_crm.get_wellness_inventory` | `WellnessOptions[]` embedded in quote |
| `PAYMENT_FLOW` | `payments.create_intent`, `payments.handle_webhook` | `PaymentResult` → triggers `CONFIRM_BOOKING` |
| `CONFIRM_BOOKING` | `operator_crm.create_booking`, `calendar.sync`, `notifications.send_confirmation` | `BookingConfirmed` event |
| `FOLLOW_UP` | `documents.generate_visa_letter`, `documents.generate_packing_list`, `notifications.schedule_reminders` | Traveler packet sent |

### 4.3 Multilingual Support

| Language | Code | Priority | Implementation |
|----------|------|----------|----------------|
| English | en | Core | Native |
| Sinhala | si | Core | LLM + Custom dictionary |
| Tamil | ta | Core | LLM + Custom dictionary |
| Russian | ru | High (Top 3 market) | LLM + Terminology glossary |
| German | de | High | LLM + Terminology glossary |
| Chinese (Simplified) | zh | High | LLM + Terminology glossary |
| French | fr | Medium | LLM |
| Arabic | ar | Medium | LLM |
| Japanese | ja | Low | LLM |
| Korean | ko | Low | LLM |
| Italian | it | Low | LLM |
| Spanish | es | Low | LLM |

**Strategy:** LLM-native translation with tourism-specific glossary (attraction names, Ayurveda terms, visa vocabulary). Human review for top 5 languages at launch.

---

## 5. User Journeys

### 5.1 Traveler Journey (WhatsApp)

```
1. Traveler messages operator's WhatsApp Business number
   "Hi, we're 2 adults from Moscow, want to visit Sri Lanka 15-25 Dec, 
    interested in wildlife + beaches + Ayurveda. Budget ~$3000."

2. LankaAgent (instant, Russian):
   "Привет! 🇱🇰 Thanks for reaching out. I've found some amazing options 
    for Dec 15-25. Let me build a custom itinerary..."

3. [2-3 seconds] Agent builds itinerary via MCP tools:
   - Yala safari (wildlife) + Mirissa (beaches/whales) + 3-night Ayurveda retreat
   - Real-time availability from operator's calendar
   - Seasonal pricing (Dec = peak)

4. Agent presents interactive quote (WhatsApp list message + web link):
   ┌─────────────────────────────────────┐
   │ 🐘 10-Day Sri Lanka Discovery       │
   │ Dec 15-25 • 2 Adults • $2,847 USD   │
   │                                     │
   │ ✅ Yala Safari (2 days)             │
   │ ✅ Mirissa Whale Watching           │
   │ ✅ 3-Night Ayurveda Retreat*        │
   │ ✅ All transfers + 4* hotels        │
   │ ✅ Visa assistance included         │
   │                                     │
   │ [View Details] [Book Now - Pay $500]│
   └─────────────────────────────────────┘
   *Ayurveda upgrade: +$420 (Dr. Priya, BIMARI-certified)

5. Traveler taps "Book Now" → Payment screen (Stripe for USD, PayHere for LKR)
   → Pays 20% deposit → Instant confirmation

6. Auto-sent (in Russian):
   - Booking voucher + itinerary PDF
   - Visa invitation letter (operator letterhead)
   - Packing list (season-specific)
   - Ayurveda pre-arrival health intake form
   - 30-day / 7-day / 1-day reminders

7. Post-trip: Review request + referral incentive + wellness follow-up
```

### 5.2 Operator Journey (Dashboard)

```
1. Operator logs into dashboard.lankaagent.com
   → Sees: "3 new leads while you slept" (flagged by language)

2. Clicks Lead #1 (Russian family) → Sees:
   - Full conversation transcript (translated to English)
   - Auto-generated itinerary (editable)
   - Traveler profile + budget + wellness interest

3. Operator can:
   - Approve itinerary as-is → "Send Quote" (one click)
   - Modify hotels/activities → Regenerates quote
   - Add custom note → "I'll call you at 7 PM SLT"

4. When traveler pays:
   - Operator gets: Email + WhatsApp + Dashboard notification
   - Calendar auto-blocked (Google Cal sync)
   - Guide assigned (auto or manual)
   - Commission calculated (operator sees net revenue)

5. Weekly: Automated performance report
   - Leads → Quotes → Bookings → Revenue
   - Response time (AI vs Human)
   - Top converting languages/itineraries
```

---

## 6. Pricing & Packaging

### 6.1 Subscription Tiers

| Feature | **Starter** $49/mo | **Professional** $199/mo | **Enterprise** $499/mo | **Wellness Add-on** +$199/mo |
|---------|-------------------|-------------------------|------------------------|------------------------------|
| **WhatsApp AI Agent** | ✅ 500 msg/mo | ✅ 5,000 msg/mo | ✅ Unlimited | ✅ Included |
| **Web Widget** | ❌ | ✅ | ✅ Custom domain | ✅ |
| **Languages** | 3 | 8 | 12 + Custom | 12 |
| **Itineraries/mo** | 20 | 200 | Unlimited | +50 wellness |
| **Operator Seats** | 1 | 5 | 20 | +3 wellness |
| **Payment Processing** | PayHere only | Stripe + PayHere | Stripe + PayHere + Bank | Split payments |
| **Commission Tracking** | Basic | Advanced | Multi-tier + Sub-agents | Wellness revenue share |
| **Calendar Sync** | ❌ | Google Cal | Google + Outlook + CalDAV | Wellness doctor cal |
| **Analytics** | Basic | Full + Cohorts | Custom dashboards | Wellness outcomes |
| **API Access** | ❌ | Read-only | Full R/W | Wellness protocol API |
| **Support** | Email | Priority + WhatsApp | Dedicated Slack + Phone | Wellness specialist |
| **White-label** | ❌ | ❌ | ✅ | ✅ |
| **SLTDA/TDL Integration** | Manual | Auto-sync | Auto + Audit | Medical compliance |

### 6.2 Transaction Fees (On Top of Subscription)

| Payment Method | Fee | Who Pays |
|----------------|-----|----------|
| **Stripe (Intl Cards)** | 2.9% + $0.30 | Operator (pass-through) |
| **PayHere (LKR Cards/Wallets)** | 3.5% + LKR 10 | Operator |
| **Bank Transfer (Manual)** | 0% | Operator (manual verify) |
| **Wellness Split** | 15% of wellness revenue | Platform (to BIMARI network) |

### 6.3 Revenue Projection (Conservative)

| Month | Operators | Avg Tier | MRR | Transaction Rev | Total MRR |
|-------|-----------|----------|-----|-----------------|-----------|
| 1-2 | 3 (Pilots) | Pro | $600 | $0 | $600 |
| 3 | 8 | Pro | $1,600 | $800 | $2,400 |
| 4 | 15 | Mix | $3,500 | $2,500 | $6,000 |
| 5 | 25 | Mix | $6,500 | $5,000 | $11,500 |
| 6 | 35 | Mix | $10,000 | $9,000 | $19,000 |
| 9 | 55 | Mix | $18,000 | $20,000 | $38,000 |
| 12 | 80 | Mix | $30,000 | $40,000 | $70,000 |

**Year 1 Target: $70K MRR ($840K ARR) — achievable with 80 operators**

---

## 7. Technical Implementation Plan

### 7.1 Sprint 0 (Week 1-2): Foundation
- [ ] Repo setup: Monorepo (FastAPI + LangGraph + React Dashboard)
- [ ] Docker Compose: Postgres, Redis, FastAPI, Worker, Dashboard
- [ ] Auth: JWT + Multi-tenant RLS (Row Level Security)
- [ ] MCP Tourism Server v1: SLTDA stats + Attractions CSV import
- [ ] CI/CD: GitHub Actions → Staging (Railway/Render) → Prod

### 7.2 Sprint 1 (Week 3-4): Core Agent + WhatsApp
- [ ] LangGraph Travel Agent: Intent → Entities → Itinerary → Quote
- [ ] WhatsApp Business API integration (Twilio)
- [ ] Webhook handling: Incoming msg → Agent → Reply
- [ ] Session management (Redis): 24hr context window
- [ ] Multilingual: EN/SI/TA/RU/DE/ZH prompt templates

### 7.3 Sprint 2 (Week 5-6): Operator CRM + Payments
- [ ] Operator Dashboard: Leads, Itineraries, Bookings, Calendar
- [ ] Stripe + PayHere integration (multi-currency)
- [ ] Payment webhooks → Booking confirmation flow
- [ ] Document generation: Voucher, Visa letter, Packing list (PDF)
- [ ] Google Calendar sync (OAuth)

### 7.4 Sprint 3 (Week 7-8): Wellness Engine + Pilot Launch
- [ ] Wellness Engine: Health intake → Protocol match → Doctor assign
- [ ] BIMARI network integration (doctor profiles, availability)
- [ ] 3 Pilot Operators onboarded (wife's network + SLTDA contacts)
- [ ] End-to-end test: WhatsApp → Quote → Pay → Book → Docs → Trip
- [ ] Analytics: PostHog self-hosted + Custom dashboards

### 7.5 Sprint 4 (Week 9-10): Hardening + Scale Prep
- [ ] Load testing (100 concurrent conversations)
- [ ] Error tracking (Sentry), Logging (Loki), Monitoring (Grafana)
- [ ] Runbooks for SEV-1/2/3
- [ ] Automated backup + DR test
- [ ] Sales enablement: Demo script, Objection handling, Pricing calculator

---

## 8. Go-to-Market Strategy

### 8.1 Pilot Acquisition (Month 1-2)
| Channel | Approach | Target | Owner |
|---------|----------|--------|-------|
| **Wife's BIMARI Network** | Direct intro to 10 Ayurveda resort owners | 3 pilots | Chairman |
| **SLTDA Contacts** | ICT Dept + SQA Dept (Chairman knows) | 2 pilots | Chairman |
| **Kingslake Network** | Corporate travel partners → their operators | 1 pilot | Chairman |
| **Cold WhatsApp/Email** | 50 operators/week, personalized video demo | 5-10 meetings | Growth |

### 8.2 Scale Acquisition (Month 3+)
| Channel | Tactics | KPI |
|---------|---------|-----|
| **Content/SEO** | "How Sri Lanka operators 3x bookings with AI" blog + case studies | 500 visits |
| **WhatsApp Broadcast** | Opt-in list of 500+ operators (SLTDA public data) | opt-in rate |
| **Partnerships** | WhatsApp BSPs (Twilio, Gupshup, Wati) → Co-sell | Referrals |
| **Referral Program** | $100 credit per referred operator (lifetime 10% rev share) | Referrals |
| **Tourism Expos** | ITB Berlin, WTM London, SATTE India (Chairman attends) | Leads |

### 8.3 Retention & Expansion
- **Month 1:** Weekly check-in (Chairman/Growth)
- **Month 2:** Monthly business review (analytics + recommendations)
- **Quarterly:** Quarterly Business Review (QBR) — upsell wellness, enterprise, API
- **Health Score:** Daily → Weekly → Monthly automated (leads, bookings, revenue, support tickets)

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **WhatsApp Business API approval delays** | Medium | High | Start with Twilio Sandbox → Parallel apply direct Meta → Fallback: Web widget + SMS |
| **SLTDA regulatory changes** | Low | High | Maintain compliance buffer; Legal review quarterly; TDL integration optional at launch |
| **Payment gateway issues (LKR)** | Medium | Medium | Dual gateway (PayHere + Stripe LankaPay); Manual bank transfer fallback |
| **Operator churn after pilot** | Medium | High | 3-month contract; Success metrics tied to renewal; Free migration assistance |
| **LLM hallucination on itineraries** | Medium | High | Structured output validation; MCP tool grounding; Human-in-loop for pilots |
| **Competition from Wati/ManyChat adding AI** | High | Medium | Domain depth (SL tourism data, Ayurveda, SLTDA compliance) = moat |
| **Chairman time constraint (Kingslake job)** | High | High | Hermes autonomous execution; Weekly 30-min sync; Decisions async via decision log |
| **Currency fluctuation (LKR/USD)** | Medium | Low | Price in USD for intl, LKR for local; Auto-FX update daily; Hedge via Stripe |

---

## 10. Success Criteria (Definition of Done per Sprint)

| Sprint | Must Ship | Metrics |
|--------|-----------|---------|
| **Sprint 0** | Repo, Docker, Auth, MCP Server v1, CI/CD | `docker compose up` → All healthy; Tests pass |
| **Sprint 1** | Agent answers WhatsApp in 3 langs, builds itinerary | 90% intent accuracy; <3s response; 5 test conversations |
| **Sprint 2** | Operator dashboard + Payments + Booking confirmation | 3 pilot operators logged in; 10 test bookings end-to-end |
| **Sprint 3** | Wellness upsell + 3 pilots live + Analytics | 50+ real traveler conversations; $5K+ booked; <5% error rate |
| **Sprint 4** | Production hardening + Sales kit | 99.9% uptime; <1hr P1 response; 10 qualified demos booked |

---

## 11. Open Decisions (Need Chairman Input)

| # | Decision | Options | Recommendation | Deadline |
|---|----------|---------|----------------|----------|
| 1 | **Legal Entity** | Sri Lanka Pvt Ltd vs US LLC vs Singapore Pte Ltd | US LLC (Stripe Atlas) + SL branch for local payments | Sprint 0 |
| 2 | **Brand Name** | LankaAgent vs LankaAI vs CeylonConcierge vs [Your Choice] | LankaAgent (descriptive, SEO-friendly) | Sprint 0 |
| 3 | **Pricing Currency** | USD only vs USD + LKR vs LKR only | USD for intl operators, LKR for local (auto-FX) | Sprint 1 |
| 4 | **Wellness Revenue Split** | 15% platform / 85% doctor vs 20/80 vs Flat fee | 15% platform (covers marketing + compliance) | Sprint 2 |
| 5 | **Data Hosting** | Sri Lanka (Dialog/AWS) vs Singapore vs US | Singapore (AWS) — latency OK, data sovereignty balance | Sprint 0 |
| 6 | **Chairman Equity for Wife/BIMARI** | % for network access + medical credibility | 5-10% advisory shares (vesting 2yr) | Before Pilot |

---

## 12. Appendix

### 12.1 Key APIs & Integrations
| Service | Purpose | Auth | Rate Limit |
|---------|---------|------|------------|
| **Meta WhatsApp Business** | Messaging | Bearer | 1,000/sec |
| **Twilio** | WhatsApp + SMS fallback | Account SID | 100/sec |
| **Stripe** | Intl Payments | Secret Key | 100/sec |
| **PayHere** | LKR Payments | Merchant ID | 50/sec |
| **Google Calendar** | Sync bookings | OAuth 2.0 | 500/day/user |
| **PostHog** | Analytics | Project Key | Unlimited |
| **Sentry** | Error Tracking | DSN | Unlimited |

### 12.2 Environment Variables (Sample)
```bash
# Core
DATABASE_URL=postgresql://user:pass@host:5432/lankaagent
REDIS_URL=redis://host:6379/0
SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Multi-tenancy
DEFAULT_TENANT_SCHEMA=public

# WhatsApp
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
META_VERIFY_TOKEN=...
META_APP_SECRET=...

# Payments
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYHERE_MERCHANT_ID=...
PAYHERE_MERCHANT_SECRET=...
PAYHERE_SANDBOX=true

# MCP
MCP_SERVER_URL=http://mcp:8000
MCP_API_KEY=...

# External
GOOGLE_CALENDAR_CLIENT_ID=...
GOOGLE_CALENDAR_CLIENT_SECRET=...
POSTHOG_API_KEY=...
SENTRY_DSN=...
```

---

**Document Control**
- **Next Review:** Sprint 1 Planning (Chairman + Hermes)
- **Version History:** v1.0 — Initial Draft (Hermes)
- **Approval:** [ ] Chairman Approved — Date: ___________

---

*Prepared by Hermes Agent — Chief of Staff*  
*For: Nishantha Priyadarshana — Chairman & CEO, LankaAgent*