---
kind: reference
title: What the runtime says to a model
status: current
date: 2026-11-20
source: maintainers
---

# What the runtime says to a model

Every line the runtime itself puts in front of a model is on this page, and nowhere else. Each section is one line, named by its heading. The runtime reads a section by name, fills in the words in braces and drops the fences around a worked example.

The runtime is nobody, so it never says "I" or "you". It narrates in the third person and names pages by name, and the code wraps each narrated line as a stage direction. Speech, with its "I" and "you", comes only from pages. A model answers in the voice it is spoken to in, so the lines are short and plain, as a person would tell them.

## page-keeps

{page} can keep pages in {space}. Whatever {page} writes outside a page is its reply. A page is kept when it is written like this:

## page-example

```
=== page: <name> ===
---
within: {space}
---
what is worth keeping
=== end ===
```

## page-rule

A page can be a note. It can also carry a rule that must stay true from now on. A rule is a line under `rules:` that says when the page is fine. It reads the page as page.FIELD and the space as space.FIELD.

## page-each

To bind every page in {space} but not {space} itself, or to have {space} count what it turns away, {space} gets `each` rules and `watch` entries and nothing else. A watch entry sets a field when something happens. It is written like this:

## page-each-example

```
=== page: {space} ===
---
rules:
  - each: page.FIELD < 50
watch:
  - on: refusal
    when: "true"
    set:
      FIELD: page.FIELD + 1
---
=== end ===
```

## page-shown

Each time {page} is asked, it is shown what {space} holds, so it sees what it kept.

## page-limits

{page} cannot write anywhere else. Writing nothing more is fine.

## plain

The prompt is all there is. No tools or files exist to consult, and nothing about where the program runs bears on the answer. The answer is plain text.

## retry

{page}'s last answer was turned away: {reason} {page} may answer again so that it holds.

## page-header

The header {shown} does not name a page. A header reads `=== page: <name> ===`, with a name of lowercase letters, digits, dashes and underscores.

## event-field

event has no field {name} here: it has {keys}. Read one of those, as in event.by.

## rule-shape

A rule is a condition written as text, or a mapping with the one key each whose value is a condition written as text. This one is {entry}.

## rule-words

A rule is a condition, and words after // say what to do instead when it is false, as in page.cups <= 50 // Sell 50 cups at most. This one is {entry}: write the condition first and the words after the //, or leave the // out.

## watch-shape

A watch entry needs on (page name, within, link or refusal), when (text) and either set (field: text) or ask (prompt, with into or writes or both, and optional provider and otherwise).

## each-watch-shape

A watch entry for the pages within a space is a mapping with the one key each, whose value is an ordinary watch entry with on, when and set. It cannot hold another each.

## each-watch-ask

A space hands down reactions that set fields, not asks, because nothing meters an ask yet. Replace the ask in the each entry on {space} with a set, or put the ask on the page that should ask.

## within-shape

A page says which spaces it is within with the name of one space or with a list of names, as in within: [den, choir]. Write within as a page name or a list of page names, or leave it out.

## within-entry

Each entry of within is the name of a page, and {entry} is not one. Write the names of the spaces as a list, as in within: [den, choir].

## within-repeat

A space is named once in within. Write each space of the list one time, the first as the home.

## breach-several

Page {name} is written by an answer into {space}, so within is the name {space} or a space inside it, and not a list: an answer cannot join a page to further spaces.

## theatre-within

The theatre is the outermost space, so the page named theatre lies within nothing. Leave within out of it.

## theatre-name

The theatre's name is {name}: write name as a page name, lower-case letters, digits, - and _, such as lemon.

## members-name

The name members is taken: it lists the pages within a space. Another name is needed.

## context-name

The name context is taken: it shows what the spaces above a page say. Another name is needed.

## budget-shape

A page says how often it may ask a model with a mapping that has the key {keys}, as in budget: {{asks: 5}}. Write asks as a whole number of zero or more, and use no other key.

## budget-spent

Page {page} has made all {asks} asks that the budget of {holder} allows, so no model was asked. Write the budget of {holder} again to refill it.

## budget-bound

Page {name} is written by an answer into {space}, so it cannot set a budget: leave a budget to the person who keeps the space.

## asks-left

{left} of {asks} asks left

## shows-shape

A space says what it shows with a mapping that has the keys {keys}, as in shows: {{most: 5, first: "text.size()"}}. Use only those keys.

## shows-most

The most a space shows is a whole number from 1 to {cap}. Write most with a number in that range, or leave it out to show {cap}.

## shows-first

The first of a space is an expression that gives a number for each member, and it can read page, space and text only: {reason}

## shows-scores

The first of {space} reads the pages within {space} and gives none of them a number, {name} for one. It must give a number for each page it reads. A whole number and a number with a fraction do not mix: write double(page.FIELD) to make a whole number one with a fraction, and double(page.FIELD) or int(page.FIELD) to read a number out of text.

## shows-unordered

({count} not ordered: first gives no number for {names})

## embed-depth

{page} is not shown here: embeds are followed only {cap} deep.

## embed-loop

{page} is already shown above, so it is not shown again here.

## model-shape

A provider page of `api: command` names its model with text that is not empty. Write model as the model's name, or leave it out.

## effort-shape

A provider page of `api: command` names its effort with one plain word of letters, digits and hyphens, as in effort: low. Write effort as one such word, or leave it out.

## effort-levels

The program {command} accepts the efforts {levels}. Write effort as one of them, or leave it out.

## effort-not-command

Only a provider page of `api: command` has an effort, because only a program is told one. Remove effort from this page, or write api: command and the command's name.

## aka-shape

A page says what it is known as with a list of phrases of at least {least} characters each, as in aka: ["Mrs Okafor", "the landlady"]. Write aka as a list with at least one phrase, or leave it out.

## missing-elsewhere

{root}.{name} does not exist here: {where} has {name}, read it as {other}.{name}

## missing-guard

{root}.{name} does not exist here: test for it first, as has({root}.{name})

## missing-unknown

This rule could not be worked out for this page.
