"""A small client for an MCP server over Streamable HTTP, standard library only.

Enough for an adapter or a smoke check to list and call a browser server's tools: `initialize`,
`notifications/initialized`, `tools/list` and `tools/call`. Replies may come as JSON or as a
server-sent event stream; both are read.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

PROTOCOL = "2025-06-18"


class McpError(Exception):
    """The server answered with an error, or not in a form this client reads."""


class McpClient:
    def __init__(self, url: str, timeout: float = 120.0) -> None:
        self.url, self.timeout = url, timeout
        self.session: str | None = None
        self.counter = 0

    def _post(self, body: dict) -> dict | None:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
            headers["MCP-Protocol-Version"] = PROTOCOL
        request = urllib.request.Request(
            self.url, data=json.dumps(body).encode(), headers=headers, method="POST"
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=self.timeout) as reply:
            self.session = reply.headers.get("Mcp-Session-Id") or self.session
            text = reply.read().decode("utf-8")
            kind = reply.headers.get("Content-Type", "")
        if "id" not in body or not text.strip():
            return None
        if "text/event-stream" in kind:
            for line in text.splitlines():
                if line.startswith("data:"):
                    found = json.loads(line[5:])
                    if found.get("id") == body["id"]:
                        return found
            raise McpError("the event stream held no reply to the request")
        return json.loads(text)

    def request(self, method: str, params: dict | None = None) -> Any:
        self.counter += 1
        found = self._post(
            {"jsonrpc": "2.0", "id": self.counter, "method": method, "params": params or {}}
        )
        if found is None or "error" in (found or {}):
            raise McpError(f"{method} failed: {found}")
        return found["result"]

    def start(self) -> dict:
        result = self.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "bench", "version": "1"},
            },
        )
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return result

    def tools(self) -> list[dict]:
        return self.request("tools/list")["tools"]

    def call(self, name: str, arguments: dict) -> list[dict]:
        """Call a tool and return its content items (text and image)."""
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise McpError(f"{name} failed: {result.get('content')}")
        return result.get("content", [])
