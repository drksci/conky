---
kind: decision
title: A model is reached by a key or by a program already on the machine
status: accepted
date: 2026-11-20
source: maintainers
---

# 0024 A model is reached by a key or by a program already on the machine

## Context

- Provider pages exist ([decision 0019](0019-providers-are-pages.md)) for two HTTP shapes with a named secret. No live provider has been called.
- Many people have a Claude or ChatGPT subscription with a command-line client and no API key.
- The first run must need nothing configured.

## Decision

A third provider shape, `api: command`. The prompt goes to a local program on standard input and the answer is read from standard output. Examples are Claude Code in print mode (`claude -p`) and the Codex client.

- The vault never holds the command line. The page names a command the way it names a secret, and the actual command comes from the environment or the key directory outside the vault, so a cloned vault cannot make a machine run anything.
- When a vault names no provider, the runtime picks one in a fixed order from what the environment offers: an explicit setting, then API keys, then a known client on the path. Otherwise it answers with the plain-sentence reflex, and says so.
- The choice made is recorded on the commit like any model answer.

## Consequences

- One command still works with nothing configured, and a subscription is enough to run a vault with real characters.
- The detection order is documented and can be overridden by one environment variable.
- Answers from a command are marked as such in the record.
- Cost limits remain the budget rule (R17).
- Unbuilt in this record: the code is being built now by another change (R26), and the [providers reference](../reference/providers.md) will carry the exact names.
