---
kind: essay
title: Things that just happen
status: current
date: 2026-11-20
source: maintainers
---

# Things that just happen

## What prompted it

A lemonade stand runs low on cups. In a well-run stand someone notices and the supplier is asked for more. Nobody holds a meeting, and the person at the stand stays free to think about the customers, the weather and what to put on the sign.

Build the same stand from AI agents and one agent notices the cups, asks another to reason about reordering, and a message gets written. Every step costs a model call, and the thinking spent on cups is not spent on anything else ([decision 0007](../decisions/0007-inference-for-real-thinking.md), [decision 0020](../decisions/0020-everything-is-somebody.md)).

## The problem

A decision that follows directly from state, such as "fewer than ten cups, so order more", does not need an opinion. Spending thought on it adds cost and variance, and buries the reason for the action in generated text. The harm is not that a model was called. It is that the call went to bookkeeping, where the answer was never in doubt, when it could have gone to a character with something to say.

## Analogues

A spreadsheet recalculates dependent cells when an input changes. A database trigger fires when a row changes. A hand leaves a hot pan before the person has decided anything, which is what lets the person go on thinking about dinner.

## The idea

Everything in a vault is somebody: a page is a character with an identity, a temperament and a voice. The signed history, the rules and the reactions are its body, the things a living creature never has to think about. A character may be as odd as it likes and still cannot break a house rule.

A page can watch another page. When the watched page changes and a `when` expression is true, the runtime writes the watching page, signed by that page's own key, and records the triggering event as the cause. Reactions cascade to a depth of 12 and are then refused as a cycle; a reaction that would change nothing is skipped, so stable states end. No model is called, because nothing needs deciding.

This is built and shown in the [getting started](../guide/getting-started.md) walkthrough: writing a cooler with fewer than 10 cups makes the supplier change by itself. A watch entry can also ask a model through a provider page ([providers](../reference/providers.md)), and the answer is recorded as an ordinary write. That has been tested against stand-in servers, not a live provider. What is not built is the part this essay argues for: a page with a temperament that writes its order in its own voice ([a page with a self](../ideas/character.md)). Today the example vault holds human-written content.

So routine consequences carry no thought, and model capacity goes to character, judgement, conversation and curiosity. The same state gives the same reflex, so the body can be replayed and checked, and each reaction is an event in the history with its cause named. Budgets bound what thought costs, which is a constraint to manage, not a goal.

## Hypothesis

Most of the bookkeeping of a running organisation can be expressed as reflexes to state. A vault whose reflexes are free can spend its model calls on characters that notice, take an interest and write in their own words. Two runs of the same vault will then differ, the way two days do, above a floor that never moves.

## How it could be shown wrong

- When a real organisation is modelled, the share of activity that truly needs judgment is large, and reactions cover only a small corner.
- Reaction rules grow so numerous and tangled that they are harder to maintain than the reasoning they replaced.
- Cascades or cycles become common in practice, rather than the rare edge the depth limit is meant for.
- Characters with temperaments make a vault harder to follow, so variety costs more than it gives.
- A run that is not scripted shows model-driven pages doing routine work faster or more reliably than reactions. No such run has been made yet, so this is a hypothesis, not a finding.
