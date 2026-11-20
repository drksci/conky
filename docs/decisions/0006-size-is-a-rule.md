---
kind: decision
title: Size is a rule
status: accepted
date: 2026-11-20
source: maintainers
---

# 0006 Size is a rule

## Context

A fixed page size limit is an arbitrary constant. Different spaces have different needs, and a single number is too tight for some pages and too loose for others.

## Decision

There is no fixed page size limit. Size is exposed to rules as a `size` variable, so a space can set its own limit and members inherit it. This folds the question into the rule primitive and removes a special case.

## Consequences

- A limit such as `size <= 2000` is an ordinary rule on a space.
- The runtime holds no size constant.

## Open questions

Whether size should be a hard rule at all or only a pressure (see [measures](../ideas/measures.md)). Today it is available as a hard rule because that is the only mechanism built.
