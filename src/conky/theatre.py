"""A theatre: a vault and the settings that are true only on the machine it runs on."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from conky import arch, cache, carrier, git, model
from conky.errors import BadInput
from conky.page import NAME, THEATRE, ShapeError, given

FILE = "marionette.md"
EXCLUDE = Path(".git") / "info" / "exclude"
KEYS = ("name", "domain", "keys", "cache", "provider", "model", "command", "carrier")
DEFAULT_DOMAIN = "local"
DEFAULT_NAME = "theatre"
DEFAULT_KEYS = "~/.conky/keys"
FLAG, ENVIRONMENT, FILE_SOURCE, DEFAULT = "flag", "environment", FILE, "default"
PAGE = "theatre page"
SHORT = 8
_DOMAIN = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
_SECRET = re.compile(r"secret|token|password|api[_-]?key", re.IGNORECASE)


@dataclass(frozen=True)
class Setting:
    """One resolved value and where it came from: flag, environment, marionette.md or default."""

    value: str | None
    source: str


@dataclass(frozen=True)
class Theatre:
    """A vault's place, and every setting it runs with."""

    root: Path
    file: Path | None
    name: Setting
    domain: Setting
    keys: Setting
    cache: Setting
    provider: Setting
    model: Setting
    commands: Mapping[str, Setting]
    carrier: Setting
    identity: str | None = None

    @property
    def short_id(self) -> str | None:
        """Return the first characters of the vault's first commit, or nothing before it."""
        return self.identity[:SHORT] if self.identity else None

    @property
    def full_name(self) -> str:
        """Return `<name>-<short id>.<domain>`, or `<name>.<domain>` before the first write."""
        suffix = f"-{self.short_id}" if self.short_id else ""
        return f"{self.name.value}{suffix}.{self.domain.value}"

    def keys_dir(self) -> Path | None:
        """Return the private key directory, or nothing when the default applies."""
        return Path(self.keys.value).expanduser() if self.keys.value else None

    def cache_dir(self) -> Path:
        """Return the cache directory."""
        return Path(str(self.cache.value)).expanduser()

    def overlay(self, environ: Mapping[str, str]) -> dict[str, str]:
        """Return the variables the file sets and the environment leaves unset."""
        wanted = {
            model.PROVIDER_VARIABLE: self.provider,
            model.MODEL_VARIABLE: self.model,
            **{f"{model.COMMAND_PREFIX}{n.upper()}": s for n, s in self.commands.items()},
        }
        return {
            variable: str(setting.value)
            for variable, setting in wanted.items()
            if setting.source == FILE_SOURCE and not environ.get(variable, "").strip()
        }

    def lines(self, environ: Mapping[str, str]) -> list[str]:
        """Return the plain lines that say what was resolved and where each value came from."""

        def show(setting: Setting, none: str) -> str:
            return f"{setting.value if setting.value else none} ({setting.source})"

        found = str(self.file) if self.file else f"none, so every setting is its default ({FILE})"
        lines = [
            f"theatre: {self.full_name}",
            f"vault: {self.root}",
            f"settings file: {found}",
            f"identity: {self.short_id or 'appears with the first write'}",
            f"name: {show(self.name, '')}",
            f"domain: {show(self.domain, '')}",
            f"keys: {show(self.keys, DEFAULT_KEYS)}",
            f"cache: {show(self.cache, '')}",
            f"provider: {show(self.provider, 'not set, so a model is detected')}",
            f"model: {show(self.model, 'not set')}",
            f"carrier: {show(self.carrier, '')}",
        ]
        lines += [f"command {n}: {show(s, '')}" for n, s in sorted(self.commands.items())]
        names = [*model.KEY_VARIABLES.values()]
        names += sorted(k for k in environ if k.startswith(model.SECRET_PREFIX))
        for n in names:
            lines.append(f"secret {n}: {'set' if environ.get(n, '').strip() else 'not set'}")
        return lines


def find(start: Path) -> Path | None:
    """Return the nearest folder at or above start that is a vault, else nothing.

    The folder a command starts in counts when it holds a Git repository, as it always has. A
    folder above it counts only when it also holds what a vault holds (pages, the list of its
    signers, or the mark `conky init` leaves), so a command run deep inside some other
    project's repository never takes that repository for a vault.
    """
    here = start.resolve()
    if git.is_repository(here):
        return here
    return next((p for p in here.parents if git.is_repository(p) and _holds_a_vault(p)), None)


def _holds_a_vault(path: Path) -> bool:
    """Say whether a folder above the current one is a vault: it has pages, the list of its
    signers, or the mark `conky init` leaves in the repository's own exclude list."""
    if (path / "pages").is_dir() or (path / "keys" / "allowed_signers").is_file():
        return True
    listed = path / ".git" / "info" / "exclude"
    return listed.is_file() and FILE in listed.read_text().split()


def _refuse(why: str) -> BadInput:
    return BadInput(f"{FILE}: {why}")


def _text(key: str, value: Any, example: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _refuse(f"{key} must be text, such as {key}: {example}")
    return value.strip()


def _checked(head: dict[str, Any]) -> dict[str, Any]:
    for key in head:
        if _SECRET.search(key):
            raise _refuse(
                f"{key} looks like a secret, and a secret is never written to a file: "
                f"put the value in an environment variable, such as {model.SECRET_PREFIX}<NAME>, "
                "and remove the key"
            )
    unknown = sorted(set(head) - set(KEYS))
    if unknown:
        raise _refuse(f"{unknown[0]} is not a setting: use one of {', '.join(KEYS)}")
    out: dict[str, Any] = {}
    for key in ("name", "domain", "keys", "cache", "provider", "model", "carrier"):
        if key in head:
            out[key] = _text(key, head[key], {"name": "lemon", "domain": "home"}.get(key, "value"))
    if "name" in out and not NAME.match(out["name"]):
        raise _refuse(
            f"name is {out['name']!r}: use lower-case letters, digits, - and _, such as lemon"
        )
    if "domain" in out and not _DOMAIN.match(out["domain"]):
        raise _refuse(
            f"domain is {out['domain']!r}: use lower-case words joined by dots, such as home"
        )
    if "provider" in out and out["provider"].lower() not in (*model.CHOICES, "none"):
        raise _refuse(
            f"provider is {out['provider']!r}: use one of {', '.join((*model.CHOICES, 'none'))}"
        )
    if "carrier" in out and out["carrier"] not in carrier.DRIVERS:
        raise _refuse(
            f"carrier is {out['carrier']!r}: use one of {', '.join(sorted(carrier.DRIVERS))}"
        )
    if "command" in head:
        out["command"] = _commands(head["command"])
    return out


def _commands(value: Any) -> dict[str, str]:
    example = "command:\n  stand: python3 stand.py"
    if not isinstance(value, dict) or not value:
        raise _refuse(f"command must map a provider name to a command line, such as\n{example}")
    for name, line in value.items():
        if not isinstance(name, str) or not NAME.match(name):
            raise _refuse(f"command names {name!r}: use a lower-case name such as stand")
        if not isinstance(line, str) or not line.strip():
            raise _refuse(f"command {name} must be a command line in text, such as python3 x.py")
    return {name: line.strip() for name, line in value.items()}


def read(root: Path) -> dict[str, Any] | None:
    """Return the settings in root's marionette.md, or nothing when there is no file.

    Reading it keeps it out of the history: it is added to the local exclude list.
    """
    path = root / FILE
    if not path.is_file():
        return None
    exclude(root)
    try:
        head, _ = given(path.read_text(encoding="utf-8"))
    except ShapeError as exc:
        raise _refuse(f"{exc}") from exc
    return _checked(head)


@arch.part(
    "part.theatre",
    "layer.edge",
    "A vault and the settings true only on this machine, from marionette.md.",
    doc="cli.md#theatre",
    roadmap="R42",
)
def resolve(
    root: Path,
    environ: Mapping[str, str],
    *,
    keys: str | None = None,
    cache_dir: str | None = None,
) -> Theatre:
    """Resolve the theatre at root: flag, then environment variable, then file, then default."""
    head = read(root)
    mine = head or {}
    here = root.resolve()

    def own(key: str) -> Setting:
        return Setting(mine[key], FILE_SOURCE) if key in mine else Setting(None, DEFAULT)

    def place(value: str) -> str:
        found = Path(value).expanduser()
        return str(found if found.is_absolute() else here / found)

    def chosen(flag: str | None, variable: str, key: str) -> Setting:
        if flag:
            return Setting(flag, FLAG)
        text = environ.get(variable, "").strip()
        if text:
            return Setting(text, ENVIRONMENT)
        return own(key)

    folder = here.name.lower() if NAME.match(here.name.lower()) else DEFAULT_NAME
    carried = _page_name(root)
    name = Setting(folder, DEFAULT)
    if "name" in mine:
        name = own("name")
    elif carried:
        name = Setting(carried, PAGE)
    domain = own("domain") if "domain" in mine else Setting(DEFAULT_DOMAIN, DEFAULT)
    keys_setting = Setting(keys, FLAG) if keys else own("keys")
    if keys_setting.source == FILE_SOURCE:
        keys_setting = Setting(place(str(keys_setting.value)), FILE_SOURCE)
    cache_setting = chosen(cache_dir, cache.DIR_VARIABLE, "cache")
    if cache_setting.source == FILE_SOURCE:
        cache_setting = Setting(place(str(cache_setting.value)), FILE_SOURCE)
    elif cache_setting.source == DEFAULT:
        cache_setting = Setting(str(cache.default_dir()), DEFAULT)
    commands = {n: Setting(line, FILE_SOURCE) for n, line in (mine.get("command") or {}).items()}
    for variable, line in environ.items():
        if variable.startswith(model.COMMAND_PREFIX) and line.strip():
            commands[variable[len(model.COMMAND_PREFIX) :].lower()] = Setting(
                line.strip(), ENVIRONMENT
            )
    return Theatre(
        root=root,
        file=root / FILE if head is not None else None,
        name=name,
        domain=domain,
        keys=keys_setting,
        cache=cache_setting,
        provider=chosen(None, model.PROVIDER_VARIABLE, "provider"),
        model=chosen(None, model.MODEL_VARIABLE, "model"),
        commands=commands,
        carrier=own("carrier") if "carrier" in mine else Setting(carrier.DEFAULT, DEFAULT),
        identity=identity(root),
    )


def identity(root: Path) -> str | None:
    """Return the id of the vault's first commit, or nothing when it has none yet.

    The theatre is known by the commit it began with, which every clone shares.
    """
    if not git.is_repository(root):
        return None
    try:
        first = git.run(["rev-list", "--max-parents=0", "--reverse", "main"], root).split()
    except (BadInput, OSError):
        return None
    return first[0] if first else None


def _page_name(root: Path) -> str | None:
    """Return the `name` the vault's theatre page carries, when it has one that is valid."""
    path = root / "pages" / f"{THEATRE}.md"
    if not path.is_file():
        return None
    try:
        head, _ = given(path.read_text(encoding="utf-8"))
    except ShapeError:
        return None
    named = head.get("name")
    return named if isinstance(named, str) and NAME.match(named) else None


def exclude(root: Path) -> None:
    """Add marionette.md to the repository's local exclude list, which is never committed."""
    path = root / EXCLUDE
    if not path.parent.is_dir():
        return
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    if FILE not in lines:
        path.write_text("\n".join([*lines, FILE]) + "\n", encoding="utf-8")


@contextmanager
def applied(settings: Theatre) -> Iterator[None]:
    """Let the file's provider, model and commands stand where the environment sets none."""
    added = settings.overlay(os.environ)
    os.environ.update(added)
    try:
        yield
    finally:
        for variable in added:
            os.environ.pop(variable, None)
