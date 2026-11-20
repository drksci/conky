---
kind: idea
title: Auto-linking
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: part
    name: part.link
    layer: layer.history
    text: A page name written in a page so that one page points at another. No runtime code reads one, so it stays a convention.
    state: idea
    roadmap: R15
---

# Auto-linking

## Idea

The runtime links new domain terms, so nobody has to link them by hand.

That needs a deterministic rule for what counts as a term. A [model page](model-pages.md) may propose links, never make them.

## Composes from

Links and reactions.

## Removes

Hand-maintained links.

## Falsifying test

Not yet worked out.
