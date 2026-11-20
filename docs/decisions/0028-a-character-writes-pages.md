---
kind: decision
title: A character writes pages
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law:pages-capability
  - law:reach-flows-down
  - flow:answer-is-pages
  - part:answer-format
---

# 0028 A character writes pages

## Context

- A page that asks a model could put the answer into one field. A character could not make a page of notes, another character, a space or a rule, so it could not organise itself.
- Behaviour is data: a prompt, a reaction and a rule are fields on a page. A character that can write pages can therefore change its own behaviour and that of what it makes ([decision 0029](0029-autonomy-inside-limits-that-hold.md)).
- A character with that power must stay inside limits that hold when the model ignores them ([rules, not requests](../essays/rules-not-requests.md)). Decision [0022](0022-leaving-a-space-is-a-write-the-space-can-refuse.md) made the leaving rule part of this and left it unbuilt.
- Prior art for the answer format: a fenced block per file, as chat models already write code, and the front matter of a Markdown page, which Conky already stores. The header line `=== page: <name> ===` is the same device as a fence with a name, and is one line a person reads at once and a model reliably produces. The reply is cut by line, so no parser for nested markup is needed.

## Decision

An `ask` entry gains one optional key, `writes`, naming a space. When it is present the answer is read as plain text plus zero or more pages. Each page is introduced by a header line `=== page: <name> ===` and given in Conky's page format. The fixed instruction for this format is appended to the prompt by the runtime. The plain text goes to `into`, when there is one.

- The key is `writes`: the verbs of the vocabulary are `read`, `write` and `watch`, a page `watch`es another page and `write`s into a space, and `into` already names a field.
- Each page is an ordinary write by the asking page, one commit each, in order, caused by the answer. The write path, the rules and the history are unchanged.
- The runtime enforces the limits: a page must be within the named space before and after the write, may not carry `secret` or `command`, and may not carry a watch entry that writes outside the space. Rules of every space involved judge the write, including the spaces the page leaves. Reactions share the depth cap of 12. A malformed block is one recorded refusal and the other pages still apply.
- The minimum of the leaving rule is built with it: a write that changes the `within` of an existing page is judged by the rules of the spaces it was in as well as those it will be in.
- `conky ask` takes `--writes` and prints what was written and what was refused.

## Consequences

- A character can make notes, characters, spaces and rules, and rewrite its own watch entries, with no mechanism beyond the write path. Reach flows down: what it creates can reach no further than it can.
- A rule on a space binds what members create, and a member cannot walk out of a rule by changing `within`. A space that says nothing lets members go.
- A character cannot rewrite a provider page that carries a secret or a command name, and cannot create one. It can create a provider page without them. Naming a secret or a program stays with the person.
- An answer that is refused as a whole writes no pages, so a question that never settles does not write the same pages again and again.
- A page that already exists outside the named space cannot be written by naming it, even to move it in. The text of the instruction is fixed, so a changed instruction changes the resolved prompt and a settled question is asked once more.
- Unbuilt: a budget on how many pages a character may write, and rules that can see who signed a change, so a space cannot yet say which characters may move which pages ([roadmap](../project/roadmap.md), R14). Unverified with a live model: the format has been tested with stand-in models only.
- Removed: the unbuilt note of decision 0022 for the leaving rule.
