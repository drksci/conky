---
kind: idea
title: Pages that ask a model
status: idea
date: 2026-11-20
source: maintainers
---

# Pages that ask a model

## Idea

Some questions cannot be answered from state. A page can pose such a question to an AI model and write the answer back as an ordinary signed change, so the answer is recorded, attributable and subject to the same rules as any other write.

A provider is itself a page: it names an endpoint and a model. Secret keys stay outside the vault, like signing keys. Any page that needs a model points at a provider page, so changing provider is editing one page, and different pages can use different providers (a cheap one for housekeeping, a strong one for hard questions).

Calls happen only when state cannot answer ([decision 0007](../decisions/0007-inference-for-real-thinking.md)). Nothing of this is built.

## Composes from

Page, key, write, watch, rule.

## Removes

Provider-specific code paths and prompts scattered in code.

## Falsifying test

The same vault runs unchanged against two different providers by editing one page. Every model answer appears in history with the question that caused it. With the provider unreachable, everything that does not need a model still works.

## Open questions

- How a question and its context are assembled.
- How cost is recorded and bounded.
- How to keep a model's claim from counting as verified fact.
