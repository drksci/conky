---
kind: idea
title: What is happening can be watched
status: idea
date: 2026-11-22
source: "reference/vocabulary.md, ideas/connectors.md, ideas/compositor.md, CLAUDE.md (the rule on derived data); outside: Git (https://git-scm.com/docs/git-log), Server-Sent Events (https://html.spec.whatwg.org/multipage/server-sent-events.html), newline-delimited JSON (https://github.com/ndjson/ndjson-spec)"
arch:
  items:
  - kind: part
    name: part.history.said
    layer: layer.edge
    text: What is happening and not yet recorded is said as a line in a file beside the vault by whoever watches, never read back by the runtime and safe to delete.
    state: idea
---

# What is happening can be watched

## Idea

Rung: idea. Nothing here is built.

What has happened is already a signed stream: the history, which anyone can follow with Git. What is happening and not yet recorded is not in it. An ask that has started and not ended, a connector that has come and gone: none of these is a commit, and a person watching a run cannot see them until the result lands.

Whoever watches says it. A watcher writes a line for each such moment to a file beside the vault, outside the history. The runtime never reads the file back and nothing may depend on it, so it can be deleted at any time and the vault is the same. A viewer, a log or a script may follow the file as it follows the history.

This is not derived data. Derived data can be rebuilt from the vault, and these lines cannot: the moment is gone once it has passed. That is why nothing is allowed to depend on them, and why they are kept apart from the history and from the caches.

The runtime speaks no protocol. A connector beside the vault can serve the history and the lines together in any shape a viewer wants, as events over HTTP or as plain files.

The matching rule for `CLAUDE.md` is proposed and not adopted: a file beside the vault that is said, not derived, is allowed only if the runtime never reads it. Until it is adopted by a decision, this page is the only place it is written.

## Composes from

The history, the connector, a file beside the vault, and a line of text per moment. No new primitive of data: a stream already means an append-only log.

## Removes

A progress channel inside the runtime, and any wish for the history to carry what has not happened yet.

## Falsifying test

The history of a run is the same with and without a watcher. Run a recorded playbook twice, once with a watcher saying its lines and once with the file deleted before and after, and compare the commits. If they differ, something has come to depend on the lines, and the idea is lost.

## Open questions

- Whether one file per run or one per vault.
- Which moments are worth a line: an ask starting and ending, a connector coming and going, or fewer.
- Whether the rule for `CLAUDE.md` is a new rule or a reading of the one on derived data.
