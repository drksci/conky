# The cli arm: a stock agent as a control

One arm is nothing but an off-the-shelf agent command line given the same task text and left to
do it however it likes. It is a control, shown beside the metered arms and never pooled with them.
The wiring and every byte the adapter adds are in `scaffold.md`.

```bash
python -m bench.run --arms cli --model <model> --out /tmp/bench-cli
```

## How it plays

The adapter starts the game once and keeps it open. The command line runs once in
`workdir/agent/`, where `./game "<line>"` types a line and prints the new screen, and `./game`
prints the current screen. Files in that folder are the agent's own.

## What differs from the metered arms

- Its model calls do not pass through the meter. Calls, tokens and cost are whatever the command
  line reports about itself, kept in `run.json` as `self_reported`; the analysis shows calls and
  tokens as unknown, not zero.
- Its budget is a turn limit (lines typed) and the command line's own dollar cap, not the meter's.
- It cannot resume, and the hostile-model probe does not apply. The runner refuses both.
- The analysis labels it `unmetered control`, and it is never paired with a metered arm.

## Options on the runner

- `--agent COMMAND`: the command line to run, `{model}` filled in. The default is in `scaffold.md`.
- `--replay RUN_DIR`: type the lines a finished run recorded, with no command line, and copy its
  self-report. The game is deterministic, so the transcript is the same.

## Record and replay

A live session is paid for once. `session.jsonl` and `report.json` in its working directory are
the whole record. A replay, a walk and any re-analysis run from them. The tests use `fake.py`,
a stub that calls `./game` with given lines; no test runs a live command line.

## Walked

The default command line has been run live once a step. The first walk typed nothing: the
permission flags, read from `claude --help` only, denied the game helper. The form that works
allows the helper by prefix, `Bash(./game:*)`, and is what the default now uses.
