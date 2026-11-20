---
kind: idea
title: Which model answers is a page
status: idea
date: 2026-11-20
source: "research/findings-rubric.md (F25, F26, F27, F28 and gap 7) and decision 0024, which fixes the order that picks a provider when a vault names none"
arch:
  items:
  - kind: archetype
    name: kind.router
    by: a person or a character
    layer: layer.character
    text: A page that orders the providers a space may use from cheapest up, with the recorded outcome that sends a question to the next.
    state: idea
    roadmap: R34
---

# Which model answers is a page

## Idea

Today a question goes to the provider its entry names, or to the first one detected in a fixed order ([decision 0024](../decisions/0024-a-model-is-reached-by-a-key-or-a-local-program.md)). A space could hand down an order instead: a page that lists provider pages from cheapest up, each with the outcome that sends a question to the next. The outcome is recorded, never guessed from the task: a refused answer, a failed verdict from a [reviewer](reviewer.md), or a [habit](habit.md) whose forecast missed. In the research read, handing routine decisions to a smaller model without a threshold fitted on the agent's own runs lowered success (F25). One well-timed handoff kept most of the accuracy at much lower cost (F26), and routers that read task descriptions did not cut cost (F27).

## Composes from

Provider pages, the habit's ladder, measures, and context handed down by a space (R22).

## Removes

Model choice held in code or in configuration outside the vault.

## Falsifying test

On a recurring task, cost per finished task falls with the order in place and success does not drop below the largest model alone. With the threshold removed, success drops, as F25 found.

## Open questions

- Whether the order is a field on a space or a page of its own.
