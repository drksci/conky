"""Asking a model: a provider page says how to reach it, and one HTTP call gets the answer."""

from __future__ import annotations

import http.client
import json
import os
import shlex
import shutil
import socket
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from conky import arch, voice
from conky.cache import Cache, Mode, digest
from conky.page import NAME

TIMEOUT = 60
COMMAND_TIMEOUT = 120
APIS = arch.constant(
    ("openai", "anthropic", "command"),
    "provider shape",
    "conky.model.APIS",
    "slot.shape",
    "How a provider page says to reach a model.",
    doc="providers.md#the-wire-formats",
)
ANTHROPIC_VERSION = "2023-06-01"
ANTHROPIC_MAX_TOKENS = 1024
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-5-5"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
# No OpenAI model id has been verified, so a detected openai choice needs CONKY_MODEL.
OPENAI_DEFAULT_MODEL: str | None = None
# What an agent program is told so that it answers as a model would: its own instructions
# are replaced, so the prompt is the only thing it reads.
PLAIN = voice.line("plain")
BUILTIN_COMMANDS = arch.constant(
    {
        "claude": [
            "claude",
            "-p",
            "--tools",
            "",
            "--strict-mcp-config",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--system-prompt",
            PLAIN,
        ],
        "codex": ["codex", "exec"],
    },
    "built-in command",
    "conky.model.BUILTIN_COMMANDS",
    "slot.command",
    "Programs a command provider can run with nothing set up.",
    doc="providers.md#command",
)
PROVIDER_VARIABLE = "CONKY_PROVIDER"
MODEL_VARIABLE = "CONKY_MODEL"
KEY_VARIABLES = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
SECRET_PREFIX = "CONKY_SECRET_"
COMMAND_PREFIX = "CONKY_COMMAND_"
CHOICES = arch.constant(
    ("anthropic", "openai", "claude", "codex", "none"),
    "provider choice",
    "conky.model.CHOICES",
    "slot.choice",
    "The models detection can choose, and none.",
    doc="providers.md#detection",
)
WAYS = (
    "set ANTHROPIC_API_KEY, set OPENAI_API_KEY with CONKY_MODEL, "
    "put claude or codex on the PATH, or write a provider page and name it"
)
PROBE = arch.constant(
    {
        "variables": ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"),
        "programs": ("claude", "codex", "llm", "ollama"),
        "address": ("ollama", "127.0.0.1", 11434),
        "host": "CLAUDECODE",
        "rooms": ("bwrap", "docker", "podman"),
    },
    "probe",
    "conky.model.PROBE",
    "slot.probe",
    "Everything the read-only look at this machine asks about, and nothing else.",
    doc="providers.md#what-conky-model-found",
)
PROBE_TIMEOUT = 0.3


@dataclass(frozen=True)
class Finding:
    """One thing the machine offers, and where Conky saw it."""

    what: str
    source: str


class ModelError(Exception):
    """A model could not be asked or did not answer; the message says what to do next."""


@dataclass(frozen=True)
class Provider:
    """How to reach a model: wire format, endpoint, model name and an optional secret name."""

    page: str
    api: str
    url: str | None
    model: str | None
    secret: str | None
    max_tokens: int | None
    command: str | None = None

    @property
    def name(self) -> str:
        """The model's name for the commit: the page's model, else the command's name."""
        return self.model or self.command or ""


@dataclass(frozen=True)
class Answer:
    """The text a model returned and, when the provider reported them, the token counts."""

    text: str
    tokens_in: int | None
    tokens_out: int | None
    cached: bool = False
    # The model a built-in program was told to answer with; None when the program's own was used.
    model: str | None = None


@arch.law(
    "law.provider.page",
    "A provider is a page, and a secret is never written to a vault.",
    doc="../decisions/0019-providers-are-pages.md",
    roadmap="R4",
)
@arch.archetype(
    "kind.provider",
    "a person, or a character without a secret or a command",
    "A page naming `api`, `url`, `model`, `secret` or `command`.",
    doc="providers.md#the-provider-page",
    roadmap="R4",
)
@arch.change(
    "place.page.known",
    "Provider fields, a connector's screen and hands, a measure's value.",
    doc="providers.md#the-provider-page",
)
@arch.step(
    "flow.ask.model",
    6,
    "lane.runtime",
    "lane.history",
    "a missing or malformed provider page is a model refusal",
    refusal=True,
)
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
    if api == "command":
        name = fields.get("command")
        if not (isinstance(name, str) and NAME.match(name)):
            raise bad("command must be the name of a program, never a command line")
        if model is not None and not (isinstance(model, str) and model):
            raise bad("model must be the model's name")
        return Provider(page, api, None, model, None, None, name)
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


def _read(path: Path) -> str:
    """Return the trimmed text of a file beside the keys, or nothing when it is absent."""
    try:
        return path.read_text(encoding="utf-8").strip() if path.is_file() else ""
    except (OSError, UnicodeDecodeError) as exc:
        raise ModelError(
            f"cannot read {path.name} in the key directory ({type(exc).__name__}): "
            "make it a readable text file or delete it"
        ) from exc


@arch.change(
    "place.beside.secret",
    "Secrets, by name, from the environment or the key directory.",
    doc="providers.md#secrets",
    roadmap="R4",
)
@arch.step(
    "flow.ask.model",
    7,
    "lane.runtime",
    "lane.outside",
    "find the secret by name: the environment, then the key directory",
)
def find_secret(name: str, keys_dir: Path) -> str:
    """Return the secret name, from CONKY_SECRET_<NAME> or else <name>.secret in keys_dir."""
    variable = f"{SECRET_PREFIX}{name.upper()}"
    value = os.environ.get(variable, "").strip()
    if not value:
        value = _read(keys_dir / f"{name}.secret")
    if not value:
        raise ModelError(
            f"secret {name!r} not found: set {variable} or put it in {name}.secret "
            "in the key directory"
        )
    return value


@arch.change(
    "place.beside.command",
    "Command lines, from the environment or the key directory, never from a page.",
    doc="providers.md#command",
    roadmap="R26",
)
def find_command(name: str, keys_dir: Path, model: str | None) -> tuple[list[str], str | None]:
    """Return the argv for a command name and the model it is told, never through a shell.

    The order is the environment variable CONKY_COMMAND_<NAME>, then <name>.command in keys_dir,
    then the built-in argv when its program is on the PATH. Only the built-in claude is given a
    model: the one the page names, else ANTHROPIC_DEFAULT_MODEL. A configured command is run as
    written, so the model told is None.
    """
    variable = f"{COMMAND_PREFIX}{name.upper()}"
    text = os.environ.get(variable, "").strip()
    if not text:
        text = _read(keys_dir / f"{name}.command")
    try:
        argv = shlex.split(text)
    except ValueError as exc:
        raise ModelError(
            f"command {name!r} in {variable} or {name}.command cannot be split into words: "
            "correct its quoting"
        ) from exc
    if not argv and name in BUILTIN_COMMANDS and shutil.which(BUILTIN_COMMANDS[name][0]):
        argv = list(BUILTIN_COMMANDS[name])
        if name == "claude":
            told = model or ANTHROPIC_DEFAULT_MODEL
            return [*argv, "--model", told], told
    if not argv:
        raise ModelError(
            f"command {name!r} is not set up: set {variable} to the program and its options, "
            f"or put them in {name}.command in the key directory"
        )
    return argv, None


def _run(found: Provider, argv: list[str], prompt: str, told: str | None) -> Answer:
    where = f"provider {found.page!r}"
    try:
        # A model sees its prompt and nothing else: the program starts in an empty folder, so
        # it finds no project files or instructions lying about.
        with tempfile.TemporaryDirectory(prefix="ask-") as room:
            done = subprocess.run(
                argv,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=COMMAND_TIMEOUT,
                check=False,
                cwd=room,
            )
    except FileNotFoundError as exc:
        raise ModelError(
            f"{where} cannot start {argv[0]!r}: install it or correct CONKY_COMMAND_"
            f"{(found.command or '').upper()}, then ask again"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ModelError(
            f"{where} gave no answer in {COMMAND_TIMEOUT} seconds: check that {argv[0]!r} "
            "runs without asking for input, then ask again"
        ) from exc
    except OSError as exc:
        raise ModelError(
            f"{where} cannot run {argv[0]!r} ({type(exc).__name__}): check the program "
            "and its permissions, then ask again"
        ) from exc
    if done.returncode != 0:
        detail = " ".join(done.stderr.split())[:200]
        raise ModelError(
            f"{where} exited with status {done.returncode}"
            f"{': ' + detail if detail else ''}: run {argv[0]!r} by hand to see why, "
            "then ask again"
        )
    text = done.stdout.rstrip()
    if not text.strip():
        raise ModelError(
            f"{where} printed no answer: check that {argv[0]!r} writes its answer to "
            "standard output"
        )
    return Answer(text, None, None, model=told)


@dataclass(frozen=True)
class Choice:
    """One model that detection found, with the secret it needs and why it was found."""

    provider: Provider
    secret: str | None
    why: str


@dataclass(frozen=True)
class Detected:
    """Every model the environment offers, in the order to try them, and what was skipped."""

    choices: list[Choice]
    notes: list[str]


@arch.law(
    "law.fallback.always",
    "Everything works with nothing configured, and rules stay strict.",
    doc="../decisions/0026-it-always-works.md",
    roadmap="R26",
)
@arch.part(
    "part.provider.detect",
    "layer.character",
    "The models the environment offers, in the order to try them.",
    doc="providers.md#detection",
    roadmap="R26",
)
@arch.change(
    "place.runtime.detect",
    "Choosing a model when none is named.",
    doc="providers.md#detection",
    roadmap="R26",
)
@arch.step(
    "flow.ask.model",
    11,
    "lane.runtime",
    "lane.outside",
    "no answer yet: detect CONKY_PROVIDER, keys, then claude, then codex",
)
def detect() -> Detected:
    """List the models to try, from the environment and the PATH alone, never from a vault.

    CONKY_PROVIDER, when it names one, goes first. Then come ANTHROPIC_API_KEY, OPENAI_API_KEY
    with a model, claude on the PATH and codex on the PATH. CONKY_PROVIDER=none lists nothing.
    """
    env = os.environ
    wanted = env.get(PROVIDER_VARIABLE, "").strip().lower()
    notes: list[str] = []
    if wanted == "none":
        return Detected([], ["CONKY_PROVIDER is none"])
    if wanted and wanted not in CHOICES:
        notes.append(
            f"CONKY_PROVIDER is {wanted!r}, which is ignored: use one of {', '.join(CHOICES)}"
        )
        wanted = ""
    override = env.get(MODEL_VARIABLE, "").strip()
    found: dict[str, Choice] = {}
    for kind, key_name, url, default in (
        ("anthropic", KEY_VARIABLES["anthropic"], ANTHROPIC_URL, ANTHROPIC_DEFAULT_MODEL),
        ("openai", KEY_VARIABLES["openai"], OPENAI_URL, OPENAI_DEFAULT_MODEL),
    ):
        key = env.get(key_name, "").strip()
        if not key:
            continue
        name = override or default
        if not name:
            notes.append(f"{key_name} is set but no default model is known: set CONKY_MODEL")
            continue
        page = f"detected:{kind}"
        found[kind] = Choice(Provider(page, kind, url, name, None, None), key, f"{key_name} is set")
    for program in BUILTIN_COMMANDS:
        if shutil.which(program):
            page = f"detected:{program}"
            provider_ = Provider(page, "command", None, None, None, None, program)
            found[program] = Choice(provider_, None, f"{program} is on the PATH")
    if wanted and wanted not in found:
        notes.append(f"CONKY_PROVIDER is {wanted} but it is not available: {_MISSING[wanted]}")
    order = ([wanted] if wanted in found else []) + [k for k in found if k != wanted]
    return Detected([found[k] for k in order], notes)


_MISSING = {
    "anthropic": "set ANTHROPIC_API_KEY",
    "openai": "set OPENAI_API_KEY and CONKY_MODEL",
    "claude": "put claude on the PATH",
    "codex": "put codex on the PATH",
}

PLAIN_LIMIT = 60


def plain_sentence(page: str, into: str, prompt: str) -> str:
    """Return the built-in sentence written when no model could answer the prompt."""
    words = prompt.split()
    asked = " ".join(words)
    if len(asked) > PLAIN_LIMIT:
        asked = asked[:PLAIN_LIMIT].rsplit(" ", 1)[0] + "..."
    return (
        f'No model was around to answer "{asked}", so {page} keeps this line in {into} '
        "until one is."
    )


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


@arch.step(
    "flow.ask.model",
    9,
    "lane.runtime",
    "lane.provider",
    "one call, no retry: an HTTP post or a local program",
)
def ask(found: Provider, secret: str | None, prompt: str, keys_dir: Path) -> Answer:
    """Send prompt to the provider once, with no retry, and return its answer."""
    where = f"provider {found.page!r}"
    if found.command is not None:
        argv, told = find_command(found.command, keys_dir, found.model)
        return _run(found, argv, prompt, told)
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


def moment_key(found: Provider, prompt: str, cause: str) -> str:
    """Return the cache key of one question put in one moment.

    It is the hash of the provider's shape, its endpoint or command name, its model, the most
    tokens it may write, the whole prompt as sent and the event that caused the question. The
    same words asked after a new event have another key, so a character answers afresh.
    """
    limit = found.max_tokens or (ANTHROPIC_MAX_TOKENS if found.api == "anthropic" else None)
    return digest(
        "answer",
        found.api,
        found.url or "",
        found.command or "",
        found.model or "",
        str(limit or ""),
        prompt,
        cause,
    )


@arch.step(
    "flow.ask.model",
    8,
    "lane.runtime",
    "lane.outside",
    "look up the cache by the question and its moment, a hit skips the call",
)
def ask_once(
    cache: Cache,
    found: Provider,
    secret: Callable[[], str | None],
    prompt: str,
    keys_dir: Path,
    cause: str,
) -> Answer | None:
    """Return the cached answer to this question in this moment, else ask the provider and keep it.

    Returns None when the cache is in mode `only` and holds no answer: no provider is called.
    The secret is looked up only when the provider is called. A failed call is never kept.
    """
    key = moment_key(found, prompt, cause)
    kept = cache.get(key)
    if isinstance(kept, dict) and isinstance(kept.get("text"), str) and kept["text"].strip():
        told = kept.get("model")
        return Answer(
            kept["text"], None, None, cached=True, model=told if isinstance(told, str) else None
        )
    if cache.mode == Mode.ONLY:
        return None
    reply = ask(found, secret(), prompt, keys_dir)
    cache.put(key, {"text": reply.text, "model": reply.model})
    return reply


def _answers(host: str, port: int) -> bool:
    try:
        socket.create_connection((host, port), PROBE_TIMEOUT).close()
    except OSError:
        return False
    return True


def probe(answers: Callable[[str, int], bool] | None = None) -> list[Finding]:
    """Say what this machine offers: names only, never a value, nothing started or sent.

    It reads whether a variable is set, whether a program is on the PATH, and whether one local
    address answers. `answers` is that one question, so a test can stand in for the network.
    """
    ask = answers or _answers
    env = os.environ
    found = [
        Finding(f"{name} is set", "the environment, by name")
        for name in PROBE["variables"]
        if env.get(name, "").strip()
    ]
    found += [
        Finding(f"{name} is on the PATH", "PATH")
        for name in (*PROBE["programs"], *PROBE["rooms"])
        if shutil.which(name)
    ]
    who, host, port = PROBE["address"]
    if ask(host, port):
        found.append(Finding(f"{who} answers on {host}:{port}", f"the address {host}:{port}"))
    if env.get(PROBE["host"], "").strip():
        found.append(
            Finding("this session is hosted by Claude Code", f"{PROBE['host']} in the environment")
        )
    return found
