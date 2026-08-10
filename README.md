# LankaAgent — AI Travel Concierge for Sri Lanka Tour Operators

[![CI](https://github.com/nispri/lankaagent/workflows/CI/badge.svg)](https://github.com/nispri/lankaagent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Turn WhatsApp inquiries into confirmed bookings while you sleep.**

LankaAgent is a multi-tenant SaaS platform that gives Sri Lanka tour operators a 24/7 AI-powered travel concierge. It handles inquiries in 12 languages, builds custom itineraries instantly, collects payments, and syncs everything to the operator's calendar — all via WhatsApp, web widget, or email.

---

## 🎯 The Problem

- **2,000+ SLTDA-registered operators** lose 40-60% of leads to slow response (avg 4-12 hours)
- **No 24/7 multilingual support** — key markets (Russia, Germany, China, India, UK) inquire outside SL business hours
- **Manual itinerary building** takes 30-60 minutes per inquiry
- **No integrated payments** — operators chase bank transfer screenshots
- **Wellness/Ayurveda upsell ignored** — high-value revenue left on the table

---

## 💡 The Solution

```
Traveler (WhatsApp, 2 AM, Russian)
        │
        ▼
┌─────────────────────────────────────┐
│     LANKAAGENT AI CONCIERGE         │
│  • Instant reply in traveler's lang │
│  • Builds custom itinerary in 3 sec │
│  • Presents interactive quote       │
│  • Collects deposit (Stripe/PayHere)│
│  • Sends visa docs, packing list    │
│  • Upsells Ayurveda wellness        │
└─────────────────────────────────────┘
        │
        ▼
Operator Dashboard: Lead → Quote → Booking → Calendar (auto-synced)
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **24/7 WhatsApp AI Agent** | Replies in 12 languages (EN/SI/TA/RU/DE/ZH/FR/AR/JA/KO/IT/ES) |
| **Instant Itinerary Builder** | MCP-powered: real SL attractions, seasonal pricing, transport options |
| **Custom Tour Pricing** | Quotes 5/7/10/14-day itineraries with exact USD from real hotel rates |
| **Voice Chat (Anuki speaks)** | Edge neural TTS + Whisper STT — mic input and spoken replies in any browser |
| **Multi-Currency Payments** | Stripe (USD/EUR/GBP) + PayHere (LKR) + Bank Transfer fallback |
| **Operator Dashboard** | Leads, Conversations, Itineraries, Bookings, Calendar, Analytics |
| **Wellness/Ayurveda Engine** | Health intake → Protocol match → BIMARI doctor assign → Post-care |
| **SLTDA Compliance** | TDL integration, license verification, arrival stats |
| **White-Label Ready** | Custom domain, branding, operator's own WhatsApp number |
| **Multi-Tenant Architecture** | Complete data isolation via PostgreSQL RLS |

---

## 🏗 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│  CHANNELS   │────►│  API GATEWAY │────►│  CORE SERVICES   │
│ WhatsApp    │     │  (FastAPI)   │     │  • Travel Agent  │
│ Web Widget  │     │  Auth, Rate  │     │  • Operator CRM  │
│ Email       │     │  Limit, RLS  │     │  • Wellness Eng  │
└─────────────┘     └─────────────┘     └────────┬─────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    ▼                            ▼                            ▼
             ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
             │  POSTGRES   │              │    REDIS    │              │   MCP       │
             │  16 + RLS   │              │  Cache/Queue│              │  (FastMCP)  │
             │  Multi-tenant│              │  Celery-like│              │  Tourism    │
             └─────────────┘              └─────────────┘              │  Data       │
                                                                        └─────────────┘
```

**Stack:** FastAPI · LangGraph · PostgreSQL 16 · Redis 7 · React 18 · Docker · Railway/Coolify

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Make (optional, for shortcuts)
- Python 3.12+ (for local development without Docker)

### 1. Clone & Configure
```bash
git clone https://github.com/nispri/lankaagent
cd lankaagent

cp .env.example .env
# Edit .env with your keys (see Configuration below)
```

### 2. Start All Services
```bash
make up
# or: docker compose up -d --build
```

### 3. Verify Health
```bash
make health
# Expected: All services ✅
```

### 4. Access Services
| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | — |
| Dashboard | http://localhost:3000 | — |
| Grafana | http://localhost:3001 | admin / `GRAFANA_PASSWORD` |
| Prometheus | http://localhost:9090 | — |
| MCP Server | http://localhost:8001 | — |

### 5. Run Tests
```bash
make test
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in:

### Required for Full Functionality
| Variable | Source | Purpose |
|----------|--------|---------|
| `TWILIO_ACCOUNT_SID` / `AUTH_TOKEN` | [Twilio Console](https://console.twilio.com) | WhatsApp Sandbox / Production |
| `STRIPE_SECRET_KEY` | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) | International payments |
| `PAYHERE_MERCHANT_ID` / `SECRET` | [PayHere Settings](https://www.payhere.lk/merchant/settings) | LKR payments |
| `ZEN_API_KEY` | [OpenCode Zen](https://opencode.ai/auth) | **Primary LLM** (deepseek-v4-flash-free, free) |
| `OPENROUTER_API_KEY` | [OpenRouter](https://openrouter.ai/keys) | LLM fallback provider |
| `GOOGLE_CALENDAR_CLIENT_ID/SECRET` | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) | Calendar sync |
| `POSTHOG_API_KEY` | [PostHog](https://app.posthog.com/project/settings) | Analytics |
| `SENTRY_DSN` | [Sentry](https://sentry.io/settings/projects/) | Error tracking |

### Development Only (Optional)
- `MOCK_EXTERNAL_APIS=true` — Skip external calls in tests
- `NGROK_URL` — For local webhook testing

---

## 📁 Project Structure

```
lankaagent/
├── .github/workflows/          # CI/CD pipelines
├── api/                        # FastAPI Gateway + CRM + Agent
│   ├── app/
│   │   ├── api/v1/            # Routes (leads, bookings, conversations)
│   │   ├── agents/            # LangGraph Travel Agent
│   │   ├── core/              # Config, Security, Database
│   │   ├── integrations/      # WhatsApp, Payments, Calendar
│   │   ├── models/            # SQLAlchemy + Pydantic
│   │   └── services/          # Business logic
│   ├── tests/
│   ├── Dockerfile.api
│   └── pyproject.toml
├── worker/                     # Background Worker
│   ├── tasks/
│   ├── Dockerfile.worker
│   └── pyproject.toml
├── mcp_servers/               # FastMCP Tourism Data Server
│   ├── tourism/
│   ├── Dockerfile
│   └── pyproject.toml
├── dashboard/                 # React + TypeScript + Vite
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── nginx/                     # Reverse Proxy Config
├── observability/             # Grafana, Prometheus, Loki Config
├── init-sql/                  # Postgres Init (RLS, Extensions)
├── sprints/                   # Sprint Plans (SPRINT-00.md, etc.)
├── decisions/                 # Decision Logs (DECISION-LOG.md)
├── docs/                      # MkDocs Documentation Site
├── docker-compose.yml         # Local Development
├── docker-compose.staging.yml # Staging Override
├── docker-compose.prod.yml    # Production Override
├── Makefile                   # Common Commands
├── .env.example               # Environment Template
├── GOVERNANCE.md              # Operating Model
├── SPEC.md                    # Product Specification
├── ARCHITECTURE.md            # Technical Architecture
└── README.md                  # This File
```

---

## 🧪 Testing

```bash
# All tests (API + pricing engine)
docker exec lankaagent-api python -m pytest tests/test_api.py tests/test_tour_pricing.py -v

# Unit only (fast)
make test-unit

# Integration (requires services running)
make test-integration

# Coverage report
docker compose exec api pytest --cov=app --cov-report=html
```

> **Note:** after any `docker compose` recreate, tests dir is wiped — re-copy:
> `docker cp C:/Users/nishanthap/lankaagent/tests lankaagent-api:/app/tests`
> Current suite: **14 passed, 1 xfailed** (9 API + 5 pricing; the xfail is a known async SQLAlchemy cleanup).

---

## 📦 Deployment

### Staging (Auto on Push to Main)
- **Platform:** Railway
- **URL:** https://lankaagent-staging.railway.app
- **Trigger:** Push to `main` branch

### Production (Manual Approval)
- **Platform:** Hetzner VPS + Coolify
- **Domain:** api.lankaagent.com / app.lankaagent.com
- **Trigger:** GitHub Actions workflow dispatch (Chairman approval required)

```bash
# Manual production deploy (after approval)
gh workflow run deploy-prod.yml -f environment=production
```

---

## 📊 Monitoring & Observability

| Tool | Purpose | Access |
|------|---------|--------|
| **Grafana** | System/Business Dashboards | http://localhost:3001 |
| **Prometheus** | Metrics Collection | http://localhost:9090 |
| **Loki** | Log Aggregation | Grafana → Explore |
| **PostHog** | Product Analytics | https://app.posthog.com |
| **Sentry** | Error Tracking | https://sentry.io |

**Key Dashboards:**
- System: CPU, Memory, Disk, Network, Container Health
- Application: Request Rate, Latency (p50/p95/p99), Error Rate, Active Tenants
- Business: Leads/Day, Conversion Funnel, MRR, Churn, Revenue/Tenant
- Agent: Conversation Length, Tool Calls, Token Usage, Hallucination Rate

---

## 🔐 Security

- **Multi-tenancy:** PostgreSQL Row Level Security (RLS) — zero data leakage
- **Auth:** JWT (RS256 in prod) + API Keys for webhooks
- **Secrets:** 1Password (dev) / Coolify Secrets (prod) — never in code
- **Rate Limiting:** Per-tenant, per-endpoint (Redis token bucket)
- **CORS:** Strict allowlist per environment
- **Dependencies:** `pip-audit` + `safety` in CI, Dependabot alerts

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SPEC.md](SPEC.md) | Product Specification (Vision, ICP, Pricing, Roadmap) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical Architecture (Components, Data Flow, ADRs) |
| [GOVERNANCE.md](GOVERNANCE.md) | Operating Model (Roles, Decisions, Escalation) |
| [SPRINT-00.md](sprints/SPRINT-00.md) | Sprint 0 Plan (Foundation) |
| [DECISION-LOG.md](decisions/DECISION-LOG.md) | Decision Register |
| [API Docs](http://localhost:8000/docs) | Interactive OpenAPI/Swagger (running) |

---

## 🤝 Contributing

This is a private commercial project. Internal contributions follow:

1. **Branch:** `feature/{ticket}-{short-desc}` or `fix/{ticket}-{short-desc}`
2. **Commit:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`)
3. **PR:** Template filled, tests passing, code review by Hermes + Chairman approval for business logic
4. **Merge:** Squash to `main` → Auto-deploy staging

---

## 📄 License

Proprietary — All Rights Reserved.  
© 2025 Nishantha Priyadarshana / LankaAgent

---

## 🙏 Acknowledgments

- **SLTDA** for tourism statistics and operator registry
- **BIMARI Naviina** for Ayurveda/wellness medical network
- **OpenCode Zen** for primary free LLM access (deepseek-v4-flash-free)
- **OpenRouter** for fallback LLM access
- **LangGraph** for production-grade agent orchestration
- **FastMCP** for elegant MCP server framework

---

**Built with ❤️ in Sri Lanka**  
*Empowering local operators to compete globally*

---

**Chairman:** Nishantha Priyadarshana  
**Chief of Staff:** Hermes Agent  
**Status:** Sprint 0 — Foundation (Days 1-7)