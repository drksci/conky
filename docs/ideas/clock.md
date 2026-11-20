---
kind: idea
title: Time as an ordinary change
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: clock
    by: undecided, a connector is the shape the documents give it
    layer: edge
    text: A page written as time passes, watched by anything that depends on time.
    roadmap: R12
  - kind: stage
    name: a clock tick
    phase: stimulus
    text: A write to a clock page. Nothing writes one yet.
    roadmap: R12
  - kind: flow
    name: clock-tick
    title: A clock tick
    statement: Time passes when a clock page is written, and anything that depends on time watches it.
    rank: 1
    steps:
    - frm: Outside
      to: Connector
      text: time passes
    - frm: Connector
      to: Runtime
      text: write the clock page, in coarse steps
    - frm: Runtime
      to: History
      text: an ordinary signed event
    - frm: Runtime
      to: Page
      text: pages that depend on time react and a staleness measure rises
    - frm: Runtime
      to: null
      text: who writes the clock and how often is open
    roadmap: R12
---

# Time as an ordinary change

## Idea

Time passes when a clock page is written, and anything that depends on time watches that page. There is no hidden timer, so time shows in history and time-dependent behaviour can be replayed. It also gives [measures](measures.md) the sense of time passing that they lack. Nothing of this is built.

## Composes from

Page, write, watch.

## Removes

Schedulers and background timers.

## Falsifying test

A page that expires does so only when the clock page changes, and replaying history gives the same result.

## Open questions

- Who writes the clock, and how often.
- How to use coarse steps so that history stays quiet.
