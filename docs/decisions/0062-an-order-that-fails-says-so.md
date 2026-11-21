---
kind: decision
title: An order that fails says so
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.embed.proven
---

# 0062 An order that fails says so

## Context

- A space that lists things ordered by distance, nearest first, wrote `shows: {first: "0.0 - page.distance"}`. The write was accepted. Every member then failed to score, with `result of type float cannot be stored`, and the list fell back to name order with no word anywhere.
- Two things were wrong. The first is in the arithmetic. cel-python maps `+`, `-` and `*` to Python's own operators, and its number with a fraction has no methods for them, so two such numbers gave a plain Python value that the runtime does not accept as a result. Division and negation did not have the fault, which is why `page.distance / 2.0` worked and `0.0 - page.distance` did not.
- The second is in the design. [Decision 0042](0042-a-space-shows-what-bears-first.md) put a member that `first` cannot score after the scored ones and refused nothing for it. That treats two cases as one: a member the order is not about, because it lacks a field `first` reads, and an expression that cannot give a number at all. The second case is a mistake in what was written, and it was silent both when written and when read.
- How numbers are already treated: a write takes "text, numbers, booleans, lists and maps" ([rules and reactions](../reference/rules-and-reactions.md#refusals)), a field may hold a number with a fraction, and a `set` value such as `page.distance / 2.0` was already stored as one. Nothing in the reference or the decisions restricts a number to whole numbers.
- Prior art: CEL itself. The standard has `int` and `double` as separate kinds with arithmetic defined on each and no arithmetic between them, and conversion is written out, as in `double(n)`. A spreadsheet that sorts a column puts the cells it cannot read last and marks them.

## Decision

**A number with a fraction is a number everywhere.** `+`, `-`, `*`, `/` and `%` on two numbers of one kind give a number of that kind, in a rule, a `when`, a `set` value and a `first` alike. Nothing new is allowed: the three operators that failed now do what division already did.

**A whole number and a number with a fraction do not mix**, on either side, as the standard says. The library's operators took the pair on one side and refused it on the other, and for division gave a whole number cut short; every such pair is now an evaluation error. `double(page.steps) - 0.5` says it.

**What can be known when `shows` is written is refused then**, with reason `shape`:

- an unknown key, a `most` outside its range, a `first` that is not text, does not parse or reads a name other than `page`, `space` and `text` (all as before);
- new: a `first` that reads members already within the space and gives none of them a number. It is tried on every page within the space at any depth. A member is read by `first` when it has every field `first` reads off `page`, the same test that says whether an `each` rule is about a page ([decision 0038](0038-a-rule-is-proven-when-written.md)). If at least one member is read and no member at all gets a number, the write is refused, and the reason names one such member and says what to write instead.

**What can only be known when the list is read lowers the result and says so.** A member that `first` reads and gives no number for, because the arithmetic fails for that member's values or its value is text, still comes after the scored ones. The list then ends with one more line, after the count of what is not shown:

```
(2 not ordered: first gives no number for ledger, till)
```

It names at most three members and counts the rest. The line is part of the resolved text, so it is in the record of an ask that embedded the list and in what `conky read` prints. Nothing is refused and nothing is stored.

**A member that lacks a field `first` reads is passed by in silence**, after the scored ones, as before. The order is not about it.

A `first` written before the space has members, or one that reads a field no member has yet, is accepted: there is nothing to try it on. Its failures are of the second kind.

## What the old behaviour guaranteed

- A write of `shows` was judged from the written value alone, so it could not be refused because of another page. Given up: a `first` that scores none of the members it reads is refused. A single member with an odd value does not refuse it, since one scored member is enough.
- The lines of an embedded list were one per member and at most one count line. Given up for a list whose `first` fails for a member it reads: one more line follows. A list with no `shows`, or whose `first` scores every member it reads, is unchanged, held by `test_a_space_that_does_not_show_lists_by_name_at_the_cap` and `test_a_space_that_shows_orders_by_first_and_cuts_to_most`.
- A member `first` cannot score comes after the scored, in name order. Kept, held by `test_a_member_first_cannot_score_comes_after_the_scored`.
- Reading stores nothing. Kept, held by `test_reading_a_space_that_shows_writes_nothing`.
- By accident: a whole number on the left of `/` or `%` with a fraction on the right gave a whole number, cut short: `page.steps / 2.0` with three steps gave `1`. That is now an error. Given up, since the answer was wrong. With `+`, `-` and `*` no mixed expression gave a result before, on either side, so none stops working.

## Consequences

- An order by distance, by price or by any other number with a fraction works.
- A `first` that can never work does not land where there is anything to try it on, and one that fails later is visible to whoever is shown the list, a model included.
- Writing `shows` on a space now costs one evaluation for each page within it.
- Not built: the reason does not say which part of `first` failed, and the line in the list does not say why a member got no number. A `first` is not tried again when a member is written, so a member written later can make an accepted `first` fail; that is the line in the list.
