---
kind: decision
title: A character is born with a memory and a sense for what changed
status: accepted
date: 2026-11-28
source: maintainers
arch:
  covers:
  - kind.mind
---

# 0066 A character is born with a memory and a sense for what changed

## Context

- The idea of attention ([attention](../ideas/attention.md), trial T2) says a thinking page is shown only what the pages within its own character passed up, and that its prompt holds no word about keeping or noticing.
- Roadmap R17 asks for the first background mind, a budgeted model page, shown by a card.
- Three forms of the card `a-clerk-has-a-memory` failed, each for a small model's judgement about what to store (the status page records the draws). The card is replaced by `a-clerk-notices-what-changed`, which keeps the third form's memory and adds a page that says when something differs from what the character knew.
- Decisions 0058 (a budget the runtime holds), 0064 (an embed inside an embed is followed) and 0065 (a command provider page names its model and effort) made it possible to say this with pages only.

## The walk

1. **The image.** A counter clerk with a notebook and a nudge. The clerk serves the person in front of it; a colleague writes down what mattered, and another taps its shoulder when the shelf is not as it was. The clerk reads what they left and is never told they exist.
2. **The general case.** A page beside another that watches it and writes for it, in its voice, at a lower price.
3. **Existing words.** A page, a space, a field, a watch, an ask, a provider, a budget, an embed, a member, `writes`, `shows`. Nothing is left over: `voice` is a field the pages of one card carry and embed, and the runtime reads no such field.
4. **The natural gesture.** One page for each thing worth knowing, named for what it is, and a sentence when something is odd.
5. **Par.** Letta keeps an agent's memory as a git repository of Markdown files with every edit committed ([harnesses](../research/harnesses.md), from its documentation, read 2026-11-28). The "Generative Agents" abstract says the architecture stores a complete record of experience in natural language, retrieves it dynamically and synthesises reflections (Park and others, 2023, [arXiv 2304.03442](https://arxiv.org/abs/2304.03442); abstract read 2026-11-28, body not read). Findings F8, F9 and F12 of the [findings rubric](../research/findings-rubric.md) say organisation of memory buys search economy more than answer quality, that retrieval matters more than how memory is written, and that a memory linked to its source helps; here every kept page carries `Cause` and its actor.
6. **Who does it.** A character could write these pages for itself. The card gives them at birth, as the starting pages that the card and its tests consume, because the runtime has no pattern maker yet (R6). Nothing is added to the runtime.
7. **The trial.** The card `a-clerk-notices-what-changed`, forecast 3 of 5 or better against a bar of 3, one dial: the two pages present or absent. It is not drawn live. A miss at the first moment would repeat the earlier finding, and the next step would be to show the clerk its own record rather than store it again.
8. **How it is seen.** `conky log` shows each kept page signed by the memory, caused by the answer it came from; the noticing page's field shows what it said.
9. **The smallest step.** The card, its tests with stand-in programs, and no change under `src/`. Waiting: the other background minds, a time window, and a draw with a live model.

## Decision

- A character is born with two pages within it that ask a provider page naming a small model and a low effort, and each carries `budget: {asks: N}`. One, the memory, watches the character's answer and writes pages of its own, with `writes: book`. The other, the noticing page, watches the desk and writes only its own field. The character's prompt embeds one page that gathers what they wrote, and holds no instruction about keeping or noticing. The test of that is made on the prompt as the program received it, not on the commit, whose `Read` trailers name the pages.
- The kept pages lie within a space of their own, `book`, which lies within the character. The listing `![[the-clerk#members]]` would name every page within the character at any depth, so the pages that ask would be named in front of the character; a listing of `book` names only what was kept. `book` carries `shows`, so what bears most on the moment comes first (the pages that share the most words with what the desk said, kept in a field by a reflex).
- The wall is `writes: book`, which refuses for `limit` any page of an answer that is not within `book` before and after, and a `budget: {asks: 0}` on `book`, which is handed down to every page within it. A page an answer writes may carry an `ask`, since only the block that names the space is held to `set`; a kept page that asks is refused for `limit` under the budget of `book`, and an answer cannot set `budget` on a page it writes. Whether such a page should be refused outright is left for later.
- A noticing page that has nothing to say answers the one word `nothing`, and a second entry of its own, a reflex, empties the field. An empty answer from a command provider is a failure, so the word is needed, and the quiet moment costs one more commit and no call.
- The pages that must act on a write before the character are named to sort before it. Reactions to one write are visited in order of page name, and the reactions to one reaction finish before the next watcher is visited, so `book` and `noticing` act before `the-clerk`. This is a limit: a character born under another name keeps working only if its pages sort before it. A stated order of reactions is later core work (R28 notes the need).
- "What bears most comes first" is built. "Unused things sink" is not: a `first` expression reads only the member's fields, its body and the space's fields, and nothing it can read says how often a page was shown. It waits on [standing](../ideas/standing.md).
- The starting pages are the card's `pages:` and its first step. conky holds no golden of pages to start from: `tests/golden/` is the vault format fixture, and the pattern maker is not built. The tests read the pages from the card, so they live in one place.
- One character and a prompt is a complete starting state. The pages that ask lie within the character and are born with it. The desk and the provider pages are the world and the models, as in every card, and nothing outside the character is installed for it.
- No word is added to `docs/reference/vocabulary.md`, and no new form a page can declare appears.

## What the old behaviour guaranteed

- The card `a-clerk-has-a-memory` guaranteed a way to ask whether a clerk told nothing about keeping can give a fact three moments later. The new card keeps that, with the same clerk, the same fact and a prompt of the clerk's that holds none of the words of keeping, held by test 4 of `tests/test_notices.py`.
- It guaranteed that a kept page is the character's own words. The new card keeps that: each prompt that asks carries the voice of the character.

## Consequences

- A character can be given a memory and a sense for change from pages alone, at a small model's cost, and each call is metered and recorded.
- Order depends on page names, and nothing sinks when unused.
- Not verified: the card has not been drawn with a live model, so whether a small model judges a parcel worth a page is unmeasured. The walls were walked with stand-in programs only.
