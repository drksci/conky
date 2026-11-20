"""The runner: each (instance, condition, repeat) goes through the meter, in a seeded order.

    python -m bench.experiments.felt_sense.run --backend conky-model --model NAME \\
        --instances 10 --repeats 1 --out DIR

The default backend is the stand-in of `walk.py`, which calls no model. `conky-model` is live
and is chosen by name only. The meter is called in process, with the same handler its server uses.
"""

from __future__ import annotations

import argparse
import json
import random
import secrets
from pathlib import Path

from bench.experiments.felt_sense import analyse, render, tasks
from bench.meter import Budget, Meter

TOKEN_LIMIT = 400
RETRIES = 2


def plan(instances: list[tasks.Instance], repeats: int, seed: int) -> list[tuple]:
    """The seeded order: instances shuffled, conditions shuffled within each, repeats together."""
    rng = random.Random(seed)
    order = list(instances)
    rng.shuffle(order)
    items = []
    for instance in order:
        conditions = list(render.CONDITIONS)
        rng.shuffle(conditions)
        items += [(instance, c, r) for c in conditions for r in range(repeats)]
    return items


def ask(meter: Meter, model: str, token: str, text: str) -> tuple[int, dict]:
    body = {
        "model": model,
        "max_tokens": TOKEN_LIMIT,
        "messages": [{"role": "user", "content": text}],
    }
    headers = {"authorization": f"Bearer {token}"}
    return meter.handle("/v1/chat/completions", headers, json.dumps(body).encode("utf-8"))


def row_of(instance: tasks.Instance, condition: str, repeat: int, answer: dict) -> dict:
    text = answer["choices"][0]["message"]["content"]
    given, confidence = analyse.parse(text, instance.task)
    usage = answer.get("usage", {})
    return {
        "instance": instance.id,
        "task": instance.task,
        "stratum": instance.stratum,
        "dimension": instance.dimension,
        "condition": condition,
        "repeat": repeat,
        "answer": given,
        "truth": instance.truth,
        "correct": given == instance.truth.lower(),
        "confidence": confidence,
        "tokens_in": usage.get("prompt_tokens"),
        "tokens_out": usage.get("completion_tokens"),
    }


def run(
    instances: list[tasks.Instance],
    backend: object,
    out: Path,
    model: str = "stand-in",
    repeats: int = 1,
    seed: int = 1,
    cache_mode: str = "off",
) -> list[dict]:
    """Send every request, write `results.jsonl` and `meter.jsonl` in `out`, return the rows.

    A call that fails is retried twice. An instance still lacking a call under any condition is
    dropped for all conditions and named in `dropped.json`. A wrong or unparsable answer is kept.
    """
    out.mkdir(parents=True, exist_ok=True)
    items = plan(instances, repeats, seed)
    token = secrets.token_hex(8)
    budget = Budget(calls=len(items) * (RETRIES + 1), tokens=10**9)
    meter = Meter(
        backend, model, token, budget, out / "meter.jsonl",
        cache_mode=cache_mode, cache=out / "cache",
    )  # fmt: skip
    rows, dropped = [], set()
    for instance, condition, repeat in items:
        text = render.prompt(instance, condition)
        for _ in range(RETRIES + 1):
            status, answer = ask(meter, model, token, text)
            if status == 200:
                rows.append(row_of(instance, condition, repeat, answer))
                break
        else:
            dropped.add(instance.id)
    rows = [r for r in rows if r["instance"] not in dropped]
    (out / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )
    (out / "dropped.json").write_text(json.dumps(sorted(dropped)), encoding="utf-8")
    return rows


def table(rows: list[dict], resamples: int = 10000) -> str:
    """One row per condition: accuracy, the paired contrast against b, consistency, tokens."""
    acc, same, spent = analyse.accuracy(rows), analyse.consistency(rows), analyse.tokens(rows)
    lines = ["cond  accuracy  minus b (95% interval)    consistency  tokens in/out"]
    for c in render.CONDITIONS:
        if c not in acc:
            continue
        if c == "b":
            versus = "-"
        else:
            d = analyse.contrast(rows, c, "b", resamples)
            versus = f"{d['difference']:+.3f} [{d['low']:+.3f}, {d['high']:+.3f}]"
        kept = "-" if same[c] is None else f"{same[c]:.2f}"
        lines.append(
            f"{c:<6}{acc[c]:<10.3f}{versus:<26}{kept:<13}{spent[c][0]:.0f}/{spent[c][1]:.0f}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the felt-sense experiment through the meter.")
    parser.add_argument("--backend", choices=["stand-in", "conky-model"], default="stand-in")
    parser.add_argument("--model", default="stand-in", help="the model name the meter enforces")
    parser.add_argument("--instances", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1, help="the order of instances and conditions")
    parser.add_argument("--pilot", action="store_true", help="use the pilot seed range")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    found = tasks.instances(args.instances, tasks.PILOT_SEED if args.pilot else tasks.MAIN_SEED)
    if args.backend == "conky-model":
        from bench.backends import ConkyModel

        backend, mode = ConkyModel(), "record"
    else:
        from bench.experiments.felt_sense.walk import StandIn

        backend, mode = StandIn(found), "off"
    rows = run(found, backend, args.out, args.model, args.repeats, args.seed, mode)
    print(table(rows))


if __name__ == "__main__":
    main()
