---
kind: essay
title: Rules, not requests
status: current
date: 2026-11-20
source: architect
---

# Rules, not requests

## What prompted it

The earlier prototype of this project passed its own tests and reported benchmark numbers. When we looked closely, neither meant what it appeared to mean. The guard checks it called proofs were string matches. A scripted demo printed hard-coded numbers instead of measuring a run. Nothing ran in a sandbox, and the keys were ephemeral. The code was deleted ([decision 0001](../decisions/0001-clean-slate.md)) and the episode became a rule about honesty ([decision 0010](../decisions/0010-evidence-not-scripts.md)). This essay is about the larger lesson: where a constraint lives decides whether it holds.

## The problem

The common way to constrain an AI system is to ask it. A prompt says "never spend more than the budget" or "keep pages short". The model usually complies, and when it does not, nothing stops it. A request is a hope. Worse, a scripted demonstration of a guard can look just like a real one, because the script only shows the cases the author chose.

## Analogues

Compilers and type systems refuse programs that break the rules; nobody relies on programmers remembering. Databases enforce constraints such as uniqueness or foreign keys at write time, so bad data cannot get in however careless the caller. A spreadsheet that rejects text in a number column does not argue with the user. Operating systems do not ask a process politely to stay inside its memory. In each case the check sits in the machinery that performs the action, not in the instructions given to the actor.

## The idea

In conky a rule is a pure boolean expression, written in CEL, attached to a page. A space is a page whose rules its members inherit down a `within` chain. On every write the runtime evaluates the rules of the page and of every space above it, against the resulting page and its byte size. If any is false the write is refused, nothing changes, and the refusal is recorded in the log. The actor needs no instructions about the rule, and cannot talk its way past it.

This is built. A space might say `page.stock >= 0` and `size <= 2000`; a member write that breaks either is refused with the reason. What is not built is any model-backed actor to test this against; today the actors are people and scripts using the command line.

The same thinking applies to our own claims. A guard is real only if a test fails when the guard is removed, and a benchmark number is real only if it came from an unscripted run with the run count and traces kept. Honesty rules are rules of the same kind, applied to ourselves.

## What it solves

- Invariants hold whoever the actor is, including an actor that misunderstands or ignores its instructions.
- Prompts can be shorter, since they no longer carry the constraints.
- A limit set once on a space applies to every member without repeating it.
- Violations are visible: refused writes are in the log.

## Hypothesis

Moving invariants out of prompts and into runtime rules makes a population of actors safer and cheaper to direct, without making them unable to do useful work.

## How we would know we are wrong

- Rules prove too blunt: actors spend most of their effort being refused, or work around rules in ways the rules cannot see.
- Real invariants turn out not to be expressible as pure boolean expressions over a page and its size. Rules see only the resulting page and its size, so anything that needs more is out of reach for now.
- Rule evaluation becomes the bottleneck or the main source of defects.
- There is already one known oddity: rules on a space also apply to the space page itself ([decision 0015](../decisions/0015-open-questions.md)). If such cases multiply, the primitive is wrong.
- A hard refusal may be the wrong shape for some limits at all; see the pressure idea in [measures](../ideas/measures.md).
