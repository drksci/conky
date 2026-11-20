---
kind: idea
title: Context that flows down
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.space.context
---

# Context that flows down

## Idea

A page sees the shared facts of the spaces above it (a season, a budget, a house style) in its rules, reactions and embeds, so they are neither repeated nor hidden. Context is one of the three things a space hands down, with rules and reactions; see [what a space hands down](inheritance.md). Only rules are inherited today.

## Composes from

Space, embed, rule.

## Removes

Copies of shared facts on every page.

## Falsifying test

Changing one field on a space changes what every member's rules and embeds see, with no member edited.
