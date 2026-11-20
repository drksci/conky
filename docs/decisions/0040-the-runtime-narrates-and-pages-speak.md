---
kind: decision
title: The runtime narrates and pages speak
status: accepted
date: 2026-11-20
source: maintainers
arch:
  covers:
  - law.embed.anonymous
---

# 0040 The runtime narrates and pages speak

## Context

- The runtime's own lines to a model were scattered through the code and read as mechanism: a header written as `=== page: <name> ===`, a rule described as a CEL condition on `page.FIELD`, a note that began "Your last answer was refused". In walked trials of this project a model answered in the register it was spoken to in, so mechanism wording produced mechanism answers. This is an observation from this project's own trials, not a citation.
- A character should not be able to tell whether a neighbour is a person or a model. Everything is somebody.
- The runtime is nobody. If it says "I" or "you", a model reads a speaker that does not exist, and cannot tell the world's own events from something a page said.

Prior art: style guides for interface text (a message says what happened and what to do next, in short plain sentences), and the stage direction of a play script, which tells what happens on stage and is plainly not a character's line.

## Decision

- Every line the runtime puts in front of a model lives in `src/conky/voice.md`, one section per line, read by `voice.line(key, **values)`. No second copy stays in code. A section holds the words; the form is decided in one place, `voice.told`, which wraps a line as a stage direction in Markdown italics. A viewer may later draw it as a chip, and only that function changes.
- The runtime narrates in the third person and names pages by name. It never says "I" or "you", so every "I" and "you" a model reads comes from somebody, a page, and the world's own events are plainly told apart from speech. The page instruction is narration too: it says what the page can do, shows the worked example of a page block and of an `each` rule, and says what the page cannot do.
- The plain line for a program standing in for a model is third person as well and is not wrapped, because the program takes it as its instructions.
- Refusal reasons keep their leading kind word (`rule:`, `shape:`, `limit:`), which code and tests read. Only their sentences moved to the page, and a reason that reaches a model through the note is ended with a full stop so a sentence can follow it.
- Nothing a model is shown says whether another page was written by a person or a model. An embed shows a page's fields, body and the members line, and none of the `Model`, `Model-Name` or provider marks, which stay in history and in the command line output for people. No leak was found when this was checked, and a test now holds the property.
- The block markers and the parsing do not change.

## What the old behaviour guaranteed

- The author's question is the last thing the model reads: the instruction still comes first and the refusal note still comes after the prompt. Held by `test_the_instruction_comes_before_the_prompt_in_what_is_sent_and_recorded` and `test_a_retried_answer_is_a_refusal_then_a_write_caused_by_it`.
- The model learns the block form, the `each` rule, that a rule can read the page and the space, and the limits. Held by `test_the_instruction_example_is_a_page_the_parser_cuts` and the playbooks.
- Every sentence the code can say to a model exists on the page and every sentence on the page is used. Held by `test_every_line_the_runtime_says_to_a_model_is_on_the_voice_page_and_used`.
- The cache key includes the prompt, so answers cached under the old lines no longer match. That is correct and needs no migration.

## Consequences

- The house style runs on `voice.md` in `scripts/check`.
- The scripted stand-in used by the benchmark recognises the new first sentence of the instruction.
- Wording is a bet that small models still answer well: the walked cards under `bench/cards/` are the test, and none was rerun live for this change.
