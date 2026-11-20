---
kind: idea
title: A page that reviews
status: idea
date: 2026-11-20
source: "research/findings-rubric.md (F15, F17, F22) and the guardrail row of research/gaps.md, which records that no idea page covered the reviewer"
arch:
  items:
  - kind: archetype
    name: kind.reviewer
    by: a person or a character
    layer: layer.character
    text: A model page that reads a proposed change and writes a signed verdict page, which a rule counts.
    state: idea
    roadmap: R35
---

# A page that reviews

## Idea

A check on meaning, such as whether a summary is faithful or a page carries planted instructions, cannot be a rule, because rules are pure ([decision 0005](../decisions/0005-rules-in-cel.md)). It can be a page. A reviewer is a model page that watches proposals in its space, reads the change and writes a verdict page: the change it judged, pass or fail, and one sentence of reason. A rule on the space refuses the change until a signed verdict for it is in place. The reviewer is a different page from the author, which the research read prefers to self-checking (F15), and it can itself be rewritten, which F22 asks of an evaluator.

## Composes from

[Approvals](approvals.md) (a proposal and a rule that counts signed pages), [pages that ask a model](model-pages.md), and rules that see who signed ([`part.seal.signer`](../reference/architecture.md#part.seal.signer)). Its spending is a budget like any background page ([background minds](background-minds.md)).

## Removes

Guardrail hooks that call a model. A review is a page with a signer and a history, not a callback.

## Falsifying test

A change the reviewer fails is refused on every write path. A reviewer cannot pass a change it wrote when the space forbids it. On a task with policy, the reviewed arm does better than the unreviewed one at its stated extra cost; if review costs more than it saves, the idea lost.

## Open questions

- How a verdict names a change that is not yet kept: by the proposal page and its event.
- Whether a space has one reviewer or one for each kind of check.
