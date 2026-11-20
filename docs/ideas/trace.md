---
kind: idea
title: The history is the trace
status: idea
date: 2026-11-20
source: maintainers
---

# The history is the trace

## Idea

Every change is already a signed entry that names its cause, so the history is a complete trace by default. What is missing is reading it comfortably: summaries per page and per period, and links from any fact to the change that set it. Those are derived data and can be regenerated ([decision 0017](../decisions/0017-derived-data.md)). They are not built. Two additions to the record are.

## What was built

Two trailers make activity readable from the history alone ([vault format](../reference/vault-format.md)).

- `Read: <page>`. When a page asks a model, the commit that records the answer carries one `Read` trailer for each distinct page whose content was embedded in the prompt, in order of first use. `conky log` shows it after the model marker, as `read a, b`.
- `From: <space>`. When a write is refused by a rule that came from a space, the refusal commit carries a `From` trailer naming that space, beside the reason text. `conky log` shows it as `from <space>`.

A reaction that fires from a watch entry records nothing new, because today the entry lives on the page itself. Watch entries inherited from spaces are not built, so there is nothing to name yet. The summaries per page and per period, and the links from any fact to the change that set it, are not built.

## An activity strip

A strip of plain-language notices on the composed screen could say "Sam read the house rules", "the supplier ordered lemons by itself" and "the house rule said no". Each is derived from the history: a `Read` trailer, a reaction with its `Cause`, and a refusal with its `From`. No page logs anything for the strip, so a page that acts needs no extra code to be noticed. It is derived data, rebuildable from the vault and safe to delete. It is not built. See [the compositor](compositor.md).

## Composes from

Event, seal, and derived data.

## Removes

A separate audit log or tracing system.

## Falsifying test

For any field of any page, the change that set it and the chain of causes behind it can be shown with nothing beyond the vault.
