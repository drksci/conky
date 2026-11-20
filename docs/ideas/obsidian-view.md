---
kind: idea
title: Obsidian view
status: idea
date: 2026-11-20
source: operator
---

# Obsidian view

## Idea

A vault is already a folder of Markdown pages with `[[links]]`, so it opens in a notes application such as Obsidian as it is. The idea is a command that generates a view for people: an index of the pages by space, recent events and refusals, and a workspace folder that lists and links several vaults so they can be browsed together. The generated view is output only, kept out of the vault's history, and can be deleted and regenerated.

## Composes from

Page, link, and the vault's Git history.

## Removes

The need for a separate dashboard.

## Falsifying test

A newcomer given only the generated workspace can find any page, see what last changed it and why, without using the command line.
