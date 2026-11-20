---
kind: decision
title: Size is a rule
status: accepted
date: 2026-11-20
source: operator
---

# 0006 Size is a rule

## Decision

There is no fixed page size limit. Size is exposed to rules as a `size` variable, so a space can set its own limit and members inherit it.

## Basis

Operator challenged the constant: the earlier 4096-byte law was arbitrary. Architect folded the question into the rule primitive, which removed a special case.

## Consequences

- A limit such as `size <= 2000` is an ordinary rule on a space.
- The runtime holds no size constant.

## Open questions

Whether size should be a hard rule at all or only a pressure (see [measures](../ideas/measures.md)). Today it is available as a hard rule because that is the only mechanism built.
