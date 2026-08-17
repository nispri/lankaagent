#!/usr/bin/env python3
"""
Simulated Pilot Test Runner
Automated test runner for all simulated pilot scenarios.
Run: python run_simulated_pilots.py
"""

import asyncio
import json
import time
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any
from urllib import request, parse
import urllib.error

# Configuration
BASE_URL = "http://localhost:8000/widget/chat"
HEADERS = {"Content-Type": "application/json"}


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PilotResult:
    pilot_name: str
    scenario_results: List[TestResult] = field(default_factory=list)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.scenario_results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.scenario_results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.scenario_results)
    
    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0


class PilotTestRunner:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: Dict[str, PilotResult] = {}
    
    def _make_request(self, message: str, language: str = "en", session_id: str = None) -> Dict:
        """Make a chat request to the API."""
        if session_id is None:
            session_id = f"test_{int(time.time() * 1000)}"
        
        payload = json.dumps({
            "message": message,
            "language": language,
            "session_id": session_id
        }).encode()
        
        req = request.Request(
            BASE_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with request.urlopen(req, timeout=90) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "body": e.read().decode()}
        except Exception as e:
            return {"error": str(e)}
    
    def _check_response(self, response: Dict, expected_keywords: List[str] = None, 
                        forbidden_keywords: List[str] = None, 
                        expected_language: str = None) -> tuple[bool, str]:
        """Validate response meets criteria."""
        if "error" in response:
            return False, f"API Error: {response['error']}"
        
        response_text = response.get("response", "")
        response_lang = response.get("language", "en")
        
        if not response_text or response_text == "<EMPTY>":
            return False, "Empty response"
        
        # Check expected keywords
        if expected_keywords:
            for kw in expected_keywords:
                if kw.lower() not in response_text.lower():
                    return False, f"Missing expected keyword: '{kw}'"
        
        # Check forbidden keywords
        if forbidden_keywords:
            for kw in forbidden_keywords:
                if kw.lower() in response_text.lower():
                    return False, f"Contains forbidden keyword: '{kw}'"
        
        # Check language
        if expected_language and response_lang != expected_language:
            return False, f"Wrong language: expected {expected_language}, got {response_lang}"
        
        return True, "OK"
    
    async def run_scenario(self, pilot_name: str, scenario: Dict) -> TestResult:
        """Run a single test scenario."""
        name = scenario["name"]
        message = scenario["message"]
        language = scenario.get("language", "en")
        expected_keywords = scenario.get("expected_keywords", [])
        forbidden_keywords = scenario.get("forbidden_keywords", [])
        expected_language = scenario.get("expected_language")
        session_id = f"test_{pilot_name}_{scenario['name'].lower().replace(' ', '_')}"
        
        start = time.time()
        
        response = self._make_request(message, language, session_id)
        duration = (time.time() - start) * 1000
        
        passed, message = self._check_response(
            response,
            expected_keywords=expected_keywords,
            forbidden_keywords=forbidden_keywords,
            expected_language=expected_language
        )
        
        return TestResult(
            name=name,
            passed=passed,
            message=message,
            duration_ms=duration,
            details={
                "input": message,
                "language": language,
                "response_preview": response.get("response", "")[:200] if "response" in response else str(response)[:200]
            }
        )
    
    async def run_pilot_scenarios(self, pilot_name: str, scenarios: List[Dict]) -> PilotResult:
        """Run all scenarios for a pilot."""
        print(f"\n{'='*60}")
        print(f"Running Pilot: {pilot_name}")
        print(f"{'='*60}")
        
        result = PilotResult(pilot_name=pilot_name)
        
        for scenario in scenarios:
            print(f"  Running: {scenario['name']}...", end=" ", flush=True)
            result_test = await self.run_scenario(pilot_name, scenario)
            result.scenario_results.append(result_test)
            
            status = "✅ PASS" if result_test.passed else "❌ FAIL"
            print(f" {status} ({result_test.duration_ms:.0f}ms)")
            if not result_test.passed:
                print(f"    Reason: {result_test.message}")
        
        print(f"\n  Pilot {pilot_name}: {result.passed}/{result.total} passed ({result.pass_rate:.1f}%)")
        self.results[pilot_name] = result
        return result
    
    def generate_report(self) -> Dict:
        """Generate summary report."""
        total_tests = sum(r.total for r in self.results.values())
        total_passed = sum(r.passed for r in self.results.values())
        total_failed = sum(r.failed for r in self.results.values())
        
        critical_failures = []
        for pilot_name, result in self.results.items():
            for test in result.scenario_results:
                if not test.passed and "critical" in test.name.lower():
                    critical_failures.append(f"{pilot_name}: {test.name} - {test.message}")
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "critical_failures": critical_failures,
            "by_pilot": {name: {"passed": r.passed, "failed": r.failed, "rate": r.pass_rate} 
                        for name, r in self.results.items()}
        }
    
    def print_report(self):
        """Print formatted report."""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("SIMULATED PILOT TEST REPORT")
        print("="*60)
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Pass Rate: {report['pass_rate']:.1f}%")
        
        if report['critical_failures']:
            print("\n❌ CRITICAL FAILURES:")
            for cf in report['critical_failures']:
                print(f"  - {cf}")
        
        print("\nBy Pilot:")
        for pilot, stats in report['by_pilot'].items():
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"  {status} {pilot}: {stats['passed']}/{stats['total']} ({stats['rate']:.1f}%)")
        
        print("\n" + "="*60)
        if report['pass_rate'] == 100:
            print("✅ GO FOR PILOT LAUNCH")
        else:
            print("❌ FIX BEFORE PILOT LAUNCH")
        print("="*60)


# ============================================================
# PILOT SCENARIOS DEFINITION
# ============================================================

PILOT_A_SCENARIOS = [
    {
        "name": "A1: Wellness Quote German",
        "message": "wellness add-on für 2 personen, 7 tage",
        "language": "de",
        "expected_keywords": ["wellness", "580", "usd", "pro person"],
        "expected_language": "de"
    },
    {
        "name": "A2: Wellness Quote English",
        "message": "wellness package for 4 people, 14 days",
        "language": "en",
        "expected_keywords": ["wellness", "580", "15%"],
        "expected_language": "en"
    },
    {
        "name": "A3: Russian Wellness Inquiry",
        "message": "велнес пакет для 2 человек, 10 дней",
        "language": "ru",
        "expected_keywords": ["велнес", "580"],
        "expected_language": "ru"
    },
    {
        "name": "A4: Multilingual Switch EN->DE",
        "message": "quote 7 day tour for 2 people",
        "language": "en",
        "expected_keywords": ["1261", "7 day"],
        "expected_language": "en"
    },
    {
        "name": "A5: High-Value Lead Capture",
        "message": "I want to book wellness for 6 clients, budget $50k",
        "language": "en",
        "expected_keywords": ["wellness", "6", "50000"],
        "expected_language": "en"
    },
    {
        "name": "A6: After-Hours German Wellness",
        "message": "velnes paket für 2 personen",
        "language": "de",
        "expected_keywords": ["wellness", "580"],
        "expected_language": "de"
    },
]

PILOT_B_SCENARIOS = [
    {
        "name": "B1: Standard Quote EN",
        "message": "14 day tour for 4 people",
        "language": "en",
        "expected_keywords": ["2490", "14 day", "4"],
        "expected_language": "en"
    },
    {
        "name": "B2: Custom Duration 11 Days",
        "message": "11 day tour for 3 people",
        "language": "en",
        "expected_keywords": ["11 day", "3"],
        "expected_language": "en"
    },
    {
        "name": "B3: Group Quote 10 Pax",
        "message": "22 day tour for 10 people",
        "language": "en",
        "expected_keywords": ["22 day", "10", "group"],
        "expected_language": "en"
    },
    {
        "name": "B4: Attractions Query",
        "message": "what UNESCO sites in cultural triangle",
        "language": "en",
        "expected_keywords": ["sigiriya", "polonnaruwa", "anuradhapura", "unesco"],
        "expected_language": "en"
    },
    {
        "name": "B5: Hotels Kandy Query",
        "message": "hotels in Kandy under 200",
        "language": "en",
        "expected_keywords": ["kandy", "cinnamon", "hotel"],
        "expected_language": "en"
    },
    {
        "name": "B6: Visa Query India",
        "message": "visa for Indian passport holders",
        "language": "en",
        "expected_keywords": ["india", "free", "visa"],
        "expected_language": "en"
    },
    {
        "name": "B7: After-Hours Lead",
        "message": "family of 4, July 15-28, want to book",
        "language": "en",
        "expected_keywords": ["family", "4", "july"],
        "expected_language": "en"
    },
    {
        "name": "B8: SLTDA Compliance Query",
        "message": "what is my SLTDA license number",
        "language": "en",
        "expected_keywords": ["sltda", "license"],
        "expected_language": "en"
    },
]

PILOT_C_SCENARIOS = [
    {
        "name": "C1: Brand Consistency",
        "message": "my brand colors are teal and gold",
        "language": "en",
        "expected_keywords": ["teal", "gold", "brand"],
        "expected_language": "en"
    },
    {
        "name": "C2: Custom Itinerary Budget",
        "message": "5 day cultural tour, budget 1500 per person",
        "language": "en",
        "expected_keywords": ["5 day", "1500", "cultural"],
        "expected_language": "en"
    },
    {
        "name": "C3: Budget Constraint Honest",
        "message": "7 days, 2 people, max 1200 per person",
        "language": "en",
        "expected_keywords": ["1200", "budget", "not possible"],
        "forbidden_keywords": ["1261"],
        "expected_language": "en"
    },
    {
        "name": "C4: Wellness Upsell",
        "message": "tell me about ayurveda wellness",
        "language": "en",
        "expected_keywords": ["ayurveda", "wellness", "580"],
        "expected_language": "en"
    },
    {
        "name": "C5: Widget Config API",
        "message": "config",
        "language": "en",
        "expected_language": "en",
        "expected_keywords": ["supported_languages", "en", "de", "fr"]
    },
]

CROSS_PILOT_SCENARIOS = [
    {
        "name": "X1: Session Persistence",
        "message": "hello",
        "language": "en",
        "session_reuse": True,
        "expected_keywords": ["welcome", "ceyloria"],
        "expected_language": "en"
    },
    {
        "name": "X1b: Session Persistence Follow-up",
        "message": "what was my first message",
        "language": "en",
        "session_reuse": True,
        "expected_keywords": ["hello"],
        "expected_language": "en"
    },
    {
        "name": "X2: Language Switch EN->DE->FR",
        "message": "quote 7 day tour for 2 people",
        "language": "de",
        "session_reuse": True,
        "expected_language": "de"
    },
    {
        "name": "X2b: Language Switch DE->FR",
        "message": "make it french",
        "language": "fr",
        "session_reuse": True,
        "expected_language": "fr"
    },
    {
        "name": "X2c: Language Switch FR->EN",
        "message": "switch back to english",
        "language": "en",
        "session_reuse": True,
        "expected_language": "en"
    },
    {
        "name": "X5: Widget Config API",
        "message": "config",
        "language": "en",
        "expected_keywords": ["supported_languages", "en", "de", "fr", "ru", "zh", "si", "ta"],
        "expected_language": "en"
    },
    {
        "name": "X9: Voice Input Simulation",
        "message": "[voice transcript] hello i want a 7 day tour",
        "language": "en",
        "expected_keywords": ["hello", "7 day"],
        "expected_language": "en"
    },
]


# ============================================================
# MAIN RUNNER
# ============================================================

async def main():
    print("="*60)
    print("SIMULATED PILOT TEST RUNNER")
    print("="*60)
    print(f"Target: {BASE_URL}")
    print()
    
    runner = PilotTestRunner()
    
    # Run all pilot scenarios
    await runner.run_pilot_scenarios("Pilot A: BIMARI Wellness", PILOT_A_SCENARIOS)
    await runner.run_pilot_scenarios("Pilot B: SLTDA Operator", PILOT_B_SCENARIOS)
    await runner.run_pilot_scenarios("Pilot C: New Operator", PILOT_C_SCENARIOS)
    await runner.run_pilot_scenarios("Cross-Pilot Scenarios", CROSS_PILOT_SCENARIOS)
    
    # Print final report
    runner.print_report()
    
    # Exit code based on results
    report = runner.generate_report()
    if report['pass_rate'] == 100:
        print("\n✅ ALL TESTS PASSED - GO FOR PILOT LAUNCH")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - FIX BEFORE PILOT LAUNCH")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))