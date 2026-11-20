"""The standard run record: every run, of any scenario and any harness, reduced to one row and one
series, and a check that a set of rows can be compared.

    row(folder)       one dict with the keys in `KEYS`, in that order
    series(folder)    one entry a step: step, progress, calls and chars so far, violations
    calls(folder)     one entry per model call: its step, bytes by origin, chars, tokens
    comparable(rows)  the reasons a set of rows is not comparable, empty when it is

The record reads the run files that `bench.run` writes (`run.json`, `meter.jsonl`,
`transcript.jsonl`). What is specific to a scenario comes from its `scenario.json` (`progress`)
and its score module (`steps`, `result`); what is specific to a harness comes from its
`adapter.json` (`gloss`, `kept`). Nothing here names a scenario or a harness. Standard library
only.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

from bench.envs import textenv

BENCH = Path(__file__).resolve().parent
KEYS = (
    "scenario",
    "scenario_version",
    "harness",
    "gloss",
    "model",
    "seed",
    "commit",
    "prompt",
    "prompt_sha",
    "budget_calls",
    "backend",
    "date",
    "ending",
    "progress",
    "value",
    "steps",
    "calls",
    "chars",
    "tokens",
    "wall_s",
    "violations",
    "kept",
    "tape",
    "version",
    "cost",
)
BUDGET_EXITS = ("budget-exhausted", "wall-clock", "stalled", "stopped")


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def _meta(folder: Path) -> dict:
    return json.loads((folder / "run.json").read_text(encoding="utf-8"))


def scenario_config(name: str) -> dict:
    """The scenario's `scenario.json`."""
    return json.loads((BENCH / "scenarios" / name / "scenario.json").read_text(encoding="utf-8"))


def _score(name: str):
    return importlib.import_module(f"bench.scenarios.{name}.score")


def manifest(harness: str) -> dict:
    """The `adapter.json` that declares this harness, or an empty one."""
    for path in sorted((BENCH / "adapters").glob("*/adapter.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if harness in data.get("arms", {}):
            return data
    return {}


def steps(folder: Path) -> list[dict]:
    """The scenario's per-decision steps for this run's transcript."""
    events = textenv.read(folder / "transcript.jsonl")
    return _score(_meta(folder).get("scenario", "")).steps(events)


def _step_of(steps_: list[dict], started: float) -> int:
    """A call belongs to the step of the decision its answer was typed for."""
    later = [s["step"] for s in steps_ if s["t"] >= started]
    return later[0] if later else (steps_[-1]["step"] if steps_ else 0)


def calls(folder: Path) -> list[dict]:
    """The model calls that were answered, each with the step it belongs to."""
    found = steps(folder)
    out = []
    answered = [c for c in _jsonl(folder / "meter.jsonl") if c.get("status") == 200]
    began = answered[0]["t_start"] if answered else 0.0
    for c in answered:
        out.append(
            {
                "step": _step_of(found, c["t_start"]),
                "at": round(c["t_start"] - began, 3),
                "seconds": round(
                    c.get("latency_s") or c.get("t_end", c["t_start"]) - c["t_start"], 3
                ),
                "answer": c.get("chars_out", 0),
                "task": c.get("pack_bytes", 0),
                "screen": c.get("screen_bytes", 0),
                "scaffold": c.get("scaffold_bytes", 0),
                "other": c.get("image_bytes", 0),
                "chars": c.get("chars_in", 0) + c.get("chars_out", 0),
                "tokens": (c.get("tokens_in") or 0) + (c.get("tokens_out") or 0),
                "tokens_known": bool(c.get("tokens_known")),
                "proposed": (c.get("note") or {}).get("proposed"),
            }
        )
    return out


def series(folder: Path) -> list[dict]:
    """One entry a step: progress (0 to 1), calls and characters so far, rules broken there."""
    meta = _meta(folder)
    name = meta.get("scenario", "")
    goal = scenario_config(name)["progress"]["goal"]
    events = textenv.read(folder / "transcript.jsonl")
    final = _score(name).result(events)
    found: dict[int, dict] = {}
    for s in steps(folder):
        entry = found.setdefault(s["step"], {"value": 0.0, "violations": []})
        entry["value"] = s["value"]
        entry["violations"] += s["violations"]
    entry = found.setdefault(final["steps"], {"value": 0.0, "violations": []})
    entry["value"] = final["value"]
    made = calls(folder)
    return [
        {
            "step": step,
            "progress": min(entry["value"] / goal, 1.0),
            "calls": sum(1 for c in made if c["step"] <= step),
            "chars": sum(c["chars"] for c in made if c["step"] <= step),
            "violations": entry["violations"],
        }
        for step, entry in sorted(found.items())
    ]


def kept(folder: Path, declared: dict | None) -> int | None:
    """Pages the harness's character kept for itself, as its `adapter.json` says to count them;
    None when the harness declares nothing to count."""
    if not declared:
        return None
    skip = set(declared.get("except", []))
    return sum(
        1
        for page in folder.glob(declared["glob"])
        if page.stem not in skip and declared.get("contains", "") in page.read_text("utf-8")
    )


def ending(meta: dict, found: dict) -> str:
    """reached, lost, capped or broke, from the scenario's verdict and how the run exited."""
    exit_ = meta.get("exit") or ""
    if found["ending"] == "reached":
        return "reached"
    if found["ending"] == "broke" or exit_ == "crashed":
        return "broke"
    if exit_ in BUDGET_EXITS:
        return "capped"
    return found["ending"] or "broke"


def row(folder: Path) -> dict:
    """The standard record of one run, with exactly the keys in `KEYS`."""
    meta = _meta(folder)
    name = meta.get("scenario", "")
    config = scenario_config(name)
    harness = meta["arm"]
    events = textenv.read(folder / "transcript.jsonl")
    found = _score(name).result(events)
    made = calls(folder)
    known = all(c["tokens_known"] for c in made)
    steps_ = series(folder)
    seg = meta.get("segments", [])
    uses_model = meta.get("uses_model", True)
    versions = meta.get("versions") or {}
    tape = hashlib.sha256((folder / "transcript.jsonl").read_bytes()).hexdigest()[:12]
    return {
        "scenario": name,
        "scenario_version": meta.get("scenario_version"),
        "harness": harness,
        "gloss": manifest(harness).get("gloss", {}).get(harness, ""),
        "model": meta.get("model", "?") if uses_model else "none",
        "seed": meta["seed"],
        "commit": (meta.get("versions") or {}).get("repository", ""),
        "prompt": meta.get("prompt", ""),
        "prompt_sha": meta.get("prompt_sha256", ""),
        "budget_calls": (meta.get("budget") or {}).get("calls", 0),
        "backend": meta.get("backend", "?"),
        "date": meta.get("start", "")[:10],
        "ending": ending(meta, found),
        "progress": round(min(found["value"] / config["progress"]["goal"], 1.0), 4),
        "value": round(found["value"], 1),
        "steps": found["steps"],
        "calls": len(made),
        "chars": sum(c["chars"] for c in made),
        "tokens": sum(c["tokens"] for c in made) if known else None,
        "wall_s": round(sum(s["end"] - s["start"] for s in seg if "end" in s), 1),
        "violations": sum(len(s["violations"]) for s in steps_),
        "kept": kept(folder, manifest(harness).get("kept")),
        "tape": tape,
        "version": versions.get("harness") or versions.get("repository", "")[:7],
        "cost": _cost(meta, made, uses_model),
    }


def _cost(meta: dict, made: list[dict], uses_model: bool) -> float | None:
    """Dollars for the run: what the harness reported of itself, else list price for its calls,
    nothing for a harness with no model, and None when neither is known."""
    if not uses_model:
        return 0.0
    told = (meta.get("self_reported") or {}).get("total_cost_usd")
    if isinstance(told, int | float):
        return round(float(told), 6)
    found = dollars(meta.get("model", ""), made)
    return round(found[0], 6) if found else None


def link(harness: str) -> str:
    """Where a reader can find the harness, from its `adapter.json`, or nothing."""
    return manifest(harness).get("link", {}).get(harness, "")


def _spread(values: set) -> str:
    return ", ".join(sorted(str(v) for v in values))


def comparable(rows: list[dict]) -> list[str]:
    """The reasons the arms of a set of rows are not comparable; empty when they are."""
    reasons = []
    models = {r["model"] for r in rows if r["model"] != "none"}
    if len(models) > 1:
        reasons.append(f"the arms that use a model use different ones ({_spread(models)})")
    seeds: dict[str, set] = {}
    for r in rows:
        seeds.setdefault(r["harness"], set()).add(r["seed"])
    if len({frozenset(s) for s in seeds.values()}) > 1:
        reasons.append("the arms were not run on the same seeds")
    for key, what in (
        ("prompt_sha", "prompts"),
        ("budget_calls", "call budgets"),
        ("scenario_version", "scenario versions"),
        ("backend", "backends"),
    ):
        values = {r[key] for r in rows}
        if len(values) > 1:
            reasons.append(f"the runs have different {what} ({_spread(values)})")
    commits = {r["commit"] for r in rows}
    if len(commits) > 1:
        reasons.append(f"the runs were made at different commits ({_spread(commits)})")
    if any(c.endswith("+changes") for c in commits):
        reasons.append("a run was made with uncommitted changes, so its commit is not what ran")
    return reasons


def label(harness: str) -> str:
    """The name a reader sees for a harness: its `adapter.json` label, or its own name."""
    return manifest(harness).get("label", {}).get(harness, harness)


def prices() -> dict:
    """The price list in `bench/prices.json`."""
    return json.loads((BENCH / "prices.json").read_text(encoding="utf-8"))


def dollars(model: str, made: list[dict]) -> tuple[float, str] | None:
    """What a run's model calls cost at list price, and how the tokens were counted.

    None when the model has no price. Tokens are the recorded counts when every call has them;
    otherwise they are estimated from characters, and the second value says so.
    """
    listed = prices()
    price = listed["models"].get(model)
    if price is None or not made:
        return None
    per = listed["characters_per_token"]
    sent = sum(c["chars"] - c.get("answer", 0) for c in made) / per
    answered = sum(c.get("answer", 0) for c in made) / per
    basis = f"tokens estimated at {per} characters each"
    return (sent * price["input"] + answered * price["output"]) / 1_000_000, basis
