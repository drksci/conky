"""Draw a card: a playbook whose `says: live` steps are answered by a real model, N times.

    python -m bench.cards CARD.yaml --draws N [--model M] [--out DIR] [--cap CALLS]

A card is a playbook (docs/reference/playbooks.md#cards). Each draw is a fresh vault in its own
folder. A live step is answered through conky's own provider detection, the path an ask without
a provider takes, and the command provider runs `relay` below so that every model call is counted
and kept. One row a draw goes to `rows.jsonl`; reports and figures are made later from the rows.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests import playbook  # noqa: E402
from tests.test_pages import Stand  # noqa: E402

from conky import Vault, model  # noqa: E402
from conky.cache import Cache, Mode  # noqa: E402
from conky.page import load_value  # noqa: E402

DEFAULT_CAP = 40
CALLS = "calls.jsonl"
BUDGET = "budget.txt"


def relay(folder: Path) -> int:
    """Answer one ask for the stand provider: live when the stand says so, else as the stand does.

    The prompt arrives on standard input and the answer leaves on standard output. Each call is
    appended to calls.jsonl in folder. A live call spends one of the calls left in budget.txt.
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
    left = int((folder / BUDGET).read_text(encoding="utf-8"))
    if left <= 0:
        print("the card's call cap is spent: raise --cap or draw fewer times", file=sys.stderr)
        return 1
    (folder / BUDGET).write_text(str(left - 1), encoding="utf-8")
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


def _keep(folder: Path, live: bool, name: str, sent: str, received: str, seconds: float) -> None:
    row = {"live": live, "model": name, "sent": len(sent), "received": len(received)}
    row["seconds"] = round(seconds, 3)
    with (folder / CALLS).open("a", encoding="utf-8") as log:
        log.write(json.dumps(row) + "\n")


def calls(folder: Path) -> list[dict]:
    """Return every call the relay kept in folder, oldest first."""
    path = folder / CALLS
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def draw(card: Path, number: int, folder: Path, left: int) -> dict:
    """Play the card once in a fresh vault under folder and return its row.

    left is how many live calls the draw may still make.
    """
    folder.mkdir(parents=True)
    stand = Stand(folder / "stand")
    (stand.folder / BUDGET).write_text(str(left), encoding="utf-8")
    here = shlex.quote(str(Path(__file__).resolve()))
    command = f"{shlex.quote(sys.executable)} {here} relay {shlex.quote(str(stand.folder))}"
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
    return row


def passed(row: dict) -> bool:
    """Return whether every expect step of a draw held and the run reached its end."""
    return "error" not in row and not any(e["failed"] for e in row["expects"])


def main(argv: list[str]) -> int:
    if argv[:1] == ["relay"]:
        return relay(Path(argv[1]))
    ask = argparse.ArgumentParser(prog="python -m bench.cards", description=__doc__)
    ask.add_argument("card", type=Path)
    ask.add_argument("--draws", type=int, required=True, help="how many times to draw the card")
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
    plan = load_value(args.card.read_text(encoding="utf-8"))
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = args.out or Path.home() / ".conky" / "runs" / "cards" / f"{args.card.stem}-{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    if args.model:
        os.environ[model.MODEL_VARIABLE] = args.model
    notes = {key: plan[key] for key in ("claim", "forecast", "par") if key in plan}
    for key, text in notes.items():
        if isinstance(text, dict):
            for part, line in text.items():
                print(f"{key} {part}: {line}")
        else:
            print(f"{key}: {text}")
    used, widest, wins, drawn = 0, 0, 0, 0
    for number in range(1, args.draws + 1):
        if used + widest > args.cap:
            print(
                f"stopped before draw {number}: it may take {widest} calls and "
                f"{used} of the cap {args.cap} are spent; raise --cap"
            )
            break
        made = draw(args.card, number, out / f"draw-{number}", args.cap - used)
        row = {"card": args.card.stem, **({} if number > 1 else notes), **made}
        with (out / "rows.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps(row) + "\n")
        drawn, used, widest, wins = (
            number,
            used + row["calls"],
            max(widest, row["calls"]),
            wins + passed(row),
        )
        held = sum(not e["failed"] for e in row["expects"])
        print(
            f"draw {number}: {'passed' if passed(row) else 'failed'}, {held} of "
            f"{len(row['expects'])} expects held, {row['calls']} calls, {row['seconds']}s"
        )
    print(f"passed {wins} of {drawn}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
