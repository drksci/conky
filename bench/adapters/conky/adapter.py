"""The Conky arm: one character page, the terminal connector, a provider page aimed at the meter.

Everything the adapter builds is listed in `scaffold.md` beside this file. The character is
the page `traveller`. It holds the prompt pack's task text and house-rule wording as fields, and
two watch entries on the screen page: ask the model what to type (into `keys`), and record which
screen is answered (into `turn`). The terminal connector runs the environment and types `keys`.
The shelf is loaded as pages in the space `shelf`.

    adapter.py [contract arguments] [--answers keys] -- COMMAND...
    adapter.py --verify  --workdir W
    adapter.py --explain --workdir W
    adapter.py --shelf-reads --workdir W
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench.adapters import base  # noqa: E402

CHARACTER = "traveller"
CLI = "import sys; from conky.cli import main; sys.exit(main(sys.argv[1:]))"
PROVIDER = "meter"
SECRET = "bench"
SHELF = "shelf"
# `keys`: the answer fills the one field the connector types. `pages`: the character lives in
# the space DEN, and its answer is the reply plus pages it may write inside that space.
ANSWERS = ("keys", "pages")
DEN = "den"
LIVE = "other.turn > 0 && (!has(other.ended) || other.ended == '')"
PROMPT = (
    "<<<pack>>>![[traveller#task]]<<</pack>>>\n\n"
    "<<<pack>>>![[traveller#house_rules]]<<</pack>>>\n\n"
    "{shelf}"
    "The screen:\n<<<screen>>>![[screen]]<<</screen>>>"
)
# With pages the character is told who it is and which screen it answers, because the screen
# page's `turn` is the one thing a case on its own page can key on.
PAGES_PROMPT = (
    "You are the page `traveller` in the space `den`.\n\n"
    "<<<pack>>>![[traveller#task]]<<</pack>>>\n\n"
    "<<<pack>>>![[traveller#house_rules]]<<</pack>>>\n\n"
    "{shelf}"
    "The screen, turn ![[screen#turn]]:\n<<<screen>>>![[screen]]<<</screen>>>"
)


def watch_of(answers: str, prompt: str, cases: tuple[tuple[int, str], ...] = ()) -> list[dict]:
    """The character's watch entries. A case is (screen turn, keys): answer that screen at once."""
    ask = {"provider": PROVIDER, "otherwise": "", "prompt": prompt, "into": "keys"}
    when = LIVE
    if answers == "pages":
        ask["writes"] = DEN
        when = f"{LIVE} && page.turn != other.turn"
    entries = [
        {
            "on": "screen",
            "when": f"other.turn == {turn} && {LIVE}",
            "set": {"keys": f"'{keys}'", "turn": "other.turn"},
        }
        for turn, keys in cases
    ]
    return [
        *entries,
        {"on": "screen", "when": when, "ask": ask},
        {"on": "screen", "when": LIVE, "set": {"turn": "other.turn"}},
    ]


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def environment(token: str) -> dict[str, str]:
    """The environment the connector runs in: no model but the meter, no proxy to it."""
    return {
        **os.environ,
        "CONKY_PROVIDER": "none",
        "CONKY_CACHE": "off",
        f"CONKY_SECRET_{SECRET.upper()}": token,
        "NO_PROXY": "127.0.0.1,localhost",
        "no_proxy": "127.0.0.1,localhost",
    }


def setup(args, shelf_dir: Path) -> None:
    """Create the vault with the one character, the provider page and the shelf."""
    from conky import Vault

    vault = Vault.init(args.workdir / "vault", args.workdir / "keys")
    pack = base.Pack.load(args.prompts)
    endpoint = args.meter.rstrip("/") + "/v1/chat/completions"
    provider = {"api": "openai", "url": endpoint, "model": args.model, "secret": SECRET}
    assert vault.write(
        PROVIDER, provider, "The model, reached through the bench's meter.", actor="bench", at=now()
    ).ok
    names = []
    if args.shelf and shelf_dir.exists():
        assert vault.write(
            SHELF, {}, "Writings anyone in this vault may read.", actor="bench", at=now()
        ).ok
        for path in sorted(shelf_dir.glob("*.md")):
            if path.name == "SOURCES.md":
                continue
            name = f"shelf-{path.stem}"
            names.append(name)
            text = path.read_text(encoding="utf-8")
            assert vault.write(name, {"within": SHELF}, text, actor="bench", at=now()).ok
    shelf = (
        f"The shelf is the space `shelf` in this vault, pages: {', '.join(names)}.\n\n"
        if names
        else ""
    )
    pages = args.answers == "pages"
    prompt = (PAGES_PROMPT if pages else PROMPT).format(shelf=shelf)
    body = "A traveller on the trail. It answers each screen with what to type."
    fields = {
        "task": pack.task,
        "house_rules": pack.rules,
        "watch": watch_of(args.answers, prompt),
    }
    if pages:
        assert vault.write(
            DEN, {}, "Where the traveller may keep what it writes.", actor="bench", at=now()
        ).ok
        fields |= {"within": DEN, "turn": 0}
    assert vault.write(CHARACTER, fields, body, actor="bench", at=now()).ok


def aim(args) -> None:
    """Point the provider page at this process's meter, which may have moved since the start."""
    from conky import Vault

    vault = Vault(args.workdir / "vault", args.workdir / "keys")
    endpoint = args.meter.rstrip("/") + "/v1/chat/completions"
    if vault.read(PROVIDER).fields.get("url") != endpoint:
        assert vault.write(PROVIDER, {"url": endpoint}, None, actor="bench", at=now()).ok


def play(args) -> int:
    if args.answers not in ANSWERS:
        print(f"--answers is one of {', '.join(ANSWERS)}", file=sys.stderr)
        return 2
    if not (args.workdir / "vault").exists():
        if args.resume:
            print("asked to resume but the working directory holds no vault", file=sys.stderr)
            return 2
        setup(args, args.scenario / "shelf")
    else:
        aim(args)
    command = [
        sys.executable, "-c", CLI,
        "--vault", str(args.workdir / "vault"), "--keys", str(args.workdir / "keys"),
        "connect", "terminal", "--hands", CHARACTER, "--settle", "0.3", "--max-steps", "2000",
        "--first-line",
        "--", *args.command,
    ]  # fmt: skip
    done = subprocess.run(command, env=environment(args.token), check=False)
    return done.returncode


def _commits(vault_dir: Path) -> list[tuple[str, str, dict]]:
    from conky import git

    out = git.run(["log", "--reverse", "--format=%x1e%H%x1f%an%x1f%B", "main"], vault_dir)
    found = []
    for record in out.split("\x1e")[1:]:
        commit, author, message = record.split("\x1f", 2)
        found.append((commit, author, git.trailers(message)))
    return found


def _page(vault_dir: Path, commit: str, page: str):
    """The page as the commit holds it: `fields` and body, and `within`, `rules`, `watch`."""
    from conky import git
    from conky.page import parse

    return parse(git.run(["show", f"{commit}:pages/{page}.md"], vault_dir))


def _fields(vault_dir: Path, commit: str, page: str) -> dict:
    return _page(vault_dir, commit, page).fields


def typed(vault_dir: Path) -> list[dict]:
    """Each line the character gave to a screen, in order: by a model answer or by one of its cases.

    A line is a commit on the character that carries a model's trailers, or that changes `keys`
    to something. A case that repeats the line before it cannot be told from the turn being
    recorded, and is missed.
    """
    answers, before = [], None
    for commit, author, tags in _commits(vault_dir):
        if tags.get("Page") != CHARACTER or tags.get("Kind") != "write":
            continue
        keys = _fields(vault_dir, commit, CHARACTER).get("keys")
        if "Model" in tags or (keys and keys != before):
            answers.append(
                {
                    "commit": commit,
                    "actor": author,
                    "keys": keys,
                    "model": tags.get("Model-Name", tags["Model"]) if "Model" in tags else "",
                    "read": tags.get("Read", ""),
                    "screen_commit": tags.get("Cause", ""),
                }
            )
        before = keys
    return answers


def explain(workdir: Path) -> list[dict]:
    """Every input the character gave, in order, with who gave it and what caused it."""
    found = []
    for answer in typed(workdir / "vault"):
        if answer["model"]:
            cause = (
                f"model answer {answer['commit'][:7]} by {answer['model']}, reading "
                f"{answer['read']}, caused by screen write {answer['screen_commit'][:7]}"
            )
        else:
            cause = (
                f"case {answer['commit'][:7]} on the character's own page, no model call, "
                f"caused by screen write {answer['screen_commit'][:7]}"
            )
        found.append({"keys": answer["keys"], "actor": answer["actor"], "cause": cause})
    return found


def shelf_reads(workdir: Path) -> list[dict]:
    reads = []
    for commit, _author, tags in _commits(workdir / "vault"):
        for name in tags.get("Read", "").split(", "):
            if name.startswith("shelf-"):
                reads.append({"name": name.removeprefix("shelf-"), "commit": commit})
    return reads


def verify(workdir: Path) -> tuple[bool, str]:
    from conky import Vault
    from conky.errors import VerifyFailed

    try:
        Vault(workdir / "vault", workdir / "keys").verify()
    except VerifyFailed as exc:
        return False, str(exc)
    return True, "verified"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--verify", "--explain", "--shelf-reads"):
        mode, rest = argv[0], argv[1:]
        workdir = Path(rest[rest.index("--workdir") + 1])
        if mode == "--verify":
            ok, why = verify(workdir)
            print(json.dumps({"ok": ok, "why": why}))
            return 0 if ok else 1
        if mode == "--shelf-reads":
            print(json.dumps(shelf_reads(workdir)))
            return 0
        print(json.dumps(explain(workdir)))
        return 0
    answers = "keys"
    if "--answers" in argv:
        at = argv.index("--answers")
        answers = argv[at + 1]
        del argv[at : at + 2]
    args = base.parse_args("The Conky arm.", argv)
    args.answers = answers
    return play(args)


if __name__ == "__main__":
    sys.exit(main())
