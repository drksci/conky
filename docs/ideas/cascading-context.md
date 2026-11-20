---
kind: idea
title: Context that flows down
status: idea
date: 2026-11-20
source: maintainers
---

# Context that flows down

## Idea

A page inherits the rules of the spaces above it. It should also be able to see their shared facts (a season, a budget, a house style) in its rules, reactions and embeds, so context is visible to every member instead of being repeated or hidden. Today only rules are inherited. Nothing more is built.

## Composes from

Space, embed, rule.

## Removes

Copies of shared facts on every page.

## Falsifying test

Changing one field on a space changes what every member's rules and embeds see, with no member edited.
