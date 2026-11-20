---
kind: decision
title: Rules in CEL
status: accepted
date: 2026-11-20
source: architect
---

# 0005 Rules in CEL

## Decision

Rules are pure boolean expressions in CEL (via the cel-python package), not a home-made expression language.

## Basis

Architect, following the rule to look for prior art before inventing.

## Consequences

- Rule authors can use an existing, documented expression language.
- The runtime depends on the cel-python package.
- Rules stay pure: they see values, they do not act.
