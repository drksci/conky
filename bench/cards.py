"""Draw a card: a playbook whose `says: live` steps are answered by a real model, N times.

    python -m bench.cards CARD.yaml --draws N [--model M] [--out DIR] [--cap CALLS] [--jobs N]
    python -m bench.cards --read DIR

A card is a playbook (docs/reference/playbooks.md#cards). Each draw is a fresh vault in its own
folder. A live step is answered through conky's own provider detection, the path an ask without
a provider takes, and the command provider runs `relay` below so that every model call is counted
and kept. Draws run in parallel worker processes and share one call count. One row a draw goes
to `rows.jsonl` and one line of what the draw did, read from its vault, to `observations.jsonl`;
`--read` prints a plain summary of the two. A card must state itself before it runs (objective,
hypothesis, success, forecast, par, dial, if_not) or the runner refuses it; after the draws it
prints and records one verdict line against the stated success.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import statistics
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests import playbook  # noqa: E402
from tests.test_pages import Stand  # noqa: E402

from conky import Vault, model  # noqa: E402
from conky import git as vault_git  # noqa: E402
from conky.cache import Cache, Mode  # noqa: E402
from conky.page import load_value  # noqa: E402

DEFAULT_CAP = 40
MOST_JOBS = 8
ASKS = 2
HEAD = 200
CALLS = "calls.jsonl"
BUDGET = "budget.txt"
ROWS = "rows.jsonl"
OBSERVATIONS = "observations.jsonl"
VERDICT = "verdict.txt"
STATEMENTS = ("objective", "hypothesis", "success", "forecast", "par", "dial", "if_not")
PAR = ("outcome", "structure", "cost", "craft")
BARS = {"draws": None, "pass": None, "calls_at_most": "calls", "sent_at_most": "sent"}


def relay(folder: Path, budget: Path) -> int:
    """Answer one ask for the stand provider: live when the stand says so, else as the stand does.

    The prompt arrives on standard input and the answer leaves on standard output. Each call is
    appended to calls.jsonl in folder. A live call spends one of the calls left in the shared
    count at budget, which every draw of a run takes from under a lock.
    """
    prompt = sys.stdin.read()
    if (folder / "answer.txt").read_text(encoding="utf-8").strip() != playbook.LIVE:
        done = subprocess.run(
            [sys.executable, str(folder / "model.py")],
            input=prompt,
            capture_output=True,
            text=True,
            check=False,
        )
        _keep(folder, False, "stand", prompt, done.stdout, 0.0)
        sys.stdout.write(done.stdout)
        return done.returncode
    if not _spend(budget):
        print("the card's call cap is spent: raise --cap or draw fewer times", file=sys.stderr)
        return 1
    found = model.detect()
    keys = Path.home() / ".conky" / "keys"
    for choice in found.choices:
        started = time.monotonic()
        try:
            reply = model.ask(choice.provider, choice.secret, prompt, keys)
        except model.ModelError as exc:
            print(exc, file=sys.stderr)
            continue
        _keep(folder, True, choice.provider.name, prompt, reply.text, time.monotonic() - started)
        print(reply.text)
        return 0
    notes = "; ".join(found.notes) or "no model was detected"
    print(f"no model answered ({notes}): see `conky model` for what to set up", file=sys.stderr)
    return 1


def _spend(budget: Path) -> bool:
    """Take one call from the shared count in budget and return whether one was left."""
    with budget.open("r+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        left = int(handle.read())
        if left > 0:
            handle.seek(0)
            handle.truncate()
            handle.write(str(left - 1))
        return left > 0


def _keep(folder: Path, live: bool, name: str, sent: str, received: str, seconds: float) -> None:
    row = {"live": live, "model": name, "sent": len(sent), "received": len(received)}
    row["seconds"] = round(seconds, 3)
    row["head"] = received.strip()[:HEAD]
    with (folder / CALLS).open("a", encoding="utf-8") as log:
        log.write(json.dumps(row) + "\n")


def calls(folder: Path) -> list[dict]:
    """Return every call the relay kept in folder, oldest first."""
    path = folder / CALLS
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def draw(card: Path, number: int, folder: Path, budget: Path) -> tuple[dict, dict]:
    """Play the card once in a fresh vault under folder and return its row and observation.

    Live calls are taken from the shared count at budget.
    """
    folder.mkdir(parents=True)
    stand = Stand(folder / "stand")
    here = shlex.quote(str(Path(__file__).resolve()))
    command = (
        f"{shlex.quote(sys.executable)} {here} relay "
        f"{shlex.quote(str(stand.folder))} {shlex.quote(str(budget))}"
    )
    expects: list[dict] = []
    error = None
    saved = os.environ.get("CONKY_COMMAND_STAND")
    os.environ["CONKY_COMMAND_STAND"] = command
    started = time.monotonic()
    try:
        vault = Vault.init(folder / "vault", folder / "keys", Cache(folder / "cache", Mode.OFF))
        playbook.run(
            card, vault, stand, lambda step, lines: expects.append({"step": step, "failed": lines})
        )
    except (AssertionError, model.ModelError, KeyError, ValueError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if saved is None:
            del os.environ["CONKY_COMMAND_STAND"]
        else:
            os.environ["CONKY_COMMAND_STAND"] = saved
    made = [c for c in calls(stand.folder) if c["live"]]
    row = {
        "draw": number,
        "model": ", ".join(sorted({c["model"] for c in made})),
        "expects": expects,
        "calls": len(made),
        "sent": sum(c["sent"] for c in made),
        "received": sum(c["received"] for c in made),
        "seconds": round(time.monotonic() - started, 3),
        "vault": str(folder / "vault"),
    }
    if error:
        row["error"] = error
    return row, observe(card, number, folder / "vault", [c["head"] for c in made])


def observe(card: Path, number: int, vault: Path, answers: list[str]) -> dict:
    """Return what a draw left in its vault, read with no model call and with no verdict.

    The pages that exist and were not the card's starting pages, the rules each page carries as
    written, every refusal in the history with its reason, and the start of each live answer.
    """
    start = set(load_value(card.read_text(encoding="utf-8")).get("pages", {}))
    found = Vault(vault, vault.parent / "keys")
    names = sorted(p.stem for p in found.pages_dir.glob("*.md"))
    log = vault_git.run(["log", "--reverse", "--format=%x1e%B", "main"], vault)
    refusals = []
    for record in log.split("\x1e")[1:]:
        tags = vault_git.trailers(record)
        if tags.get("Kind") == "refused":
            refusals.append({"page": tags.get("Page"), "reason": tags.get("Reason")})
    return {
        "draw": number,
        "new_pages": [n for n in names if n not in start],
        "rules": {n: found.read(n).rules for n in names if found.read(n).rules},
        "refusals": refusals,
        "answers": answers,
    }


def passed(row: dict) -> bool:
    """Return whether every expect step of a draw held and the run reached its end."""
    return "error" not in row and not any(e["failed"] for e in row["expects"])


def lines(path: Path) -> list[dict]:
    """Return the rows of a jsonl file, or none when it is not there."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def trim(text: object, width: int = 90) -> str:
    """Return text on one line, cut to width."""
    line = " ".join(str(text).split())
    return line if len(line) <= width else line[: width - 3] + "..."


def missing(plan: dict) -> list[str]:
    """Return what a card lacks of the seven statements, each as a line saying what to write."""
    found = [
        f"{key}: write this statement at the top of the card"
        for key in STATEMENTS
        if key not in plan
    ]
    par = plan.get("par")
    if isinstance(par, dict):
        found += [f"par {part}: write this line under par" for part in PAR if part not in par]
    elif "par" in plan:
        found.append(f"par: write the lines {', '.join(PAR)} under par")
    bar = plan.get("success")
    if isinstance(bar, dict):
        found += [
            f"success {k}: write this bar as a whole number"
            for k in ("draws", "pass")
            if not isinstance(bar.get(k), int)
        ]
        found += [
            f"success {k}: not a bar, use one of {', '.join(BARS)}" for k in bar if k not in BARS
        ]
        if (
            isinstance(bar.get("draws"), int)
            and isinstance(bar.get("pass"), int)
            and bar["pass"] > bar["draws"]
        ):
            found.append("success pass: cannot be more than success draws")
    elif "success" in plan:
        found.append("success: write `{draws: N, pass: K}` so the bar is data")
    return found


def show(statements: dict) -> None:
    """Print each statement the card carries, a line a statement and a line a part of a mapping."""
    for key in STATEMENTS:
        text = statements.get(key)
        if isinstance(text, dict):
            for part, line in text.items():
                print(f"{key} {part}: {line}")
        elif text is not None:
            print(f"{key}: {text}")


def verdict(bar: dict, rows: list[dict]) -> str:
    """Return the verdict line, `success met` or `success not met`, with the numbers per bar."""
    wins = sum(map(passed, rows))
    drawn = len(rows)
    held = wins >= bar["pass"] and drawn >= bar["draws"]
    parts = [f"passed {wins} of {drawn} (bar: at least {bar['pass']} of {bar['draws']})"]
    if drawn < bar["draws"]:
        parts.append(f"drew {drawn} of the {bar['draws']} stated")
    for key, field in BARS.items():
        if field is None or key not in bar:
            continue
        middle = statistics.median(row[field] for row in rows)
        held = held and middle <= bar[key]
        parts.append(f"median {field} a draw {middle:g} (bar: at most {bar[key]})")
    return f"success {'met' if held else 'not met'}: " + "; ".join(parts)


def read(out: Path) -> int:
    """Print a plain summary of a run from its rows and observations."""
    rows = lines(out / ROWS)
    if not rows:
        print(f"no rows in {out}: draw a card first, python -m bench.cards CARD.yaml --draws 1")
        return 1
    show(rows[0])
    seen = {o["draw"]: o for o in lines(out / OBSERVATIONS)}
    print(f"passed {sum(map(passed, rows))} of {len(rows)}")
    if isinstance(rows[0].get("success"), dict):
        print(verdict(rows[0]["success"], rows))
    for row in rows:
        did = seen.get(row["draw"], {})
        parts = [
            f"rule on {page}: {trim(rule.get('each', rule) if isinstance(rule, dict) else rule)}"
            for page, rules in did.get("rules", {}).items()
            for rule in rules
        ]
        parts += [f"refused {r['page']}: {trim(r['reason'])}" for r in did.get("refusals", [])]
        if "error" in row:
            parts.append(trim(row["error"]))
        print(f"draw {row['draw']}: {'passed' if passed(row) else 'failed'}; " + "; ".join(parts))
    return 0


def worst(plan: dict, draws: int, cap: int) -> str | None:
    """Return why the draws could pass the cap in the worst case, or None when they cannot."""
    asks = max(sum(1 for step in plan["steps"] if step.get("says") == playbook.LIVE), 1)
    each = asks * ASKS
    if draws * each <= cap:
        return None
    return (
        f"{draws} draws may take up to {draws} x {each} = {draws * each} calls "
        f"({asks} live steps x {ASKS} asks, as an answer a rule refuses is asked "
        f"again once) and the cap is {cap}: raise --cap to {draws * each} or draw fewer times"
    )


def main(argv: list[str]) -> int:
    if argv[:1] == ["relay"]:
        return relay(Path(argv[1]), Path(argv[2]))
    ask = argparse.ArgumentParser(prog="python -m bench.cards", description=__doc__)
    ask.add_argument("card", type=Path, nargs="?")
    ask.add_argument("--draws", type=int, help="how many times to draw the card")
    ask.add_argument("--read", type=Path, metavar="DIR", help="summarise the run kept in DIR")
    ask.add_argument(
        "--jobs",
        type=int,
        default=None,
        help=f"draws run at once (default the draws, at most {MOST_JOBS})",
    )
    ask.add_argument(
        "--model",
        default=None,
        help="sets CONKY_MODEL for an anthropic or openai key; a command provider takes its "
        "model from CONKY_COMMAND_<NAME>",
    )
    ask.add_argument(
        "--out", type=Path, default=None, help="default ~/.conky/runs/cards/<card>-<time>"
    )
    ask.add_argument("--cap", type=int, default=DEFAULT_CAP, help="most live model calls in all")
    args = ask.parse_args(argv)
    if args.read:
        return read(args.read)
    if args.card is None or args.draws is None:
        ask.error("draw a card with CARD.yaml and --draws N, or read a run with --read DIR")
    plan = load_value(args.card.read_text(encoding="utf-8"))
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lacks = missing(plan)
    if lacks:
        print(f"refused: {args.card.name} does not state itself before it runs:")
        print("\n".join(f"  {line}" for line in lacks))
        return 1
    out = args.out or Path.home() / ".conky" / "runs" / "cards" / f"{args.card.stem}-{stamp}"
    why = worst(plan, args.draws, args.cap)
    if why:
        print(f"refused: {why}")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    (out / BUDGET).write_text(str(args.cap), encoding="utf-8")
    if args.model:
        os.environ[model.MODEL_VARIABLE] = args.model
    notes = {key: plan[key] for key in STATEMENTS}
    show(notes)
    jobs = args.jobs or min(args.draws, MOST_JOBS)
    done: dict[int, tuple[dict, dict]] = {}
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        waiting = [
            pool.submit(draw, args.card, n, out / f"draw-{n}", out / BUDGET)
            for n in range(1, args.draws + 1)
        ]
        for future in as_completed(waiting):
            row, seen = future.result()
            done[row["draw"]] = (row, seen)
            held = sum(not e["failed"] for e in row["expects"])
            print(
                f"draw {row['draw']}: {'passed' if passed(row) else 'failed'}, {held} of "
                f"{len(row['expects'])} expects held, {row['calls']} calls, {row['seconds']}s",
                flush=True,
            )
    with (out / ROWS).open("a", encoding="utf-8") as log:
        for number in sorted(done):
            first = {} if number > 1 else notes
            log.write(json.dumps({"card": args.card.stem, **first, **done[number][0]}) + "\n")
    with (out / OBSERVATIONS).open("a", encoding="utf-8") as log:
        for number in sorted(done):
            log.write(json.dumps(done[number][1]) + "\n")
    wins = sum(passed(row) for row, _ in done.values())
    drawn = len(done)
    if int((out / BUDGET).read_text(encoding="utf-8")) <= 0:
        print(f"the cap of {args.cap} calls is spent: later calls were refused")
    print(f"passed {wins} of {drawn}")
    line = verdict(plan["success"], [done[n][0] for n in sorted(done)])
    (out / VERDICT).write_text(line + "\n", encoding="utf-8")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
