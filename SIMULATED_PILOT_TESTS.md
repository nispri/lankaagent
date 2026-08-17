# Simulated Pilot Test Suite

**Purpose**: Comprehensive pre-pilot validation using 3 simulated pilot personas covering all realistic scenarios before onboarding real pilots.

---

## Simulated Pilot Personas

| Pilot | Profile | Pain Points | Test Focus |
|-------|---------|-------------|------------|
| **Pilot A: "Sarah - BIMARI Wellness Coordinator"** | Wellness tourism coordinator, manages high-value clients, needs multilingual support | Manual quotes, wellness add-on tracking, German/Russian clients | Wellness pricing, multilingual quotes, lead capture |
| **Pilot B: "Rajesh - SLTDA-Registered Operator"** | Mid-size operator (15 tours/yr), SLTDA member, team of 3 agents | Inconsistent quotes, after-hours leads, no CRM | Quote accuracy, 24/7 coverage, lead dashboard |
| **Pilot C: "Priya - New Operator (Ceyloria Partner)"** | First-year operator, tech-savvy, budget-conscious | Building credibility, custom itineraries, budget management | Custom quotes, brand consistency, cost control |

---

## Test Scenarios per Pilot

### Pilot A: BIMARI Wellness Coordinator (Sarah)

| Scenario | Input | Expected Behavior | Pass Criteria |
|----------|-------|-------------------|---------------|
| **A1: Wellness Quote DE** | "wellness add-on für 2 personen, 7 tage" (German) | Returns wellness price €580/pp + tour quote in German | ✅ German response, correct wellness price |
| **A2: Wellness Quote EN** | "wellness package for 4 people, 14 days" | Returns wellness + tour quote, 15% split mentioned | ✅ Correct math, 15% split noted |
| **A3: Russian Wellness Inquiry** | "велнес пакет для 2 человек, 10 дней" | Russian response with wellness pricing | ✅ Russian response, correct price |
| **A4: Multilingual Switch** | Start EN → switch to DE mid-conversation | Maintains context, switches language seamlessly | ✅ Context preserved, language switches |
| **A5: High-Value Lead Capture** | "I want to book wellness for 6 clients, budget $50k" | Captures lead, flags high-value, triggers notification | ✅ Lead captured, high-value flag |
| **A6: After-Hours Wellness** | 2 AM query in German about wellness | Responds in German instantly | ✅ 24/7 German response |

---

### Pilot B: SLTDA Operator (Rajesh)

| Scenario | Input | Expected Behavior | Pass Criteria |
|----------|-------|-------------------|---------------|
| **B1: Standard Quote EN** | "14 day tour for 4 people" | $2,490/pp, accurate quote | ✅ Correct price |
| **B2: Custom Duration** | "11 day tour for 3 people" | Computes custom price (interpolates) | ✅ Interpolated price |
| **B3: Group Quote** | "22 day tour for 10 people" | Group rate, correct vehicle calc | ✅ Group pricing logic |
| **B4: Attractions Query** | "what UNESCO sites in cultural triangle" | Lists Sigiriya, Polonnaruwa, Anuradhapura with fees | ✅ Accurate attractions list |
| **B5: Hotel Query** | "hotels in Kandy under $200" | Returns Cinnamon Citadel, Earl's Regency | ✅ Correct hotel list |
| **B6: Visa Query** | "visa for Indian passport holders" | Free visa on arrival for India | ✅ Correct visa info |
| **B7: After-Hours Lead** | 11 PM: "family of 4, July 15-28" | Captures lead, sends email notification | ✅ Lead captured, notified |
| **B8: Team Handoff** | Agent A starts quote, Agent B continues | Session persists, context maintained | ✅ Session continuity |
| **B9: SLTDA Compliance** | "SLTDA license number?" | Returns operator's SLTDA registration | ✅ Returns reg number |

---

### Pilot C: New Operator (Priya)

| Scenario | Input | Expected Behavior | Pass Criteria |
|----------|-------|-------------------|---------------|
| **C1: Brand Consistency** | "my brand colors are teal/gold" | Widget uses teal/gold, shows "Premium Tours by Priya" | ✅ Brand applied |
| **C2: Custom Itinerary** | "5 day cultural tour, budget $1500pp" | Returns feasible itinerary within budget | ✅ Budget-respecting itinerary |
| **C3: White-Label Widget** | Embed code with priya-tours.com | Widget loads with priya-tours.com branding | ✅ White-label works |
| **C4: Budget Constraint** | "7 days, 2 people, max $1200pp" | Suggests feasible options or says not possible | ✅ Honest budget feedback |
| **C5: Upsell Wellness** | Guest asks about Ayurveda | Suggests wellness add-on, shows $580/pp | ✅ Wellness upsell |
| **C6: CRM Integration** | Lead captured → appears in HubSpot | Webhook fires to configured CRM | ✅ Webhook fires |
| **C7: White-Label Domain** | widget.priya-tours.com | Custom domain works | ✅ Custom domain |

---

## Cross-Pilot Shared Scenarios

| Scenario | Description | All Pilots Pass If |
|----------|-------------|-------------------|
| **X1: Session Persistence** | 30-min gap between messages | Context maintained |
| **X2: Language Switch Mid-Chat** | EN → DE → FR in same session | Each reply in correct language |
| **X3: Long Session** | 50+ messages over 2 hours | No context loss, no memory leak |
| **X4: Concurrent Users** | 10 simultaneous sessions | All respond <3s |
| **X5: Widget Embed** | Embed in test HTML page | Loads <2s, no console errors |
| **X6: Mobile Responsive** | Test on 375px viewport | Usable on mobile |
| **X7: Voice Input** | Click mic, speak, get transcript | STT works, sends transcript |
| **X8: Voice Output** | Enable voice, get reply | TTS plays audio |
| **X9: Widget Config API** | GET /widget/config returns correct config | Returns supported languages |
| **X10: Health Checks** | All /health endpoints return 200 | All green |

---

## Execution Plan

### Phase 1: Automated API Tests (30 min)
```bash
python run_simulated_pilots.py --pilot=A --scenarios=all
python run_simulated_pilots.py --pilot=B --scenarios=all
python run_simulated_pilots.py --pilot=C --scenarios=all
python run_simulated_pilots.py --cross=all
```

### Phase 2: Manual Widget Tests (45 min)
- Open widget in browser
- Test language selector UI
- Test voice input/output
- Test mobile viewport
- Test widget embed in iframe

### Phase 3: Load & Stress (15 min)
```bash
locust -f load_test.py --users=50 --spawn-rate=5 --run-time=60s
```

---

## Success Criteria

| Metric | Target |
|---|---|
| **All Pilot Scenarios** | 100% pass |
| **Cross-Pilot Scenarios** | 100% pass |
| **API Response Time (P95)** | < 3 seconds |
| **Widget Load Time** | < 2 seconds |
| **Concurrent Users (10)** | All respond < 3s |
| **Error Rate** | < 0.1% |
| **Language Accuracy** | 100% correct language replies |

---

## Go/No-Go Decision

| Condition | Action |
|---|---|
| **All scenarios pass** | ✅ Proceed to real pilot onboarding |
| **1-2 minor failures** | ⚠️ Fix, re-test, then proceed |
| **Critical failure (quote wrong, language broken)** | ❌ Fix, full re-test before pilots |

---

## Test Runner Script Template

```python
# run_simulated_pilots.py
import asyncio
from pilot_test_framework import PilotTestRunner

async def main():
    runner = PilotTestRunner()
    
    # Run all pilot scenarios
    results = await runner.run_all([
        "pilot_a_wellness",
        "pilot_b_sltda", 
        "pilot_c_new_operator",
        "cross_pilot"
    )
    
    # Generate report
    report = runner.generate_report()
    print(f"Pass Rate: {report.pass_rate}%")
    print(f"Critical Failures: {report.critical_failures}")
    
    if report.pass_rate == 100:
        print("✅ GO FOR PILOT LAUNCH")
    else:
        print("❌ FIX BEFORE PILOT LAUNCH")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| **QA Lead** | | | |
| **Product Owner** | | | |
| **Technical Lead** | | | |

---

*Document Version: 1.0 | Last Updated: 2026-08-17 | Next Review: Post-Pilot-1*