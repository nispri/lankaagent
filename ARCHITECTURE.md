# LankaAgent — Architecture Decision Record (ADR)

**Version:** 1.0  
**Status:** Draft — Pending Chairman Confirmation (DEC-20250721-005)  
**Related:** SPEC.md, SPRINT-00.md, DECISION-LOG.md

---

## 1. System Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LANKAAGENT PLATFORM                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   CHANNELS  │  │   GATEWAY   │  │  CORE       │  │  DATA & INTEGRATIONS│  │
│  │             │  │             │  │  SERVICES   │  │                     │  │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────────────┤  │
│  │ WhatsApp    │──►│  FastAPI    │──►│  Travel     │──►│ PostgreSQL 16       │  │
│  │ Business API│   │  (API GW)   │   │  Agent      │   │ + pgvector        │  │
│  │ (Twilio)    │   │  Auth       │   │  (LangGraph)│   │ Multi-tenant RLS  │  │
│  ├─────────────┤   │  Rate Limit │   ├─────────────┤   ├─────────────────────┤  │
│  │ Web Widget  │   │  Router     │   │ Operator    │   │ Redis 7           │  │
│  │ (React)     │   │  Webhooks   │   │  CRM        │   │ Cache + Streams   │  │
│  ├─────────────┤   └─────────────┘   ├─────────────┤   ├─────────────────────┤  │
│  │ Email       │                      │ Wellness    │   │ MCP Server        │  │
│  │ Forward     │                      │ Engine      │   │ (FastMCP)         │  │
│  └─────────────┘                      └─────────────┘   ├─────────────────────┤  │
│                                                          │ Payments          │  │
│                                                          │ Stripe + PayHere  │  │
│                                                          ├─────────────────────┤  │
│                                                          │ External APIs     │  │
│                                                          │ Google Cal, Maps  │  │
│                                                          └─────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 API Gateway (FastAPI)
| Aspect | Decision |
|--------|----------|
| **Framework** | FastAPI 0.110+ (Python 3.12) |
| **Async** | Full async (AsyncPG, Redis-py async, HTTPX) |
| **Validation** | Pydantic v2 (strict mode) |
| **Auth** | JWT (RS256) + API Keys for webhooks |
| **Multi-tenancy** | Header-based tenant resolution → Postgres RLS |
| **Rate Limiting** | Redis token bucket (per-tenant, per-endpoint) |
| **OpenAPI** | Auto-generated, served at `/docs`, `/redoc` |
| **Error Handling** | RFC 7807 Problem Details + Sentry capture |

**Key Middleware Stack:**
```
Request → Correlation ID → Tenant Resolution → Auth → Rate Limit → Route → Response
                ↓                                              ↓
            Logging                                         Error Handler
```

### 2.2 Travel Agent (LangGraph)
| Aspect | Decision |
|--------|----------|
| **Orchestration** | LangGraph (StateGraph) — not LangChain AgentExecutor |
| **State Schema** | TypedDict with Pydantic validation at each node |
| **Checkpointing** | PostgresSaver (async) — full conversation history |
| **Human-in-Loop** | `interrupt()` at quote presentation → Operator approval |
| **Tools** | Structured tools (Pydantic args/returns) — no raw function calling |
| **LLM Provider** | OpenRouter (multi-model, fallback chain) |
| **Models** | Primary: Nemotron 3 Ultra (code/reasoning) / Fallback: Claude 3.5 Sonnet / GPT-4o |
| **Temperature** | 0.1 (deterministic) for extraction, 0.7 for generation |
| **Multilingual** | Single graph, language in state → Prompt templates per language |

**Node Types:**
| Node | Type | Tools Called |
|------|------|--------------|
| `classify_intent` | LLM (structured) | — |
| `extract_entities` | LLM (structured) | — |
| `build_itinerary` | Tool-calling LLM | `mcp.search_attractions`, `mcp.get_pricing`, `mcp.get_transport`, `crm.check_availability` |
| `present_quote` | Template (Jinja2 + i18n) | — |
| `wellness_upsell` | Tool-calling LLM | `wellness.match_protocol`, `crm.get_wellness_inventory` |
| `payment_flow` | Tool-calling LLM | `payments.create_intent`, `payments.verify_webhook` |
| `confirm_booking` | Tool-calling LLM | `crm.create_booking`, `calendar.sync`, `notifications.send` |
| `follow_up` | Tool-calling LLM | `docs.generate_visa`, `docs.generate_packing`, `notifications.schedule` |

### 2.3 Operator CRM (FastAPI + SQLAlchemy)
| Aspect | Decision |
|--------|----------|
| **ORM** | SQLAlchemy 2.0 (async) + Alembic migrations |
| **Multi-tenancy** | Row-Level Security (RLS) — `SET app.current_tenant = 'tenant_id'` |
| **Schema** | Single schema, `tenant_id` on every table, RLS policies enforce isolation |
| **Migrations** | Alembic (async) — run at container startup |
| **Seeding** | Demo tenant + sample data for staging |

**Core Tables (RLS Enabled):**
```sql
-- All tables have tenant_id UUID NOT NULL
CREATE TABLE operators (id, tenant_id, name, slug, sltda_license, settings, subscription, created_at);
CREATE TABLE leads (id, tenant_id, source, contact, status, intent, conversation_id, assigned_guide, created_at);
CREATE TABLE itineraries (id, tenant_id, lead_id, version, status, days, pricing, valid_until, accepted_at);
CREATE TABLE bookings (id, tenant_id, itinerary_id, lead_id, status, payment, travelers, documents, calendar_events);
CREATE TABLE wellness_protocols (id, tenant_id, booking_id, intake, matched_doctor, protocol, followup_schedule);
CREATE TABLE guides (id, tenant_id, name, languages, specialties, calendar_id, active);
CREATE TABLE audit_logs (id, tenant_id, user_id, action, entity_type, entity_id, old, new, created_at);
```

### 2.4 Wellness Engine
| Aspect | Decision |
|--------|----------|
| **Architecture** | Rule-based matching + LLM enrichment |
| **Rules Engine** | Python `business-rules` library (declarative, auditable) |
| **Doctor Matching** | Weighted scoring: specialty, language, availability, rating, proximity |
| **Protocol Templates** | YAML files (versioned) — Ayurveda, Panchakarma, Yoga, Meditation |
| **Compliance** | Medical disclaimer, informed consent, data encryption at rest |

### 2.5 MCP Tourism Server (FastMCP)
| Aspect | Decision |
|--------|----------|
| **Framework** | FastMCP 0.2+ (Python) |
| **Transport** | HTTP (Streamable HTTP) — not stdio |
| **Auth** | API Key header (validated by API Gateway) |
| **Data Sources** | PostgreSQL (SLTDA stats, attractions, pricing, visa rules) |
| **Tools** | 12 tools (see SPEC.md Section 3.2) |
| **Caching** | Redis (TTL: stats=1h, attractions=24h, pricing=6h) |
| **Versioning** | Semantic version in tool descriptions |

**Tool Catalog:**
| Tool | Description | Cache TTL |
|------|-------------|-----------|
| `search_attractions` | Filter by province, type, rating, season | 24h |
| `get_attraction_details` | Full description, hours, pricing, accessibility | 24h |
| `get_seasonal_pricing` | Peak/shoulder/low rates for accommodation/activities | 6h |
| `get_transport_options` | Routes, duration, cost, operators (car/train/flight/domestic) | 24h |
| `get_visa_requirements` | By nationality, entry type, duration | 168h (1 week) |
| `get_weather_forecast` | 7-day forecast for destination | 3h |
| `get_tourism_statistics` | Arrivals by country/month, trends, forecasts | 1h |
| `check_operator_availability` | Real-time calendar check for specific operator | 5min |
| `get_ayurveda_centers` | SLTDA-licensed centers with specialties, doctors | 24h |
| `get_festival_calendar` | Poya days, cultural festivals, closures | 168h |
| `calculate_route_time` | Travel time between attractions (road conditions) | 24h |
| `get_emergency_contacts` | Hospitals, police, tourist police, embassies | 168h |

### 2.6 Payments
| Aspect | Decision |
|--------|----------|
| **International** | Stripe (Cards, Wallets, Bank Redirects) — USD, EUR, GBP, AUD, CAD |
| **Local (LKR)** | PayHere (Visa/Mastercard, LankaPay, Genie, Frimi, EzCash) |
| **Split Payments** | Stripe Connect (Platform) — Operator gets net, platform takes commission |
| **Webhooks** | Idempotent processing (event ID dedup) → Booking confirmation |
| **Refunds** | Operator-initiated (dashboard) → Platform approval (SEV-2) |
| **Invoicing** | Auto-generated PDF (operator branding) → Email + WhatsApp |
| **Reconciliation** | Daily cron → Stripe/PayHere balance → Postgres → Operator payout report |

---

## 3. Data Flow Patterns

### 3.1 Inbound Message (WhatsApp → Agent → Reply)
```
1. Twilio Webhook → /webhook/whatsapp
2. Verify Twilio signature (HMAC)
3. Extract: tenant (from phone number), message, media
4. Resolve/create Lead (tenant_id, contact, source=whatsapp)
5. Load Conversation State (LangGraph PostgresSaver)
6. Invoke Agent Graph (async, stream tokens)
7. Agent executes nodes → Tools → State updates
8. Final state → Render reply (template + i18n)
9. Send via Twilio API (async, fire-and-forget)
10. Persist message to audit_log
```
**Latency Budget:** <3s end-to-end (P95)

### 3.2 Booking Confirmation (Payment → Booking → Docs → Calendar)
```
1. Payment Webhook (Stripe/PayHere) → /webhook/payments
2. Verify signature → Idempotency check
3. Load Booking (pending_payment status)
4. Update payment status → confirmed
5. Create Booking record (CRM)
6. Sync to Google Calendar (async task)
7. Generate Documents (PDF): Voucher, Visa Letter, Packing List
8. Send Notifications (parallel):
   - WhatsApp (Traveler, Operator, Guide)
   - Email (Traveler, Operator)
   - SMS (Traveler - backup)
9. Schedule Follow-up Tasks (30d, 7d, 1d reminders)
10. Emit Analytics Event (booking_confirmed)
```
**Consistency:** Eventual (async tasks) — Booking record = source of truth

### 3.3 Multi-Tenant Data Isolation
```
Request → Middleware: resolve_tenant()
  → Header: X-Tenant-ID (dashboard) OR phone_number_mapping (WhatsApp)
  → SET LOCAL app.current_tenant = 'tenant-uuid'
  → All subsequent queries auto-filtered by RLS
  → RESET at end of request
```
**Security:** RLS policies on ALL tables — `tenant_id = current_setting('app.current_tenant')::uuid`

---

## 4. Infrastructure Architecture

### 4.1 Environments
| Env | Purpose | Infra | Data |
|-----|---------|-------|------|
| **Local** | Dev (Docker Compose) | Laptop/WSL2 | Synthetic |
| **Staging** | Integration + Demo | Railway (free tier) | Anonymized production subset |
| **Production** | Live | Hetzner VPS (CX42) + Coolify | Real (encrypted) |

### 4.2 Production Topology (Hetzner + Coolify)
```
┌─────────────────────────────────────────────────────────────┐
│                    HETZNER CX42 (8 vCPU, 16GB, 160GB NVMe)   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    COOLIFY (Docker Manager)          │    │
│  ├──────────────┬──────────────┬──────────────┬────────┤    │
│  │   API (x2)   │  Worker (x2) │   MCP (x1)    │ Dashboard│    │
│  │  2GB/1CPU    │  2GB/1CPU    │  1GB/0.5CPU   │ 512MB   │    │
│  ├──────────────┼──────────────┼──────────────┼────────┤    │
│  │ Postgres 16  │   Redis 7    │  Grafana     │ Prometheus│    │
│  │ 4GB/2CPU     │  1GB/0.5CPU  │  512MB       │ 512MB    │    │
│  ├──────────────┼──────────────┼──────────────┼────────┤    │
│  │    Loki      │   Nginx      │  Certbot     │  PostHog │    │
│  │  512MB       │  128MB       │  64MB        │ 1GB/0.5C │    │
│  └──────────────┴──────────────┴──────────────┴────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
             ┌──────────┐    ┌──────────┐
             │ Wasabi   │    │  Uptime  │
             │ S3 (Bkp) │    │ Robot    │
             └──────────┘    └──────────┘
```

**Estimated Monthly Cost:** ~$45/mo (Hetzner CX42 $35 + Wasabi $5 + Domain $5)

### 4.3 Backup & Disaster Recovery
| Component | RPO | RTO | Method |
|-----------|-----|-----|--------|
| **PostgreSQL** | 1 hour | 2 hours | Continuous WAL-G to Wasabi S3 + Daily pg_dump |
| **Redis** | 24 hours | 1 hour | RDB snapshots to Wasabi (acceptable loss — cache) |
| **Application Code** | 0 | 0 | GitHub (source of truth) |
| **MCP Data** | 24 hours | 4 hours | Rebuild from SLTDA sources (deterministic) |
| **Secrets** | 0 | 0 | 1Password (source) → Coolify env vars |

**DR Test:** Monthly (first Sunday) — Restore staging from backup, verify data integrity

---

## 5. Security Architecture

### 5.1 Network
- **VPC:** Hetzner Private Network (isolated from internet)
- **Ingress:** Nginx only (ports 80/443) → Internal services via service mesh (Coolify internal DNS)
- **Egress:** Restricted — Only API endpoints (Meta, Stripe, PayHere, Google, OpenRouter)
- **Database:** No public access — Only API/Worker/MCP containers

### 5.2 Application Security
| Control | Implementation |
|---------|----------------|
| **Authentication** | JWT (RS256, 30min access, 7d refresh) + API Keys (webhooks) |
| **Authorization** | RBAC (Owner, Admin, Manager, Guide, Viewer) + RLS |
| **Secrets** | 1Password → Coolify Env Vars (never in code, never in logs) |
| **Encryption** | TLS 1.3 (Let's Encrypt), AES-256 at rest (Postgres TDE), Field-level for PII |
| **Input Validation** | Pydantic strict mode on ALL inputs |
| **Rate Limiting** | Per-tenant, per-endpoint, per-IP (Redis token bucket) |
| **Audit Logging** | Every mutating operation → audit_logs table (immutable) |
| **Vulnerability Scanning** | Trivy (CI), Dependabot (weekly), Snyk (PR checks) |

### 5.3 Data Privacy (Sri Lanka + GDPR)
| Requirement | Implementation |
|-------------|----------------|
| **PDPA (Sri Lanka)** | Consent records, Purpose limitation, 2-year retention max, Right to erasure API |
| **GDPR** | DPA with subprocessors (Stripe, Twilio, OpenRouter), DPIA for wellness health data |
| **Health Data (Wellness)** | Separate encryption key, Access logging, Doctor-only decryption, Auto-expiry 90 days post-trip |
| **Data Residency** | Primary: Hetzner Falkenstein (Germany) — Adequacy decision. Backup: Wasabi EU Central |

---

## 6. Observability

### 6.1 Metrics (Prometheus + Grafana)
| Dashboard | Key Metrics |
|-----------|-------------|
| **System** | CPU, Memory, Disk, Network, Container restarts |
| **API** | RPS, Latency (p50/p95/p99), Error rate, Active tenants |
| **Agent** | Conversations/min, Tool calls, LLM tokens, Hallucination rate (eval) |
| **Business** | MRR, Active operators, Leads→Bookings funnel, Churn, Wellness attach rate |
| **Payments** | Success rate, Volume, Refund rate, Payout latency |

### 6.2 Logging (Loki + Structured JSON)
```json
{
  "timestamp": "2025-07-21T10:30:00.123Z",
  "level": "INFO",
  "service": "api",
  "trace_id": "abc123",
  "span_id": "def456",
  "tenant_id": "tenant-uuid",
  "user_id": "user-uuid",
  "message": "Booking confirmed",
  "context": {"booking_id": "...", "amount": 2847, "currency": "USD"}
}
```

### 6.3 Tracing (Future: Tempo)
- Currently: Correlation IDs passed through all services
- Phase 2: OpenTelemetry → Tempo (Grafana Cloud free tier)

### 6.4 Alerting (Grafana Alertmanager → Telegram)
| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| **API Down** | Health check fails 3x | SEV-1 | Telegram + Phone |
| **High Error Rate** | 5xx > 5% for 5min | SEV-2 | Telegram |
| **Queue Backlog** | Worker queue > 100 for 10min | SEV-2 | Telegram |
| **Payment Failure** | Webhook verification fails | SEV-2 | Telegram |
| **Low Disk** | >80% | SEV-3 | Telegram (daily) |
| **MRR Drop** | Day-over-day >10% | SEV-3 | Daily Briefing |

---

## 7. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
stages:
  - lint:        ruff, mypy, bandit, hadolint (Dockerfile)
  - test:        pytest (unit + integration) → coverage >80%
  - security:    trivy (image), dependabot (deps), secret scan
  - build:       docker buildx (multi-arch: amd64/arm64) → GHCR
  - deploy-staging:  auto on main → Railway (preview URL)
  - deploy-prod:   manual approval → Coolify (Hetzner) → Health checks → Traffic switch
```

**Branch Strategy:** `main` (protected) → `feature/*` → PR → Review → Merge → Auto-deploy staging

---

## 8. Development Standards

| Standard | Tool | Config |
|----------|------|--------|
| **Python** | 3.12 | `pyproject.toml` (uv) |
| **Formatting** | Ruff | `line-length=100`, `target-version=py312` |
| **Type Checking** | Mypy | `strict=true`, `warn_unused_ignores=true` |
| **Testing** | Pytest | `asyncio`, `pytest-cov`, `pytest-mock` |
| **Pre-commit** | Ruff + Mypy + Bandit | `.pre-commit-config.yaml` |
| **API Contract** | OpenAPI 3.1 | Generated from FastAPI → Spectral lint |
| **Database Migrations** | Alembic | `alembic.ini` + env.py (async) |
| **Documentation** | MkDocs Material | `docs/` → GitHub Pages |

---

## 9. Open Architecture Decisions (Need Chairman Input)

| ADR | Topic | Options | Recommendation | Deadline |
|-----|-------|---------|----------------|----------|
| ADR-001 | **Legal Entity Jurisdiction** | US LLC (Stripe Atlas) vs Singapore Pte Ltd vs Sri Lanka Pvt Ltd | **US LLC + SL Branch** — Banking, Stripe, IP protection | Sprint 0 |
| ADR-002 | **Primary Data Region** | EU (Hetzner) vs Singapore vs Sri Lanka (Dialog/AWS) | **EU (Hetzner)** — GDPR adequacy, latency acceptable | Sprint 0 |
| ADR-003 | **LLM Provider Strategy** | OpenRouter (multi) vs Direct Anthropic + OpenAI vs Local (Ollama) | **OpenRouter** — Flexibility, cost, fallback | Sprint 0 |
| ADR-004 | **WhatsApp Provider** | Meta Direct (slow approval) vs Twilio (instant sandbox) vs Gupshup | **Twilio** — Start now, migrate to Meta Direct later | Sprint 1 |
| ADR-005 | **Frontend Framework** | React + Vite vs Next.js vs SvelteKit | **React + Vite** — Team familiarity, hiring pool | Sprint 1 |
| ADR-006 | **Real-time Updates** | WebSocket (native) vs Server-Sent Events vs Polling | **WebSocket (FastAPI)** — Bidirectional, low latency | Sprint 2 |
| ADR-007 | **Search/Discovery** | Postgres FTS vs Meilisearch vs Typesense | **Postgres FTS + pg_trgm** — Zero infra, good enough | Sprint 2 |
| ADR-008 | **Email Provider** | SendGrid vs Mailgun vs Postmark vs AWS SES | **Postmark** — Best deliverability, simple API | Sprint 1 |

---

## 10. Appendix

### 10.1 Repository Structure
```
lankaagent/
├── .github/workflows/          # CI/CD
├── api/                        # FastAPI Gateway + CRM
│   ├── app/
│   │   ├── api/               # Routes (v1/)
│   │   ├── core/              # Config, Security, Database
│   │   ├── models/            # SQLAlchemy + Pydantic
│   │   ├── services/          # Business logic
│   │   ├── agents/            # LangGraph Travel Agent
│   │   ├── integrations/      # WhatsApp, Payments, Calendar
│   │   └── utils/
│   ├── tests/
│   ├── Dockerfile.api
│   └── pyproject.toml
├── worker/                     # Background Worker (Celery-style, custom)
│   ├── tasks/
│   ├── Dockerfile.worker
│   └── pyproject.toml
├── mcp_servers/               # FastMCP Tourism Server
│   ├── tourism/
│   ├── Dockerfile
│   └── pyproject.toml
├── dashboard/                 # React + Vite + TypeScript
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── nginx/                     # Reverse Proxy Config
├── observability/             # Grafana, Prometheus, Loki Config
├── init-sql/                  # Postgres Init (RLS, Extensions)
├── sprints/                   # Sprint Plans
├── decisions/                 # Decision Logs
├── docs/                      # MkDocs Site
├── docker-compose.yml         # Local Dev
├── docker-compose.staging.yml # Staging Override
├── docker-compose.prod.yml    # Production Override (Coolify uses this)
├── .env.example
├── Makefile                   # Common Commands
├── README.md
├── GOVERNANCE.md
├── SPEC.md
└── ARCHITECTURE.md (this file)
```

### 10.2 Key Dependencies (Pinned)
```toml
# api/pyproject.toml (core)
fastapi = "0.110.1"
uvicorn = "0.29.0"
sqlalchemy = "2.0.30"
asyncpg = "0.29.0"
redis = "5.0.1"
pydantic = "2.7.1"
pydantic-settings = "2.3.3"
python-jose = "3.3.0"
passlib = "1.7.4"
bcrypt = "4.1.2"
langgraph = "0.1.20"
langchain-core = "0.2.35"
langchain-openai = "0.1.20"  # OpenRouter compatible
httpx = "0.27.0"
tenacity = "8.2.3"
structlog = "24.1.0"
prometheus-client = "0.19.0"
posthog = "3.5.0"
stripe = "7.8.0"
twilio = "8.10.0"
google-auth = "2.29.0"
google-api-python-client = "2.118.0"
python-multipart = "0.0.9"
jinja2 = "3.1.4"
babili18n = "0.3.0"  # or custom i18n
alembic = "1.12.0"
pytest = "8.2.0"
pytest-asyncio = "0.23.0"
pytest-cov = "4.1.0"
ruff = "0.4.4"
mypy = "1.10.0"
```

---

**Document Control**
- **Next Review:** Sprint 1 Planning (with SPEC.md approval)
- **Version History:** v1.0 — Initial Draft (Hermes)
- **Approval:** [ ] Chairman Approved — Date: ___________

*Prepared by Hermes Agent — Chief of Staff*  
*For: Nishantha Priyadarshana — Chairman & CEO, LankaAgent*