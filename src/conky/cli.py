"""The conky command line. The only place the wall clock is read."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from conky import demo, present
from conky.errors import BadInput, VerifyFailed
from conky.page import load_value, serialize
from conky.vault import Vault


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="conky", description="A vault of living Markdown pages.")
    parser.add_argument("--vault", default=".", help="vault directory (default: .)")
    parser.add_argument(
        "--keys", default=None, help="private key directory (default: ~/.conky/keys)"
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
    ask.add_argument("into", metavar="into-field")
    ask.add_argument("--provider", required=True, help="the page that describes the model")
    ask.add_argument("--prompt", required=True)
    ask.add_argument("--as", dest="actor", required=True)
    read = sub.add_parser("read", help="print a page with embeds resolved")
    read.add_argument("page")
    sub.add_parser("log", help="print the history, oldest first")
    sub.add_parser("verify", help="check the tree, the objects, the seals and the history")
    sub.add_parser("rebuild", help="restore the working tree to the committed state")
    demo_cmd = sub.add_parser("demo", help="build a small example vault and show it working")
    demo_cmd.add_argument("name", nargs="?", default="stall", help="the example (default: stall)")
    demo_cmd.add_argument(
        "--into", default=None, help="folder to create (default: ./conky-demo-NAME)"
    )
    demo_cmd.add_argument("--list", action="store_true", help="list the examples")
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
    if args.command == "init":
        Vault.init(args.path, args.keys)
        print(ui.initialised(args.path))
        return 0
    vault = Vault(Path(args.vault), args.keys)
    if args.command in ("write", "ask"):
        if args.command == "write":
            result = vault.write(
                args.page, _fields(args.fields), args.body, actor=args.actor, at=_now()
            )
        else:
            result = vault.ask(
                args.page,
                args.into,
                provider=args.provider,
                prompt=args.prompt,
                actor=args.actor,
                at=_now(),
            )
        if not result.ok:
            print(err.refused(result.id[:7], result.reason or ""), file=sys.stderr)
            return 1
        print(ui.written(result.id[:7]))
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


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    args = _parser().parse_args(argv)
    ui = present.choose(args.color, sys.stdout)
    err = present.choose(args.color, sys.stderr)
    try:
        return _run(args, ui, err)
    except (BadInput, VerifyFailed) as exc:
        print(err.error(str(exc)), file=sys.stderr)
        return 1
