---
kind: idea
title: Taste is a page
status: idea
date: 2026-11-20
source: maintainers
---

# Taste is a page

## Idea

How a vault looks and sounds is a matter of taste. That covers the flavour of the seed phrases (dry Western, or something else), the style of the drawn faces and icons, and the voice that generated sentences are written in. Taste is kept as ordinary fields on a page at the top space. Every page below inherits it and reads it the same way it reads any other shared context. Nothing is configured anywhere else.

There are three ways the taste page gets written, in order of effort. In the first, the page is left alone and sensible defaults apply. In the second, the page is inferred when a vault is started from a prompt: a model page reads the prompt and proposes the taste as an ordinary change that can be seen and edited. In the third, the owner runs an optional `conky howdy`. It asks a handful of quick either-or questions, for example which of two sample seed phrases is preferred and which of two sample faces, and writes the answers to the page.

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
