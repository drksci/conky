---
kind: decision
title: A space hands down reactions
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.reflex.down
  - law.reflex.free
  - part.space
---

# 0056 A space hands down reactions

## Context

- A space handed down its rules ([decision 0034](0034-a-rule-for-the-pages-within.md)), its fields as `space` ([decision 0045](0045-a-page-may-be-within-several-spaces.md)) and its words ([decision 0047](0047-a-character-is-shown-what-its-spaces-say.md)). A habit of a whole room still had to be written on every member, so a house custom such as "everything here is stamped when the bell rings" was copied page by page.
- A character may give its space reflexes ([decision 0041](0041-a-character-gives-its-space-reflexes.md)), and the theatre is a page and the outermost space ([decision 0051](0051-the-theatre-is-a-page.md)).
- Prior art: a default inherited down a directory tree, a mixin whose methods every instance has, the house rules of a building that bind everyone inside it.
- The image is the custom of the house: everyone who lives here takes their shoes off at the door, and nobody was told one by one.

## Decision

- A space's `watch` list may hold `each: ENTRY`, where ENTRY is an ordinary watch entry with `on`, `when` and `set`. Every page within the space has it as if it carried ENTRY itself, at any depth and by any path, every page when it is on the theatre. `page` is the member, and `space`, `event`, `other` and `text` are as for any entry of the member. It is the same word as for a rule, with the same meaning: for the pages within, not for the space.
- The space does not get it. A page gets the entry of a space once however many paths lead to it.
- A page reacts by its own entries first, in the order written, then by the entries handed down from the nearest space outward, in the order `conky.page.above` gives, the theatre last.
- `on` means what it means for the member: a page name, or `within`, `link`, `refusal` relative to the member. No word names the member itself, since a measure watches itself by naming its own page and a space cannot name a page it does not know. A handed-down entry therefore cannot yet say "when this page itself is written". The gap is recorded here and no word is added: a character that needs it writes the entry on the member.
- Like an `each` rule, the entry speaks only of members that have the fields it reads off `page`. For a member without one it does nothing and nothing is refused.
- Only `set` is handed down. An `each` entry with `ask` is refused for `limit`, with the reason that asking is not handed down because nothing meters it yet. It is the wall of decision 0041, and an answer that gives its space an `each` entry meets it too. The wall stays until budgets exist.
- Cost: one evaluation of each handed-down entry per member per event, and one write per member whose `when` holds. The depth limit of 12 applies to the chain as to any reaction. A test settles a fan-out of twenty members.
- In the history the reaction is the member's write, signed by the member, with `Cause` the commit it answered. A reader finds the entry that fired in the `watch` of the spaces the member lies within.

## What the old behaviour guaranteed

- A watch entry without `each` is the page's own and binds no other page. Kept, under `test_a_watch_entry_without_each_is_the_pages_own_and_binds_no_other`.
- A reaction obeys the depth limit and ends in `cycle`. Kept for handed-down entries, under `test_a_handed_down_entry_that_feeds_itself_stops_at_the_depth_limit`.
- Reading evaluates nothing, and `verify` and `rebuild` agree. Kept, under `test_every_page_within_a_space_reacts_as_if_it_carried_the_entry`.
- A space spends nothing on its own. Kept: an `ask` cannot be handed down.
- A watch entry's keys were `on`, `when`, `set` and `ask`. Given up in writing: the stored form may also be a mapping with the one key `each`, and every reader of `watch` takes the entry as the member's own only when it has no `each`.

## Consequences

- A room can have a habit in one entry: a character may write it to its space by its binding, with `set` only.
- Roadmap step R22 is built in all its parts: rules, context, reactions and several spaces. The fields of a space are not shown as prose; a space says what it means in its words, which are shown.
- Handing down asks waits for budgets for background work.
