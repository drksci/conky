---
kind: decision
title: A page is known by its phrases
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.link.known
---

# 0044 A page is known by its phrases

## Context

- A link is `[[name]]`, typed by whoever writes. People write "Mrs Okafor", not `[[mrs-okafor]]`, so the pages that watch a name by `on: link` and the pages a character is shown by what they link to miss most of what is said about it. The [auto-linking idea](../ideas/auto-linking.md) asks for recognition at the write, with no brackets and no change to the body.
- The index at the back of a book is kept as the book is written: a term, and the places that use it. The general case is recognising a known name in running text.
- Prior art: SKOS gives a concept one preferred label and any number of alternative labels, and a match on any of them is a match on the concept ([SKOS Reference, W3C, section 5, read 2026-11-21](https://www.w3.org/TR/skos-reference/#labels)). Wikis and note tools that auto-link do the same by title and alias. A glossary is the human form. This decision takes the alternative labels, and takes no vocabulary from the others.

## Decision

A page may carry a field `aka`, a list of one or more phrases, each text of at least two characters. It is a field, not a reserved key. It is proven when written: a value that is not a list, an empty list, an empty or one-character phrase or a phrase that is not text is refused for shape, with the sentence in `voice.md` saying what to write.

A phrase is recognised in a text when it occurs as whole words: compared without regard to case, with any run of whitespace standing for one space, and with a trailing `'s` or `’s` allowed after its last word. A letter or digit directly before or after the phrase, apart from that possessive, means it is not recognised. A page's own name is a phrase only when it is listed, so a page called `order` is not linked by every use of the word. A page does not recognise itself.

The pages a page links to are its explicit `[[...]]` links plus every page one of whose phrases its body uses. Nothing is written into the body. A write whose body uses a phrase therefore tells that page's `on: link` watchers at the write itself, in the same chain of events as any other reaction.

Expressions gain one function, `terms(TEXT)`, which gives the sorted names of the pages whose phrases the text uses. It is usable in rules, watch `when` and `set` and in `shows.first`, and it reads the pages that exist when the expression is evaluated. For example `terms(space.heard).filter(t, terms(text).contains(t)).size()` orders members by the terms they share with what was just heard, although they share no ordinary word.

## Purity and cost

Recognition is worked out when asked, from the pages as they are, and nothing is stored, so reading history evaluates nothing and `conky verify` and `conky rebuild` agree on a vault with terms. A page written before a term page existed counts as linking to it as soon as the term page exists. Its watchers are not told late: a watch fires at a write, and there is no later pass.

The phrases are read from the vault once per evaluation, when first needed: once for the links of a write and once for the expressions of a reaction, a rule judgement or an embed. Each phrase is then tried against the text, so a recognition costs the phrases in the vault times the length of the text. A vault with no `aka` pays one read of the pages and no matching. A faster index is derived data and is not built.

## What the old behaviour guaranteed

- A page links only to what its body or text fields name in brackets. Given up in writing: a page also links to the pages whose stated phrases its body uses.
- A body is never changed by linking. Kept: nothing is written to a body.
- Explicit links work as before, and a vault with no `aka` behaves as before. Kept, held by `test_a_vault_with_no_phrases_links_only_by_brackets`.
- A page never reacts to its own write through `on: link`. Kept, held by the playbook `a-text-that-uses-a-term-links-to-its-page`.
- Only the body is read for phrases, as against the body and the text fields for brackets, so a field never links a page by accident.

## Consequences

- Whoever writes a term page, a character or later a faculty, makes every use of the phrase a link from then on, signed as its own work.
- Phrases are not disambiguated: two pages known by the same phrase are both recognised.
- Not built: a background faculty that finds recurring phrases and gives them term pages, a listing of the pages that link to a page, and retroactive notice to watchers.
