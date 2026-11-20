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

A page sees the shared facts of the spaces above it (a season, a budget, a house style) in its rules, reactions and embeds, so they are neither repeated nor hidden. Context is one of the three things a space hands down, with rules and reactions; see [what a space hands down](inheritance.md). Rules are inherited, and the fields of the spaces are readable as `space` in rules, watch conditions and `set` values; embeds of context and reactions are not built. Rung: idea.

## What a character is shown of a space

The list of what is within a space is ordered by a field that a measure keeps, the page's [standing](standing.md), and not only by name. Showing the urgent page first needs no declaration from its author. The order is the one runtime change standing asks for.

## Composes from

Space, embed, rule.

## Removes

Copies of shared facts on every page.

## Falsifying test

Changing one field on a space changes what every member's rules and embeds see, with no member edited. In a space whose members are listed by standing, the page with the highest value is listed first, and a page whose standing falls is listed later with no member edited.
