# LankaAgent — Governance & Operating Model

**Version:** 1.0  
**Date:** 2025-07-21  
**Chairman:** Nishantha Priyadarshana (Nishantha Priyadarshana)  
**Chief of Staff / Orchestrator:** Hermes Agent  
**Status:** ACTIVE — Effective Immediately

---

## 1. Organizational Structure

```
NISHANTHA (Chairman / CEO / Final Decision Maker)
│
├─ HERMES (Chief of Staff / Orchestrator / 24×7 Operator)
│   ├─ Delegates to AI Employees
│   ├─ Tracks KPIs & Health Metrics
│   ├─ Escalates Decisions Requiring Chairman Approval
│   ├─ Daily Briefings (Async + Weekly Sync)
│   └─ Quality Gates & Release Management
│
├─ AI EMPLOYEE: LEAD DEVELOPER (Codex / Claude Code)
│   ├─ Repository: lankaagent/
│   ├─ Stack: FastAPI, LangGraph, PostgreSQL, Redis, Docker
│   ├─ Responsibilities: Scaffold → Features → Tests → CI/CD → Deploy
│   └─ Approval Required: Architecture changes, Major refactors, Tech debt >2 days
│
├─ AI EMPLOYEE: GROWTH LEAD (Hermes + Web Research)
│   ├─ Channels: SEO, Cold Email, LinkedIn, Partnerships, Content
│   ├─ Responsibilities: Lead gen, Pipeline, Partner outreach, Case studies
│   └─ Approval Required: Target ICP list, Pricing in outreach, Discount >20%
│
├─ AI EMPLOYEE: OPS LEAD (Hermes + Monitoring)
│   ├─ Stack: Uptime monitoring, Stripe/PayHere billing, Support triage
│   ├─ Responsibilities: 99.9% uptime, Invoice gen, Payment retry, Ticket routing
│   └─ Approval Required: Refunds >$100, SLA changes, Vendor contracts >$500/mo
│
└─ AI EMPLOYEE: PRODUCT ANALYST (Hermes)
    ├─ Data: PostHog / Mixpanel + Postgres analytics
    ├─ Responsibilities: Feature adoption, Churn signals, Cohort analysis
    └─ Approval Required: Roadmap priorities (quarterly review with Chairman)
```

---

## 2. Decision Rights Matrix (RACI)

| Decision Category | Chairman (You) | Hermes (COS) | AI Employees |
|-------------------|:--------------:|:------------:|:------------:|
| **Pricing & Packaging** | **A/R** | C | I |
| **Target Market / ICP** | **A/R** | C | I |
| **Product Roadmap (Quarterly)** | **A/R** | R (d | C |
| **Tech Stack / Architecture (Major)** | **A** | R | C |
| **Tech Stack / Architecture (Minor)** | I | **A/R** | C |
| **Hiring (Human)** | **A/R** | C | I |
| **Hiring (AI Agent / New Capability)** | **A** | R | C |
| **Legal / Compliance / Contracts** | **A/R** | C (drafts) | I |
| **Fundraising / Equity / Investment** | **A/R** | C (prepares) | I |
| **Brand / Public Statements / Press** | **A/R** | R (drafts/schedules) | I |
| **Daily Code / Features / Tests / Deploy** | I | A | **R** |
| **Content / SEO / Cold Email / LinkedIn** | I | A | **R** |
| **Support Responses (Within Policy)** | I | A | **R** |
| **Invoice Gen / Payment Retry / Billing Ops** | I | A | **R** |
| **Monitoring / Alerting / Auto-scaling** | I | A | **R** |
| **Vendor / Tool Selection (<$500/mo)** | I | **A/R** | C |
| **Vendor / Tool Selection (>$500/mo)** | **A** | R | C |
| **Refunds >$100 / SLA Changes** | **A** | R | C |
| **Discount >20% / Enterprise Custom Terms** | **A** | R | C |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 3. Approval Gates & Workflows

### 3.1 Weekly Sprint Planning (30 min, Chairman + Hermes)
**When:** Every Monday 09:00 SLT (or async via briefing doc)  
**Artifacts:** `sprints/SPRINT-{N}.md` (prepared by Hermes Friday prior)

```
SPRINT PLANNING AGENDA
├─ 1. KPI Review (5 min) — MRR, Pipeline, Churn, Uptime, Support SLA
├─ 2. Sprint Goal & Commitment (10 min)
│   ├─ Features to ship (Dev)
│   ├─ Growth experiments (Growth)
│   ├─ Ops improvements (Ops)
│   └─ Analytics insights (Product)
├─ 3. Decision Requests (10 min) — Items needing Chairman approval
│   ├─ Pricing/discount requests
│   ├─ Partnership terms
│   ├─ Legal/compliance items
│   └─ Budget >$500
├─ 4. Risk & Blockers (5 min)
└─ 5. Chairman Approves / Modifies / Rejects → Hermes executes
```

### 3.2 Daily Standup (Async, 5 min read)
**When:** Daily 08:00 SLT (Hermes posts to `daily-briefings/`)  
**Format:**
```
DAILY BRIEFING — YYYY-MM-DD
├─ 🎯 Top Priority Today
├─ 📊 KPI Snapshot (MRR, Active Trials, Pipeline, Uptime)
├─ 🚀 Dev: Shipped / In Progress / Blocked
├─ 📈 Growth: Outreach sent / Replies / Meetings booked
├─ ⚙️ Ops: Tickets / Uptime / Billing / Deployments
├─ 🧠 Product: Key insight / Experiment result
└─ ⚠️ Decisions Needed from Chairman (with options + recommendation)
```

### 3.3 Business-Critical Decision Request (Async, 2-hour SLA)
**Trigger:** Any decision in "Chairman Approves" column above  
**Format:** `decisions/DEC-{YYYYMMDD}-{topic}.md`

```markdown
# Decision Request: [Topic]

## Context
[2-3 sentences: what happened, why it matters]

## Options
| Option | Pros | Cons | Cost | Timeline | Recommendation |
|--------|------|------|------|----------|----------------|
| A | ... | ... | $X | Y days | ✅ Recommended |
| B | ... | ... | $X | Y days | |
| C | ... | ... | $X | Y days | |

## Hermes Recommendation
[1 paragraph with reasoning]

## Chairman Decision
[ ] Approve Option A
[ ] Approve Option B
[ ] Approve Option C
[ ] Defer — Need: ___________
[ ] Reject — Reason: ___________

Signed: ___________  Date: ___________
```

---

## 4. AI Employee Operating Protocols

### 4.1 Lead Developer (Codex / Claude Code)
- **Repository:** `lankaagent/` (monorepo)
- **Branching:** `main` (protected) → `feature/*` → PR → Review → Merge → Auto-deploy staging
- **Quality Gates:** 
  - All PRs: Tests pass, Typecheck, Lint, Security scan
  - Staging deploy: Smoke tests + Hermes verification
  - Production deploy: Chairman approval (via decision request) for major releases
- **Documentation:** Every feature = README update + OpenAPI spec update
- **Secrets:** 1Password / GitHub Environments — never in code

### 4.2 Growth Lead (Hermes)
- **ICP List:** Maintained in `growth/icp-list.csv` (Chairman approves quarterly)
- **Outreach Templates:** `growth/templates/` (Chairman approves messaging)
- **CRM:** HubSpot Free / Attio — all leads tracked
- **Content Calendar:** `growth/content-calendar.md` (monthly, Chairman reviews)
- **Partnership Pipeline:** `growth/partnerships.md` — terms need Chairman approval

### 4.3 Ops Lead (Hermes)
- **Monitoring:** UptimeRobot + Grafana Cloud (free tiers) → PagerDuty free for alerts
- **Support:** Shared inbox (support@lankaagent.com) → Triage rules → Auto-reply + Human escalation
- **Billing:** Stripe (intl) + PayHere (LK) → Webhooks → Postgres → Invoices PDF → Email
- **Runbooks:** `ops/runbooks/` — every incident type has runbook
- **Disaster Recovery:** Daily PG dump to S3 (Wasabi), RPO 24h, RTO 2h

### 4.4 Product Analyst (Hermes)
- **Events:** PostHog (self-hosted on Railway/Render) — $0-50/mo
- **Dashboards:** MRR, Activation, Retention, Feature Adoption, Churn Cohorts
- **Weekly Insight:** `analytics/weekly-insight-{YYYY-WW}.md` (Friday)
- **Quarterly Review:** Deep dive + Roadmap recommendations (Chairman attends)

---

## 5. Financial Controls

| Control | Threshold | Process |
|---------|-----------|---------|
| **Monthly Burn** | >$2,000/mo | Chairman review required |
| **Single Expense** | >$500 | Decision request required |
| **Contract / Vendor** | >$1,000/yr | Chairman signature required |
| **Revenue Recognition** | Monthly | Stripe/PayHere → Postgres → Accrual basis |
| **Tax Compliance** | Quarterly | Hermes prepares → Chairman reviews → CPA files |
| **Banking** | Mercury / Wise (USD) + Sampath/HSBC (LKR) | Chairman only signatory |

---

## 6. Escalation Paths

| Severity | Example | Response | Escalation |
|----------|---------|----------|------------|
| **SEV-1** (Business Down) | API 5xx >5%, Payment failing, Data breach | Immediate (Hermes pages Chairman) | Chairman → Hermes → Dev → Fix → Postmortem |
| **SEV-2** (Degraded) | Slow responses, Partial outage, Billing error | <1 hour (Hermes leads) | Hermes → Dev/Ops → Fix → Update Chairman |
| **SEV-3** (Minor) | Bug non-critical, Support ticket backlog | <24 hours (AI Employees) | Hermes tracks → Weekly review |
| **SEV-4** (Improvement) | Feature request, Tech debt, Doc update | Next sprint | Sprint planning |

---

## 7. Communication Channels

| Channel | Purpose | Participants |
|---------|---------|--------------|
| **Telegram: LankaAgent-Ops** | SEV-1/2 alerts, Daily briefing, Quick decisions | Chairman + Hermes |
| **GitHub: lankaagent/lankaagent** | Code, PRs, Issues, Projects, Wiki | Hermes + Dev AI |
| **Notion / Obsidian: LankaAgent Wiki** | Specs, Runbooks, Decisions, Meeting notes | Chairman + Hermes |
| **Email: nishantha.priyadarshana@gmail.com** | Formal approvals, Contracts, Legal | Chairman only |
| **Calendar: Weekly Sync (Mon 09:00 SLT)** | Sprint planning, Decision review | Chairman + Hermes |

---

## 8. Success Metrics (North Stars)

| Metric | Target (Month 6) | Target (Month 12) | Owner |
|--------|------------------|-------------------|-------|
| **MRR** | $30,000 | $100,000 | Chairman / Growth |
| **Active Operators** | 30 | 80 | Growth |
| **Net Revenue Retention** | >110% | >120% | Product / Ops |
| **Gross Margin** | >85% | >90% | Chairman / Ops |
| **Uptime** | 99.9% | 99.95% | Ops |
| **Support SLA (P1)** | <1 hour | <30 min | Ops |
| **CAC Payback** | <3 months | <2 months | Growth |
| **Chairman Time** | <10 hrs/wk | <5 hrs/wk | Hermes (optimize) |

---

## 9. Amendment Process

- **Minor edits** (typos, formatting): Hermes updates, logs in changelog
- **Major changes** (decision rights, financial controls, org structure): Decision request → Chairman approval → Version bump

---

**Signed:** _________________________  
**Nishantha Priyadarshana** — Chairman & CEO  
**Date:** _________________________  

**Acknowledged:** Hermes Agent — Chief of Staff  
**Date:** _________________________