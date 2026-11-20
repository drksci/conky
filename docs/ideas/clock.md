---
kind: idea
title: Time as an ordinary change
status: idea
date: 2026-11-20
source: maintainers
arch:
  items:
  - kind: archetype
    name: kind.clock
    by: undecided, a connector is the shape the documents give it
    layer: layer.edge
    text: A page written as time passes, watched by anything that depends on time.
    roadmap: R12
  - kind: stage
    name: stage.stimulus.clock
    phase: stimulus
    text: A write to a clock page. Nothing writes one yet.
    roadmap: R12
  - kind: flow
    name: flow.clock.tick
    title: A clock tick
    statement: Time passes when a clock page is written, and anything that depends on time watches it.
    rank: 1
    steps:
    - frm: lane.outside
      to: lane.connector
      text: time passes
    - frm: lane.connector
      to: lane.runtime
      text: write the clock page, in coarse steps
    - frm: lane.runtime
      to: lane.history
      text: an ordinary signed event
    - frm: lane.runtime
      to: lane.page
      text: pages that depend on time react and a staleness measure rises
    - frm: lane.runtime
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
