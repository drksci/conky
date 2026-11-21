---
kind: decision
title: A budget the runtime holds
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.budget.held
  - stage.think.budget
  - place.runtime.budget
---

# 0058 A budget the runtime holds

## Context

- Asking a model is the one costly thing a page does ([decision 0019](0019-providers-are-pages.md), [decision 0030](0030-pay-once.md)). Nothing bounded it: a page woken a hundred times asked a hundred times, and an `ask` could not be handed down by a space only because nothing metered the cost ([decision 0041](0041-a-character-gives-its-space-reflexes.md), [decision 0056](0056-a-space-hands-down-reactions.md)).
- The rule that anything running in the background declares a budget and is metered was held by review alone.
- [Harnesses](../research/harnesses.md) records that cost bounding is built in conky nowhere yet and that several harnesses ship turn and budget caps. Prior art is the quota and the rate limit, and the prepaid meter: a stated allowance, counted by the one who provides the service.
- The image is a monthly allowance in an envelope. When the envelope is empty the spending stops, and someone refills it. Nobody has to remember to be careful.

## Decision

- A page may carry a field `budget`, a mapping with the one key `asks`, a whole number of zero or more. A wrong form is refused for `shape`, with the form to write.
- A page's asks spent are counted from the history alone, since its budget was last written. An ask is spent when a commit of the page, kept or refused, records a model's answer: it has a `Model` trailer that is not `none`, and no `Cache` trailer. An answer a rule refused is spent, and so is the ask repeated after it. An answer replayed from the cache is not spent, because nothing was paid. A plain sentence, a failed provider and a refusal for `limit` are not asks. Nothing is stored for the count, so `verify` and `rebuild` need nothing new.
- The budget is last written by a write that sets the field `budget`, on the page or on the space that holds the budget it lives under. A write that leaves `budget` alone does not refill it. A write that sets it to the same value does: a refill of the same size is a deliberate act. Such a write carries a trailer `Budget`, the number of asks or `none`, which is how the count finds it, even when the file does not change.
- When a page would ask and its asks spent have reached its asks, no model is called and a refusal for `limit` is recorded on the page, saying that the budget is spent, how many asks it allowed and that writing the budget again refills it. A cached answer is not looked for either: a spent budget stops the ask before the cache. `on: refusal` entries hear it as any refusal: the page, the actor and the spaces above. A keeper, a person or a reflex can be told and can refill or not.
- A space may give its members a default budget. A member with no `budget` of its own takes the `budget` of the nearest space above it that has one, in the order of `page.above` and the theatre last. A member's own budget wins. A space's budget is a default for each member, not a pool the members share. A shared pool is not built. A space that has a budget lives under it as well, so the theatre's budget bounds the theatre page.
- A condition reads `asks.spent` and `asks.left` for the page it judges or the page that reacts. With no budget nothing is counted: `asks.spent` is 0 and `asks.left` is 1000000, a number no page spends, so a condition such as `asks.left > 0` is always true for a page with none. A prompt embeds `![[PAGE#asks]]`, which resolves to `3 of 5 asks left` for a page with a budget, and otherwise reads the field called `asks`, as before. The name `asks` is not reserved as a field, so no page that has one is broken.
- No clock is involved. The window is set by a write: a budget that renews each month is a clock page, when there is one, writing the budget again. The refill is an ordinary signed write, so a history shows who refilled it and why.
- A write bound to a space, which is how an answer writes pages, may not set `budget`: a budget the model could raise would be no budget.
- The two walls the budget lets down are not lowered here. An answer still may not add an `ask` watch entry to its space, and a space still may not hand down an `ask`. They may be lowered next, only for pages that have a budget.

## Why a write and not a clock

A clock would make the count depend on when it is read, so reading the history would not give the same answer twice. A write is in the history, so the count is the same on every machine and in every replay.

## What the old behaviour guaranteed

- A page could ask without limit. Changed only for a page with a budget, its own or handed down. Kept for every other page, under `test_no_budget_means_no_limit` and the playbooks.
- A refused ask is recorded and never dropped. Kept: the spent budget is a recorded refusal, under `test_a_budget_cannot_be_exceeded`.
- It always works. A spent budget lowers the result and says so in the record. It does not block a write or break a vault, under the same test.
- A page called `asks` could be a field. Kept: the name is not reserved.
- An answer could write any field of a page within its space. Given up for `budget` only, under `an-answer-giving-a-page-a-budget`.

## Consequences

- Cost is a limit the runtime holds and a page can read, so a character can see how much it has left and a rule can judge it.
- Not built: time windows (they wait for the clock), tokens, money, a pool shared by a space, budgets for connectors, and lowering the two walls.
- Each ask reads the history of the page with `git log` and a filter on its name. The cost grows with the page's own history; a derived index is not built.
- Roadmap step R17 is built in this part. The first background mind is not.
