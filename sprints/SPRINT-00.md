# LankaAgent — Sprint 0: Foundation (Days 1-7)

**Goal:** Production-ready infrastructure, CI/CD, auth, MCP server v1, health checks — all green  
**Chairman Review:** Day 7 (Friday) — Demo: `docker compose up` → All services healthy, API docs load, MCP tools callable  
**Definition of Done:** [ ] All checks pass [ ] Chairman approves architecture [ ] Repo ready for Sprint 1 feature work

---

## Day-by-Day Plan

| Day | Focus | Deliverable | Owner | Approval |
|-----|-------|-------------|-------|----------|
| **Day 1** (Mon) | Repo Scaffold + Docker + CI | `docker compose up` works, GitHub Actions green | Dev AI | Hermes |
| **Day 2** (Tue) | PostgreSQL Schema + Migrations + RLS | Multi-tenant tables, indexes, seed data | Dev AI | Hermes |
| **Day 3** (Wed) | FastAPI Core + Auth + Health | `/health`, `/docs`, JWT auth, tenant middleware | Dev AI | Hermes |
| **Day 4** (Thu) | MCP Server v1 (Tourism Data) | 5 tools callable: operators, attractions, stats, seasons, visa | Dev AI | Chairman (data review) |
| **Day 5** (Fri) | Redis + Celery + Background Jobs | Worker processes, scheduled tasks, monitoring | Dev AI | Hermes |
| **Day 6** (Sat) | Observability Stack | Prometheus + Grafana + Loki dashboards live | Dev AI | Hermes |
| **Day 7** (Sun) | **SPRINT REVIEW** | Demo to Chairman → Approve / Pivot | All | **Chairman** |

---

## Detailed Tasks

### Day 1: Repo Scaffold + Docker + CI
- [ ] Initialize monorepo structure:
  ```
  lankaagent/
  ├── .github/workflows/ci.yml
  ├── docker-compose.yml          ✓ (done)
  ├── docker-compose.staging.yml
  ├── docker-compose.prod.yml
  ├── Makefile                    # Common commands
  ├── pyproject.toml              # Poetry config
  ├── apps/
  │   ├── api/                    # FastAPI app
  │   ├── worker/                 # Celery worker
  │   ├── dashboard/              # React/Vue dashboard
  │   └── mcp/                    # MCP server
  ├── packages/
  │   ├── shared/                 # Shared Python models, utils
  │   └── ui-components/          # Shared UI components
  ├── observability/
  │   ├── prometheus/
  │   ├── grafana/
  │   └── loki/
  ├── nginx/
  └── scripts/
  ```
- [ ] `pyproject.toml` with Poetry: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`, `pydantic-settings`, `python-jose`, `passlib`, `celery`, `redis`, `httpx`, `langgraph`, `langchain`, `posthog`, `sentry-sdk`, `pytest`, `ruff`, `mypy`
- [ ] `Dockerfile.api` + `Dockerfile.worker` + `Dockerfile.mcp` (multi-stage, non-root)
- [ ] GitHub Actions CI: Lint → Typecheck → Test → Build → Push to GHCR
- [ ] `Makefile` targets: `up`, `down`, `logs`, `shell-api`, `shell-worker`, `migrate`, `test`, `lint`

### Day 2: PostgreSQL Schema + Migrations + RLS
- [ ] Alembic init + `alembic.ini`
- [ ] Core tables (multi-tenant via Row Level Security):
  ```sql
  -- Tenants (Operators)
  CREATE TABLE tenants (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      slug TEXT UNIQUE NOT NULL,
      plan TEXT NOT NULL DEFAULT 'starter',  -- starter, professional, enterprise
      settings JSONB DEFAULT '{}',
      stripe_customer_id TEXT,
      payhere_merchant_id TEXT,
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Users (Operator staff)
  CREATE TABLE users (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      email TEXT NOT NULL,
      password_hash TEXT NOT NULL,
      full_name TEXT,
      role TEXT NOT NULL DEFAULT 'agent',  -- owner, admin, agent, viewer
      is_active BOOLEAN DEFAULT true,
      last_login_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Leads (Incoming inquiries)
  CREATE TABLE leads (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      source TEXT NOT NULL,  -- whatsapp, web_widget, email, referral
      external_id TEXT,      -- WhatsApp message ID, etc.
      contact_name TEXT,
      contact_phone TEXT,
      contact_email TEXT,
      language TEXT DEFAULT 'en',
      status TEXT DEFAULT 'new',  -- new, qualified, quoted, booked, lost
      intent JSONB DEFAULT '{}',  -- Parsed: dates, pax, budget, interests
      assigned_to UUID REFERENCES users(id),
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Conversations (WhatsApp/Web chat history)
  CREATE TABLE conversations (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
      channel TEXT NOT NULL,  -- whatsapp, web, email
      external_thread_id TEXT,
      language TEXT DEFAULT 'en',
      metadata JSONB DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Messages
  CREATE TABLE messages (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
      role TEXT NOT NULL,  -- user, assistant, system, tool
      content TEXT NOT NULL,
      tool_calls JSONB,
      tool_results JSONB,
      tokens_used INT,
      created_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Itineraries (Generated quotes)
  CREATE TABLE itineraries (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
      version INT DEFAULT 1,
      title TEXT NOT NULL,
      days JSONB NOT NULL,  -- Structured day-by-day
      total_price_usd DECIMAL(10,2),
      total_price_lkr DECIMAL(12,2),
      currency TEXT DEFAULT 'USD',
      status TEXT DEFAULT 'draft',  -- draft, sent, accepted, expired, revised
      valid_until TIMESTAMPTZ,
      created_by UUID REFERENCES users(id),  -- AI or human
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Bookings (Confirmed)
  CREATE TABLE bookings (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
      itinerary_id UUID REFERENCES itineraries(id) ON DELETE SET NULL,
      booking_reference TEXT UNIQUE NOT NULL,
      status TEXT DEFAULT 'confirmed',  -- confirmed, cancelled, completed, refunded
      travelers JSONB NOT NULL,  -- Array of traveler objects
      special_requests TEXT,
      payment_status TEXT DEFAULT 'pending',  -- pending, partial, paid, refunded
      payment_intent_id TEXT,  -- Stripe/PayHere reference
      commission_usd DECIMAL(10,2),
      commission_lkr DECIMAL(12,2),
      starts_at DATE NOT NULL,
      ends_at DATE NOT NULL,
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Payments
  CREATE TABLE payments (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
      amount_usd DECIMAL(10,2),
      amount_lkr DECIMAL(12,2),
      currency TEXT NOT NULL,
      gateway TEXT NOT NULL,  -- stripe, payhere, bank_transfer
      gateway_payment_id TEXT,
      gateway_response JSONB,
      status TEXT DEFAULT 'pending',  -- pending, succeeded, failed, refunded
      fee_usd DECIMAL(10,2),
      created_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Wellness/Ayurveda Protocols
  CREATE TABLE wellness_protocols (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
      health_intake JSONB NOT NULL,  -- Structured health questionnaire
      recommended_treatments JSONB NOT NULL,
      assigned_doctor_id UUID,  -- References BIMARI doctor directory
      status TEXT DEFAULT 'proposed',  -- proposed, accepted, in_progress, completed
      total_price_usd DECIMAL(10,2),
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );
  
  -- Analytics Events
  CREATE TABLE analytics_events (
      id BIGSERIAL PRIMARY KEY,
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
      event_name TEXT NOT NULL,
      properties JSONB DEFAULT '{}',
      user_id UUID,
      session_id TEXT,
      created_at TIMESTAMPTZ DEFAULT now()
  );
  CREATE INDEX idx_analytics_tenant_time ON analytics_events(tenant_id, created_at DESC);
  ```
- [ ] Enable RLS on all tenant tables:
  ```sql
  ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
  ALTER TABLE users ENABLE ROW LEVEL SECURITY;
  -- ... all tables
  
  CREATE POLICY tenant_isolation ON tenants
      USING (id = current_setting('app.current_tenant_id')::uuid);
  -- Repeat for each table
  ```
- [ ] Seed script: 3 demo tenants (starter/pro/enterprise), sample attractions, seasons

### Day 3: FastAPI Core + Auth + Health
- [ ] `apps/api/main.py` — FastAPI app with lifespan (startup/shutdown)
- [ ] `apps/api/core/` — Config (Pydantic Settings), Security (JWT, bcrypt), Database (AsyncEngine, Session), Redis, Logging
- [ ] `apps/api/middleware/` — Tenant resolution (subdomain/header/JWT), Request ID, Rate limiting, Error handling
- [ ] Auth endpoints: `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`, `POST /auth/register` (invite only)
- [ ] Health endpoints: `GET /health` (liveness), `GET /health/ready` (readiness - DB, Redis, MCP)
- [ ] OpenAPI tags + descriptions + examples
- [ ] Pytest: Auth flow, Tenant isolation, Health checks

### Day 4: MCP Server v1 (Tourism Data) — **CHAIRMAN REVIEW REQUIRED**
- [ ] `apps/mcp/server.py` — FastMCP server with 5 tools:
  ```python
  @mcp.tool()
  async def search_operators(
      region: str | None = None,
      specialty: str | None = None,  # wildlife, cultural, beach, wellness, adventure
      min_rating: float = 4.0
  ) -> list[Operator]:
      """Search SLTDA-registered operators by region and specialty."""
  
  @mcp.tool()
  async def get_attractions(
      province: str | None = None,
      category: str | None = None,  # nature, heritage, religious, adventure, wellness
      limit: int = 20
  ) -> list[Attraction]:
      """Get Sri Lanka attractions with descriptions, coordinates, best season."""
  
  @mcp.tool()
  async def get_seasonal_pricing(
      attraction_id: str,
      month: int
  ) -> SeasonalPricing:
      """Get peak/shoulder/low pricing for an attraction by month."""
  
  @mcp.tool()
  async def get_visa_requirements(
      nationality: str,
      purpose: str = "tourism"
  ) -> VisaInfo:
      """Visa requirements, fees, processing time, e-visa eligibility."""
  
  @mcp.tool()
  async def get_tourism_stats(
      year: int = 2024,
      month: int | None = None
  ) -> TourismStats:
      """Monthly arrivals by country, purpose, duration — from SLTDA."""
  ```
- [ ] Data sources: SLTDA Excel/CSV → PostgreSQL (ETL script in `scripts/etl_sltda.py`)
- [ ] Unit tests for each tool with mocked data
- [ ] **Chairman reviews:** Data accuracy, completeness, tool schemas

### Day 5: Redis + Celery + Background Jobs
- [ ] `apps/worker/celery_app.py` — Celery config (Redis broker, result backend)
- [ ] Tasks:
  - `send_whatsapp_message` (idempotent, retry 3x)
  - `generate_itinerary` (LangGraph agent call)
  - `process_payment_webhook` (Stripe/PayHere)
  - `sync_google_calendar` (booking → calendar)
  - `daily_analytics_rollup` (scheduled 02:00)
  - `lead_follow_up_reminder` (24h/72h no response)
- [ ] Flower monitoring (port 5555)
- [ ] Dead letter queue + retry policy

### Day 6: Observability Stack
- [ ] Prometheus `prometheus.yml` — Scrape: API, Worker, MCP, Postgres (exporter), Redis (exporter), Node (exporter)
- [ ] Grafana dashboards (provisioned):
  - **System:** CPU, Memory, Disk, Network, Container health
  - **Application:** Request rate, Latency (p50/p95/p99), Error rate, Active tenants
  - **Business:** Leads/day, Conversion funnel, MRR, Churn, Revenue/tenant
  - **Agent:** Conversation length, Tool calls, Token usage, Hallucination rate
- [ ] Loki: Log aggregation with labels (tenant, service, level)
- [ ] Alert rules: API down >1min, Error rate >5%, P95 latency >2s, Queue depth >100

### Day 7: Sprint Review — **CHAIRMAN APPROVAL GATE**
- [ ] Demo script (15 min):
  1. `make up` → All 9 containers healthy
  2. `curl /health/ready` → All deps green
  3. Swagger UI → Auth flow → Tenant-scoped API calls
  4. MCP tools called via CLI → Real SLTDA data returned
  5. Grafana dashboards live
  6. Worker processes Celery task end-to-end
- [ ] Decision Request: `decisions/DEC-20250728-sprint0-approval.md`
- [ ] Chairman: Approve / Modify / Reject → Sprint 1 planning

---

## Success Criteria (All Must Pass)

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **Infrastructure** | All 9 containers healthy >10 min | `docker compose ps` + Grafana |
| **API Health** | `/health/ready` = 200 with all deps | `curl -f` |
| **Auth** | Login → JWT → Access tenant data only | Pytest + Manual |
| **Multi-tenancy** | Tenant A cannot see Tenant B data | Pytest (RLS) |
| **MCP Tools** | 5 tools return valid data | `mcp cli call` + Chairman review |
| **Background Jobs** | Task queued → Executed → Result stored | Flower + DB check |
| **Observability** | Dashboards load, alerts fire | Grafana + Alertmanager test |
| **CI/CD** | Push to main → Build → Test → Deploy staging | GitHub Actions |

---

## Risks & Mitigations (Sprint 0)

| Risk | Mitigation |
|------|------------|
| Docker on Windows/WSL2 slow | Use `docker compose` with BuildKit; pre-build base images |
| SLTDA data format changes | ETL script versioned; schema validation; fallback to static seed |
| MCP tool schema mismatch | Pydantic models shared via `packages/shared`; contract tests |
| Celery broker connection issues | Health check includes Redis ping; retry with backoff |
| Chairman time for review | Async review via decision doc; 2-hour SLA |

---

## Next Sprint Preview (Sprint 1: Agent Core)

| Feature | Est. Days |
|---------|-----------|
| LangGraph Travel Agent (Intent → Itinerary → Quote) | 5 |
| WhatsApp Webhook + Session Management | 3 |
| Multi-language Support (12 langs via LLM) | 2 |
| Operator Dashboard: Leads, Conversations, Itineraries | 4 |
| **Total** | **14 days (2 weeks)** |

---

**Document Control**  
- Created: 2025-07-21  
- Owner: Hermes (Chief of Staff)  
- Approval: [ ] Chairman — Date: ___________  
- Next Review: Sprint 1 Planning (Day 8)