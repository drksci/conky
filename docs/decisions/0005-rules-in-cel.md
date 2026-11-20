---
kind: decision
title: Rules in CEL
status: accepted
date: 2026-11-20
source: maintainers
---

# 0005 Rules in CEL

## Context

Rules must be pure: they see values and return a boolean, with no clock, randomness or input and output. Designing a new expression language for this would add something to learn and to maintain.

## Decision

Rules are pure boolean expressions in CEL (Common Expression Language), evaluated with the cel-python package, not a home-made expression language. The choice follows the aim of looking for prior art and standards before inventing.

## Consequences

- Rule authors can use an existing, documented expression language.
- The runtime depends on the cel-python package.
- Rules stay pure: they see values, they do not act.
