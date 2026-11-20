"""The two no-model floors: always carry on, or answer at random. They cost nothing.

adapter.py [contract arguments] --policy continue|random -- COMMAND...
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench.adapters import base  # noqa: E402
from bench.backends import screen_state  # noqa: E402
from bench.scenarios.trail import policies  # noqa: E402

KEEP = 3000


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    at = argv.index("--policy")
    policy = {"continue": policies.floor_continue, "random": policies.floor_random}[argv[at + 1]]
    del argv[at : at + 2]
    args = base.parse_args("A no-model floor.", argv)
    rng = random.Random(f"floor|{args.seed}")
    terminal = base.Terminal(args.command)
    seen = ""
    try:
        while True:
            screen = terminal.read()
            seen = (seen + screen)[-KEEP:]
            if terminal.ended:
                return 0
            terminal.type(policy(screen_state(seen), rng))
    finally:
        terminal.close()


if __name__ == "__main__":
    sys.exit(main())
