"""The plain baseline: one loop around one model, and nothing else.

Each turn it reads the screen, sends the prompt pack, the recent turns and the screen to the
model, and types back the first non-empty line of what the model says, and keeps the whole answer in
its transcript. A reply that starts with SHELF is answered from the
shelf instead of typed. Its only persisted state is `transcript.jsonl` in the working directory.

    adapter.py [contract arguments] -- COMMAND...
    adapter.py --verify  --workdir W
    adapter.py --explain --workdir W
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench.adapters import base  # noqa: E402

HISTORY_CHARS = 6000
SHELF_HELP = (
    "To consult the shelf, reply SHELF to list it or SHELF READ <name> to read one writing; "
    "such a reply is answered here and not typed into the game."
)


def shelf(meter: str, token: str, path: str) -> str:
    request = urllib.request.Request(
        meter.rstrip("/") + path, headers={"Authorization": f"Bearer {token}"}
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=30) as reply:
            data = json.loads(reply.read())
    except OSError as exc:
        return f"(the shelf could not be reached: {exc})"
    if "items" in data:
        return "The shelf holds: " + ", ".join(i["name"] for i in data["items"])
    return data.get("text") or data.get("error", "(nothing)")


def first_line(answer: str) -> str:
    """The first non-empty line of an answer: the only part that is typed."""
    return next((line.strip() for line in answer.splitlines() if line.strip()), "")


def history(notes: list[dict]) -> str:
    parts, size = [], 0
    for entry in reversed(notes):
        piece = f"<<<screen>>>{entry['screen']}<<</screen>>>\nTyped: {entry['typed']}\n"
        if size + len(piece) > HISTORY_CHARS:
            break
        parts.append(piece)
        size += len(piece)
    return "".join(reversed(parts))


def play(args) -> int:
    pack = base.Pack.load(args.prompts)
    notes = base.Notes(args.workdir / "transcript.jsonl")
    done = notes.read()
    if done and not args.resume:
        print("the working directory already holds a transcript; pass --resume", file=sys.stderr)
        return 2
    seq = sum(1 for e in done if "typed" in e)
    terminal = base.Terminal(args.command)
    system = f"{pack.mark(pack.task)}\n\n{pack.mark(pack.rules)}"
    if args.shelf:
        system += f"\n\n{SHELF_HELP}"
    try:
        while True:
            screen = terminal.read()
            if terminal.ended and not screen.strip():
                return 0
            extra = ""
            for _attempt in range(4):
                user = (
                    f"Earlier screens and what was typed:\n{history(notes.read())}\n"
                    f"The screen now:\n{base.mark_screen(screen)}{extra}"
                )
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ]
                status, answer = base.ask_meter(args.meter, args.token, args.model, messages)
                if status != 200:
                    notes.add({"error": status, "detail": answer[:300]})
                    print(f"the meter answered {status}: {answer[:200]}", file=sys.stderr)
                    return 3
                if not answer.upper().startswith("SHELF"):
                    break
                words = answer.split()
                path = "/shelf" if len(words) < 3 else f"/shelf/{words[2]}"
                found = shelf(args.meter, args.token, path)
                notes.add({"shelf": path, "bytes": len(found)})
                extra += f"\n\nYou asked: {answer}\nThe shelf answered:\n{found}"
            seq += 1
            line = first_line(answer)
            notes.add({"seq": seq, "screen": screen, "typed": line, "answer": answer})
            if terminal.ended:
                return 0
            terminal.type(line)
    finally:
        terminal.close()


def explain(workdir: Path) -> list[dict]:
    """Every line the loop typed, in order, with who gave it and what caused it."""
    found = []
    for entry in base.Notes(workdir / "transcript.jsonl").read():
        if "typed" in entry:
            cause = f"the model's reply to screen {entry['seq']}"
            found.append({"keys": entry["typed"], "actor": "loop", "cause": cause})
    return found


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--verify", "--explain"):
        workdir = Path(argv[argv.index("--workdir") + 1])
        if argv[0] == "--verify":
            ok = (workdir / "transcript.jsonl").exists()
            print(json.dumps({"ok": ok, "why": "transcript present" if ok else "no transcript"}))
            return 0 if ok else 1
        print(json.dumps(explain(workdir)))
        return 0
    return play(base.parse_args("The plain loop.", argv))


if __name__ == "__main__":
    sys.exit(main())
