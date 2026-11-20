---
kind: idea
title: Time as an ordinary change
status: idea
date: 2026-11-20
source: maintainers
---

# Time as an ordinary change

## Idea

There is no hidden timer. Time passes when a clock page is written, and anything that depends on time watches that page. This keeps time visible in history and makes time-dependent behaviour reproducible. It also gives [measures](measures.md) the notion of time passing that they lack. Nothing of this is built.

## Composes from

Page, write, watch.

## Removes

Schedulers and background timers.

## Falsifying test

A page that expires does so only when the clock page changes, and replaying history gives the same result.

## Open questions

- Who writes the clock, and how often.
- How to use coarse steps so that history stays quiet.
