---
kind: idea
title: A seed, an identity and a face
status: idea
date: 2026-11-20
source: maintainers
---

# A seed, an identity and a face

## Idea

Every identifiable thing (an actor, a tool, a space, any page that wants one) carries a `seed`: a short, memorable, slightly absurd phrase generated when the page is created, such as "reluctant sheriff of small numbers". The seed never changes. The name can.

Two things come from the seed alone: a stable identifier, so a rename breaks nothing and the same thing is recognisable across vaults, and a face, a small monochrome dithered portrait drawn by code, which always works and needs no model.

A profile is ordinary fields on the page: the seed, the current name, a line in its own words, and optionally a portrait it chose. If a portrait provider is available (a provider page, as for models), an actor may ask for a made portrait in the same style, or write its own profile through a model page. Otherwise the drawn face is used.

The seed is public and never a source of keys, which stay separate and secret. The flavour of the phrases and the style of the faces come from the vault's taste page ([house-style](house-style.md)). Nothing of this is built.

## Composes from

Page, rule (a seed may not be changed once set), derived data ([decision 0017](../decisions/0017-derived-data.md): the face and the identifier can always be recomputed), and [pages that ask a model](model-pages.md).

## Removes

Identifiers people cannot remember, broken references after renames, and blank avatars.

## Falsifying test

The same seed gives the same identifier and face on any machine. Renaming a page changes neither. With no provider configured every actor still has a face. A write that changes a seed is refused.

## Open questions

- The word lists and their tone.
- Whether links should resolve by identifier underneath.
- How much of the face is drawn from the seed and how much is chosen.
