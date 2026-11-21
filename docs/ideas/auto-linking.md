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

Terms found by use are the work of a reflex [faculty](faculties.md), and the linking is automatic and continuous: nobody asks for it and nobody accepts it. In the background the faculty notices a phrase used across a space and writes a page for the term, signed as its own work like any other write. From then on every use of the term counts as a link to that page, in what a character is shown, in what a person sees through a mount, and in the graph of who refers to what. The text an author wrote is not touched: the link is woven when the page is read, not typed into its body, so an author never writes brackets and never finds their words changed.

Built, as the first half only ([decision 0044](../decisions/0044-a-page-is-known-by-its-phrases.md), rung enforced for recognition): a page lists the phrases it is known by in `known_as`, text that uses one counts as linking to the page at the write with no brackets and no change to the body, and `terms(TEXT)` names the pages a text uses. Not built, and still an idea: the background faculty that finds a recurring phrase and writes its term page.

The linking happens at two moments, by one recognition. When a page is written, the terms that already have pages are recognised in it as part of the write, the way its rules and its shape are checked there, so the page counts as linking to them from its first commit and whatever watches a term by `on: link` is told in the same chain of events. In the background, a phrase that recurs across a space is given its term page, and the pages written before that term existed are caught up by the same recognition. A page never waits in history unlinked because a background pass has not reached it. This holds for every page whoever wrote it: a character's page, the notes a memory keeps, what a faculty writes and what a connector brings in are all recognised at their own write.

A phrase used across a space gains a term page without any character being asked, every later use of it resolves to that page, and the pages that use it are byte-identical before and after. If a character has to mark or accept the link for it to hold, or any page body changes without its author's write, the idea is wrong as built. A page written after a term exists is told to that term's watchers at the write itself, with no later pass; if it is not, the write-time half is missing.
