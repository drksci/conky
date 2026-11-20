---
kind: idea
title: A page with a self
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: part
    name: self
    layer: characters
    text: A seed, a face, a temperament and a voice for every page.
    roadmap: R23
---

# A page with a self

## Idea

Any page may carry a self: a seed and face (see [seeds and faces](seeds-and-faces.md)), a few words of temperament such as "weary but reliable" or "smug about being right", and a voice. When it writes, the words are its own, so the supplier's order sounds like the supplier.

With a model available, the page's temperament and recent history go to the model as context and the sentence is written fresh. Without one, a plain sentence is used and nothing breaks.

Temperament is context a model reads. It never controls anything and never gets round a rule. A vault's general manner comes from its taste page ([house-style](house-style.md)), and a page's own temperament sits within it. The premise is recorded in [decision 0020](../decisions/0020-everything-is-somebody.md).

Nothing of this is built. Pages in the example vault carry human-written content, a page can ask a model, and no page has a generated temperament or voice.

## Composes from

Page, seed, watch, [pages that ask a model](model-pages.md), and context handed down by spaces ([inheritance](inheritance.md)).

## Removes

Identical flat text from every part of a system, and the feeling that only "agents" are alive.

## Falsifying test

With a model attached, two runs of the same example produce different wording and the same rule outcomes. A reader shown three pages can tell which character wrote which. With no model, every page still writes something sensible. No temperament changes whether a rule holds.

## Open questions

- How a temperament is described.
- How much variety is welcome before a vault becomes hard to follow.
- How character is kept consistent over time.
