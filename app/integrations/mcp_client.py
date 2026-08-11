"""LankaAgent MCP Client — lets Anuki query the MCP Tourism Server for real data.

Speaks the Model Context Protocol (streamable-http transport) to the
lankaagent-mcp container (`http://mcp:8000/mcp`). Every call is wrapped in
try/except so a down MCP server degrades gracefully to the static knowledge
base instead of failing the guest's chat.

Protocol flow per session:
    POST initialize        -> 200 + Mcp-Session-Id header
    POST notifications/initialized
    POST tools/call        -> tool result (JSON-RPC response)
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

MCP_URL = "http://mcp:8000/mcp"  # docker-compose service name on internal net
_SESSION_TTL = 300.0  # refresh session after 5 minutes
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


class _MCPClient:
    """Minimal streamable-http MCP client with session caching."""

    def __init__(self, url: str = MCP_URL) -> None:
        self.url = url
        self._session_id: str | None = None
        self._session_ts = 0.0
        self._lock = asyncio.Lock()

    async def _ensure_session(self, client: httpx.AsyncClient) -> str | None:
        """Return a valid Mcp-Session-Id, initializing one if needed."""
        if self._session_id and (time.monotonic() - self._session_ts) < _SESSION_TTL:
            return self._session_id
        async with self._lock:
            if self._session_id and (time.monotonic() - self._session_ts) < _SESSION_TTL:
                return self._session_id
            resp = await client.post(
                self.url,
                headers=_HEADERS,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "lankaagent-api", "version": "0.1.0"},
                    },
                },
            )
            if resp.status_code != 200:
                return None
            sid = resp.headers.get("mcp-session-id")
            if not sid:
                return None
            self._session_id = sid
            self._session_ts = time.monotonic()
            # Mark the session initialized (best-effort).
            with contextlib.suppress(Exception):
                await client.post(
                    self.url,
                    headers={**_HEADERS, "Mcp-Session-Id": sid},
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                )
            return sid

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
        """Call an MCP tool; return its parsed result dict, or None on failure."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                sid = await self._ensure_session(client)
                if not sid:
                    logger.warning("MCP: no session (server down?)")
                    return None
                resp = await client.post(
                    self.url,
                    headers={**_HEADERS, "Mcp-Session-Id": sid},
                    json={
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": arguments},
                    },
                )
                if resp.status_code != 200:
                    return None
                return _parse_tool_result(_sse_or_json(resp.text))
        except Exception as exc:  # pragma: no cover - network hardening
            logger.warning("MCP tool call failed: %s", exc)
            return None


def _sse_or_json(text: str) -> dict[str, Any]:
    """FastMCP streamable-http replies with SSE frames (event: message / data:).

    Parse the first `data:` payload as JSON; fall back to plain JSON bodies.
    """
    try:
        return json.loads(text)
    except Exception:
        pass
    data_lines = [
        line[6:].strip()
        for line in text.splitlines()
        if line.startswith("data:") and line[6:].strip()
    ]
    for raw in data_lines:
        try:
            return json.loads(raw)
        except Exception:
            continue
    return {}


def _parse_tool_result(result: dict[str, Any]) -> dict[str, Any]:
    """Extract a plain dict from an MCP tools/call result."""
    structured = result.get("structured_content")
    if isinstance(structured, dict):
        if "result" in structured:
            return structured["result"]
        return structured
    text = "".join(c.get("text", "") for c in result.get("content") or [])
    parsed: dict[str, Any] | None = None
    with contextlib.suppress(Exception):
        parsed = json.loads(text)
    return parsed if isinstance(parsed, dict) else {"raw": text}


_client = _MCPClient()


async def mcp_tool_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
    """Module-level convenience: call an MCP tool (see _MCPClient.call_tool)."""
    return await _client.call_tool(tool_name, arguments)
