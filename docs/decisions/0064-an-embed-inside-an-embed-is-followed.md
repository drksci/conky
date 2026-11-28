---
kind: decision
title: An embed inside an embedded page is followed
status: accepted
date: 2026-11-28
source: maintainers
arch:
  covers:
  - law.embed.followed
---

# 0064 An embed inside an embedded page is followed

## Context

- A prompt can embed a page, `![[senses]]`, and that page's body can embed a field of another, `![[ear#heard]]`. Until now the inner embed reached the model as the raw text `![[ear#heard]]`, because an embedded body was inserted as stored and not resolved again ([vault-format](../reference/vault-format.md)). Nothing tested that sentence.
- A character composed from pages needs one page to gather what other pages wrote, so that a prompt stays one line. The only way round it was to copy the text by hand into the page that embeds it.
- Nothing looped only because nothing was followed. Following embeds makes a loop possible, and a page may be written before what it embeds exists, so a loop cannot be refused when it is written.

## The walk

1. **The image.** A footnote that points to another footnote. A reader follows a few, and a printer sets a limit and prints "see above" where the trail comes back round.
2. **The general case.** Substitution that is applied to its own result, with a bound.
3. **Existing words.** An embed, a body, a field, a stage direction from `voice.md`, a constant declared with `arch.constant`. Nothing new in the vocabulary.
4. **The natural gesture.** Writing `![[ear#heard]]` in a page and expecting the words, wherever the page is shown.
5. **Par.** MediaWiki expands templates inside templates, writes "Template loop detected" in the page where the loop is met, and keeps limits on expansion depth ([Help:Templates](https://www.mediawiki.org/wiki/Help:Templates) and the page it names on expansion depth, read 2026-11-28). The C preprocessor limits the nesting of `#include` files ([GCC, implementation limits](https://gcc.gnu.org/onlinedocs/cpp/Implementation-limits.html), read 2026-11-28). Both follow nested inclusion, bound it, and say in the output where it was cut. Obsidian and TiddlyWiki have the same transclusion, listed in [pkms](../research/pkms.md); their depth behaviour was not read and nothing is claimed from it.
6. **Who does it.** A character cannot add this for itself: it is how the runtime reads an embed.
7. **The trial.** The card `a-clerk-reads-through-its-senses`: a clerk whose prompt embeds one page that embeds a field of another. Forecast 5 of 5; a miss would be the clerk reading the fact and giving another shelf. It was drawn with a stand-in that prints the prompt back, and not with a live model.
8. **How it is seen.** `conky read` shows the words, and the `Read` trailer in `conky log` names every page that was shown.
9. **The smallest step.** Built now: following, the limit, the loop line. Waiting: nothing.

Said once more: an embed's words may hold embeds, followed a few deep. That is shorter than the request, and adds no word.

## Decision

- Embeds are followed by default, on read, in a prompt and in `otherwise`. There is no switch.
- The limit is `EMBED_DEPTH`, 3, one constant. An embed in the prompt or the page read is at depth 1, one in the text it brought in at depth 2. An embed past the limit is replaced by a stage direction that names the page and says embeds are followed only so deep.
- An embed of a page and part (`a`, `a#x`) already being resolved on the way down is replaced by a stage direction that names the page and says it is already shown above. Another field of the same page is not a loop. Nothing is refused when it is written; the loop is cut on reading and said in what is shown, as [decision 0062](0062-an-order-that-fails-says-so.md) does for an order that fails.
- The text of `#members` and `#context` is shown as written. An embed of them written in followed text is resolved like any other, and a nested `![[PAGE#asks]]` reads as at the top.
- `Read` names each page whose words were shown at any depth, once, in order of first use, outer before inner. A page cut for depth or for a loop is not named for that embed.
- Stored pages keep their embed text. Only reading resolves.

## What the old behaviour guaranteed

- A text whose embedded pages hold no embeds resolves byte for byte as before, so the cache key of [decision 0030](0030-pay-once.md) and the settled marker are unchanged for it. Kept under a test with a fixed expected string.
- Nothing could loop. Given up in the sense that a loop can now be written; kept in effect by the loop line and the depth limit, each under a test.
- Stored pages are the source, and reading changes nothing. Kept: a read test checks the stored file still holds the embed.
- An embed shows words and nothing about who wrote them. Kept for nested embeds under `law.embed.anonymous`.

## Consequences

- A prompt with a nested embed now changes, so a question that held one is asked afresh once.
- A model reads the words of a page that gathers other pages, and the prompt stays one line.
- A text that quotes embed syntax inside an embedded page now has it resolved. There is no escape; a page that must show the syntax holds it where it is not embedded.
- No live model has read a nested embed. The card was drawn with a stand-in only.
