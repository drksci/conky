---
kind: decision
title: The theatre is a page, the outermost space
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - law.context.down
  - law.embed.context
  - part.space
---

# 0051 The theatre is a page, the outermost space

## Context

- Decision 0050 named the theatre as the outermost thing everything in it lives in, and expected it to become a page. Until now a vault had no outermost space: a page that named no space was bound by no rule, told nothing and heard by nobody, and a rule meant for a whole vault had to be written into every page's `within`.
- Decision 0045 gave a page several spaces and one ordering of the spaces above it. Decision 0047 let a character be shown what those spaces say. Both already say everything an outermost space needs, except that nothing was at the far end.
- Prior art: an organisation-level policy at the root of a directory or cloud account binds every project beneath it and can only be tightened further down; the root of a namespace holds names for everything inside it; the house rules on the wall of a building apply to every room.
- The image is the building itself. Every company, stage and prop is inside it, and the rules on the wall are for all of them.

## Decision

- The theatre is not a new kind of thing. It is a page, named `theatre`, and a space. When a vault has that page, every other page lies within it implicitly, at the far end of its order of spaces: after every space it names and every space above those. A page that names no space has the theatre as its only space. When the vault has no such page nothing changes.
- This is one change to the one function that orders the spaces above a page (`conky.page.above`). Everything that already reads that order follows: the `each` rules of the theatre judge every write to every other page and a refusal names the theatre as the space the rule came from; its fields are context at the lowest precedence; its body is the last block of `![[page#context]]`; `on: within` and `on: refusal` entries on the theatre hear every write and refusal, each once; `![[theatre#members]]` lists every other page. A plain rule on the theatre binds only the theatre page, as for any page.
- The theatre lies within nothing. Writing `within` on it is refused for shape, with a reason that says the theatre is the outermost space. Naming `theatre` in another page's `within` is allowed and changes nothing: it is listed once, and last. A write that changes a page's `within` neither joins nor leaves the theatre, so its rules are judged once, as a space the page stays in.
- The cap on `![[page#context]]` cuts the middle. When the context has more spaces with words than the cap and the theatre speaks, the nearer spaces are shown up to the cap less one, the count line says how many were left out, and the theatre is still the last block. The house rules are read whatever the nearer spaces say.
- An answer that writes pages (`writes: S`) must still name `S` in `within` of each page it writes, and `S` named as `theatre` has to be named explicitly: the implicit membership does not count for that limit, so an answer cannot make a page by leaving `within` out. The theatre's rules judge those pages like any other.
- An answer with `writes: theatre` may add rules and reflex watch entries to the theatre, by the limits decision 0035 and decision 0041 already set. This lets a character tighten the whole house. It can never loosen it, because an entry can be added by this path and never removed.
- Name and identity. The theatre page may carry a field `name`, a valid page name: the theatre's short name, which travels with the vault. The name is the one in `marionette.md`, else the theatre page's `name`, else the vault folder's name. The theatre's identity is the id of the vault's first commit, which every clone shares; its short form is the first eight characters. `conky theatre` prints it and the full name `<name>-<short id>.<domain>`. A vault with no commit yet prints the name without the suffix and says the identity appears with the first write.

## Consequences

- Property audit. Old guarantee: a page that names no space is bound by no space's rules, and a vault has no outermost space. It changes only for a vault that has a `theatre` page, where every page is bound by that page's `each` rules. Kept and tested: a vault without the page is unchanged; rules only tighten; the nearest space still wins for context; a plain rule stays with its own page; `verify` and `rebuild` agree.
- Nothing is stored twice: the membership is not written into any page, so removing the `theatre` page removes the theatre and every page is as it was.
- The full name of a theatre now depends on the history, so it changes by one fixed suffix at the first write and never again.
- Not built: infrastructure within the theatre, supervision and letters between theatres. The domain and the full name still have no consumer beyond the printout.
- Whoever keeps the theatre writes its page. Nothing exists until they do.
