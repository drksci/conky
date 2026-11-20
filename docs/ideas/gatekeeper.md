---
kind: idea
title: Permission that stays out of the way
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: gatekeeper
    by: a person or a character
    layer: spaces
    text: A page a space names to answer a request for permission.
    roadmap: R14
---

# Permission that stays out of the way

## Idea

A space can name a gatekeeper page, and a change that needs permission is held as a proposal until the gatekeeper answers, so the actor never handles permission itself.

Identity is already the bottom layer: every actor has a key and every change is signed. Permission sits just above it and is inherited like everything else on a space ([what a space hands down](inheritance.md)).

The gatekeeper may be plain rules, a person who is asked, or an agent with a posture set once, permissive or restrictive. It answers allow once, allow always, or use discretion. "Always" writes a standing grant into the space, so it applies to everything below and is not asked again. Repeated identical answers are promoted to standing grants, so the asking fades with use.

Every change records the grant that allowed it, so the chain of authority is in the history. A gatekeeper can widen what is allowed only within the space's hard rules. Nothing of this is built.

## Composes from

Key, seal, space, rule, watch, and [pages that ask a model](model-pages.md).

## Depends on

Rules that can see who signed a change, described in [approvals](approvals.md).

## Removes

Permission prompts in the actor's path, and a separate access-control system.

## Falsifying test

After one "always", the same kind of change passes with no question. A permissive gatekeeper cannot allow a change that a hard rule forbids. For any change, the grant behind it can be found from the history alone.

## Open questions

- How a grant is scoped and expires.
- What counts as "the same kind of change".
