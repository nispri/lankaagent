# LankaAgent Pilot Tracker — Google Sheets Template

## Setup Instructions
1. Create new Google Sheet: `https://sheets.new`
2. Rename to **"LankaAgent Pilot Tracker"**
3. Create 4 tabs with exact names below
4. Paste each section into its tab (File → Import → Paste values)
5. Share with team (Viewer/Editor as needed)
6. Set up Conditional Formatting (see bottom)

---

## TAB 1: Pipeline

| Pilot # | Operator Name | SLTDA License | Contact Person | Email | WhatsApp | Website | Status | LOI Sent | LOI Signed | Branding Received | Tenant Created | Widget Live | Week 1 Check-in | Week 2 Check-in | Week 3 Check-in | Week 4 Check-in | Report Sent | Decision | Contract Signed | Notes |
|---------|---------------|---------------|----------------|-------|----------|---------|--------|----------|------------|-------------------|----------------|-------------|-----------------|-----------------|-----------------|-----------------|-------------|----------|-----------------|-------|
| 1 | Ceyloria Holidays | SLTDA/TO/2024/0045 | Nishantha Priyadarshana | nishantha.priyadarshana@gmail.com | +9477XXXXXXX | https://ceyloria-site.vercel.app | ✅ PAID | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PAID | ✅ | Self-pilot / reference |
| 2 | | | | | | | 🟡 Prospect | | | | | | | | | | | | | |
| 3 | | | | | | | 🟡 Prospect | | | | | | | | | | | | | |
| 4 | | | | | | | 🟡 Prospect | | | | | | | | | | | | | |
| 5 | | | | | | | 🟡 Prospect | | | | | | | | | | | | | |

**Status Values:** 🟡 Prospect → 🔵 LOI Sent → 🟢 LOI Signed → 🟣 Branding Received → 🟠 Tenant Created → 🟢 Widget Live → 🔵 Pilot Running → 📊 Report Sent → ✅ PAID / ❌ Declined / ⏸ Extended

---

## TAB 2: Weekly Check-ins

| Date | Pilot # | Operator | Week | Conversations | New Leads | Itineraries | Wellness Triggers | Quality Score (1-5) | Blockers | Action Items | Next Check-in | Owner |
|------|---------|----------|------|---------------|-----------|-------------|-------------------|---------------------|----------|--------------|---------------|-------|
| | 1 | Ceyloria | 1 | | | | | | | | | |
| | 1 | Ceyloria | 2 | | | | | | | | | |
| | 1 | Ceyloria | 3 | | | | | | | | | |
| | 1 | Ceyloria | 4 | | | | | | | | | |
| | 2 | | 1 | | | | | | | | | |
| | 2 | | 2 | | | | | | | | | |
| | 2 | | 3 | | | | | | | | | |
| | 2 | | 4 | | | | | | | | | |
| | 3 | | 1 | | | | | | | | | |

---

## TAB 3: Metrics Dashboard

### Pilot #1 — Ceyloria Holidays (Reference)

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Total | Target | % of Target |
|--------|--------|--------|--------|--------|-------|--------|-------------|
| Conversations | | | | | =SUM(B2:E2) | 20 | =B3/20 |
| Qualified Leads | | | | | =SUM(B3:E3) | 5 | =B4/5 |
| Itineraries Generated | | | | | =SUM(B4:E4) | 3 | =B5/3 |
| Wellness Triggers | | | | | =SUM(B5:E5) | 2 | =B6/2 |
| Avg Response Time (s) | | | | | =AVERAGE(B6:E6) | < 3 | |
| Languages Used | | | | | =COUNTA(UNIQUE(...)) | 2+ | |
| After-Hours % | | | | | =AVERAGE(B8:E8) | > 30% | |
| Operator NPS | | | | | =B9 | 8+ | |

### Pilot #2 — [Name]

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Total | Target | % of Target |
|--------|--------|--------|--------|--------|-------|--------|-------------|
| Conversations | | | | | =SUM(B14:E14) | 20 | =B15/20 |
| Qualified Leads | | | | | =SUM(B15:E15) | 5 | =B16/5 |
| Itineraries Generated | | | | | =SUM(B16:E16) | 3 | =B17/3 |
| Wellness Triggers | | | | | =SUM(B17:E17) | 2 | =B18/2 |
| Avg Response Time (s) | | | | | =AVERAGE(B18:E18) | < 3 | |
| Languages Used | | | | | =COUNTA(UNIQUE(...)) | 2+ | |
| After-Hours % | | | | | =AVERAGE(B20:E20) | > 30% | |
| Operator NPS | | | | | =B21 | 8+ | |

### Pilot #3 — [Name]

| Metric | Week 1 | Week 2 | Week 3 | Week 4 | Total | Target | % of Target |
|--------|--------|--------|--------|--------|-------|--------|-------------|
| Conversations | | | | | =SUM(B26:E26) | 20 | =B27/20 |
| Qualified Leads | | | | | =SUM(B27:E27) | 5 | =B28/5 |
| Itineraries Generated | | | | | =SUM(B28:E28) | 3 | =B29/3 |
| Wellness Triggers | | | | | =SUM(B29:E29) | 2 | =B30/2 |
| Avg Response Time (s) | | | | | =AVERAGE(B30:E30) | < 3 | |
| Languages Used | | | | | =COUNTA(UNIQUE(...)) | 2+ | |
| After-Hours % | | | | | =AVERAGE(B32:E32) | > 30% | |
| Operator NPS | | | | | =B33 | 8+ | |

### Portfolio Summary (Auto-Calc)

| Metric | Pilot 1 | Pilot 2 | Pilot 3 | Total | Target (3 Pilots) |
|--------|---------|---------|---------|-------|-------------------|
| Total Conversations | =B3 | =B15 | =B27 | =SUM(B37:D37) | 60 |
| Total Leads | =B4 | =B16 | =B28 | =SUM(B38:D38) | 15 |
| Total Itineraries | =B5 | =B17 | =B29 | =SUM(B39:D39) | 9 |
| Total Wellness Triggers | =B6 | =B18 | =B30 | =SUM(B40:D40) | 6 |
| Projected Monthly Revenue | =B5*199*0.3 | =B17*199*0.3 | =B29*199*0.3 | =SUM(B42:D42) | $3,000+ |
| Wellness Revenue Share (15%) | =B6*199*0.15 | =B18*199*0.15 | =B30*199*0.15 | =SUM(B43:D43) | |

---

## TAB 4: Documents & Links

| Pilot # | Operator | LOI Link | Branding Questionnaire | Branding JSON | Tenant API Response | Widget Snippet | Pilot Report | Contract | Drive Folder |
|---------|----------|----------|------------------------|---------------|---------------------|----------------|--------------|----------|--------------|
| 1 | Ceyloria | [Link] | [Link] | [Link] | [Link] | [Link] | [Link] | [Link] | [Link] |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |

---

## Conditional Formatting Rules

### Pipeline Tab (Column H - Status)
| Rule | Format |
|------|--------|
| Text contains "PAID" | Green fill, white text |
| Text contains "Widget Live" | Light green fill |
| Text contains "Branding Received" | Light yellow fill |
| Text contains "LOI Signed" | Light blue fill |
| Text contains "Prospect" | Gray fill |
| Text contains "Declined" | Red fill, white text |
| Text contains "Extended" | Orange fill |

### Weekly Check-ins (Column I - Quality Score)
| Rule | Format |
|------|--------|
| ≥ 4 | Green fill |
| = 3 | Yellow fill |
| ≤ 2 | Red fill |

### Metrics Dashboard (% of Target columns)
| Rule | Format |
|------|--------|
| ≥ 100% | Green fill, white text |
| ≥ 75% | Light green fill |
| ≥ 50% | Yellow fill |
| < 50% | Red fill |

---

## Data Validation (Dropdowns)

### Pipeline!H:H (Status)
```
🟡 Prospect,🔵 LOI Sent,🟢 LOI Signed,🟣 Branding Received,🟠 Tenant Created,🟢 Widget Live,🔵 Pilot Running,📊 Report Sent,✅ PAID,❌ Declined,⏸ Extended
```

### Pipeline!C:C (SLTDA License format)
Custom formula: `=REGEXMATCH(C2, "SLTDA/TO/\d{4}/\d{4}")`

---

## Automation Ideas (Apps Script)

### 1. Daily Metric Pull (Run 6 AM)
```javascript
function pullDailyMetrics() {
  // Call /api/v1/tenants/{slug}/analytics for each active pilot
  // Append to Weekly Check-ins tab
}
```

### 2. Slack/Email Reminders
```javascript
function sendCheckinReminders() {
  // Check Pipeline for "Widget Live" pilots without check-in this week
  // Send WhatsApp/Email to owner
}
```

### 3. Auto-Generate Report
```javascript
function generatePilotReport(pilotNumber) {
  // Read Metrics Dashboard + Weekly Check-ins
  // Populate PILOT_REPORT_TEMPLATE.md
  // Save as PDF in Drive folder
}
```

---

## Sharing Permissions

| Role | Access |
|------|--------|
| You (Founder) | Editor |
| Co-founder / CTO | Editor |
| Pilot Partner (if shared) | Viewer (own columns only) |
| Investor / Advisor | Viewer |
| Future Sales Hire | Editor |

---

## Quick Links (Add to Sheet Header Row 1)

| Label | Formula |
|-------|---------|
| **Ceyloria Live Widget** | `=HYPERLINK("https://ceyloria-site.vercel.app", "🌐 View")` |
| **Ngrok Health** | `=HYPERLINK("https://cycling-handwash-oversweet.ngrok-free.dev/health/ready", "❤️ Health")` |
| **API Docs** | `=HYPERLINK("https://cycling-handwash-oversweet.ngrok-free.dev/docs", "📚 Docs")` |
| **Tenant API** | `=HYPERLINK("https://cycling-handwash-oversweet.ngrok-free.dev/api/v1/tenants", "🏢 Tenants")` |
| **Leads Dashboard** | `=HYPERLINK("https://cycling-handwash-oversweet.ngrok-free.dev/api/v1/leads", "👥 Leads")` |