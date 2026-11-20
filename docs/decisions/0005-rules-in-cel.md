---
kind: decision
title: Rules in CEL
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.never
  - part.rule
  - layer.reflex
---

# 0005 Rules in CEL

## Context

- Rules must be pure: they see values and return a boolean, with no clock, randomness or input and output.
- A new expression language would be one more thing to learn and to maintain.

## Decision

Rules are pure boolean expressions in CEL (Common Expression Language), evaluated with the cel-python package. This follows the aim of looking for prior art and standards before inventing.

## Consequences

- Rule authors use an existing, documented expression language.
- The runtime depends on the cel-python package.
- Rules stay pure: they see values, they do not act.
