---
kind: idea
title: Taste is a page
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: taste
    by: a person, or inferred by a model page
    layer: spaces
    text: How a vault looks and sounds, kept at the top space.
    roadmap: R23
---

# Taste is a page

## Idea

How a vault looks and sounds is kept as ordinary fields on a taste page at the top space, and every page below inherits it like any other shared context. That covers the flavour of the seed phrases (dry Western, or something else), the style of the drawn faces and icons, and the voice generated sentences are written in. Nothing is configured anywhere else.

The page gets written in one of three ways, in order of effort:

- Left alone, so sensible defaults apply.
- Inferred when a vault is started from a prompt: a model page reads the prompt and proposes the taste as an ordinary change that can be seen and edited.
- Asked for by the owner with an optional `conky howdy`, which poses a handful of either-or questions, such as which of two sample seed phrases or faces is preferred, and writes the answers to the page.

Changing taste later is an edit to that page. Things already made keep their seed and identifier. Only how they are drawn and described changes.

## Composes from

Page, space (context handed down, see [what a space hands down](inheritance.md)), [pages that ask a model](model-pages.md), and [seeds and faces](seeds-and-faces.md).

## Removes

A settings file, a theme system, and questions asked before a person has seen anything work.

## Falsifying test

With no taste page, a new vault still produces seeds and faces. Changing one field on the taste page changes how every page below is drawn, with no other page edited and no identifier changed. A vault started from a prompt carries a proposed taste page whose every field can be traced to the change that wrote it.

## Open questions

- Which few choices are worth asking about.
- How the tone of a prompt is read without overreaching.
- Whether a space lower down may override the taste it inherits.
