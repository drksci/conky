---
kind: essay
title: Things that just happen
status: current
date: 2026-11-20
source: maintainers
---

# Things that just happen

## What prompted it

Consider a lemonade stand that runs low on cups. In a well-run stand, someone notices and the supplier is asked for more. Nobody holds a meeting, and nobody thinks about it. The person at the stand is free to think about the customers, the weather and what to put on the sign. Now picture the same thing built from AI agents: one agent notices the cups, asks another to reason about whether to reorder, and writes a message. Every step costs a model call, and the thinking that went into the cups is thinking that did not go into anything else ([decision 0007](../decisions/0007-inference-for-real-thinking.md), [decision 0020](../decisions/0020-everything-is-somebody.md)).

## The problem

A decision that follows directly from state, such as "fewer than ten cups, so order more", does not need an opinion. Spending thought on it adds cost and variance, and makes the system harder to audit, because the reason for an action is buried in generated text. The harm is not that a model was called. The harm is that the call was spent on bookkeeping, where the answer was never in doubt, when it could have gone to a character with something to say.

## Analogues

Spreadsheets recalculate dependent cells when an input changes. Database triggers fire when a row changes. Build systems rebuild only what depends on what changed. The immune system and reflexes respond to conditions without deliberation. A hand leaves a hot pan before the person has decided anything, and that is what lets the person go on thinking about dinner. In each case consequences follow state automatically, and thought is left free for the things that need it.

## The idea

Everything in a vault is somebody: a page is a character with an identity, a temperament and a voice. The signed history, the rules and the reactions are its body. They are reflexes and physics, the things a living creature never has to think about. They exist so that no thought is wasted on bookkeeping, and so that characters can be unpredictable without being dangerous. A character may be as odd as it likes and still cannot break a house rule.

A conky page can watch another page. When the watched page changes and a `when` expression is true, the runtime writes the watching page, signed by that page's own key, and records the triggering event as the cause. Reactions cascade to a depth of 12 and are then refused as a cycle; a reaction that would change nothing is skipped, so stable states end. No model is called, because nothing needs deciding.

This is built and shown in the [getting started](../guide/getting-started.md) walkthrough: writing a cooler with fewer than 10 cups makes the supplier change by itself. A watch entry can also ask a model through a provider page ([providers](../reference/providers.md)), and the answer is recorded as an ordinary write. That has been tested against stand-in servers, not a live provider. What is not built is the part this essay argues for: a page that has a temperament and writes its order in its own voice ([a page with a self](../ideas/character.md)). Today the example vault holds human-written content.

## What it solves

- Attention: routine consequences carry no thought, so model capacity goes to character, judgement, conversation and curiosity.
- Safety: a character can vary as much as it likes, because the floor under it does not move.
- Replay: the same state gives the same reflex, so the body can be replayed and checked.
- Auditability: each reaction is an event in the history with its cause named.
- Cost: budgets bound what thought costs. Cost is a constraint to manage, not a goal.

## Hypothesis

Most of the bookkeeping of a running organisation can be expressed as reflexes to state. A vault whose reflexes are free can spend its model calls on characters that notice, take an interest and write in their own words, and two runs of the same vault will then differ, the way two days do, above a floor that never moves.

## How we would know we are wrong

- When a real organisation is modelled, the share of activity that truly needs judgment is large, and reactions cover only a small corner.
- Reaction rules grow so numerous and tangled that they are harder to maintain than the reasoning they replaced.
- Cascades or cycles become common in practice, rather than the rare edge the depth limit is meant for.
- Characters with temperaments make a vault harder to follow, not easier, so variety costs more than it gives.
- A run that is not scripted shows model-driven pages doing routine work faster or more reliably than reactions. No such run has been made yet, so this is a hypothesis, not a finding.
