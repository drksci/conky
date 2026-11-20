---
kind: idea
title: Assimilation test
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - flow:assimilate
  - part:assimilate
  items:
  - kind: part
    name: resume-test
    layer: edge
    text: 'The model-backed resume test: a fresh model-driven consumer handed only a stopped vault, with behavioural continuity scored apart from state continuity.'
    roadmap: R7
---

# Assimilation test

## Idea

Hand a fresh consumer only a stopped vault, by `git clone` or a bundle, and score whether it resumes correctly. It is a scenario in the benchmark described in [decision 0014](../decisions/0014-benchmark-shape.md).

## What was built

The mechanical form exists as `conky assimilate` ([command line reference](../reference/cli.md#assimilate)). It takes a stopped vault from its folder alone, by directory, bundle or URL, checks it with `verify`, reads the pages and their rules and watches from the files, and carries on as a new actor with a new key. Without a source it uses a small stopped vault that ships in the package.

No model is involved, so this is a mechanism result. It shows that state travels and resumes, not that anything behaves intelligently, and it scores state continuity only.

The model-backed form is not built: a fresh model-driven consumer handed only the stopped vault, with behavioural continuity scored apart from state continuity.

## Composes from

The vault travels alone (a vault is a Git repository, moved by clone or bundle); `verify` and `rebuild`.

## Removes

Not yet worked out.

## Falsifying test

A fresh consumer given only a stopped vault fails to resume correctly where the vault's own pages should have been enough.

## Prior art

The [research index](../research/dair-2026.md) lists "Runtime-Independent Persistent Agents", described there as a six-step pause, save, validate, attach, load, resume handoff. Its authors note that behavioural continuity is a separate question from state continuity, so the test should score both.
