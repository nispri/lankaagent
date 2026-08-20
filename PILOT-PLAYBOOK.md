# Pilot Engagement Playbook — LankaAgent

**Version:** 1.0 (2026-08-11)
**Author:** Nishantha Priyadarshana (Priya) — Chairman/CEO
**Purpose:** End-to-end script and checklist for converting the 3 pilot channels (BIMARI, SLTDA ICT, Ceyloria partners) into signed, paying pilots. Every step maps to Revenue-First Rule (DEC-20260810-001).

---

## 1. Pilot Profiles (what we know)

| Channel | Contact | Org Type | Pain Points (inferred) | Pipeline Value |
|---|---|---|---|---|
| **1. BIMARI Network** | Wife's Ayurvedic network (BIMARI Naviina) | Wellness + medical tourism referrals | High-value leads leaking; no automated follow-up; wellness add-on hard to sell | $398/mo (Pro + Wellness split) |
| **2. SLTDA ICT** | SLTDA ICT Committee contact | Industry association / regulator | Members asking for digital tools; need a vetted, SLTDA-aligned platform | $199/mo (Growth tier) |
| **3. Ceyloria Partners** | Your own operator network (fellow SLTDA operators) | Peer inbound operators | Same problems you had: manual quotes, WhatsApp chaos, no 24/7 concierge | $199/mo (Growth tier) |

> **Key insight:** Each pilot has a *different* primary pain point. Tailor the demo narrative accordingly.

---

## 2. Pre-Call Preparation (do once, reuse)

### 2.1 Technical verification (5 min before call)
```bash
# 1. Stack health
curl -sf https://cycling-handwash-oversweet.ngrok-free.dev/health/ready
docker ps --format "{{.Names}} | {{.Status}}" | grep -E "api|mcp|postgres|redis"

# 2. Widget loads
open https://cycling-handwash-oversweet.ngrok-free.dev/widget/iframe/ceyloria-holidays

# 3. MCP trace ready (separate terminal)
docker logs -f lankaagent-mcp | grep "POST /mcp"
```

### 2.2 Demo data set (pre-seeded in session)
- Session ID: `pilot-demo-<channel>` (e.g., `pilot-demo-bimari`)
- Language: English (switch live to their preferred language)
- Sample tour: **7-day highlights** (quicker to demo than 14-day)

### 2.3 Materials open on your screen
- [ ] This playbook (PDF/print)
- [ ] Widget tab (widget/embed)
- [ ] Ceyloria landing (ceyloria-site.vercel.app) — "this is *your* customer view"
- [ ] Pilot Agreement (from `PILOT-OUTREACH.md` Appendix A)
- [ ] Pricing one-pager (tiers + what's included)
- [ ] Onboarding checklist (Section 6)

---

## 3. Call Structure (30 minutes total)

| Phase | Time | Goal |
|---|---|---|
| **Rapport & Context** | 5 min | "You're pilot #X of 3. Here's what we're building together." |
| **Live Demo** | 12 min | Show → Don't tell. MCP-grounded, their language, their data. |
| **Pain-Point Mapping** | 5 min | "Which of these costs you the most time/money?" |
| **Pilot Terms & Close** | 5 min | Agreement → signature → onboarding date |
| **Next Steps** | 3 min | Calendar invite for onboarding, Slack/WhatsApp group |

---

## 3. Live Demo Script (12 minutes — rehearsed)

> **Principle:** Every click fires a real MCP tool call. Narrate the *business value*, not the tech.

### 3.1 Opening (1 min)
> *"This is **Anuki** — your AI Travel Concierge. It runs on *your* data: your hotels, your pricing, your tours. It speaks 7 languages, works 24/7, and captures every lead into your dashboard. Let me show you."*

### 3.2 Demo Flow (click-by-click)

| Step | You type / click | MCP tool fired | Business value you narrate |
|---|---|---|---|
| **A. Quote** | `"quote a 7 day tour for 2 people"` | `get_tour_quote` | *"Instant, accurate quote — **$1,261/pp**. No spreadsheet, no back-and-forth. Your margin (25.95%) baked in."* |
| **B. Customize** | `"make it 10 days for 4 people"` | `get_tour_quote` | *"Any duration, any party size — engine recomputes in <2 sec. **$1,369/pp**."* |
| **C. Attractions** | `"what wildlife can we see?"` | `search_attractions` | *"Guest asks 'what animals?' — Anuki answers from *your* attraction database with fees. Upsell opportunity."* |
| **D. Hotels** | `"hotels in Kandy"` | `get_hotels` | *"Your contracted rates, your photos. Guest books *your* room block."* |
| **E. Visa** | `"do I need a visa from Germany?"` | `get_visa_requirements` | *"One less email for your ops team. ETA $50, done."* |
| **F. Language switch** | Click 🌐 → **Deutsch** → repeat A | — | *"7 languages. German guest gets **ab $1.261 pro Person** — same engine, zero translation work."* |
| **G. Voice (optional)** | Click 🎙️ → speak query | — | *"Voice in/out. Accessibility + luxury feel."* |

> **Pro tip:** After each reply, point to the MCP terminal: *"See? That was a real API call to your Tourism Server — not a canned response."*

### 3.3 Channel-specific pivots

| Channel | Extra 2 minutes | Why |
|---|---|---|
| **BIMARI** | `"wellness add-on for 2 people"` → shows $580/pp | Wellness = your wife's domain = **15% revenue split** (new money line) |
| **SLTDA ICT** | Show `/api/v1/leads` dashboard (admin) | *"Association view: aggregate leads across members, compliance reporting"* |
| **Ceyloria Partners** | `"my tour is 5 days, 6 pax, budget $1,500"` → custom quote | *"Your weird requests — engine handles any combo. No more 'let me check and revert'."* |

---

## 4. Pain-Point Mapping (5 minutes — diagnostic)

> **Ask:** *"Of these three, which costs you the most right now?"* (Show the card)

| Burning Problem | LankaAgent Solution | Quantified Impact |
|---|---|---|
| **1. Manual quotes** (30–60 min each, error-prone) | Instant MCP-grounded quote engine | **Save 5–10 hrs/week** per consultant |
| **2. Leads lost after hours / on WhatsApp** | 24/7 widget + lead capture + CRM sync | **Recover 15–30% more leads** |
| **3. Language barrier** (can't serve German/Russian/Chinese) | 7 languages, native-quality replies | **Open 3 new source markets** without hiring |

**Listen, note their #1.** That becomes the "pilot success metric" in the agreement.

---

## 5. Pilot Terms & Close (5 minutes)

### 5.1 Standard Pilot Agreement (non-negotiable core)

| Term | Value |
|---|---|
| **Duration** | 90 days (auto-renews month-to-month) |
| **Tier** | Growth ($199/mo) or Pro ($499/mo if >500 leads/mo) |
| **Includes** | Widget embed (site + WhatsApp), 7 languages, MCP data, lead dashboard, email/Slack notifications |
| **Your data** | You own all guest data; we process only |
| **SLA** | 99.5% uptime, <3s median reply, 90%+ accuracy on pricing |
| **Success metric** | Agreed in call (e.g., "10 qualified leads/mo from widget") |
| **Exit** | 30-day notice, data export in CSV/JSON |
| **Reference** | Willing to take 1 reference call from future pilot |

### 5.2 Channel-specific add-ons

| Channel | Add-on |
|---|---|
| **BIMARI** | Wellness add-on module ($199/mo extra, 15% split to BIMARI Naviina) |
| **SLTDA ICT** | Association dashboard (aggregate view) — *co-branded "Powered by LankaAgent + SLTDA"* |
| **Ceyloria Partners** | White-label widget (their logo, their domain, their Stripe) |

### 5.3 Closing line
> "We're taking 3 pilots total. You're [#1/#2/#3]. The agreement is 2 pages. If the success metric hits in 30 days, we both win. Shall I send the DocuSign now and schedule onboarding for [Tuesday/Thursday]?"

---

## 6. Onboarding Checklist (post-signature, Day 1–7)

| Day | Task | Owner | Done? |
|---|---|---|---|
| **0** | Signed agreement + payment method (Stripe/PayHere) | Pilot | ☐ |
| **1** | Create tenant in dashboard (`POST /api/v1/tenants`) | You (dev) | ☐ |
| **1** | Import their hotel/attraction/tour data (CSV → `data/tour_data.py`) | You + Pilot ops | ☐ |
| **2** | Widget embed code + WhatsApp webhook config | You (dev) | ☐ |
| **2** | Language defaults + brand voice (tone guide) | Pilot marketing | ☐ |
| **3** | Test booking flow end-to-end (guest → lead → dashboard) | Both | ☐ |
| **4** | Go-live on their site / WhatsApp | Pilot IT | ☐ |
| **7** | First weekly review (leads, accuracy, feedback) | Both | ☐ |
| **30** | Pilot success metric review → renew / expand / exit | Both | ☐ |

---

## 7. Objection Handling (ready responses)

| Objection | Response |
|---|---|
| **"$199 is too much"** | "One converted booking at $2,490 = 12 months of pilot. Break-even = 1 booking/year." |
| **"We have a chatbot already"** | "Does it quote your exact pricing from your data in 7 languages? Ours does — let's A/B test for 30 days." |
| **"We need to think about it"** | "Totally fair. The 3-pilot window closes [date]. Happy to follow up in 2 weeks — but the Pro tier ($499) may not be available after the pilot cohort fills." |
| **"Data privacy / guest PII"** | "You own the data. We're a processor. DPA attached. No training on your data. Sri Lanka PDPA compliant." |
| **"Our IT can't embed a widget"** | "We give you one `<script>` tag. Or WhatsApp-only (no site changes). 5-min setup." |

---

## 8. Post-Call Actions (within 1 hour)

1. **Email** with: Pilot Agreement (DocuSign), this playbook (PDF), pricing one-pager, onboarding calendar link.
2. **Slack/WhatsApp group** created: "LankaAgent Pilot — [Partner Name]" — you + pilot ops + pilot owner.
3. **CRM note** (Google Sheet Pilot Leads tab): update status → "Demo Done / Agreement Sent".
4. **Calendar invite** for Day 1 onboarding (30 min technical).

---

## 9. Success Metrics (pilot cohort level)

| Metric | Target (90 days) |
|---|---|
| **Signed pilots** | 3 / 3 |
| **MRR from pilots** | $796 (current pipeline) → $1,500+ (with upsells) |
| **Leads captured per pilot** | >50 / month |
| **Quote accuracy** | >95% vs manual quote |
| **Guest satisfaction (CSAT)** | >4.5 / 5 |
| **Reference willingness** | 3 / 3 say yes |

---

## Appendix A: Quick Links (bookmark these)

| Asset | URL |
|---|---|
| **Widget demo (Ceyloria)** | `https://cycling-handwash-oversweet.ngrok-free.dev/widget/iframe/ceyloria-holidays` |
| **Ceyloria landing (customer view)** | `https://ceyloria-site.vercel.app` |
| **Pilot Agreement template** | `PILOT-OUTREACH.md` (Appendix A) |
| **Pricing one-pager** | `REVENUE-PLAN.md` § Pricing Tiers |
| **MCP tool trace (live)** | `docker logs -f lankaagent-mcp | grep "POST /mcp"` |
| **Google Sheet (Pilot Leads)** | `https://docs.google.com/spreadsheets/d/16e3EFOkIbyc3a8xG23D61MWVQEAtTNrvh2RAxHWfS2o` |
| **Onboarding calendar** | (add your Calendly/Cal.com link) |

---

## Appendix B: One-Pager for Pilot (send after call)

> **LankaAgent — Your AI Travel Concierge**
>
> - **Instant quotes** from *your* pricing engine (any duration, any pax)
> - **24/7 guest replies** in 7 languages (EN, DE, FR, RU, ZH, SI, TA)
> - **Your data, your brand** — hotels, attractions, tours, visa rules
> - **Lead capture** → your dashboard / Slack / email / CRM
> - **WhatsApp + Website embed** — 5 min setup
> - **Pilot: $199/mo** (90 days, cancel anytime)
> - **Built by a Sri Lanka operator, for Sri Lanka operators**
>
> *Three pilots only. You're invited.*

---

*End of Playbook. Print one copy per pilot call. Update after each call with their specific pain-point ranking and agreed success metric.*