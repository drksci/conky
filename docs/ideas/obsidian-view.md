---
kind: idea
title: Obsidian view
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a generated index for a notes application
    text: Derived data under R11. Nothing is designed beyond the idea.
---

# Obsidian view

## Idea

A vault is already a folder of Markdown pages with `[[links]]`, so it opens in Obsidian as it is. A command could add a view for people: an index of the pages by space, recent events and refusals, and a workspace folder that links several vaults for browsing together. The view is output only, kept out of the vault's history, and can be deleted and regenerated. In the sense of [decision 0017](../decisions/0017-derived-data.md), it is derived data.

## Composes from

Page, link, and the vault's Git history.

## Removes

The need for a separate dashboard.

## Falsifying test

A newcomer given only the generated workspace can find any page and see what last changed it and why, without the command line.
