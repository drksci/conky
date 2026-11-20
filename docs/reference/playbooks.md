---
kind: reference
title: Playbooks
status: current
date: 2026-11-20
source: maintainers
---

# Playbooks

A playbook is a short scenario in YAML, run as a test. It gives some starting pages, then steps in order: a write, what the stand-in model will say, and what must then be true. One runner, `tests/playbook.py`, plays every file in `tests/playbooks/`. A step with a write uses the same keys as a [demo example](cli.md#demo).

## Keys

| Key | Meaning |
|---|---|
| `pages` | Starting pages, each a name with its fields. Written by `alice`. |
| `steps` | A list. Each step has exactly one of the three keys below. |
| `write` | `page`, `actor` (default `alice`), `fields` and `body`. The write is made, and may be refused. |
| `says` | The text the stand-in model gives the next time it is asked. It may hold pages as an answer does. |
| `expect` | Checks against the vault now, listed below. |

The checks in `expect`:

| Check | Holds when |
|---|---|
| `fields` | Each `page.field: value` is equal. |
| `exists`, `missing` | Each page in the list is, or is not, a file. |
| `refused` | The last write was refused, with a reason starting with this word. |
| `model_calls` | The stand-in model has been asked this many times in all. |
| `model_commits` | This many commits in the history were answered by a model. |
| `verify` | `true`: the vault verifies. |

A failed check names the playbook, the step number, what was expected and what was found.

## Example

```yaml
# A rule on a space refuses a page one of its characters tries to write.
pages:
  camp:
    rules: ["!has(page.cups) || page.cups >= 0"]
  scout:
    within: camp
steps:
  - write: {page: store, actor: scout, fields: {within: camp, cups: -1}}
  - expect: {refused: rule, missing: [store]}
  - write: {page: store, actor: scout, fields: {within: camp, cups: 3}}
  - expect: {exists: [store], fields: {store.cups: 3}, verify: true}
```

Playbooks never reach a live model. A test that needs more than this stays a Python test.
