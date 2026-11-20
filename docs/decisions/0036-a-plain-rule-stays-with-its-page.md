---
kind: decision
title: A plain rule stays with its page
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - part.space
---

# 0036 A plain rule stays with its page

## Context

- Until now a plain rule on a space judged the space and every page within it. [Decision 0034](0034-a-rule-for-the-pages-within.md) added `each` for the pages within, so one condition could be written two ways with two meanings.
- The card `a-keeper-binds-itself` was walked a third time with a small model. In two of five draws the model wrote `page.cash >= 20` on the den, meaning the den's own cash, the cleanest statement of the limit. Because a plain rule was still handed down, every payment within the den was refused for lacking `cash`.
- [Decision 0033](0033-ahead-or-different-with-each-step.md) asks that a rule mean what it says where it is written. Now that `each` says "the pages within", the old double meaning of a plain rule only causes this failure.

## Decision

A plain rule applies to the page that carries it and to no other page. Only an `each` rule applies to the pages within a space, at any depth, and never to the space itself.

The walk of rules judges the page's own plain rules and the `each` rules of every space above it. Leaving a space ([decision 0022](0022-leaving-a-space-is-a-write-the-space-can-refuse.md)) is judged by the `each` rules of the spaces left and by the page's own plain rules. A refusal still names the condition and the space it came from.

The fixed statement of an ask that writes pages says that a rule can read the space's fields as `space.FIELD` as well as the page's as `page.FIELD`. This amends 0034: the old behaviour is removed, with no alias.

## Consequences

- A space can state an invariant of its own state in one plain line, and a whole kind of act within it in one `each` line.
- Every rule written to bind members is now an `each` rule: the `lemonade` and `team` examples, the stopped vault in the package (rebuilt by `scripts/build_stopped_vault.py`), the guide commands and the tests and playbooks that relied on a plain rule being handed down. The golden vault in `tests/golden/` holds a plain rule only as stored text that is read and verified, never judged, so it is unchanged.
- `conky assimilate` counts a page's rules as its own plain rules plus the `each` rules of the spaces above it.
- A vault written before this change that relied on a plain rule binding its members stops binding them. The pages are unchanged, and the rule is changed to `each` by an ordinary write.
