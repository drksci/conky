"""The one metering door: every model call from every arm goes through this local server.

It speaks the OpenAI chat-completions shape (`POST /v1/chat/completions`) and the Anthropic
messages shape (`POST /v1/messages`), text and images in both. For every run it:

- checks the run's token (`Authorization: Bearer T` or `x-api-key: T`);
- refuses a request that names any model but the run's model (HTTP 400, `model_mismatch`);
- enforces the budget identically for every arm: at most `calls` calls and `tokens` tokens in
  and out; once spent it answers HTTP 429 `budget_exhausted`, and the trace records it;
- strips the prompt-pack markers and counts the bytes of each call by origin: inside
  `<<<pack>>>`...`<<</pack>>>` (the shared prompt pack, checked verbatim against the selected
  variant), inside `<<<screen>>>`...`<<</screen>>>` (what the environment showed), image bytes,
  and everything else (the arm's own scaffolding);
- appends one JSON line per call to the run's trace: times, latency, the request with images
  replaced by their size and hash, the answer, token counts (or `null` with characters when the
  backend reports none) and the byte accounting.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bench.backends import BackendError, Call, Completion, screen_key

PACK = ("<<<pack>>>", "<<</pack>>>")
SCREEN = ("<<<screen>>>", "<<</screen>>>")
SPAN = re.compile(r"<<<(pack|screen)>>>(.*?)<<</\1>>>", re.DOTALL)


CACHE_MODES = ("record", "replay", "branch", "off")


@dataclass
class Budget:
    calls: int
    tokens: int


@dataclass
class Account:
    """Where the bytes of one call came from."""

    pack: int = 0
    screen: int = 0
    scaffold: int = 0
    image: int = 0
    pack_ok: bool = True
    screens: list[str] = field(default_factory=list)

    def take(self, text: str, pack_texts: set[str]) -> str:
        """Count text by origin and return it with the markers removed."""
        plain, last = [], 0
        for found in SPAN.finditer(text):
            outside = text[last : found.start()]
            self.scaffold += len(outside.encode("utf-8"))
            plain.append(outside)
            kind, inner = found.group(1), found.group(2)
            size = len(inner.encode("utf-8"))
            if kind == "pack":
                self.pack += size
                if pack_texts and inner.strip() not in pack_texts:
                    self.pack_ok = False
            else:
                self.screen += size
                self.screens.append(inner)
            plain.append(inner)
            last = found.end()
        rest = text[last:]
        stray = rest.count(PACK[0]) + rest.count(SCREEN[0])
        if stray:
            self.pack_ok = False
        self.scaffold += len(rest.encode("utf-8"))
        plain.append(rest)
        return "".join(plain)


def _image_part(media_type: str, data: str, account: Account) -> dict:
    raw = base64.b64decode(data)
    account.image += len(raw)
    return {
        "type": "image",
        "media_type": media_type,
        "data": data,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest()[:16],
    }


def normalise(shape: str, body: dict, pack_texts: set[str]) -> tuple[Call, Account]:
    """Read a request of either shape into a `Call`, with markers stripped and bytes counted."""
    account = Account()
    system = ""
    messages = []
    if shape == "anthropic":
        raw = body.get("system") or ""
        if isinstance(raw, list):
            raw = "".join(b.get("text", "") for b in raw if b.get("type") == "text")
        system = account.take(raw, pack_texts)
    for message in body.get("messages", []):
        role, content = message.get("role", "user"), message.get("content", "")
        parts = []
        items = [{"type": "text", "text": content}] if isinstance(content, str) else content
        for item in items:
            kind = item.get("type")
            if kind == "text":
                parts.append({"type": "text", "text": account.take(item["text"], pack_texts)})
            elif kind == "image_url":
                url = item["image_url"]["url"] if isinstance(item["image_url"], dict) else ""
                head, _, data = url.partition(",")
                media = head.removeprefix("data:").split(";")[0] or "image/png"
                parts.append(_image_part(media, data, account))
            elif kind == "image" and item.get("source", {}).get("type") == "base64":
                source = item["source"]
                parts.append(_image_part(source["media_type"], source["data"], account))
        if shape == "openai" and role == "system":
            system = "\n\n".join(filter(None, [system, *[p["text"] for p in parts if "text" in p]]))
            continue
        messages.append({"role": role, "parts": parts})
    limit = body.get("max_tokens") or body.get("max_completion_tokens")
    call = Call(system, messages, limit if isinstance(limit, int) else None, account.screens)
    return call, account


def _for_trace(call: Call) -> dict:
    messages = []
    for message in call.messages:
        parts = [
            {k: v for k, v in p.items() if k != "data"} if p["type"] == "image" else p
            for p in message["parts"]
        ]
        messages.append({"role": message["role"], "parts": parts})
    return {"system": call.system, "messages": messages, "max_tokens": call.max_tokens}


def reply(shape: str, model: str, done: Completion, n: int) -> dict:
    if shape == "openai":
        found: dict = {
            "id": f"bench-{n}",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": done.text},
                    "finish_reason": "stop",
                }
            ],
        }
        if done.tokens_in is not None and done.tokens_out is not None:
            found["usage"] = {
                "prompt_tokens": done.tokens_in,
                "completion_tokens": done.tokens_out,
                "total_tokens": done.tokens_in + done.tokens_out,
            }
        return found
    found = {
        "id": f"bench-{n}",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": done.text}],
        "stop_reason": "end_turn",
    }
    if done.tokens_in is not None and done.tokens_out is not None:
        found["usage"] = {"input_tokens": done.tokens_in, "output_tokens": done.tokens_out}
    return found


def error(shape: str, kind: str, message: str) -> dict:
    if shape == "anthropic":
        return {"type": "error", "error": {"type": kind, "message": message}}
    return {"error": {"type": kind, "code": kind, "message": message}}


class Meter:
    """The meter for one run. `start()` returns its base URL; `stop()` closes it."""

    def __init__(
        self,
        backend,
        model: str,
        token: str,
        budget: Budget,
        trace: Path,
        pack_texts: list[str] | None = None,
        shelf: Path | None = None,
        shelf_log: Path | None = None,
        cache_mode: str = "off",
        cache: Path | None = None,
        replay_from: Path | None = None,
        live_from: int | None = None,
    ) -> None:
        if cache_mode not in CACHE_MODES:
            raise ValueError(f"cache mode must be one of {', '.join(CACHE_MODES)}")
        if cache_mode == "branch" and replay_from is None:
            raise ValueError("cache mode branch needs replay_from: the record to branch from")
        self.live_from = live_from
        self.branched = {"replayed": 0, "live": 0}
        self.cache_mode, self.cache, self.replay_from = cache_mode, cache, replay_from
        self.seen: dict[str, int] = {}
        self.backend, self.model, self.token, self.budget = backend, model, token, budget
        self.shelf, self.shelf_log = shelf, shelf_log
        self.trace = trace
        self.pack_texts = {t.strip() for t in pack_texts or []}
        self.calls = self.tokens = 0
        self.exhausted = self.closed = False
        self.lock = threading.Lock()
        self.server: ThreadingHTTPServer | None = None

    # The request handler calls this; tests call it directly.
    def handle(self, path: str, headers: dict, body: bytes) -> tuple[int, dict]:
        shape = "anthropic" if path.rstrip("/").endswith("/messages") else "openai"
        if not path.rstrip("/").endswith(("/chat/completions", "/messages")):
            return 404, error(shape, "not_found", f"no such path {path}")
        given = headers.get("authorization", "").removeprefix("Bearer ").strip()
        given = given or headers.get("x-api-key", "").strip()
        if given != self.token:
            return 401, error(shape, "authentication_error", "wrong or missing run token")
        try:
            data = json.loads(body or b"{}")
        except ValueError:
            return 400, error(shape, "invalid_request_error", "the body is not JSON")
        with self.lock:
            return self._call(shape, data)

    def _key(self, data: dict) -> str:
        """The record key of a request: backend, model, every parameter, the whole body."""
        name = getattr(self.backend, "name", "?")
        blob = json.dumps({"backend": name, "model": self.model, "body": data}, sort_keys=True)
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        self.seen[digest] = self.seen.get(digest, 0) + 1
        return f"{digest[:32]}-{self.seen[digest]}"

    def _complete(self, call: Call, data: dict, entry: dict) -> Completion:
        """Answer from the backend, recording it, or from this run's record, by cache mode.

        The record belongs to one run: a key counts repeats within the run, and nothing is
        shared between runs, so independent runs stay independent. Mode `branch` reads another
        run's record while a request matches it and goes live, recording, from the first that
        does not, or from call number `live_from` whatever matches.
        """
        if self.cache_mode == "off" or self.cache is None:
            return self.backend.complete(call)
        key = self._key(data)
        entry["cache_key"] = key
        if self.cache_mode in ("replay", "branch"):
            source = (self.replay_from or self.cache) / f"{key}.json"
            forced = self.live_from is not None and self.calls >= self.live_from
            if self.cache_mode == "branch" and (forced or not source.exists()):
                self.branched["live"] += 1
            elif not source.exists():
                entry["cache"] = "miss"
                raise BackendError(
                    f"no recorded answer for this request ({key}) in {source.parent}"
                )
            else:
                stored = json.loads(source.read_text(encoding="utf-8"))
                entry["cache"] = "replayed"
                self.branched["replayed"] += 1
                return Completion(
                    stored["text"],
                    stored["tokens_in"],
                    stored["tokens_out"],
                    {**stored.get("note", {}), "replayed": True},
                )
        done = self.backend.complete(call)
        self.cache.mkdir(parents=True, exist_ok=True)
        stored = {
            "text": done.text,
            "tokens_in": done.tokens_in,
            "tokens_out": done.tokens_out,
            "note": done.note,
            "request": data,
        }
        (self.cache / f"{key}.json").write_text(json.dumps(stored), encoding="utf-8")
        entry["cache"] = "recorded"
        return done

    def shelf_items(self) -> dict[str, Path]:
        if self.shelf is None or not self.shelf.exists():
            return {}
        return {p.stem: p for p in sorted(self.shelf.glob("*.md")) if p.name != "SOURCES.md"}

    def handle_get(self, path: str, headers: dict) -> tuple[int, dict]:
        """The shelf: `GET /shelf` lists it, `GET /shelf/<name>` reads one writing. Logged."""
        given = headers.get("authorization", "").removeprefix("Bearer ").strip()
        given = given or headers.get("x-api-key", "").strip()
        if given != self.token:
            return 401, {"error": "wrong or missing run token"}
        items = self.shelf_items()
        parts = path.strip("/").split("/")
        if parts[0] != "shelf" or not items:
            return 404, {"error": "no shelf on this run"}
        if len(parts) == 1:
            found: dict = {"items": [{"name": n} for n in items]}
            status, name = 200, ""
        elif parts[1] in items:
            name = parts[1]
            status, found = 200, {"name": name, "text": items[name].read_text(encoding="utf-8")}
        else:
            name = parts[1]
            status, found = 404, {"error": f"no writing named {name!r}: GET /shelf lists them"}
        if self.shelf_log is not None:
            entry = {"t": round(time.time(), 3), "path": path, "name": name, "status": status}
            entry["bytes"] = len(found.get("text", ""))
            entry["source"] = "service"
            with self.shelf_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry) + "\n")
        return status, found

    def _call(self, shape: str, data: dict) -> tuple[int, dict]:
        started = time.time()
        entry: dict = {"n": self.calls + 1, "t_start": round(started, 3), "shape": shape}
        entry["model_requested"] = data.get("model")
        call, account = normalise(shape, data, self.pack_texts)
        entry.update(
            {
                "request": _for_trace(call),
                "pack_bytes": account.pack,
                "screen_bytes": account.screen,
                "scaffold_bytes": account.scaffold,
                "image_bytes": account.image,
                "pack_ok": account.pack_ok,
                "screen_key": screen_key(call.last_screen()),
                "chars_in": len(call.text()),
                "backend": getattr(self.backend, "name", "?"),
            }
        )
        status, answer = 200, None
        if self.closed:
            status, answer = 503, error(shape, "run_stopped", "the run has stopped")
        elif data.get("model") != self.model:
            status = 400
            answer = error(
                shape,
                "model_mismatch",
                f"this run's model is {self.model!r}; the request named {data.get('model')!r}",
            )
        elif self.calls >= self.budget.calls or self.tokens >= self.budget.tokens:
            self.exhausted = True
            status = 429
            answer = error(
                shape,
                "budget_exhausted",
                f"budget spent: {self.calls} of {self.budget.calls} calls, "
                f"{self.tokens} of {self.budget.tokens} tokens",
            )
        else:
            self.calls += 1
            try:
                done = self._complete(call, data, entry)
            except BackendError as exc:
                kind = "cache_miss" if entry.get("cache") == "miss" else "backend_error"
                status, answer = 502, error(shape, kind, str(exc))
            else:
                spent = (done.tokens_in or 0) + (done.tokens_out or 0)
                self.tokens += spent
                known = done.tokens_in is not None and done.tokens_out is not None
                entry.update(
                    {
                        "response_text": done.text,
                        "tokens_in": done.tokens_in,
                        "tokens_out": done.tokens_out,
                        "tokens_known": known,
                        "chars_out": len(done.text),
                        "note": done.note,
                    }
                )
                answer = reply(shape, self.model, done, entry["n"])
        ended = time.time()
        entry.update(
            {
                "status": status,
                "t_end": round(ended, 3),
                "latency_s": round(ended - started, 3),
                "budget_after": {"calls": self.calls, "tokens": self.tokens},
            }
        )
        if status != 200:
            entry["error"] = answer
        with self.trace.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return status, answer

    def start(self) -> str:
        meter = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                headers = {k.lower(): v for k, v in self.headers.items()}
                self._send(*meter.handle_get(self.path, headers))

            def do_POST(self) -> None:  # noqa: N802
                size = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(size)
                headers = {k.lower(): v for k, v in self.headers.items()}
                self._send(*meter.handle(self.path, headers, body))

            def _send(self, status: int, answer: dict) -> None:
                data = json.dumps(answer).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_args) -> None:
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def stop(self) -> None:
        self.closed = True
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
