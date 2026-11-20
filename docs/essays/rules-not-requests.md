---
kind: essay
title: Rules, not requests
status: current
date: 2026-11-20
source: maintainers
---

# Rules, not requests

## What prompted it

Systems built around AI models usually state their constraints in prose: a prompt, a policy, a set of instructions. Whether such a constraint holds depends on where it lives. A constraint written in a prompt is a request. A constraint in the machinery that performs the action is a rule. This essay is about the difference, and about what it takes for a claim that a rule holds to be trusted.

## The problem

The common way to constrain an AI system is to ask it. A prompt says "never spend more than the budget" or "keep pages short". The model usually complies, and when it does not, nothing stops it. A request is a hope. A scripted demonstration of a safeguard can also look just like a real one, because the script only shows the cases its author chose.

## Analogues

Compilers and type systems refuse programs that break the rules; nobody relies on programmers remembering. Databases enforce constraints such as uniqueness or foreign keys at write time, so bad data cannot get in however careless the caller. A spreadsheet that rejects text in a number column does not argue with the user. Operating systems do not ask a process politely to stay inside its memory. In each case the check sits in the machinery that performs the action, not in the instructions given to the actor.

## The idea

In conky a rule is a pure boolean expression, written in CEL, attached to a page. A space is a page whose rules its members inherit down a `within` chain. On every write the runtime evaluates the rules of the page and of every space above it, against the resulting page and its byte size. If any is false the write is refused, nothing changes, and the refusal is recorded in the history. The actor needs no instructions about the rule, and cannot talk its way past it.

This is built. A space might say `page.stock >= 0` and `size <= 2000`; a member write that breaks either is refused with the reason. A page can now ask a model, and its answer is checked by the same rules as any write. No run against a live model has been made, so this is tested only against stand-in servers.

The same thinking applies to claims about the system. A rule is real only if a test fails when the rule is removed. A benchmark number is real only if it came from an unscripted run with the run count and traces kept ([decision 0013](../decisions/0013-evidence-not-scripts.md)).

## What it solves

- Invariants hold whoever the actor is, including an actor that misunderstands or ignores its instructions.
- Prompts can be shorter, since they no longer carry the constraints.
- A limit set once on a space applies to every member without repeating it.
- Violations are visible: refused writes are in the history.

## Hypothesis

Moving invariants out of prompts and into runtime rules makes a population of actors safer and cheaper to direct, without making them unable to do useful work.

## How we would know we are wrong

- Rules prove too blunt: actors spend most of their effort being refused, or work around rules in ways the rules cannot see.
- Real invariants turn out not to be expressible as pure boolean expressions over a page and its size. Rules see only the resulting page and its size, so anything that needs more is out of reach for now.
- Rule evaluation becomes the bottleneck or the main source of defects.
- One oddity is already known: rules on a space also apply to the space page itself ([open questions](../project/open-questions.md)). If such cases multiply, the primitive is wrong.
- A hard refusal may be the wrong shape for some limits at all; see the pressure idea in [measures](../ideas/measures.md).
