---
kind: decision
title: An answer refused for its shape is asked again
status: accepted
date: 2026-11-28
source: maintainers
arch:
  covers:
  - stage.think.retry
---

# 0067 An answer refused for its shape is asked again

## Context

- A refused answer is asked again once, with the reason as the last thing the model reads, when a rule refused it. A refusal for shape was recorded and left, although its reason says exactly what to write instead (the retry is described in [decision 0038](0038-a-rule-is-proven-when-written.md)).
- One draw of the card `a-clerk-notices-what-changed` with a live small model showed the cost. The memory page answered with a page block headed `=== page: Mrs Okafor's parcel, shelf 12 ===`. The write was refused for shape, the reason said how a header is written, and the question was not asked again. The parcel was never kept, and the clerk could not give the shelf at the fourth moment. On later answers the same model named its pages rightly, so it can do the form once it has seen it.
- The law is that nothing malformed lands and every refusal says what to write instead. A reason nobody is shown teaches nobody.
- The image is a form handed back across the counter with the box circled in red: the clerk is allowed to fill it in once more, and no more.

## Decision

- The retry covers a refusal for shape as it covers one by a rule: the same prompt is sent once more with the reason after it, caused by the refusal, whether the shape refusal is of the write to `into` or of a page block the answer holds.
- It stays one retry. A second refusal for a rule or its shape writes the entry's `otherwise` text when it has one, and stops. A refusal for `limit` or `cycle`, and a failure to ask (`model:`), are not retried.
- The stage direction is the existing `retry` line in `src/conky/voice.md`. It reads rightly for a shape reason, so it is not reworded.
- The second ask is an ordinary ask. A budget ([decision 0058](0058-a-budget-the-runtime-holds.md)) counts it and, when spent, stops it with a `limit` refusal.
- The card `a-clerk-notices-what-changed` gives its memory page seven asks for five moments, so a retry has room, and its bar of calls becomes 17.
- No word is added to the vocabulary.

## What the old behaviour guaranteed

- A refusal for shape cost one ask and stopped. That kept the cost of a malformed answer to one call. It is given up in writing: a shape refusal may now cost two asks. The ceiling a question had, one retry, is kept under `tests/test_retry.py`.
- A retried question is not answered from the cache of the refused answer, because the second prompt differs. That is unchanged.
- A rule's refusal is asked again exactly as before.

## Consequences

- A small model that misnames a page sees the form in the reason and can write the page on the second answer. Measured only with stand-in programs, in `tests/test_retry.py`. Whether a live small model does so is not measured here.
- A character whose answers are often malformed spends more of its budget. The budget still bounds it.
- Not built: a different note for a shape reason. The one line serves both.
- Two older tests recorded the old behaviour and change with it: the playbook `a-shape-refusal-is-not-asked-again` becomes `a-shape-refusal-is-asked-again-once` (two calls where there was one), and the test of a malformed block in `tests/test_pages.py` now finds each refusal once a try. No decision stood behind the old behaviour; the playbook recorded what the code did.
