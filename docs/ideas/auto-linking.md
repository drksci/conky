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

A phrase used across a space gains a term page without any character being asked, every later use of it resolves to that page, and the pages that use it are byte-identical before and after. If a character has to mark or accept the link for it to hold, or any page body changes without its author's write, the idea is wrong as built.
