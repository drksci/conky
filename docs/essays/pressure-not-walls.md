---
kind: essay
title: Pressure, not walls
status: current
date: 2026-11-20
source: architect
---

# Pressure, not walls

## What prompted it

The project began with a fixed 4096-byte page limit inherited from an earlier design. The operator called the number arbitrary, and [decision 0006](../decisions/0006-size-is-a-rule.md) turned size into an ordinary rule a space can set. Then the operator went further and proposed that size should build pressure rather than stop work.

## The problem

A wall is a refusal. When a write would take a page over its limit, the write is turned away and the actor is interrupted. The actor must now spend thought on housekeeping: trim, split, retry. For a model, thought means inference, and it is spent at the worst moment, in the middle of something else, on a chore that has nothing to do with the task. The limit also tends to be wrong in both directions: too tight for the page that needs room, too loose to help the page that is merely untidy.

## Analogues

These come from general experience, not from any study.

- A desk that gets cluttered. Nobody refuses you another sheet of paper; the clutter itself becomes a nudge to tidy up, and you tidy when it suits.
- A fuel gauge versus an engine cut-out. The gauge tells you the level is falling and lets you decide when to stop. The cut-out stops the engine on the road.
- Back-pressure in plumbing or in data streams. A rising signal tells the producer to ease off, and nothing is thrown away at the point of overload.
- Hunger. It is a signal that grows and prompts action; it does not lock the body.

## The idea

A measure is a page watching itself. A `watch` entry whose `on` is the page's own name sets a field computed from the page's state, using `size`, the byte length of the page. Pressure is such a measure: a number that rises as the page grows. Thresholds are further entries that fire when the number passes a value, setting a state that other pages can watch and react to. Walls remain for what must never happen, such as a negative balance. See [decision 0019](../decisions/0019-measures-are-self-watches.md).

What is built is the measure and the threshold reaction. A page with no size rule accepts a large write, its pressure field rises as a recorded event, a threshold sets a state, and a watching page reacts, with no model call and no refusal. What is not built is anything that actually relieves the pressure, such as splitting or summarising a page. Today pressure is noticed and nothing yet acts on it.

## What it solves

- The writer is not interrupted by a limit, so no inference is spent on housekeeping at the moment of writing.
- Growth becomes visible in the log as recorded events, each with its cause named.
- Replay stays simple: the computed value is an ordinary event, so rebuilding a vault never evaluates an expression.
- No new word or mechanism is added to the model.

## Hypothesis

With pressure in place, pages in a long run stay bounded without any refused write, and without spending inference on housekeeping.

## How we would know we are wrong

- In a long run that is not scripted, pages still grow without bound because nothing acts on the pressure, so the signal is noticed and ignored.
- Housekeeping triggered by pressure turns out to need a model call each time, so inference is spent anyway.
- Measures that change on every write make the log so noisy that it is harder to read than a plain limit would have been.
- A measure turns out to need a clock, randomness or input outside pages and the log to compute what it was meant to.
- We have no such run yet, and until we do this is a hypothesis, not a finding.
