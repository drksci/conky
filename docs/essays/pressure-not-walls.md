---
kind: essay
title: Pressure, not walls
status: current
date: 2026-11-20
source: maintainers
---

# Pressure, not walls

## What prompted it

A page needs a size limit, and a fixed one such as 4096 bytes is easy to state and hard to justify. The number is arbitrary, and wrong for most pages. [Decision 0006](../decisions/0006-size-is-a-rule.md) made size an ordinary rule a space can set. The next question is whether size should be a wall at all, or a pressure that builds.

## The problem

A wall is a refusal. A write that would take a page over its limit is turned away, and the actor must now spend thought on housekeeping: trim, split, retry. For a model that thought is inference, spent in the middle of something else on a chore unrelated to the task. The limit is also wrong in both directions: too tight for the page that needs room, too loose to help the page that is merely untidy.

## Analogues

These come from general experience, not from any study. Nobody refuses you another sheet of paper on a cluttered desk; the clutter becomes a nudge, and you tidy when it suits. A fuel gauge lets you pick the moment to stop, where an engine cut-out stops you on the road. Back-pressure in plumbing or in data streams tells the producer to ease off, and nothing is thrown away. Hunger grows and prompts action; it does not lock the body.

## The idea

A measure is a page watching itself. A `watch` entry whose `on` is the page's own name sets a field computed from the page's state, using `size`, the byte length of the page. Pressure is such a measure: a number that rises as the page grows. Thresholds are further entries that fire when the number passes a value, setting a state that other pages can watch and react to. Walls remain for what must never happen, such as a negative balance. See [decision 0008](../decisions/0008-measures-are-self-watches.md).

The measure and the threshold reaction are built. A page with no size rule accepts a large write, its pressure field rises as a recorded event, a threshold sets a state, and a watching page reacts, with no model call and no refusal. Anything that relieves the pressure, such as splitting or summarising a page, is not built. Today pressure is noticed and nothing yet acts on it.

So the writer is not interrupted, and no inference is spent on housekeeping at the moment of writing. Growth is visible in the history as recorded events, each with its cause named. The computed value is an ordinary event, so rebuilding a vault never evaluates an expression, and no new word or mechanism enters the model.

## Hypothesis

With pressure in place, pages in a long run stay bounded without any refused write and without spending inference on housekeeping.

## How it could be shown wrong

- In a long run that is not scripted, pages still grow without bound because nothing acts on the pressure, so the signal is noticed and ignored.
- Housekeeping triggered by pressure needs a model call each time, so inference is spent anyway.
- Measures that change on every write make the log so noisy that it is harder to read than a plain limit would have been.
- A measure needs a clock, randomness or input outside pages and the history to compute what it was meant to.
- No such run has been made yet, so this is a hypothesis, not a finding.
