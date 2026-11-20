---
kind: decision
title: The vocabulary is what exists
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:vocabulary-is-what-exists
  - part:commands
---

# 0027 The vocabulary is what exists

## Context

- [Decision 0004](0004-plain-vocabulary.md) fixed a small set of plain words. It was held by a list of retired words that tests searched for in the code, and a second list of private wording that tests searched for in tracked text.
- A list of dead words grows with every rename and is kept forever. It says what is gone and nothing about what is there. The second list spelled out private wording inside the public repository.
- The same shape recurs wherever a check is written as a list of negative cases: banned strings, exceptions, retired names. Each list is debt. It is never finished, it needs a keeper, and it keeps the memory of things that no longer exist.
- Prior art: a schema or an API reference states what is valid and validates against it, and a linter rule states a property. A deny-list is the weaker form of both.

## Decision

State what exists and what is allowed, in one place the code is checked against. Never keep a growing list of what is banned, excepted or retired. A check asserts a property or an agreement between two sources, not the absence of named strings.

The vocabulary is the first use. [The vocabulary page](../reference/vocabulary.md) lists the concept words and everything the runtime exposes by name: commands, options, reserved and watch keys, trailer keys, kinds, refusals, errors, provider shapes, detected models and environment variables. Tests derive each set from the code and compare it with the page in both directions. A name in the code without a row fails, and a row without a name in the code fails. Each failure says which name and which file to edit.

## Consequences

- The two lists are removed, not moved. No file in the repository holds a list of banned or retired words in their place.
- The vocabulary page is the single place a new name is introduced. A rename changes the code and the page in the same change.
- Where the code had no single constant for a set, one was added and is used by the code: the trailer keys and the refusal words in `vault.py`, the watch and ask keys in `page.py`, and the environment variable names in `model.py`, `present.py` and `connect.py`.
- A scan for private wording, if the maintainers want one, belongs in private tooling and not in this repository. The rule that nothing internal is committed is held by review.
- The marker check for fix-later notes stays. It tests a property of the code, and a word is only how the property is written down.
- A growing list of negative cases elsewhere is a gap to close in the same way, by stating the property or the positive set.
