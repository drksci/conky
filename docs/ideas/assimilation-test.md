---
kind: idea
title: Assimilation test
status: idea
date: 2026-11-20
source: maintainers
---

# Assimilation test

## Idea

Hand a fresh consumer only a stopped vault and score whether it resumes correctly. The vault is handed over with `git clone` or a bundle. It is a scenario in the benchmark described in [decision 0014](../decisions/0014-benchmark-shape.md).

## What was built

The mechanical form exists as `conky assimilate` ([command line reference](../reference/cli.md#assimilate)). It takes a stopped vault from its folder alone, by directory, bundle or URL, checks it with `verify`, reads the pages and their rules and watches from the files, and carries on as a new actor with a new key. Without a source it uses a small stopped vault that ships in the package. No model is involved, so it is a mechanism result: it shows that the state travels and resumes, not that anything behaves intelligently. It scores state continuity only.

The model-backed form is not built: handing a fresh model-driven consumer only the stopped vault and scoring whether it resumes correctly, with behavioural continuity scored apart from state continuity.

## Composes from

The vault travels alone (a vault is a Git repository, moved by clone or bundle); `verify` and `rebuild`.

## Removes

Not yet worked out.

## Falsifying test

A fresh consumer given only a stopped vault fails to resume correctly where the vault's own pages should have been enough.

## Prior art

The [research index](../research/dair-2026.md) lists "Runtime-Independent Persistent Agents", described there as a six-step pause, save, validate, attach, load, resume handoff. Its authors note that behavioural continuity is a separate question from state continuity, so the test should score both.
