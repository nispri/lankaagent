#!/usr/bin/env python3
"""
Daily LLM Usage Email Cron Job.
Runs at end of day UTC to send usage report.
"""
import asyncio
import sys
sys.path.insert(0, "/app")

from app.integrations.llm_usage import send_daily_usage_email

async def main():
    success = await send_daily_usage_email()
    if success:
        print("✅ Daily usage email sent successfully")
    else:
        print("❌ Failed to send daily usage email")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())