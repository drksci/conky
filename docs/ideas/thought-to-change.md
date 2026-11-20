---
kind: idea
title: Thought to change
status: idea
date: 2026-11-20
source: maintainers
arch:
  covers:
  - flow.ask.pages
  - law.answer.pages
---

# Thought to change

## Idea

A background process turns free-form thinking into validated changes. The translation is always shown to the thinker, who can override it, and never bypasses rules: a translated change is an ordinary write, checked like any other.

## Built so far

Rung: idea. One part is enforced. An `ask` entry with `writes` turns a model's free-form answer into zero or more pages, each an ordinary write by the asking page into a space, checked by the rules of every space involved ([decision 0028](../decisions/0028-a-character-writes-pages.md), [an answer that is pages](../reference/rules-and-reactions.md#an-answer-that-is-pages)). The tests in `tests/test_pages.py` fail when a limit is removed. Still unbuilt: a background process that does this unasked, and showing each translation to the thinker for an override before it takes effect. With stand-in models only.

## Composes from

Writes checked by rules; [background minds](background-minds.md).

## Removes

Not yet worked out.

## Falsifying test

The translation changes a page in a way the thinker cannot see or override before it takes effect.

A character binding itself with a rule of its own, then being refused when an answer breaks it, is held by the playbook `tests/playbooks/a-character-binds-itself.yaml`.
