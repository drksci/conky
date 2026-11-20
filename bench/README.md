# The bench

A harness comparison on a real text game, run by Conky and by other harnesses on the same model,
budget and start. The methods are fixed in
[the benchmark protocol](../docs/research/benchmark-protocol.md). It has no results yet.

Standard library only, beside Conky's own dependencies. POSIX only (pseudo-terminals).

## One command: the smoke run

No model is called; the `scripted` stand-in answers. The first run fetches the 1975 game into
`~/.cache/conky-bench` and checks its hash.

```
python -m bench.walk --arm conky --out /tmp/bench-walk-conky
```

It walks one run stage by stage and stops at the first stage that fails: the game fetched and
verified, the same first screen twice, the opening, one metered call, what the agent receives,
the answer reaching the game, a full turn, a stop and a fresh process carrying on, the analysis
reading the run. `--arm loop` walks the baseline.

## Running a matrix

```
python -m bench.run --arms conky,loop,floor-continue,floor-random --prompts full,minimal \
    --seeds 1-5 --backend scripted --out /tmp/bench-results
python -m bench.analyse /tmp/bench-results
```

The analysis refuses runs on the `scripted` backend; they show the plumbing only.

## A live pilot

Live runs happen only after review. With a model reachable through Conky's model code (an API
key, or `claude` on the path), a small pilot:

```
python -m bench.run --arms conky,loop,floor-continue,floor-random --prompts full \
    --seeds 1-5 --backend conky-model --model claude-sonnet-5-5 \
    --calls 120 --tokens 300000 --wall 1800 --stall 300 --out /tmp/bench-pilot
```

`--model` must name the model the backend uses; the meter refuses any other. Every live call is
kept in each run's `cache/`, and `--cache-mode replay --replay-from /tmp/bench-pilot` re-does
runs without paying again (never reported as new results).

## Stepping and stop points

- `--stop-when COND` (repeatable): `turn>=8`, `food<50`, `prompt==eat`, `inputs>=20`. The run
  ends cleanly with exit reason `stopped`, everything kept.
- `--resume RUN_DIR [--arm NAME]`: carry on a stopped run in a fresh process.
- `--step`: one run; after each input, print the screen, the line typed and the model calls,
  and wait for Enter.

A stepped or hand-resumed run is never a reported result.

## Probes

`--probe constraint|resume|portability|overhead`; definitions in `probes/`. The constraint probe
also walks without a model: `python -m bench.walk --probe constraint --out DIR`.

`--answers pages` (the Conky arm only) lets the character answer with pages as well as a line;
`python -m bench.walk --arm conky --out DIR` walks it as stage 10.

## Layout

- `envs/oregon_trail_1975/`: fetch, launcher (pins, transcript, stops, replay), parser.
- `envs/textenv.py`: the runner's hold on any line-based game.
- `envs/oregon_trail_site/`: the 1992 web game in a browser, for the second scenario.
- `scenarios/trail/`: the scenario document, prompt pack, shelf, scoring, scripted policies.
- `meter.py`, `backends.py`: the metering door and what answers behind it.
- `adapters/`: the contract and the arms.
- `run.py`, `analyse.py`, `walk.py`: runner, analysis, walkthrough.

Runs write only to `--out`, which must be outside this repository.
