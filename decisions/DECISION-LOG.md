# LankaAgent — Decision Log

**Format:** `DEC-{YYYYMMDD}-{topic}.md`  
**Location:** `decisions/`  
**Process:** Hermes drafts → Chairman reviews → Approves/Modifies/Rejects → Logged here

---

## DECISION REGISTER

| ID | Date | Topic | Status | Chairman Decision |
|----|------|-------|--------|-------------------|
| DEC-20250721-001 | 2025-07-21 | Governance Model & AI Org Structure | ✅ Approved | Approved as-written |
| DEC-20250721-002 | 2025-07-21 | Product Spec (SPEC.md) v1.0 | ⏳ Pending Review | — |
| DEC-20250721-003 | 2025-07-21 | Sprint 0 Plan & Timeline | ⏳ Pending Review | — |
| DEC-20250721-004 | 2025-07-21 | Pricing & Packaging (SPEC Section 6) | ⏳ Pending Review | — |
| DEC-20250721-005 | 2025-07-21 | Tech Stack Confirmation (FastAPI, LangGraph, Postgres, Redis) | ⏳ Pending Review | — |

---

## DEC-20250721-001: Governance Model & AI Org Structure

**Status:** ✅ **APPROVED**  
**Date:** 2025-07-21  
**Chairman:** Nishantha Priyadarshana  
**Document:** `GOVERNANCE.md` v1.0

### Summary
Established operating model: Chairman (final decision authority) + Hermes (Chief of Staff/Orchestrator) + 4 AI Employees (Dev, Growth, Ops, Product). Decision rights matrix (RACI), approval gates, weekly sprint planning, daily briefings, escalation paths defined.

### Key Decisions
1. **Chairman approves:** Pricing, ICP, Roadmap, Architecture (major), Hiring, Legal, Fundraising, Brand, Discounts >20%, Contracts >$500
2. **Hermes + AI execute:** Daily code, content, support, billing, monitoring, deployments
3. **Weekly Sync:** Monday 09:00 SLT (30 min) — Sprint planning + Decision review
4. **Daily Briefing:** Async 08:00 SLT — KPIs, Progress, Decisions needed
5. **Business-Critical Decisions:** Async decision doc with 2-hour SLA

### Next Actions
- [x] GOVERNANCE.md written and stored
- [ ] Weekly calendar invite created (Chairman + Hermes)
- [ ] Telegram channel "LankaAgent-Ops" created for alerts
- [ ] Notion/Obsidian workspace initialized

---

## DEC-20250721-002: Product Specification v1.0

**Status:** ⏳ **PENDING CHAIRMAN REVIEW**  
**Date:** 2025-07-21  
**Document:** `SPEC.md` v1.0  
**Review Deadline:** 2025-07-23 (48 hours)

### Summary
Complete product specification covering: Vision, ICP, System Architecture, Agent Graph (LangGraph), Data Models, User Journeys, Pricing, Implementation Plan (4 sprints), Go-to-Market.

### Key Decisions Needed from Chairman

| Decision Point | Options | Hermes Recommendation |
|----------------|---------|----------------------|
| **Primary Channel** | WhatsApp Business API (Meta) vs Twilio WhatsApp vs Web-first | **Twilio WhatsApp** — Faster setup (sandbox instant), Meta verification parallel |
| **Pricing Tiers** | $49/$199/$499 vs $99/$399/$899 vs Custom | **$49/$199/$499** — Lower entry, easier pilot close |
| **Wellness Add-on** | $199/mo vs Revenue share (15%) vs Both | **$199/mo + 15% wellness revenue** — Aligns incentives, recurring base |
| **MCP Data Scope** | SLTDA only vs +Custom operator data vs +Competitor intel | **SLTDA + Operator-contributed** — Start authoritative, expand |
| **Pilot Count** | 3 operators vs 5 vs 10 | **3 pilots** — Deep engagement, measurable case studies |
| **Launch Geography** | Sri Lanka only vs SL + Maldives vs Global English | **Sri Lanka only** — Master home market, then replicate |

### Chairman Action Required
Review `SPEC.md` → Create decision doc `decisions/DEC-20250723-spec-approval.md` with selections above → Hermes executes Sprint 1 per approved spec.

---

## DEC-20250721-003: Sprint 0 Plan & Timeline

**Status:** ⏳ **PENDING CHAIRMAN REVIEW**  
**Date:** 2025-07-21  
**Document:** `sprints/SPRINT-00.md`  
**Review Deadline:** 2025-07-22 (24 hours — Sprint starts tomorrow)

### Summary
14-day sprint broken into 7 daily goals. Day 7 = Sprint Review with Chairman approval gate.

### Key Decisions Needed

| Decision Point | Options | Hermes Recommendation |
|----------------|---------|----------------------|
| **Sprint Duration** | 7 days (as written) vs 10 days vs 14 days | **7 days** — Aggressive but achievable with AI team |
| **Staging Environment** | Railway (free) vs Render (free) vs VPS (self-managed) | **Railway** — Simplest Postgres+Redis+Deploy, $0-5/mo |
| **MCP Data Source** | SLTDA Excel download vs API (if exists) vs Manual entry | **SLTDA Excel → ETL → Postgres** — We have the files |
| **Chairman Review Format** | Live 30-min call vs Async doc review vs Hybrid | **Async doc + 15-min call** — Respects Chairman time |

### Chairman Action Required
Confirm sprint start date, staging platform, review format → Hermes kicks off Day 1 tasks.

---

## DEC-20250721-004: Pricing & Packaging

**Status:** ⏳ **PENDING CHAIRMAN REVIEW**  
**Date:** 2025-07-21  
**Document:** `SPEC.md` Section 6  
**Review Deadline:** 2025-07-23 (with SPEC review)

### Summary
Four-tier subscription + transaction fees + wellness add-on + professional services.

### Key Decisions Needed

| Decision Point | Current Spec | Alternatives | Hermes Recommendation |
|----------------|--------------|--------------|----------------------|
| **Starter Price** | $49/mo | $29/mo (micro) / $79/mo | **$49** — Covers costs, signals value |
| **Pro Price** | $199/mo | $299/mo / $149/mo | **$199** — Sweet spot for 10-30 guide ops |
| **Enterprise Price** | $499/mo | $799/mo / $999/mo | **$499** — Leave room for custom enterprise |
| **Wellness Add-on** | $199/mo + 15% rev share | $99/mo flat / 25% rev share | **$199 + 15%** — Recurring + upside |
| **Transaction Fees** | Pass-through (Stripe 2.9%/PayHere 3.5%) | Platform fee + gateway | **Pass-through** — Transparent, operators prefer |
| **Annual Discount** | 20% (standard) | 15% / 25% / None | **20%** — Industry standard, improves cash flow |

### Chairman Action Required
Confirm or adjust prices → Hermes updates SPEC.md v1.1 → Sprint 1 builds billing per approved pricing.

---

## DEC-20250721-005: Tech Stack Confirmation

**Status:** ⏳ **PENDING CHAIRMAN REVIEW**  
**Date:** 2025-07-21  
**Review Deadline:** 2025-07-22 (before Sprint 0 Day 1)

### Summary
Lock core technology choices to prevent mid-sprint changes.

### Stack Decisions

| Layer | Choice | Alternatives Considered | Rationale |
|-------|--------|------------------------|-----------|
| **API Framework** | **FastAPI** (Python 3.12) | Node/Express, Go/Gin, Django | Async, OpenAPI, Pydantic, ML ecosystem |
| **Agent Orchestration** | **LangGraph** | AutoGen, CrewAI, Custom | Graph-based, stateful, human-in-loop, production-ready |
| **LLM Provider** | **OpenRouter** (Nemotron 3 Ultra, Claude 3.5 Sonnet, GPT-4o) | Direct Anthropic, Direct OpenAI, Local (Ollama) | Model flexibility, cost optimization, fallback |
| **Database** | **PostgreSQL 16** (AsyncPG) | MySQL, MongoDB, PlanetScale | RLS, JSONB, maturity, extensions |
| **Cache/Queue** | **Redis 7** (Valkey compatible) | RabbitMQ, Kafka, SQS | Pub/sub, streams, sorted sets, simple |
| **MCP Server** | **FastMCP** (Python) | Custom, TypeScript SDK | Your existing skill, Python ecosystem |
| **Frontend (Dashboard)** | **React 18 + TypeScript + Vite + Tailwind** | Vue, Svelte, Next.js | Hiring pool, component libs, performance |
| **Deployment** | **Railway (Staging) → Hetzner VPS + Coolify (Prod)** | Render, Fly.io, AWS, GCP | Cost control, data sovereignty (SL), simplicity |
| **Observability** | **Grafana Cloud (Free) + Loki + Prometheus + PostHog** | Datadog, New Relic, Honeycomb | Free tier generous, self-hostable, unified |
| **CI/CD** | **GitHub Actions** | GitLab CI, CircleCI, Jenkins | Free for private, OIDC, matrix builds |
| **Auth** | **JWT + bcrypt + Pydantic Settings** | Auth0, Clerk, Supabase Auth | Zero cost, full control, multi-tenant RLS |
| **Payments** | **Stripe (Intl) + PayHere (LK)** | Dlocal, Rapyd, Manual only | Coverage: Cards + LKR wallets + Bank transfer |

### Chairman Action Required
Confirm stack → Hermes documents in `ARCHITECTURE.md` → Sprint 0 Day 1 uses these exact versions.

---

## TEMPLATE: New Decision Request

```markdown
# DEC-{YYYYMMDD}-{topic}

**Status:** ⏳ Pending Review  
**Date:** {YYYY-MM-DD}  
**Requested By:** Hermes / Chairman  
**Deadline:** {YYYY-MM-DD} ({24h/48h/1 week})

## Context
[2-3 sentences: what changed, why decision needed now]

## Options
| Option | Description | Pros | Cons | Cost | Timeline | Recommendation |
|--------|-------------|------|------|------|----------|----------------|
| A | ... | ... | ... | $X | Y days | ✅ / ❌ |
| B | ... | ... | ... | $X | Y days | |
| C | ... | ... | ... | $X | Y days | |

## Hermes Recommendation
[1 paragraph with reasoning]

## Chairman Decision
[ ] Approve Option A
[ ] Approve Option B
[ ] Approve Option C
[ ] Defer — Need: ___________
[ ] Reject — Reason: ___________

**Signed:** _________________________  **Date:** _______________
```