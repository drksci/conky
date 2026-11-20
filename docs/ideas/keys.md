---
kind: idea
title: Keys that change hands
status: idea
date: 2026-11-20
source: "project/open-questions.md (how keys are rotated and revoked) and the verify step in reference/vault-format.md"
arch:
  items:
  - kind: part
    name: part.key.rotate
    layer: layer.git
    text: Adding, retiring and revoking a signer as recorded events, with each event judged against the signers in force when it was made.
    state: idea
    roadmap: R32
---

# Keys that change hands

## Idea

A vault outlives its keys. A key is retired when its owner stops writing and revoked when it is lost. Both are changes to `keys/allowed_signers`, which is already a committed file, so both can be ordinary signed events. What changes is how `verify` judges: today it checks every commit against the signers file as it stands now, so removing a line would make that key's past events fail. Under this idea each event is judged against the signers as of the event before it. A retired key still verifies what it signed while it was in force, and anything it signs afterwards fails.

## Composes from

The signers file, a write, and `verify`.

## Removes

Any key server outside the vault. A vault still verifies alone, with no network ([decision 0002](../decisions/0002-git-is-the-store.md)).

## Falsifying test

After a key is retired, its earlier events verify and a later event signed by it fails. A clone verified with no network gives the same answers.

## Open questions

- Who may retire whose key. A rule over the signers file needs rules that see who signed (R14).
- Whether a revoked key should also cast doubt on events it signed before revocation, when the key was stolen earlier.
