---
kind: essay
title: Rules, not requests
status: current
date: 2026-11-20
source: maintainers
---

# Rules, not requests

## What prompted it

A sign on a door says "Please do not enter". A lock says nothing. Systems built around AI models mostly use signs: a prompt, a policy, a set of instructions. A constraint in a prompt is a request. A constraint in the machinery that performs the action is a rule.

## The problem

The prompt says "never spend more than the budget" or "keep pages short". The model usually complies, and when it does not, nothing stops it. A request is a hope, and a scripted demo of a safeguard proves little, because it shows only the cases its author chose.

## Analogues

A compiler refuses the program that breaks the rules; nobody relies on programmers remembering. A database enforces uniqueness at write time, so bad data stays out however careless the caller. A spreadsheet that rejects text in a number column does not argue with the user. The check sits in the machinery, not in the instructions given to the actor.

## The idea

In conky a rule is a pure boolean expression, written in CEL, attached to a page. A space is a page whose rules its members inherit down a `within` chain. On every write the runtime evaluates the rules of the page and of every space above it, against the resulting page and its byte size. If any is false, the write is refused, nothing changes, and the refusal is recorded in the history. The actor needs no instructions about the rule and cannot talk its way past it.

This is built. A space might say `page.stock >= 0` and `size <= 2000`; a member write that breaks either is refused with the reason. A page can now ask a model, and the answer is checked by the same rules as any write. No run against a live model has been made, so this is tested only against stand-in servers.

So invariants hold whoever the actor is, including one that misunderstands its instructions, and prompts get shorter because they no longer carry the constraints. A limit set once on a space applies to every member.

The same standard applies to claims about the system. A rule is real only if a test fails when the rule is removed. A benchmark number is real only if it came from an unscripted run with the run count and traces kept ([decision 0013](../decisions/0013-evidence-not-scripts.md)).

## Hypothesis

Moving invariants out of prompts and into runtime rules makes a population of actors safer and cheaper to direct, without making them unable to do useful work.

## How it could be shown wrong

- Rules prove too blunt: actors spend most of their effort being refused, or work around rules in ways the rules cannot see.
- Real invariants turn out not to be expressible as pure boolean expressions over a page and its size. Anything that needs more is out of reach for now.
- Rule evaluation becomes the bottleneck or the main source of defects.
- One oddity was found and closed: a rule on a space applied to the space page itself, which an `each` rule now avoids ([decision 0034](../decisions/0034-a-rule-for-the-pages-within.md)). If such cases multiply, the primitive is wrong.
- A hard refusal may be the wrong shape for some limits at all; see the pressure idea in [measures](../ideas/measures.md).
