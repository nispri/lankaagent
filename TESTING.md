# LankaAgent — Testing Guide (Anuki Concierge + MCP Tourism Server)

*For Priya, pilot operators, and anyone who wants to kick the tires. Last verified: 2026-08-11 (MCP-grounded chat live).*

---

## 1. 🖥️ Browser test (easiest — recommended)

Open the embedded widget:

```
https://cycling-handwash-oversweet.ngrok-free.dev/widget/embed
```

> First visit shows ngrok's "You are about to visit…" page — click **Visit Site** once (anti-abuse interstitial, harmless).

You get the **Ceyloria Holidays AI Travel Concierge**:

| Control | What it does |
|---|---|
| Chat box | Ask anything about Sri Lanka tours |
| 🎙️ Voice input (mic) | Speak instead of typing |
| 🔈 Voice replies toggle | Anuki speaks back (TTS) |
| 🌐 Language button | Switch language — replies come in that language |

**Try these questions** (each fires a real MCP Tourism Server tool call):

| You ask | MCP tool triggered | Expect |
|---|---|---|
| "quote a 7 day tour for 2 people" | `get_tour_quote` | **$1,261/pp** (half-board, double occ.) |
| "quote a 14 day tour for 2 people" | `get_tour_quote` | **$2,490/pp** — the signature tour |
| "what wildlife can we see?" | `search_attractions` | Yala, Minneriya — elephants, leopards |
| "hotels in Kandy?" | `get_hotels` | Cinnamon Citadel etc. |
| "do I need a visa?" | `get_visa_requirements` | ETA $50 guidance |
| "whats the best time for Yala?" | `get_seasonal_pricing` | Peak vs shoulder rates |

## 2. 📱 Phone test

Same URL on any phone browser — mobile-friendly widget. Handy for live demos to pilots.

## 3. ⌨️ Command-line test (quick API check)

```bash
curl -X POST https://cycling-handwash-oversweet.ngrok-free.dev/widget/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"quote a 10 day tour for 4 people","language":"en","session_id":"test-1"}'
```

Expected: `{"response": "…$1,369 per person…"}` — 10-day/4-pax, computed by the pricing engine via MCP.

**Response key note:** the API returns the reply under the key **`response`** (not `reply`).

### Multilingual (non-ASCII gotcha)

On Windows, curl + PowerShell mangles UTF-8. Use Python for non-English tests:

```bash
python3 -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:8000/widget/chat',
    data=json.dumps({'message': 'quote 7 day tour for 2 people', 'language': 'de',
                     'session_id': 'de-1'}).encode(),
    headers={'Content-Type': 'application/json'})
print(json.loads(urllib.request.urlopen(req, timeout=90).read())['response'])
"
```

Expect a German reply quoting **ab $1.261 pro Person** (matches pricing engine).

## 4. 🔍 Verify it's really MCP (not canned text)

```bash
docker logs lankaagent-mcp --since 5m | grep "POST /mcp"
```

Every grounded reply produces this handshake from the API container:
`initialize → 200` → `notifications/initialized → 202` → `tools/call → 200`

## 5. ⚠️ Known caveats

- **ngrok dies on PC sleep/restart.** If the URL stops responding:
  ```bash
  cd ~/lankaagent && python3 tunnel.py
  ```
  (background process; needs `.env` `NGROK_AUTH_TOKEN` — loads automatically.)
- **Free-tier Zen model** is occasionally slow or empty (≈40% of calls need a retry — the app retries automatically; worst case, re-ask).
- **Local (no ngrok):** swap the URL for `http://localhost:8000` — works the same.
- **Container rebuilds** wipe `/app/tests` — test files are re-copied by the dev (normal CI runs are unaffected).

## 6. Health checks

```bash
curl http://localhost:8000/health/ready        # API: {"status":"ready",...}
curl http://localhost:8001/health              # MCP: (FastMCP — no /health endpoint; use logs instead)
docker ps --format "{{.Names}} | {{.Status}}"  # api/postgres/redis/mcp all healthy
```

## 7. Tool-level test (MCP direct — dev only)

```bash
docker exec lankaagent-mcp python -c "
import sys, asyncio
sys.path.insert(0, '/app')
from mcp_server import mcp

async def main():
    tools = await mcp.list_tools()
    print(len(tools), 'tools:', [t.name for t in tools])
    r = await mcp.call_tool('get_tour_quote', {'pax': 2, 'days': 14})
    print(r)

asyncio.run(main())
"
```

Expect `6 tools` and a full priced quote with day-by-day itinerary.
