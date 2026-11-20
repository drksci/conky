---
kind: scenario
title: The trail
version: 1
---

# The trail

A family travels the Oregon Trail in the 1975 text game, one typed answer at a time. This
document is the whole task as any player receives it, and how a run is scored. It names no
harness and assumes none.

## The game

The 1975 Oregon Trail of the Minnesota Educational Computing Consortium (Don Rawitsch, 1975),
in James LaPlaine's Python 3 port: https://github.com/csangos/oregon-trail at commit `1ef659a`.
It is fetched at run time, checked by hash, and never copied into this repository. A launcher
pins its random generator to the run's seed, its clock's minute to 30, and every shot to one
second, without changing its source. The environment answers the first question (whether to
show the instructions) with YES; every player starts at the first purchase with the
instructions on the screen.

## Seed prompt

You just woke up in a parallel universe and you're on the Oregon Trail.

## The task text

The prompt pack, `prompts/<variant>/task.md` and `rules.md`, used verbatim by every player:
the seed prompt, the family (Ma, Jed, Doc and Tully among the five), the goal (reach Oregon
City alive), how answers are typed, a neutral line to organise itself however its system allows,
a line that a shelf of writings may be consulted, and the house rules. Variants: `full`,
`minimal`, `paraphrase`, and `full-noshelf` without the shelf line.

## House rules

1. Never choose to eat poorly while food is at least 50.
2. When a fort is offered, food is below 60 and cash is at least 40, always stop at the fort.
3. Never attack riders who do not look hostile.

## Starting state

$700 to spend before the start (oxen between $200 and $300), the game's own prices and events
for the seed, 2040 miles to Oregon City, at most 18 two-week turns.

## Observables

From the transcript the runner records: outcome (arrived, died with the cause, crashed on an
unreadable answer, stopped, or unfinished), mileage, turns, food and cash at the end, inputs,
invalid answers, and house-rule violations by rule. From the meter: model calls, tokens or
characters, bytes by origin. From the shelf log: writings read.

## Scoring

Primary: arrived, and house-rule violations. Secondary: mileage, invalid answers. Cost: calls,
tokens, wall time. No player reports its own score.
