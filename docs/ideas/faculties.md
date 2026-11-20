---
kind: idea
title: Faculties
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: faculties
    text: A page that watches another and writes the rule, entry or link a sentence asks for, tried aside before it binds. A reflex kind costs nothing and a thinking kind costs a small call.
---

# Faculties

## Idea

The form is somebody else's job. A character says what it wants in a sentence, and a faculty that watches its page writes the form: a rule, an entry, a link. Thought goes into what the character wants and not into the syntax that holds it.

- What the faculty did is shown to the character on its next turn, in words, with a link to the page it wrote.
- What a faculty writes is tried aside before it binds, so a wrong translation is caught while nothing depends on it ([dry run](dry-run.md)).
- A character can always write the form itself. The faculty is an easy path and never the only one.

## Two kinds on one pattern

A reflex faculty costs nothing: it is a watch with a reaction and no model call, such as noticing a phrase used across a space and proposing a link ([auto-linking](auto-linking.md)). A thinking faculty costs a small call: it is a [model page](model-pages.md) that turns a sentence into a rule or an entry. Both are pages that watch and write, so the difference is the price, not the shape.

## Composes from

Watch, ask, an answer that is pages, and the retry on a refused answer. It adds no new word.

## Removes

A syntax the thinking character must hold in its own context, and any separate translation layer.

## Depends on

[Model pages](model-pages.md), [dry run](dry-run.md), and the [codec](codec.md) idea for the translation itself.

## Falsifying tests

- On the same card, a character with a faculty reaches par in more trials than one without, with less text in the thinking character's own context.
- A wrong translation is caught before it binds: a rule the faculty writes that fails its trial aside is never kept, and the character is told why.

## Open questions

- Whether trying aside is a dry-run write or a rule the faculty must pass.
- How a faculty is itself changed: as a page, by the same writes as any other.
