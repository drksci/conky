---
kind: idea
title: A seed, an identity and a face
status: idea
date: 2026-11-20
source: maintainers
---

# A seed, an identity and a face

## Idea

Every identifiable thing (an actor, a tool, a space, any page that wants one) carries a `seed`: a short, memorable, slightly absurd phrase, generated when the page is created. An example is "reluctant sheriff of small numbers". The seed never changes. The name can.

From the seed alone come two things. One is a stable identifier, so a rename breaks nothing and the same thing is recognisable across vaults. The other is a face: a small monochrome dithered portrait drawn by code from the seed, which always works and needs no model.

A profile is ordinary fields on the page: the seed, the current name, a line in its own words, and optionally a portrait it chose. If a portrait provider is available (a provider page, as for models), an actor may ask for a made portrait in the same monochrome style, or write its own profile through a model page. When none is available, the seed's drawn face is used.

The seed is public and is never a source of keys. Signing keys stay separate and secret. Nothing of this is built.

## Composes from

Page, rule (a seed may not be changed once set), derived data ([decision 0017](../decisions/0017-derived-data.md): the face and the identifier can always be recomputed), and [pages that ask a model](model-pages.md).

## Removes

Identifiers people cannot remember, broken references after renames, and blank avatars.

## Falsifying test

The same seed gives the same identifier and the same face on any machine. Renaming a page changes neither. With no provider configured every actor still has a face. A write that changes a seed is refused.

## Open questions

- The word lists and their tone.
- Whether links should resolve by identifier underneath.
- How much of the face is drawn from the seed and how much is chosen.
