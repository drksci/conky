"""Read the 1975 game's state and decisions from a transcript of its own printed lines.

Every number comes from what the game printed; nothing is inferred from a player.
"""

from __future__ import annotations

import re

STATUS_HEADER = "FOOD, BULLETS, CLOTHING, SUPPLIES, CASH"
NUMBER = r"-?\d+(?:\.\d+)?"
DATE = re.compile(r"^MONDAY ([A-Z]+ \d+) 1847$")
MILEAGE = re.compile(r"^TOTAL MILEAGE IS (" + NUMBER + ")")
STATUS_LINE = re.compile(r"^[\s0-9.\-]+$")
STATUS_NUMBER = re.compile(r"-\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?")
DEATHS = ("YOU DIED OF", "YOU DIE OF", "STARVED TO DEATH", "GOT MASSACRED")
PROMPTS = (
    ("instructions", "DO YOU NEED INSTRUCTIONS"),
    ("buy-oxen", "SPEND ON YOUR OXEN TEAM"),
    ("buy-food", "SPEND ON FOOD"),
    ("buy-ammunition", "SPEND ON AMMUNITION"),
    ("buy-clothing", "SPEND ON CLOTHING"),
    ("buy-supplies", "SPEND ON MISCELLANEOUS SUPPLIES"),
    ("action", "DO YOU WANT TO (1)"),
    ("eat", "DO YOU WANT TO EAT"),
    ("tactics", "CHOICE:"),
    ("bang", "TYPE BANG"),
    ("fort-food", "FOOD:"),
    ("fort-ammunition", "AMMUNITION:"),
    ("fort-clothing", "CLOTHING:"),
    ("fort-supplies", "MISCELLANEOUS SUPPLIES:"),
    ("formalities", "WOULD YOU LIKE"),
)
RETRY = ("NOT ENOUGH", "TOO MUCH", "YOU CAN'T EAT THAT WELL", "YOU OVERSPENT")
MENUS = {"action": None, "eat": 3, "tactics": 4}


def _last_line(screen: str) -> str:
    return screen.rstrip("\n").split("\n")[-1] if screen.strip() else ""


def prompt_kind(screen: str) -> str:
    """Return the kind of question the screen ends with."""
    last = _last_line(screen)
    for kind, words in PROMPTS:
        if words in last:
            return kind
    return "other"


def _number(text: str) -> float | int:
    value = float(text.replace(" ", ""))
    return int(value) if value.is_integer() else value


def blank() -> dict:
    return {
        "turn": 0,
        "date": "",
        "mileage": 0,
        "food": None,
        "bullets": None,
        "clothing": None,
        "supplies": None,
        "cash": None,
        "fort": False,
        "riders": "",
        "inputs": 0,
        "prompt": "",
    }


def _read_lines(state: dict, chunk: str, ending: dict) -> None:
    """Read the complete lines in chunk; a partial last line waits for the next chunk."""
    lines = (state.pop("_partial", "") + chunk).split("\n")
    state["_partial"] = lines.pop()
    for line in lines:
        line = line.rstrip()
        numbers = STATUS_NUMBER.findall(line) if STATUS_LINE.match(line) else []
        if found := DATE.match(line):
            state["turn"] += 1
            state["date"] = found.group(1)
            state["riders"] = ""
        elif found := MILEAGE.match(line):
            state["mileage"] = _number(found.group(1))
        elif len(numbers) == 5 and state.get("_header"):
            for key, value in zip(
                ("food", "bullets", "clothing", "supplies", "cash"), numbers, strict=True
            ):
                state[key] = _number(value)
        elif "RIDERS AHEAD" in line:
            state["riders"] = "friendly-looking" if "DON'T LOOK HOSTILE" in line else "hostile"
        elif "YOU FINALLY ARRIVED AT OREGON CITY" in line:
            ending["outcome"] = "arrived"
        elif any(words in line for words in DEATHS) and "outcome" not in ending:
            ending["outcome"] = "died"
            ending["cause"] = line.strip()
        state["_header"] = line.strip() == STATUS_HEADER


def walk(events: list[dict]) -> tuple[list[dict], dict, dict]:
    """Return the decisions, the state now and how the game ended (if it did).

    Decisions include the environment's own opening answers, marked `"by": "opening"`.
    """
    state, ending = blank(), {}
    last_end = ""
    decisions: list[dict] = []
    screen = ""
    for event in events:
        kind = event["kind"]
        if kind == "out":
            screen += event["text"]
            _read_lines(state, event["text"], ending)
            if decisions and decisions[-1].get("after") is None:
                decisions[-1]["reply"] = decisions[-1].get("reply", "") + event["text"]
        elif kind == "in":
            asked = prompt_kind(screen)
            state["fort"] = asked == "action" and "STOP AT THE NEXT FORT" in _last_line(screen)
            before = {k: v for k, v in state.items() if not k.startswith("_")}
            before["prompt"] = asked
            decisions.append(
                {"n": event["n"], "line": event["line"], "prompt": asked, "state": before,
                 "by": event.get("by", "player")}
            )  # fmt: skip
            state["inputs"] = event["n"]
            screen = ""
        elif kind == "crash":
            ending.setdefault("outcome", "crashed")
            ending.setdefault("cause", event.get("error", ""))
        elif kind == "end":
            last_end = event.get("outcome", "ended")

    if "outcome" not in ending and last_end:
        ending["outcome"] = last_end
    for decision in decisions:
        decision["invalid"] = _invalid(decision)
    state["prompt"] = prompt_kind(screen)
    state["fort"] = state["prompt"] == "action" and "STOP AT THE NEXT FORT" in _last_line(screen)
    now = {k: v for k, v in state.items() if not k.startswith("_")}
    return decisions, now, ending


def _invalid(decision: dict) -> bool:
    line, kind = decision["line"].strip(), decision["prompt"]
    reply = decision.get("reply", "")
    first = next((part.strip() for part in reply.split("\n") if part.strip()), "")
    if any(first.startswith(words) for words in RETRY):
        return True
    if kind in ("instructions", "bang", "formalities", "other"):
        return kind == "instructions" and not line
    if not re.fullmatch(r"-?\d+", line):
        return True
    top = MENUS.get(kind)
    if kind == "action":
        top = 3 if decision["state"]["fort"] else 2
    return top is not None and not 1 <= int(line) <= top


def state_of(events: list[dict]) -> dict:
    """The state a stop condition is tested against."""
    return walk(events)[1]
