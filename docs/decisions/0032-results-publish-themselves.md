---
kind: decision
title: Results publish themselves
status: accepted
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: results publish themselves
    text: A benchmark's charts, data, results page and README block are generated from the run files by one command and never edited by hand.
---

# 0032 Results publish themselves

## Context

- Runtime output was kept out of the repository entirely, with the golden vault as the one exception. A benchmark result is runtime output that readers need to see.
- A result copied by hand into a page drifts from the runs behind it, and every new run means the same rework.
- A chart alone cannot be checked or redrawn by a reader.
- The first pilot showed the value of looking at raw runs before trusting a number: two of three Conky runs ended on the first answer, because the instruction for writing pages came after the game's question and a small model answered the wrong one.

## Decision

One command, `bench/publish.py`, turns a results directory into everything that is published: the charts, one row per run as `runs.csv` and `runs.json`, the results page, and the block between two markers in the README. Running it again on the same runs writes the same files. Nobody edits its output.

Published results live under `docs/results/<name>/` and are the second exception to the rule that runtime output stays out of the repository. Raw transcripts are not published: they hold the game's own text, which has no licence to republish.

Every publication says what kind it is. A `pilot` states that it supports no claim. A `result` comes from the fixed protocol. Runs on a scripted stand-in are labelled as not a result on every chart and in the words.

The plate shown on the README is a printout in the house style: one ink, grey for what is secondary, dot textures for tone, filled and hollow squares for marks, and two soft pens only: the yellow of the other figures for the harness under test, and a pale cyan for a broken rule. Time and text are each drawn as a flame graph, the root on top and one soft hue for each kind of frame, on one scale so that a narrower graph spent less. It states what was held equal: the model, the seeds, the budget and the commit that was run.

## Consequences

- A new run updates the README, the results page and the data with no hand work.
- The numbers in the words and the marks in the charts come from the same rows, so they cannot disagree.
- The repository grows by a few small generated files for each published run. Older runs are replaced, not accumulated, unless a comparison needs them.
- `tests/test_bench_charts.py` holds the publisher to being repeatable and to labelling stand-in runs.
