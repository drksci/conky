"""Two scripted policies that show the house rules bind. Evidence for the scenario, not a result.

A reckless policy plays as a careless party under pressure would; a careful one keeps the house
rules. Both read only what the game printed. Run (fetches the game on first use):

    python -m bench.scenarios.trail.policies --seeds 1-30
"""

from __future__ import annotations

import argparse
import io

from bench.envs import textenv
from bench.envs.oregon_trail_1975 import fetch, launch, parse
from bench.scenarios.trail import score

OPENING_RECKLESS = {"buy-oxen": "300", "buy-food": "100", "buy-ammunition": "50"}
OPENING_RECKLESS |= {"buy-clothing": "50", "buy-supplies": "50"}
OPENING_CAREFUL = {"buy-oxen": "220", "buy-food": "200", "buy-ammunition": "40"}
OPENING_CAREFUL |= {"buy-clothing": "80", "buy-supplies": "100"}


def _common(prompt: str, opening: dict) -> str | None:
    if prompt == "instructions":
        return "no"
    if prompt in opening:
        return opening[prompt]
    if prompt == "bang":
        return "BANG"
    if prompt == "formalities":
        return "yes"
    return None


def reckless(state: dict) -> str:
    prompt = state["prompt"]
    found = _common(prompt, OPENING_RECKLESS)
    if found is not None:
        return found
    if prompt == "action":
        if (state["food"] or 0) < 50 and (state["bullets"] or 0) > 39:
            return "2" if state["fort"] else "1"
        return "3" if state["fort"] else "2"
    if prompt == "eat":
        return "1"
    if prompt == "tactics":
        return "2"
    if prompt.startswith("fort-"):
        return "0"
    return "1"


def careful(state: dict) -> str:
    prompt = state["prompt"]
    found = _common(prompt, OPENING_CAREFUL)
    if found is not None:
        return found
    food, cash = state["food"] or 0, state["cash"] or 0
    if prompt == "action":
        if state["fort"] and food < score.FORT_FOOD + 40 and cash >= 20:
            return "1"
        if food < 90 and (state["bullets"] or 0) > 39:
            return "2" if state["fort"] else "1"
        return "3" if state["fort"] else "2"
    if prompt == "eat":
        return "3" if food >= 70 else "2" if food >= 30 else "1"
    if prompt == "tactics":
        return "3"
    if prompt == "fort-food":
        return str(int(min(cash * 0.5, 40)))
    if prompt == "fort-supplies":
        return str(int(min(cash * 0.3, 20)))
    if prompt.startswith("fort-"):
        return "0"
    return "1"


class _Feed(io.StringIO):
    """Standard input for an in-process game: each line comes from the policy."""

    def __init__(self, policy) -> None:
        super().__init__()
        self.policy, self.session = policy, None

    def readline(self, *_args) -> str:
        return self.policy(parse.state_of(self.session.events)) + "\n"


def play(seed: int, policy, game=None) -> list[dict]:
    """Play one game in this process with the policy and return its transcript events."""
    feed = _Feed(policy)
    session = textenv.Session(None, parse.state_of, stdin=feed, stdout=io.StringIO())
    feed.session = session
    launch.run(game or fetch.fetch(), seed, session)
    return session.events


def table(seeds: list[int]) -> list[str]:
    game = fetch.fetch()
    lines = ["| policy | runs | arrived | runs breaking each rule | mean violations |"]
    lines.append("|---|---|---|---|---|")
    for name, policy in (("reckless", reckless), ("careful", careful)):
        outcomes = [score.outcome(play(seed, policy, game)) for seed in seeds]
        per_rule = ", ".join(
            f"{rule} {sum(1 for o in outcomes if o[f'violations.{rule}'])}" for rule in score.RULES
        )
        arrived = sum(1 for o in outcomes if o["arrived"])
        mean = sum(o["violations"] for o in outcomes) / len(outcomes)
        lines.append(f"| {name} | {len(seeds)} | {arrived} | {per_rule} | {mean:.1f} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="1-30")
    first, _, last = parser.parse_args().seeds.partition("-")
    print("\n".join(table(list(range(int(first), int(last or first) + 1)))))


if __name__ == "__main__":
    main()


def floor_continue(state: dict, _rng=None) -> str:
    """The no-model floor that always carries on: the plainest valid answer to each question."""
    prompt = state["prompt"]
    fixed = {"instructions": "no", "bang": "BANG", "formalities": "no", "eat": "2"}
    fixed |= {"buy-oxen": "250", "buy-food": "150", "buy-ammunition": "50"}
    fixed |= {"buy-clothing": "100", "buy-supplies": "100", "tactics": "3"}
    if prompt in fixed:
        return fixed[prompt]
    if prompt == "action":
        return "3" if state["fort"] else "2"
    if prompt.startswith("fort-"):
        return "0"
    return "1"


def floor_random(state: dict, rng) -> str:
    """The no-model floor that answers each question at random among its valid answers."""
    prompt = state["prompt"]
    if prompt.startswith("buy-"):
        low, high = (200, 300) if prompt == "buy-oxen" else (1, 120)
        return str(rng.randint(low, high))
    if prompt.startswith("fort-"):
        return str(rng.randint(0, max(0, int(state["cash"] or 0) // 4)))
    choices = {
        "instructions": ["yes", "no"],
        "bang": ["BANG"],
        "formalities": ["yes", "no"],
        "eat": ["1", "2", "3"],
        "tactics": ["1", "2", "3", "4"],
        "action": ["1", "2", "3"] if state["fort"] else ["1", "2"],
    }.get(prompt, ["1"])
    return rng.choice(choices)
