---
kind: idea
title: Measures
status: idea
date: 2026-11-20
source: archive turn 36
---

# Measures

## Idea

A measure is a pure function over pages and the log, like a rule that returns a number. It could unify attention, decay and metrics.

## First candidate: pressure

The operator proposed that size should not be a wall that refuses work but a pressure that builds. A page that grows past what its space considers comfortable is still written, but its pressure rises, and at a threshold a reaction fires (for example the page is asked to split, or a tidy-up is triggered) with no model call and without the actor having to think about it. The aim is that limits act like friction that is felt and resolved in the background, rather than a gate that stops work.

A hard rule remains the right tool for things that must never happen (a negative balance). Pressure is for things that should be noticed and dealt with.

Falsifying test: with pressure in place, pages in a long run stay bounded without any refused write, and without spending inference on housekeeping.

Source for this section: operator, this session.

## Composes from

Rules (pure, over pages) and the log.

## Removes

Separate mechanisms for attention, decay and metrics, if one measure can serve each.

## Falsifying test

A measure that needs a clock, randomness or input outside pages and the log to compute what it was meant to.
