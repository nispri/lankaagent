"""Start the ngrok tunnel for the LankaAgent widget API (port 8000).

Usage: python tunnel.py            # start and stay alive (Ctrl+C to stop)
       python tunnel.py --once     # start, print URL, exit (for scripting)

Keeps the tunnel alive and re-prints the public URL if it changes.
"""
import os
import sys
import time
from contextlib import suppress

from pyngrok import conf, ngrok

# Read from env so the token never lives in the repo. Set in ~/.bashrc or .env:
#   export NGROK_AUTH_TOKEN=...
AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")
PORT = 8000

conf.get_default().auth_token = AUTH_TOKEN


def out(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def main() -> None:
    if "--once" not in sys.argv:
        # Kill stale agents from dead runs so they don't hold the endpoint.
        with suppress(Exception):
            ngrok.kill()

    try:
        tunnel = ngrok.connect(PORT, bind_tls=True)
    except Exception as exc:
        msg = str(exc)
        if "already online" in msg or "ERR_NGROK_334" in msg:
            out("Endpoint already online (a tunnel is already running).")
            out("URL: https://cycling-handwash-oversweet.ngrok-free.dev")
            return
        out(f"Failed to start tunnel: {msg}")
        raise SystemExit(1) from None

    url = tunnel.public_url
    out(f"NGROK_URL: {url}")
    out(f"Widget:    {url}/widget/embed")
    out(f"Docs:      {url}/docs")

    if "--once" in sys.argv:
        return

    # Keep the process (and thus the tunnel) alive.
    while True:
        time.sleep(30)
        try:
            for t in ngrok.get_tunnels():
                if t.public_url != url:
                    out(f"NGROK_URL_CHANGED: {t.public_url}")
                    url = t.public_url
        except Exception as exc:  # pragma: no cover - defensive
            out(f"tunnel check failed: {exc}")


if __name__ == "__main__":
    main()
