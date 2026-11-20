---
kind: decision
title: A rule is proven when it is written
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.proven
---

# 0038 A rule is proven when it is written

## Context

- Before `each` existed, every rule on a space was evaluated against the space page itself when written, so a syntax error or an unknown name in any rule was refused at once. An `each` rule is not evaluated against the page that carries it, so the guarantee was lost for it: `each: bogus.x > 1` was accepted and failed on a later write.
- The cost showed in a trial. Five of five draws of a small model wrote `space.cash >= 20` on a den that has `cash` and no space above it. The refusal said the rule failed to evaluate, with the evaluator's own text, and none of the five recovered on the one retry a refused answer gets.

## Decision

- When a page is written, every rule entry, plain and `each`, and every watch entry's `when` and `set` expressions are parsed. A syntax error is refused with reason `shape`.
- The names an expression may read are fixed by where it is. A rule reads `page`, `space`, `size` and `text`. A watch entry reads those and `other`, `other_text`, `other_size`, `other_name` and `event`. Any other name is refused with reason `shape`, and the reason lists the names allowed. The names are found from the parsed tree, not by evaluation: a name outside a comprehension is a reference, a variable bound by `all`, `exists`, `exists_one`, `map` or `filter` is not. Evaluation would miss a name behind a short-circuit.
- A newly added `each` rule is tried against every page already within the page that carries it, at any depth. If it is false or cannot be evaluated for one, the write is refused with reason `rule`, naming that page. Rules that were already there are not tried again, so a write that changes a field of a space does not re-judge its pages.
- A reason says in plain words which field was read on which thing and, when another thing in scope has a field of that name, names it: `space.cash does not exist here: this page has cash, read it as page.cash`. The evaluator's exception text is no longer shown. The first word of a reason is unchanged.
- `tests/invalid/` holds one small file for each wrong form, and `tests/test_invalid.py` fails if any is accepted.

## Consequences

- A rule that could never be evaluated cannot land. A small model that used the wrong name has the right one in the reason on its one retry.
- Prior art: CEL checks declared identifiers at compile time in cel-go and cel-java. cel-python offers no such check, so the same check is made here on the parse tree.
- A space written together with fields that its members depend on is judged against the fields it had before, since the members are tried against the stored space. A space adds the field first, then the rule.
- A card or a playbook that adds an `each` rule to a space whose members the rule breaks is now refused at that write.
