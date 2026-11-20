---
kind: decision
title: Python core
status: accepted
date: 2026-11-20
source: architect
---

# 0004 Python core

## Decision

The core is Python, replacing the Rust scaffold.

## Basis

Architect. The reasons: the operator builds proofs of concept in Python; Parquet and DuckDB tooling is native there; the agent harnesses to benchmark against are Python; and nothing yet consumed a Wasm sandbox.

## Consequences

- The runtime lives in `src/conky/` as Python.
- Tables will use Python Parquet tooling.

## Open questions

Whether a sandbox for untrusted code is needed later.
