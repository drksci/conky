---
kind: decision
title: Rust core planned
status: accepted
date: 2026-11-20
source: maintainers
---

# 0012 Rust core planned

## Context

The reference implementation is in Python while the design is still changing ([0011](0011-python-reference-implementation.md)). Python needs an interpreter and, for this design, Git and `ssh-keygen` on the machine. That limits where a vault can be used: not in a browser, and not on a machine without those tools.

## Decision

Once the vault format is settled, a core in Rust is intended. It would be compiled natively and to WebAssembly, so that it can run without Git or other tools installed and in a browser. This is a plan, not a present capability, and nothing of it is built.

Any other implementation, including that one, must pass the same conformance suite: the golden vault fixture in `tests/golden/` and the tests in `tests/`. The golden vault is a bundle of a small vault that every implementation must verify and read to identical pages. A change that breaks the fixture is a break in the vault format and needs a decision record first.

## Consequences

- Until the format is settled, the Python code is the reference and the tests are the specification.
- The vault format is documented in [the vault format](../reference/vault-format.md) so that another implementation can be written from it.
- The golden vault must not be regenerated to make a test pass.
- A feasibility test showed that a Rust-only core can write a Git repository that Git accepts, sign and verify commits in Git's SSH format, evaluate rule expressions, and compile to WebAssembly. The WebAssembly build was not run, and reading packed repositories was not attempted.
