"""Asking a model: a provider page says how to reach it, and one HTTP call gets the answer."""

from __future__ import annotations

import http.client
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from conky.page import NAME

TIMEOUT = 60
APIS = ("openai", "anthropic")
ANTHROPIC_VERSION = "2023-06-01"
ANTHROPIC_MAX_TOKENS = 1024


class ModelError(Exception):
    """A model could not be asked or did not answer; the message says what to do next."""


@dataclass(frozen=True)
class Provider:
    """How to reach a model: wire format, endpoint, model name and an optional secret name."""

    page: str
    api: str
    url: str
    model: str
    secret: str | None
    max_tokens: int | None


@dataclass(frozen=True)
class Answer:
    """The text a model returned and, when the provider reported them, the token counts."""

    text: str
    tokens_in: int | None
    tokens_out: int | None


def provider(page: str, fields: dict[str, Any] | None) -> Provider:
    """Return the provider described by the fields of the page called page."""
    if fields is None:
        raise ModelError(
            f"provider page {page!r} does not exist: write it with api, url, model and secret"
        )

    def bad(why: str) -> ModelError:
        return ModelError(f"provider page {page!r} is malformed, {why}: correct that field")

    api, url, model = fields.get("api"), fields.get("url"), fields.get("model")
    secret, limit = fields.get("secret"), fields.get("max_tokens")
    if api not in APIS:
        raise bad(f"api must be one of {', '.join(APIS)}")
    if not (isinstance(url, str) and url.startswith(("http://", "https://"))):
        raise bad("url must be an http or https address")
    if not (isinstance(model, str) and model):
        raise bad("model must be the model's name")
    if secret is not None and not (isinstance(secret, str) and NAME.match(secret)):
        raise bad("secret must be the name of a secret, not the secret itself")
    if limit is not None and not (
        isinstance(limit, int) and not isinstance(limit, bool) and limit > 0
    ):
        raise bad("max_tokens must be a positive whole number")
    return Provider(page, api, url, model, secret, limit)


def find_secret(name: str, keys_dir: Path) -> str:
    """Return the secret name, from CONKY_SECRET_<NAME> or else <name>.secret in keys_dir."""
    variable = f"CONKY_SECRET_{name.upper()}"
    value = os.environ.get(variable, "").strip()
    if not value:
        path = keys_dir / f"{name}.secret"
        value = path.read_text(encoding="utf-8").strip() if path.is_file() else ""
    if not value:
        raise ModelError(
            f"secret {name!r} not found: set {variable} or put it in {name}.secret "
            "in the key directory"
        )
    return value


def _request(found: Provider, secret: str | None, prompt: str) -> urllib.request.Request:
    headers = {"Content-Type": "application/json"}
    messages = [{"role": "user", "content": prompt}]
    if found.api == "openai":
        body: dict[str, Any] = {"model": found.model, "messages": messages}
        if found.max_tokens is not None:
            body["max_tokens"] = found.max_tokens
        if secret is not None:
            headers["Authorization"] = f"Bearer {secret}"
    else:
        body = {
            "model": found.model,
            "max_tokens": found.max_tokens or ANTHROPIC_MAX_TOKENS,
            "messages": messages,
        }
        headers["anthropic-version"] = ANTHROPIC_VERSION
        if secret is not None:
            headers["x-api-key"] = secret
    return urllib.request.Request(
        found.url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )


def _count(usage: Any, key: str) -> int | None:
    value = usage.get(key) if isinstance(usage, dict) else None
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _parse(found: Provider, data: Any) -> Answer:
    if found.api == "openai":
        text = data["choices"][0]["message"]["content"]
        names = ("prompt_tokens", "completion_tokens")
    else:
        text = next(b["text"] for b in data["content"] if b["type"] == "text")
        names = ("input_tokens", "output_tokens")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("no text")
    usage = data.get("usage")
    return Answer(text.strip(), _count(usage, names[0]), _count(usage, names[1]))


def ask(found: Provider, secret: str | None, prompt: str) -> Answer:
    """Send prompt to the provider once, with no retry, and return its answer."""
    where = f"provider {found.page!r}"
    try:
        with urllib.request.urlopen(_request(found, secret, prompt), timeout=TIMEOUT) as reply:
            data = json.loads(reply.read())
    except urllib.error.HTTPError as exc:
        raise ModelError(
            f"{where} answered HTTP {exc.code}: check its url, model and secret, then ask again"
        ) from exc
    except (OSError, http.client.HTTPException) as exc:
        reason = getattr(exc, "reason", exc)
        raise ModelError(
            f"cannot reach {where} ({type(reason).__name__}): check its url and the network, "
            "then ask again"
        ) from exc
    except ValueError as exc:
        raise ModelError(
            f"{where} did not send JSON: check that its url is the right endpoint"
        ) from exc
    try:
        return _parse(found, data)
    except (KeyError, IndexError, TypeError, StopIteration, ValueError, AttributeError) as exc:
        raise ModelError(
            f"{where} sent no answer text in the {found.api} format: check that api matches "
            "the service"
        ) from exc
