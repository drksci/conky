---
kind: decision
title: A page may be within several spaces
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - law.context.down
  - part.space
---

# 0045 A page may be within several spaces

## Context

- A page that is at once a worker on a shift, a tenant and a member of a choir is bound by each of them while it belongs, and sheds each when it leaves. A space hands down its rules ([decision 0036](0036-a-plain-rule-stays-with-its-page.md)), its fields as `space`, and judges leaving ([decision 0022](0022-leaving-a-space-is-a-write-the-space-can-refuse.md)); all of that assumed one space.
- The general case is belonging to more than one group at a time. Nothing new is needed beyond letting `within` name several.
- Prior art, one line each. Directory group membership: an account is in any number of groups, and what each group allows or denies applies together; here every `each` rule applies, so membership only tightens. Mixins and method resolution order: a class takes from several bases and a linearisation (C3) says which wins a name; list order was chosen here over a linearisation because a person writes the order they mean (the first is home) and a distance-then-order rule needs no graph algorithm to explain. Role-based access control: a subject holds several roles and the permissions of each apply ([NIST RBAC, ANSI INCITS 359](https://csrc.nist.gov/projects/role-based-access-control), read 2026-11-21).

## Decision

`within` is a page name or a list of distinct page names. A single name is stored as it is, a list of one is stored as the name, and an empty list means no space. No vault is migrated. A repeated name, an entry that is not a page name and a value that is neither a name nor a list are refused for shape, and the reason in `voice.md` says what to write. A space that does not exist, a page within itself and a list that leads back to the page are refused for rule, as for one name.

- Membership. A page lies within a space when the space is one of its own or lies above one of them, by any path. The graph of spaces may be a DAG.
- Rules. The `each` rules of every space above a page apply, each space judged once however many paths lead to it, and a write is kept only if all hold. A plain rule still applies only to its own page.
- Context. The fields of every space above are merged into `space`. Nearer beats farther. Among a page's own spaces the one listed first beats those listed after, so the first is its home. A space reached by two paths counts at its nearest distance. Spaces at one distance are ordered by the order they are reached, breadth first, following the page's list.
- Joining and leaving. A write that changes `within` is judged by the `each` rules of every space joined and every space left, the left ones against the page as it would be after the write, as well as those it stays in.
- Relations. `on: within` tells every space the written page lies within, by any path, each once. `on: refusal` likewise, by the kept `within` or else the attempted one, list or name.
- Embeds. `![[space#members]]` lists a page under every space it lies within.
- Exports and descriptions show the first space as the page's home and list the rest.
- Answers that write pages. An answer may write a page only with `within` naming the space it writes into or a space inside it, as a name and not a list, and may change only a page whose spaces all lie inside it. It cannot join a page to further spaces in this step. That is a deliberate limit: what a character may join is a larger question than what it may write.

## What the old behaviour guaranteed

- A page had at most one space. Given up in writing.
- The nearest space's field wins. Kept: nearer still beats farther, whatever the order.
- Leaving is judged by the space left. Kept, and extended to every space left.
- A single `within` behaves as before. Kept, held by the existing playbooks passing unchanged and by a test that a list of one equals the name.
- A refusal names the rule and the space it came from. Kept.

## Consequences

- A character joins and leaves a space by writing its own `within`, and the spaces judge it. Nothing new is built for activities, shifts or working sessions.
- Handing reactions down a space is a separate step and is not built.
- The list order carries meaning, so reordering a list is a change of home and is a write.
