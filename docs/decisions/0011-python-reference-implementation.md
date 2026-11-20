---
kind: decision
title: Python reference implementation
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - part.vault
---

# 0011 Python reference implementation

## Context

- The design is still changing, so the runtime needs a language that is quick to change and to test.
- Parquet and DuckDB tooling is native to Python.
- The agent harnesses conky is to be compared with are written in Python.
- No part of the runtime yet needs a sandbox for untrusted code.

## Decision

The reference implementation is Python, in `src/conky/`. A later core in another language is considered in [0012](0012-rust-core-planned.md).

## Consequences

- Tables will use Python Parquet tooling.
- The runtime depends on `pyyaml` and `cel-python`.

## Open questions

Whether a sandbox for untrusted code is needed later.
