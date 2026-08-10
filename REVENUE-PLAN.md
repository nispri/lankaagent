# LankaAgent — Revenue & Profit Plan (Owner's Document)

**Version:** 1.0 · **Date:** 2026-08-10 · **Owner:** Chairman (Nishantha Priyadarshana)
**Prepared by:** Hermes (Chief of Staff) · **Status:** ✅ Live model, reviewed with owner
**Governing rule:** Revenue-First (DEC-20260810-001) — every feature must add money. Minimize cost · Maximize profit · Enhance quality.

---

## 0. Executive Summary

| Metric | Year 1 Target (Conservative) | Stretch |
|--------|------------------------------|---------|
| **Monthly Recurring Revenue (MRR)** | $70,000 (Month 12) | $100,000+ |
| **Annual Recurring Revenue (ARR)** | $840,000 | $1,200,000 |
| **Year 1 Total Revenue** | ~$291,000 | ~$400,000+ |
| **Year 1 Total Cost** | **< $1,500** (near-zero infra) | < $3,000 |
| **Year 1 Profit** | **~$290,000 (99.5% margin)** | ~$397,000 |
| **Operators at Month 12** | 80 | 100+ |

**The business model in one line:** We sell an AI concierge that answers every operator's WhatsApp/website guest 24/7 in 12 languages, quotes and closes tour bookings with real prices — operators pay us per month + a share of every booking. Our cost to serve one more operator is ~$0 (free LLM, free hosting). **Every extra operator is nearly pure profit.**

---

## 1. How We Earn Money — ALL Revenue Streams (nothing skipped)

| # | Revenue Stream | Model | Price/Share | Status | When it pays |
|---|---------------|-------|-------------|--------|--------------|
| 1 | **SaaS Subscription** (Starter/Pro/Enterprise) | Monthly recurring | $49 / $199 / $499 | ✅ Documented (SPEC §6.1) | Month 1 (pilots) |
| 2 | **Wellness Add-on** | Monthly recurring | +$199/mo per operator | ✅ Documented | Month 2 (BIMARI network) |
| 3 | **Transaction Fee (platform share)** | % of every booking paid through us | ~2.9% Stripe / 3.5% PayHere (pass-through to operator; platform earns markup via volume) | ✅ Documented (SPEC §6.2) | Month 3 (first bookings) |
| 4 | **Wellness Revenue Split** | 15% of all wellness revenue booked | 15% platform / 85% doctor | ✅ Documented (SPEC §6.2) | Month 3+ |
| 5 | **White-label / API Access** | Enterprise-only premium | Included in $499 tier | ✅ Documented | Month 6+ (enterprise deals) |
| 6 | **Setup / Onboarding Fee** | One-time per operator | $99 (proposed) | 💡 Proposed value-add | Month 1 |
| 7 | **Referral Program** | $100 credit per referred operator + 10% rev share to referrer (acquisition engine, cost offset by new MRR) | $100 credit | ✅ Documented (SPEC §8.2) | Month 3+ |
| 8 | **Ceyloria Own-Brand Tour Sales** (pilot #1 — the Chairman's own operator) | Direct tour revenue | 14-day tour $2,490/pp · margin 25.95% | ✅ LIVE | **This week (first booking)** |
| 9 | **Group Departures** (fixed-date group tours) | Higher margin per guest, capacity fills | 6 pax × $2,490 = $14,940/departure | 💡 Proposed value-add | Month 2+ |

**Ceyloria margin worked example (stream 8):**
- 2-pax booking: $4,980 revenue → ~$1,292 gross profit (25.95% margin, pricing engine calibrated)
- 6-pax group: $14,940 revenue → ~$3,877 gross profit
- + Wellness add-on $580/pp → 15% split to platform on top

---

## 2. Pricing & Packaging (SPEC §6.1 — authoritative)

| Feature | **Starter** $49/mo | **Professional** $199/mo | **Enterprise** $499/mo | **Wellness Add-on** +$199/mo |
|---------|-------------------|--------------------------|------------------------|------------------------------|
| WhatsApp AI Agent | 500 msg/mo | 5,000 msg/mo | Unlimited | Included |
| Web Widget | ❌ | ✅ | ✅ Custom domain | ✅ |
| Languages | 3 | 8 | 12 + Custom | 12 |
| Itineraries/mo | 20 | 200 | Unlimited | +50 wellness |
| Operator Seats | 1 | 5 | 20 | +3 wellness |
| Payments | PayHere only | Stripe + PayHere | + Bank | Split payments |
| Commission Tracking | Basic | Advanced | Multi-tier | Wellness rev share |
| Calendar Sync | ❌ | Google Cal | + Outlook/CalDAV | Doctor calendar |
| Analytics | Basic | Full + Cohorts | Custom dashboards | Wellness outcomes |
| API Access | ❌ | Read-only | Full R/W | Wellness protocol API |
| White-label | ❌ | ❌ | ✅ | ✅ |
| SLTDA/TDL Integration | Manual | Auto-sync | Auto + Audit | Medical compliance |

### Transaction fees (stream 3) — who pays what
| Method | Fee | Who Pays |
|--------|-----|----------|
| Stripe (intl cards) | 2.9% + $0.30 | Operator (pass-through) |
| PayHere (LKR) | 3.5% + LKR 10 | Operator |
| Bank transfer (manual) | 0% | Operator |
| Wellness split | 15% of wellness revenue | Platform receives |

---

## 3. Cost Structure — MINIMIZED by design

### Current monthly costs (Month 1–2, live today)
| Cost Item | Monthly | Notes |
|-----------|---------|-------|
| LLM (OpenCode Zen free tier) | **$0** | deepseek-v4-flash-free — primary engine |
| Hosting (Docker Desktop local + ngrok free) | **$0** | ngrok free stable domain |
| Landing page (Vercel free) | **$0** | ceyloria-site.vercel.app |
| Database (Postgres/Redis local Docker) | **$0** | |
| TTS (Edge neural, free) + STT (faster-whisper local) | **$0** | |
| Domain (when needed) | ~$1/mo | amortized $12/yr |
| **Total now** | **~$1/mo** | |

### Ramp-up costs (as we scale, still minimal)
| Item | Month 3–6 | Month 9–12 | Notes |
|------|-----------|------------|-------|
| Cloud hosting (Railway/Render) | $5–20/mo | $50–150/mo | only when operators exceed local capacity |
| WhatsApp production API (Twilio) | ~$5/mo | ~$50/mo | $0.005/msg |
| Analytics (PostHog self-hosted) | $0 | $0–20/mo | self-hosted = free |
| Monitoring (Sentry free tier) | $0 | $0 | free tier sufficient |
| Marketing | $0 (networks) | $0–200/mo | Chairman's networks + referrals first |
| **Total scaled** | **~$10–30/mo** | **~$50–400/mo** | still < 1% of revenue |

### One-time costs (all optional, ~$0 strategy)
- GitHub Actions CI: free tier ✅ · Docker: free ✅ · Vercel: free ✅
- Stripe/PayHere accounts: free setup ✅ · SLTDA registration: already owned (Ceyloria license SLTDA/TO/2024/0045) ✅

**Cost philosophy:** stay on free tiers until revenue justifies spend. Every dollar of cost must be proven to increase revenue faster than it costs (e.g., production WhatsApp API only after 3+ pilots demand it).

---

## 4. Financial Projection — Month by Month (Year 1, Conservative)

Base = SPEC §6.3 projection. Interpolated months shown in brackets.

| Month | Operators | Revenue (MRR + txn) | Cost | **Profit** | Margin | Key Milestone |
|-------|-----------|--------------------|------|-----------|--------|---------------|
| **M1** | 2–3 (pilots) | $300 | $5 | **$295** | 98% | First booking (Ceyloria) |
| **M2** | 3 | $600 | $5 | **$595** | 99% | **$3K MRR goal checkpoint** (3 pilots live) |
| **M3** | 8 | $2,400 | $15 | **$2,385** | 99% | First operator bookings + txn fees |
| **M4** | 15 | $6,000 | $25 | **$5,975** | 99.6% | Wellness add-on live (BIMARI) |
| **M5** | 25 | $11,500 | $35 | **$11,465** | 99.7% | Scale acquisition begins (SEO/broadcast) |
| **M6** | 35 | $19,000 | $50 | **$18,950** | 99.7% | Operator dashboard + payments complete |
| **M7** | 42 | $24,000 | $60 | **$23,940** | 99.8% | White-label/enterprise conversations |
| **M8** | 49 | $31,000 | $70 | **$30,930** | 99.8% | Hardening complete |
| **M9** | 55 | $38,000 | $100 | **$37,900** | 99.7% | 50+ real conversations, $5K+ booked |
| **M10** | 62 | $47,000 | $130 | **$46,870** | 99.7% | |
| **M11** | 70 | $58,000 | $160 | **$57,840** | 99.7% | |
| **M12** | 80 | $70,000 | $200 | **$69,800** | 99.7% | **YEAR 1 TARGET: $70K MRR / $840K ARR** |

**Year 1 totals (conservative):** Revenue ~$291,000 · Cost ~$855 · **Profit ~$290,000 (99.7% margin)**
**Stretch target:** $100K+ MRR by M12 (per owner's target) → Year 1 profit ~$397,000.

> ⚠️ Note: profit margin shown is **operational margin** (platform economics). Ceyloria tour revenue (stream 8) is separate and adds direct cash flow from day 1.

---

## 5. Project Plan & Timeline (aligned with SPEC §7)

| Sprint | Weeks | Scope | Money Impact | Status |
|--------|-------|-------|--------------|--------|
| **Sprint 0** Foundation | 1–2 | Repo, Docker, Auth, RLS | Enables everything | ~85% ✅ |
| **Sprint 1** Core Agent + WhatsApp | 3–4 | Anuki concierge, widget, voice, pricing, WhatsApp | **First revenue** — demo-ready product | ~70% ✅ LIVE |
| **Sprint 2** Operator CRM + Payments | 5–6 | Dashboard, Stripe/PayHere, booking flow, docs | **Txn fees + setup fees** | ⏳ Next |
| **Sprint 3** Wellness + Pilot Launch | 7–8 | Wellness engine, BIMARI integration, 3 pilots, analytics | **15% wellness split + pilot MRR** | ⏳ |
| **Sprint 4** Hardening + Scale | 9–10 | Load testing, Sentry/Grafana, runbooks, sales kit | Protects revenue (uptime) | ⏳ |

### Money-linked milestones (what must happen, when)
1. **THIS WEEK:** First booking from Ceyloria (pilot #1) — live widget demo
2. **Weeks 3–4:** 3 pilot operators onboarded → $3K MRR
3. **Weeks 5–6:** Payments live → first transaction fees + setup fees
4. **Weeks 7–8:** Wellness sell-through → 15% split revenue
5. **Weeks 9–10:** Hardening + sales kit → scale acquisition

---

## 6. Goals & Targets (North Star = money)

### Revenue targets
| Timeline | Target | Source |
|----------|--------|--------|
| This week | First booking (pilot #1) | Owner's goal |
| Month 2 | $3K MRR (3 pilots × Pro) | Owner's goal |
| Month 6 | $19K MRR | SPEC §6.3 |
| Month 12 | $70K MRR / $840K ARR (conservative) · $100K+ MRR (stretch) | SPEC §6.3 + owner target |

### Profit & efficiency targets
- Year 1 profit: **>$290K**, margin **>99%**
- Cost cap: never exceed 2% of MRR
- Every $1 spent must return ≥ $2 in revenue within 90 days (cost filter)

### Quality targets (quality = trust = bookings = money)
| KPI | Target |
|-----|--------|
| Agent response time | < 3 seconds |
| Intent accuracy | ≥ 90% |
| Error rate | < 5% |
| Uptime | 99.9% |
| Conversation → booking conversion | ≥ 10% (pilots) |
| Guest satisfaction | ≥ 4.5/5 (reviewed post-trip) |

---

## 7. Cost Minimization Strategy (always on)
1. **Free-tier first:** Zen LLM, Vercel, ngrok, PostHog self-hosted, Sentry free — revisit only when scale demands
2. **No paid ads until proven** — networks (wife's BIMARI, SLTDA, Kingslake) are $0 acquisition
3. **One infra decision at a time** — pay for cloud hosting only when local Docker + ngrok stops scaling
4. **Open-source tools** (faster-whisper, Edge TTS, Postgres, Redis) — no licensing costs
5. **Referrals before ads** — $100 credit costs less than any paid channel

## 8. Profit Maximization Strategy
1. **Tier upgrades** — Pro ($199) is the default pitch; Enterprise ($499) for larger operators (20+ seats)
2. **Wellness add-on ($199) on every onboarding** — 15% split is pure platform margin
3. **Group departures** — fill capacity, higher per-guest margin (Ceyloria)
4. **Setup fee $99** — front-load cash at signup
5. **Upsell ladder:** Starter → Pro → Enterprise + Wellness → White-label
6. **Price in USD for international operators** — FX protection (SPEC §9)

## 9. Quality Enhancement Strategy (quality drives conversion)
1. **Voice in/out** on widget (done) — removes friction for older guests
2. **Custom tour pricing engine** (done) — never invented numbers = trust
3. **Multi-language accuracy** — SI/TA/DE/ZH verification in progress (Sprint 1 tail)
4. **Human-in-loop for pilots** — Chairman approves quotes for first operators
5. **Post-trip review + referral nudge** (SPEC §5.1 step 7) — repeat bookings
6. **Weekly quality review** in owner sync — error rate, conversion, satisfaction

---

## 10. Revenue Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| No first booking this week | Medium | High | Widget live + outreach messages ready; offer first pilot 30-day free trial |
| WhatsApp sandbox blocks SL numbers | High | High | Web widget is the global path (already live); apply for production API in parallel |
| Operator churn after pilot | Medium | High | 3-month contract; success metrics tied to renewal (SPEC §9) |
| LLM hallucination on quotes | Medium | High | Pricing engine computes numbers (done); human-in-loop for pilots |
| Payment gateway friction (LKR) | Medium | Medium | Dual gateway Stripe + PayHere; bank transfer fallback |
| Zen free tier flakiness | Medium | Low | OpenRouter fallback + retry loop (done) |

---

## 11. Owner's Dashboard (reviewed weekly)

**Money first:** Bookings this week · MRR · Pipeline (quotes outstanding) · Cost burn
**Then quality:** Response time · Error rate · Guest satisfaction
**Then progress:** Sprint status vs plan · Revenue Filter check on any new scope

---

*This document is the authoritative money plan. SPEC §6/§8 remain the source of truth for pricing & GTM. Any change to revenue streams, pricing, or costs requires Chairman approval (DEC-20260810-001).*
