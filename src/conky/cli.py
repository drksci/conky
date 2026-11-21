"""The conky command line. The only place the wall clock is read."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from conky import arch, assimilate, cache, connect, demo, export, model, present, theatre
from conky.assimilate import INTO
from conky.errors import BadInput, VerifyFailed
from conky.page import load_value, serialize
from conky.vault import Vault


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="conky", description="A vault of living Markdown pages.")
    parser.add_argument(
        "--vault",
        default=None,
        help="vault directory (default: the nearest folder at or above this one that is a vault)",
    )
    parser.add_argument(
        "--keys", default=None, help="private key directory (default: ~/.conky/keys)"
    )
    parser.add_argument(
        "--cache-dir", default=None, help="cache directory (default: ~/.conky/cache)"
    )
    parser.add_argument(
        "--cache-mode",
        choices=[str(mode) for mode in cache.Mode],
        default=None,
        help="what the cache may do: on, off, refresh or only (default: on)",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="style output: auto styles a terminal unless NO_COLOR is set (default: auto)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create an empty vault")
    init.add_argument("path")
    write = sub.add_parser("write", help="write fields and a body to a page")
    write.add_argument("page")
    write.add_argument("fields", nargs="*", metavar="field=value")
    write.add_argument("--body", default=None)
    write.add_argument("--as", dest="actor", required=True)
    ask = sub.add_parser("ask", help="ask a model and write the answer to a field of a page")
    ask.add_argument("page")
    ask.add_argument(
        "into",
        nargs="?",
        default=None,
        metavar="into-field",
        help="the field that receives the answer",
    )
    ask.add_argument(
        "--writes",
        default=None,
        metavar="SPACE",
        help="let the answer hold pages, written as the actor into this space",
    )
    ask.add_argument(
        "--provider",
        default=None,
        help="the page that describes the model (default: detect one, see `conky model`)",
    )
    ask.add_argument("--prompt", required=True)
    ask.add_argument("--as", dest="actor", required=True)
    sub.add_parser("theatre", help="print the vault and settings this folder runs with, and why")
    sub.add_parser("model", help="print which model an ask without a provider would use")
    store = sub.add_parser("cache", help="show the cache of costly answers, or clear it")
    store.add_argument("action", nargs="?", choices=["clear"], default=None)
    read = sub.add_parser("read", help="print a page with embeds resolved")
    read.add_argument("page")
    sub.add_parser("log", help="print the history, oldest first")
    sub.add_parser("verify", help="check the tree, the objects, the seals and the history")
    sub.add_parser("rebuild", help="restore the working tree to the committed state")
    link = sub.add_parser("connect", help="run a connector beside the vault")
    kinds = link.add_subparsers(dest="connector", required=True)
    term = kinds.add_parser("terminal", help="give a vault eyes and hands on a terminal program")
    term.add_argument("--vault", default=argparse.SUPPRESS, help="vault directory")
    term.add_argument(
        "--keys", default=argparse.SUPPRESS, help="private key directory (default: ~/.conky/keys)"
    )
    term.add_argument("--as", dest="actor", default="terminal", help="the connector's actor name")
    term.add_argument("--screen", default="screen", help="page that receives the screen")
    term.add_argument("--hands", default="hands", help="page that says what to type")
    term.add_argument(
        "--settle", type=float, default=connect.SETTLE, help="seconds of quiet that end a screen"
    )
    term.add_argument(
        "--max-steps", type=int, default=connect.MAX_STEPS, help="most screens to write"
    )
    term.add_argument(
        "--first-line",
        action="store_true",
        help="type only the first non-empty line of the keys; the page keeps the rest",
    )
    term.add_argument("program", nargs="+", metavar="COMMAND", help="after --, the program to run")
    demo_cmd = sub.add_parser("demo", help="build a small example vault and show it working")
    demo_cmd.add_argument(
        "name", nargs="?", default="lemonade", help="the example (default: lemonade)"
    )
    demo_cmd.add_argument(
        "--into", default=None, help="folder to create (default: ./conky-demo-NAME)"
    )
    demo_cmd.add_argument("--list", action="store_true", help="list the examples")
    shown = sub.add_parser("export", help="show the vault as a folder another program can open")
    shown.add_argument("format", choices=["obsidian", "notion"])
    shown.add_argument("--out", default=None, help="folder to write (default: VAULT/dist/FORMAT)")
    assim = sub.add_parser("assimilate", help="take over a stopped vault from its folder alone")
    assim.add_argument(
        "source",
        nargs="?",
        default=None,
        help="a vault directory, a Git bundle or a URL (default: a stopped vault in the package)",
    )
    assim.add_argument("--into", default=INTO, help=f"folder to create (default: ./{INTO})")
    assim.add_argument("--as", dest="actor", default="newcomer", help="the new actor's name")
    assim.add_argument(
        "--keys", default=argparse.SUPPRESS, help="where the new key goes (default: ./keys)"
    )
    assim.add_argument(
        "--then",
        nargs="+",
        action="append",
        default=[],
        metavar=("PAGE", "FIELD=VALUE"),
        help="a write to make as the newcomer; repeat to make several",
    )
    return parser


def _fields(pairs: list[str]) -> dict[str, object]:
    changes: dict[str, object] = {}
    for pair in pairs:
        name, sep, value = pair.partition("=")
        if not sep or not name:
            raise BadInput(f"expected field=value, got {pair!r}")
        try:
            changes[name] = load_value(value)
        except yaml.YAMLError as exc:
            raise BadInput(f"cannot parse value of {name}: {exc}") from exc
    return changes


def _model_lines() -> list[str]:
    found = model.detect()
    if not found.choices:
        lines = ["no model is available, so an ask writes a plain sentence"]
    else:
        first, *rest = found.choices
        lines = [f"{first.provider.page}: {first.why}, so asks run it first"]
        lines += [f"then {c.provider.page}: {c.why}" for c in rest]
        lines.append("if all of these fail, an ask writes a plain sentence")
    lines += [f"note: {note}" for note in found.notes]
    if not found.choices:
        lines.append(f"to give Conky a model: {model.WAYS}")
    lines.append("a provider page named by an ask is tried before all of these")
    return lines


def _cache_lines(store: cache.Cache, *, clear: bool) -> list[str]:
    if clear:
        return [f"cleared {_count(store.clear(), 'entry', 'entries')} from {store.directory}"]
    found = store.stats()
    return [
        f"cache: {store.directory}",
        f"{_count(found.entries, 'entry', 'entries')}, {found.size} bytes, "
        f"kept up to {store.limit} bytes; mode {store.mode}",
        "to empty it: conky cache clear",
    ]


def _count(number: int, one: str, many: str) -> str:
    return f"{number} {one if number == 1 else many}"


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(args: argparse.Namespace, ui: present.Plain, err: present.Plain) -> int:
    if args.command == "demo":
        if args.list:
            print("\n".join(demo.listing(ui)))
        else:
            into = Path(args.into if args.into else f"conky-demo-{args.name}")
            keys = Path(args.keys) if args.keys else None
            demo.build(args.name, into, keys, _now, ui, print)
        return 0
    if args.command == "assimilate":
        extra = []
        for page, *pairs in args.then:
            if not pairs:
                raise BadInput(f"--then {page} has no field=value: give at least one")
            say = f"Write {' '.join(pairs)} to {page}."
            step = demo.Step(say, page, args.actor, _fields(pairs), None)
            extra.append(assimilate.Carry(step))
        keys = Path(args.keys) if args.keys else None
        return assimilate.run(
            args.source, Path(args.into), args.actor, keys, extra, _now, ui, print
        )
    if args.command == "init":
        store = cache.Cache.open(args.cache_dir, args.cache_mode)
        Vault.init(args.path, args.keys, store)
        print(ui.initialised(args.path))
        return 0
    root = Path(args.vault) if args.vault else theatre.find(Path.cwd()) or Path(".")
    settings = theatre.resolve(root, os.environ, keys=args.keys, cache_dir=args.cache_dir)
    if args.command == "theatre":
        for line in settings.lines(os.environ):
            print(line)
        return 0
    with theatre.applied(settings):
        return _in(args, ui, err, root, settings)


def _in(
    args: argparse.Namespace,
    ui: present.Plain,
    err: present.Plain,
    root: Path,
    settings: theatre.Theatre,
) -> int:
    if args.command == "model":
        for line in _model_lines():
            print(line)
        return 0
    store = cache.Cache.open(settings.cache_dir(), args.cache_mode)
    if args.command == "cache":
        for line in _cache_lines(store, clear=args.action == "clear"):
            print(line)
        return 0
    vault = Vault(root, settings.keys_dir(), store)
    if args.command == "connect":
        settings = connect.Settings(
            args.actor, args.screen, args.hands, args.settle, args.max_steps, args.first_line
        )
        return connect.terminal(vault, args.program, settings, _now, ui, print)
    if args.command == "export":
        show = export.obsidian if args.format == "obsidian" else export.notion
        folder, count = show(vault, Path(args.out) if args.out else None)
        print(f"wrote {_count(count, 'page', 'pages')} to {folder}")
        return 0
    if args.command in ("write", "ask"):
        if args.command == "write":
            result = vault.write(
                args.page, _fields(args.fields), args.body, actor=args.actor, at=_now()
            )
        else:
            result = vault.ask(
                args.page,
                args.into,
                writes=args.writes,
                provider=args.provider,
                prompt=args.prompt,
                actor=args.actor,
                at=_now(),
            )
        if not result.ok:
            print(err.refused(result.id[:7], result.reason or ""), file=sys.stderr)
            return 1
        print(ui.written(result.id[:7]))
        for name, landed in result.pages:
            if landed.ok:
                print(f"{name}: {ui.written(landed.id[:7])}")
            else:
                print(f"{name}: {err.refused(landed.id[:7], landed.reason or '')}", file=sys.stderr)
        if result.plain:
            print(vault.read(args.page).fields[args.into])
            print(f"No model answered. To give Conky one: {model.WAYS}.", file=sys.stderr)
        if not all(landed.ok for _, landed in result.pages):
            return 1
    elif args.command == "read":
        print(ui.read(serialize(vault.read(args.page))), end="")
    elif args.command == "log":
        for line in ui.log(vault.log()):
            print(line)
    elif args.command == "verify":
        vault.verify()
        print(ui.verified(len(vault.log())))
    else:
        vault.rebuild()
        print(ui.restored())
    return 0


@arch.law(
    "law.word.exist",
    "The vocabulary is what exists, checked against the code both ways.",
    doc="../decisions/0027-the-vocabulary-is-what-exists.md",
)
@arch.part(
    "part.cli.command",
    "layer.edge",
    "`init write ask model read log verify rebuild connect demo assimilate cache export`.",
    doc="cli.md#commands",
)
@arch.stage(
    "stimulus",
    "stage.stimulus.person",
    "`conky write` and `conky ask`.",
    doc="cli.md#write",
)
@arch.change(
    "place.runtime.clock",
    "Reading the clock, in this one place, to stamp each write.",
    doc="cli.md#time",
)
@arch.step("flow.write.accept", 9, "lane.runtime", "lane.person", "written, with the commit id")
@arch.step(
    "flow.write.refuse",
    8,
    "lane.runtime",
    "lane.person",
    "refused with the commit id and reason, exit 1",
)
@arch.step("flow.vault.verify", 8, "lane.runtime", "lane.person", "ok, with the number of commits")
@arch.step(
    "flow.vault.rebuild", 6, "lane.runtime", "lane.person", "restored from the committed history"
)
def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    args = _parser().parse_args(argv)
    ui = present.choose(args.color, sys.stdout)
    err = present.choose(args.color, sys.stderr)
    try:
        return _run(args, ui, err)
    except (BadInput, VerifyFailed, model.ModelError) as exc:
        print(err.error(str(exc)), file=sys.stderr)
        return 1
