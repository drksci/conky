---
kind: decision
title: A rule sees who acts, and a name cannot be borrowed
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.name.claimed
  - law.rule.who
  - part.rule.within
---

# 0053 A rule sees who acts, and a name cannot be borrowed

## Context

- Every write is signed, but until now `verify` accepted a commit signed by any listed key whatever name the commit carried, and a rule could not see who was writing. A space could not say "only the owner changes the price" or "staff may write here".
- Decision 0039 made an event something a page can notice, with `kind`, `by`, `reason` and `id`. Decision 0051 made the theatre a page, so a rule on it can speak for the whole vault.
- Prior art: role-based access control for deciding by identity and role; required signed commits with a stated signer for binding a name to a key; trust on first use, as in SSH known hosts, for claiming a name by its first appearance.
- The image is the doorman who checks that the signature in the visitors' book matches the name beside it, and the sign that says "staff only".

## Decision

- A name cannot be borrowed. `verify` requires, for every commit, that the principal whose key signed it is `<author>@conky`, the actor the commit names. A commit signed by one listed name and made as another fails, and the reason names both.
- The signers only grow. A name is claimed by first use. `verify` fails on a commit that changes, reorders or removes an existing line of `keys/allowed_signers`, or lists a name twice. A write by an actor whose listed key differs from the one in the key folder is refused before it is made, with the advice to pass the right key folder.
- `event` is readable in rules, plain and `each`, with the shape a watch sees: `event.kind` is `write`, `event.by` is the actor, `event.reason` is empty and `event.id` is empty, since the commit does not exist yet. A rule reading another field of `event` is refused for shape.
- One new function, `within(NAME, SPACE)`: true when a page called NAME exists and lies within SPACE by any path, including the outermost `theatre` when that page exists, and false otherwise. It is usable wherever `terms` is, and reads the pages that exist when it is evaluated.
- With these a space says who may write: `each: "event.by == 'owner' || !has(page.price)"`, or `each: "within(event.by, 'staff')"`. A reaction is a write by the page that reacted, so `event.by` is that page.
- A refusal reason that reaches a model through the retry note names the rule and the space as before and not the actor.

## Consequences

- Guarantee given up in writing: a vault made before this change in which two names share one key no longer verifies, because a commit by one of them is signed as the other. The remedy is to refound it with a key per name. The packaged stopped vault used by `conky assimilate` was rebuilt for that reason, with one key per name and the same pages, writes and authors, so its commit ids changed.
- Kept: a vault travels alone and verifies with no private key; a refusal is recorded; rules stay pure; the golden vault verifies unchanged.
- What this gives and does not give: within one machine the key folder is the credential, so whoever holds it can act under the names whose keys are in it. What is now impossible is a history in which a write claims a name its signature does not carry.
- Not built: approvals by several signers, key rotation and revocation (a later step, which will replace the rule that a signers line never changes), and private pages.
