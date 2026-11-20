---
kind: idea
title: Vault splitting
status: idea
date: 2026-11-20
source: maintainers
---

# Vault splitting

## Idea

When a vault grows too large or too busy, a space becomes its own vault (its own Git repository) that the parent links to, so history and write load divide along lines the organisation already has. Rules and reactions across two vaults are not worked out.

## Composes from

Space, link, and Git's own ways of referring to another repository.

## Removes

Any need for a different store at scale.

## Falsifying test

A space is moved out to its own vault and back without losing history or breaking a link or a rule that crosses the boundary.
