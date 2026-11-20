"""A stand-in command line for tests, named `stub`: it plays `./game` with scripted lines.

    fake.py LINE...

It reads the prompt on standard input as a real command line would, looks at the screen, types
each given line with `./game` in its working directory, then prints one JSON object shaped like
the report a print-mode agent gives about itself. It calls no model and costs nothing.
"""

import json
import subprocess
import sys


def main(argv: list[str]) -> int:
    prompt = sys.stdin.read()
    turns = 0
    for line in [None, *argv[1:]]:
        command = ["./game"] if line is None else ["./game", line]
        done = subprocess.run(command, capture_output=True, text=True, check=False)
        turns += 1
        if done.returncode != 0 or "the game has ended" in done.stdout:
            break
    usage = {"input_tokens": len(prompt), "output_tokens": turns}
    report = {"type": "result", "num_turns": turns, "total_cost_usd": 0.0, "usage": usage,
              "is_error": False}  # fmt: skip
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
