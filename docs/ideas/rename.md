---
kind: idea
title: Renaming without breaking anything
status: idea
date: 2026-11-20
source: maintainers
---

# Renaming without breaking anything

## Idea

Renaming or moving a page is one change that also rewrites every link and embed that points to it, so nothing breaks and nobody has to tidy up. Old names live only in history. Nothing of this is built.

## Composes from

Write, link, embed.

## Removes

Broken links and manual fixes.

## Falsifying test

After a rename, no link or embed in the vault points at the old name, verify passes, and reactions that named the page still fire.
