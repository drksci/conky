---
kind: idea
title: The history is the trace
status: idea
date: 2026-11-20
source: maintainers
---

# The history is the trace

## Idea

Every change is already a signed entry that names its cause, so the history is a complete trace by default. What is missing is reading it comfortably: summaries per page and per period, and links from any fact to the change that set it.

Those are derived data and can be regenerated ([decision 0017](../decisions/0017-derived-data.md)). Nothing of this is built.

## Composes from

Event, seal, and derived data.

## Removes

A separate audit log or tracing system.

## Falsifying test

For any field of any page, the change that set it and the chain of causes behind it can be shown without special tooling beyond the vault.
