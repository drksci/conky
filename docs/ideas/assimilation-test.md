---
kind: idea
title: Assimilation test
status: idea
date: 2026-11-20
source: operator, this session
---

# Assimilation test

## Idea

Hand a fresh consumer only a stopped vault and score whether it resumes correctly. It is a scenario in the benchmark described in [decision 0011](../decisions/0011-benchmark-shape.md).

## Composes from

The vault travels alone (a vault is a directory); `verify` and `rebuild`.

## Removes

Not yet worked out.

## Falsifying test

A fresh consumer given only a stopped vault fails to resume correctly where the vault's own pages should have been enough.

## Prior art

The [research index](../research/dair-2026.md) lists "Runtime-Independent Persistent Agents", described there as a six-step pause, save, validate, attach, load, resume handoff. Its authors note that behavioural continuity is a separate question from state continuity, so the test should score both.
