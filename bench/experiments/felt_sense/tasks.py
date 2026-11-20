"""The three task generators. Each instance has an exact answer, computed from rounded values."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

STRATA = ("below", "inside", "beyond")
MARGIN = 1.3
BANDS = {
    "time": {"below": (0.2, 2.0), "inside": (2.0, 7889400.0), "beyond": (7889400.0, 3.2e9)},
    "money": {"below": (0.05, 4.0), "inside": (4.0, 400000.0), "beyond": (400000.0, 4e9)},
}
MAIN_SEED, PILOT_SEED = 1_000_000, 9_000_000
LETTERS = "ABCD"


@dataclass
class Instance:
    """One task instance. `values` are magnitudes in base units, `slots` fill the sentence."""

    task: str
    seed: int
    stratum: str
    dimension: str
    template: str
    values: dict[str, float]
    slots: dict[str, int | str]
    truth: str
    order: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.task}-{self.stratum}-{self.seed}"


def sig(value: float, digits: int = 3) -> float:
    return float(f"{value:.{digits}g}")


def log_uniform(rng: random.Random, low: float, high: float) -> float:
    return 10 ** rng.uniform(math.log10(low), math.log10(high))


def reference(rng: random.Random, dimension: str, stratum: str) -> float:
    return sig(log_uniform(rng, *BANDS[dimension][stratum]))


def other(rng: random.Random, m0: float) -> float:
    return sig(m0 * log_uniform(rng, 0.1, 10.0))


def t1(seed: int, stratum: str) -> Instance:
    rng = random.Random(seed)
    while True:
        stock = rng.randint(3, 400)
        wait = reference(rng, "time", stratum)
        rho = 10 ** rng.uniform(-1.5, 1.5)
        step = sig(wait / (stock * rho))
        ratio = stock * step / wait
        if step > 0 and not 1 / MARGIN < ratio < MARGIN:
            break
    template = (
        "A store holds {S} units and uses one unit every {p}. The next resupply arrives in {D}. "
        "Do the supplies last until the resupply? The answer is `lasts` or `runs out`."
    )
    return Instance(
        "T1", seed, stratum, "time", template, {"p": step, "D": wait}, {"S": stock},
        "lasts" if ratio >= 1 else "runs out",
    )  # fmt: skip


def t2(seed: int, stratum: str) -> Instance:
    rng = random.Random(seed)
    while True:
        m0 = reference(rng, "time", stratum)
        elapsed = [other(rng, m0) for _ in LETTERS]
        elapsed[rng.randrange(4)] = m0
        waits = [other(rng, m0) for _ in LETTERS]
        urgency = [e / w for e, w in zip(elapsed, waits, strict=True)]
        ranked = sorted(urgency, reverse=True)
        if all(a / b >= MARGIN for a, b in zip(ranked, ranked[1:], strict=False)):
            break
    order = [LETTERS[i] for i in sorted(range(4), key=lambda i: -urgency[i])]
    lines = " ".join(f"{k}: happened {{e{k}}} ago, can wait {{w{k}}}." for k in LETTERS)
    template = (
        f"Four events. {lines} Urgency is the time since it happened divided by the time it can "
        "wait. Which event is most urgent? List all four, most urgent first, as letters "
        "separated by commas."
    )
    values = {f"e{k}": elapsed[i] for i, k in enumerate(LETTERS)}
    values |= {f"w{k}": waits[i] for i, k in enumerate(LETTERS)}
    return Instance("T2", seed, stratum, "time", template, values, {}, order[0], order)


def t3(seed: int, stratum: str) -> Instance:
    rng = random.Random(seed)
    while True:
        size = reference(rng, "money", stratum)
        times = rng.randint(2, 60)
        rho = 10 ** rng.uniform(-1.5, 1.5)
        cost = sig(size * times * rho)
        ratio = size * times / cost
        if cost > 0 and not 1 / MARGIN < ratio < MARGIN:
            break
    template = (
        "An overrun of {d} will recur {n} times before the plan ends. Correcting it costs {K} "
        "once. Is it worth correcting? The answer is `correct` or `leave`."
    )
    return Instance(
        "T3", seed, stratum, "money", template, {"d": size, "K": cost}, {"n": times},
        "correct" if ratio > 1 else "leave",
    )  # fmt: skip


GENERATORS = {"T1": t1, "T2": t2, "T3": t3}


def generate(task: str, seed: int, stratum: str) -> Instance:
    return GENERATORS[task](seed, stratum)


def instances(count: int, base: int = MAIN_SEED) -> list[Instance]:
    """`count` instances cycling the tasks, then the strata, each with its own seed."""
    tasks = list(GENERATORS)
    return [generate(tasks[i % 3], base + i, STRATA[(i // 3) % 3]) for i in range(count)]
