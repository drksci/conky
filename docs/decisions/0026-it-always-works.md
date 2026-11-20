---
kind: decision
title: It always works
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.fallback.always
---

# 0026 It always works

## Context

- A vault now depends on things that can be absent: a model, a key, a program on the path, a connector, a network.
- Each of those was first written to refuse when missing. A refusal is recorded and safe, but a newcomer with nothing configured sees a system that stops.
- The easy-path rule asks for one command and nothing to configure. It did not say what happens when a piece is missing later.

## Decision

Everything works out of the box, in every case. Every optional part has a default. Anything that can be missing or fail has a fallback that still does something useful, tried in a stated order that ends in one needing nothing at all.

A missing or failing piece lowers the result and says so in the record. It never blocks a write, breaks a vault or stops a run. When the better piece appears later, the vault uses it without being told.

This is a design rule for every part, written into the contributor rules, not a feature of one part.

## Consequences

- A page that asks a model gets a plain sentence when no model can answer, and asks again for real when one can ([decision 0024](0024-a-model-is-reached-by-a-key-or-a-local-program.md)).
- A go-between falls back from a capable model to a small one to a reflex ([the outside arrives as pages](../ideas/tools.md)).
- The screen degrades from composed, to plain, to text.
- Rules are the exception and stay strict: a rule that cannot be evaluated refuses the write. Falling back there would turn a rule into a request.
- Every fallback is recorded, so a lowered result is visible and never mistaken for the real thing.
- Each part lands with a test of its fallback. An error that remains says what to do next.
