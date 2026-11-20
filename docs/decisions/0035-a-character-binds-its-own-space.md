---
kind: decision
title: A character binds its own space
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.rule.tighten
  - law.reach.down
  - part.space
---

# 0035 A character binds its own space

## Context

- Decision 0034 added a rule entry for every page within a space, spelled `within: CONDITION`. The card `a-keeper-binds-itself` was walked twice with a small model, five draws each time, with the rule form named in the fixed statement. In all five draws of the second walk the model tried to state a standing rule, and none of them succeeded.
- Two draws wrote `within: CONDITION` as a field at the top of a page. The same word, one line above in the example, means that the page lies inside a space, so the model read it as a membership field. One draw wrote the rule on the space itself and was refused, because an answer may not write the space it writes into. One wrote it on a page that lacks the field the rule reads. One wrote it in plain words.
- The natural home for a rule about every page in a space is the space. An answer could not write there.
- Prior art: a folder-level policy that covers what lies inside it is the usual home of an inherited constraint in access and policy systems, and the one who administers the folder writes it. Here the writer is a character that works in the space.

## Decision

The mapping form of a rule entry has the single key `each`, in place of `within`. There is no alias: the old key is a shape refusal like any other mapping.

An answer that is pages may add rule entries to the space it writes into. A page block that names that space is allowed if and only if it holds `rules:` and nothing else: no other field, no `within`, no body. Its entries are added after the rules the space has. An entry already there is kept once, so a duplicate adds nothing. Nothing the space has can be removed or changed by this path, and a block that tries anything else to that page is refused with reason `limit`, as before.

The write is an ordinary signed write by the asker. It is judged by the rules of the spaces above the space, and recorded like any other write.

The fixed statement tells the character this in one clause and shows it in an example, so the word `within` appears in it only for membership.

## Consequences

- Decision 0029 says a character writes only inside the space it was given, and its reference text says the space page itself is outside. That stays true for every field, the body and `within`. The one addition is rules, and it follows the second law: a space's rules only tighten, because an entry can be added by this path and never removed. A character that works in a space can bind that space, which every page within it, including the character, must then satisfy, so it can bind itself. It cannot loosen a space or free itself from one, and it cannot reach a space above, which stays with whoever wrote it. The 0029 sentence that the rules of the outermost space stay with people holds when the outermost space is not one an answer writes into.
- A character can now leave itself unable to write, by adding a rule it fails. The refusal is recorded, and a person can undo the change in the history.
- Whether a small model states an `each` rule on the den is a forecast on the card `a-keeper-binds-itself`, not yet drawn. The card now writes the breaking payment directly within the den, so a rule on a page nested under the den does not refuse it, and the draw shows where the model puts the rule.
- Playbooks: the checks `within_rules` and `within_ruled` are now `each_rules` and `each_ruled`. `each_rules` counts the space itself as well as the pages within it.
