"""A stock agent command line as a control arm: it gets the task text and plays however it likes.

The adapter starts the game once and keeps it open. The command line (default: Claude Code in
print mode) is run once in `workdir/agent`, with the task text on standard input and the helper
`./game` beside it. `./game "<line>"` types a line and prints the new screen; `./game` prints
the current screen. Every line and screen goes to `session.jsonl`; what the command line says
about itself goes to `report.json`. The game's own transcript stays the ground truth.

Its model calls do not pass through the meter, so nothing here is metered: the turn limit is a
count of the lines typed into the game.

    adapter.py [contract arguments] [--agent CMD] [--turn-limit N] [--replay RUN_DIR] -- COMMAND...
    adapter.py --explain --workdir W

With `--replay RUN_DIR` no command line runs: the lines recorded in that run are typed again.
"""

from __future__ import annotations

import json
import os
import select
import shlex
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench.adapters import base  # noqa: E402

HERE = Path(__file__).resolve().parent
SCENARIO_TURNS = 150
DEFAULT_AGENT = (
    "claude -p --model {model} --output-format json --permission-mode dontAsk "
    "--tools Bash,Read,Write,Edit --allowedTools Bash(./game),Bash(./game\\ *),Read,Write,Edit "
    "--no-session-persistence --disable-slash-commands --max-budget-usd 5"
)
DECLARED = (
    'The game is already running. Type one line into it by running ./game "<line>" in your working '
    "directory, which prints the new screen; ./game with no argument prints the current screen. "
    "Your reply is not typed into the game: only ./game types.\n"
    "Files in your working directory are yours to read and write; the shelf, if there is one, is "
    "the folder shelf/ there."
)
GRACE = 5.0
ENDED = "\n(the game has ended)\n"


def parse(argv: list[str]):
    found = base.parser("A stock agent command line as a control arm.")
    found.add_argument("--agent", default=DEFAULT_AGENT, help="the command line, {model} filled in")
    found.add_argument("--turn-limit", type=int, default=SCENARIO_TURNS)
    found.add_argument("--replay", type=Path, default=None, help="a finished run's directory")
    args = found.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise SystemExit("give the environment command after --")
    args.workdir.mkdir(parents=True, exist_ok=True)
    return args


def prompt_text(args) -> str:
    pack = base.Pack.load(args.prompts)
    return f"{pack.task}\n\n{pack.rules}\n\n{DECLARED}\n"


def prepare(args) -> Path:
    """The agent's own folder: the helper, and the shelf as files when the run offers it."""
    folder = args.workdir / "agent"
    folder.mkdir()
    helper = folder / "game"
    shutil.copy2(HERE / "game.py", helper)
    helper.chmod(0o755)
    config = json.loads((args.scenario / "scenario.json").read_text())
    shelf = args.scenario / "shelf"
    prompt = args.prompts.name
    offered = args.shelf or config["prompts"].get(prompt, {}).get("shelf")
    if offered and shelf.is_dir():
        shutil.copytree(shelf, folder / "shelf")
    return folder


class Game:
    """The game held open, with its record of every line typed and screen shown."""

    def __init__(self, command: list[str], record: base.Notes) -> None:
        self.terminal = base.Terminal(command)
        self.record = record
        self.screen = self.terminal.read()
        self.typed = 0
        record.add({"seq": 0, "typed": None, "screen": self.screen})

    @property
    def ended(self) -> bool:
        return self.terminal.ended

    def show(self) -> str:
        return self.screen + (ENDED if self.ended else "")

    def type(self, line: str) -> str:
        if self.ended:
            return self.show()
        line = line.strip("\r\n")
        self.terminal.type(line)
        self.typed += 1
        self.screen = self.terminal.read()
        self.record.add({"seq": self.typed, "typed": line, "screen": self.screen})
        return self.show()


def serve(game: Game, listener: socket.socket, limit: int, alive) -> str:
    """Answer the helper until the game ends, the turn limit is hit or the agent is gone."""
    while alive() and not game.ended:
        if not select.select([listener], [], [], 0.2)[0]:
            continue
        link, _ = listener.accept()
        with link:
            data = b""
            while chunk := link.recv(65536):
                data += chunk
            text = data.decode("utf-8", "replace")
            if text.startswith("T") and game.typed >= limit:
                link.sendall(f"(the turn limit of {limit} lines is reached)\n".encode())
                return "turn-limit"
            link.sendall((game.type(text[1:]) if text.startswith("T") else game.show()).encode())
    return "game-ended" if game.ended else "agent-exited"


def play(args) -> int:
    if args.resume:
        print(
            "this arm cannot resume: a command line run once has no state to carry on",
            file=sys.stderr,
        )
        return 2
    record = base.Notes(args.workdir / "session.jsonl")
    if record.read():
        print("the working directory already holds a session", file=sys.stderr)
        return 2
    game = Game(args.command, record)
    try:
        if args.replay:
            return replay(args, game)
        return run_agent(args, game)
    finally:
        game.terminal.close()


def replay(args, game: Game) -> int:
    """Type the lines a finished run recorded, with no command line at all."""
    source = base.Notes(args.replay / "workdir" / "session.jsonl").read()
    for entry in source:
        if entry["typed"] is None:
            continue
        if game.ended:
            break
        game.type(entry["typed"])
    report = args.replay / "workdir" / "report.json"
    if report.exists():
        shutil.copy2(report, args.workdir / "report.json")
    return 0


def run_agent(args, game: Game) -> int:
    folder = prepare(args)
    command = [part.format(model=args.model) for part in shlex.split(args.agent)]
    sock = ".game.sock"
    here = os.getcwd()
    os.chdir(folder)
    listener = socket.socket(socket.AF_UNIX)
    listener.bind(sock)
    listener.listen(4)
    os.chdir(here)
    with (
        (args.workdir / "agent.out").open("w") as out,
        (args.workdir / "agent.err").open("w") as err,
    ):
        proc = subprocess.Popen(
            command, cwd=folder, stdin=subprocess.PIPE, stdout=out, stderr=err, text=True,
            start_new_session=True,
        )  # fmt: skip
        assert proc.stdin is not None
        try:
            proc.stdin.write(prompt_text(args))
            proc.stdin.close()
        except BrokenPipeError:
            pass
        ended = serve(game, listener, args.turn_limit, lambda: proc.poll() is None)
        deadline = time.monotonic() + GRACE
        while proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.1)
        if proc.poll() is None:
            os.killpg(proc.pid, 15)
            proc.wait()
    listener.close()
    stdout = (args.workdir / "agent.out").read_text(encoding="utf-8", errors="replace")
    report = {"command": command, "returncode": proc.returncode, "ended": ended,
              "lines_typed": game.typed, "self_reported": self_report(stdout)}  # fmt: skip
    (args.workdir / "report.json").write_text(json.dumps(report, indent=1))
    return 4 if ended == "turn-limit" else 0


def self_report(stdout: str) -> dict | None:
    """What the command line said about itself, when its last line is a JSON object."""
    for line in reversed(stdout.strip().splitlines()):
        try:
            found = json.loads(line)
        except ValueError:
            return None
        return found if isinstance(found, dict) else None
    return None


def explain(workdir: Path) -> list[dict]:
    found = []
    for entry in base.Notes(workdir / "session.jsonl").read():
        if entry["typed"] is not None:
            cause = f"the command line's ./game call {entry['seq']}"
            found.append({"keys": entry["typed"], "actor": "agent", "cause": cause})
    return found


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--explain":
        print(json.dumps(explain(Path(argv[argv.index("--workdir") + 1]))))
        return 0
    return play(parse(argv))


if __name__ == "__main__":
    sys.exit(main())
