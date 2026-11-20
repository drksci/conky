# Probe: resume from stored state alone

Class: harness with a model; mechanism with fixed answers.

- Asked of a harness: after `--stop-when` holds (for example `turn>=6`), the game stops, the
  arm's process ends, and a fresh process of the same arm starts with `--resume` and only its
  working directory. The game replays its own recorded inputs silently and shows the current
  situation, so the world stands where it stopped.
- Score from the transcript: resumed (an accepted input after the second start), the first
  input after the resume valid, invalid answers and violations after the resume, outcome.
- Works on any scenario whose environment can stop and replay.
- Run: `python -m bench.run --probe resume --stop-when turn>=6 --arms conky,loop --out DIR`
