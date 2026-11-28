---
kind: reference
title: Rules and reactions
status: current
date: 2026-11-20
source: maintainers
---

# Rules and reactions

This page specifies how a write is checked, how pages react to each other and how a measure is built from the same parts. The stored format is in [vault format](vault-format.md).

## Expressions

Rules, watch conditions and watch values are CEL (Common Expression Language) expressions, evaluated with the cel-python package ([decision 0005](../decisions/0005-rules-in-cel.md)). They are pure: they see values and return a value, with no clock, randomness or input and output.

A rule or a `when` condition holds only if it evaluates to the boolean `true`. Any other result, including a non-boolean, counts as false. An expression that fails to parse or evaluate is refused under its own reason ([Refusals](#refusals)).

### What an expression costs

An expression is read from left to right and stops as soon as its answer is known. `a || b` does not evaluate `b` when `a` is true, and `a && b` does not evaluate `b` when `a` is false. `list.exists(x, ...)` stops at the first item that gives true, and `list.all(x, ...)` at the first that gives false. A rule over a list therefore costs at most one evaluation of its inner expression for each item.

The answers are the ones the CEL standard gives. `true` beside an error is still `true` under `||`, on either side, and `false` beside an error is still `false` under `&&`. Where nothing decides, an error, or a value that is neither true nor false, makes the whole expression an error. An error is carried as it is: the reason for a list in which every item fails is as short as the reason for one item.

`+` joins two texts or two lists into a text or a list like any other, so `('\n' + page.can + '\n').contains('\nb\n')` works and a `set` value can be a joined text.

A number is whole or has a fraction, and arithmetic keeps the kind: `0.0 - page.distance` is a number with a fraction and `page.steps + 1` a whole one. The two kinds do not mix in `+`, `-`, `*`, `/` and `%`, on either side, as in the CEL standard; `double(page.steps) - 0.5` turns the whole number first, and `int(...)` goes the other way. A comparison such as `page.steps > 0.5` may mix them ([decision 0062](../decisions/0062-an-order-that-fails-says-so.md)).

cel-python alone does none of this: it evaluates both sides and every item first, quotes both errors inside a new one whenever two meet, which doubles the message for each item of a list, gives joined text and the sum, difference or product of two numbers with a fraction back as values with no methods that cannot be stored, and takes a whole number beside a fraction on one side only, with a wrong answer for division. The runtime replaces those four folds and the five arithmetic functions ([`rules.py`](../../src/conky/rules.py)).

### A rule that says why

A rule may carry words after `//`, the comment of the rule language, saying what to do instead:

```yaml
rules:
  - each: "!has(page.cups) || page.cups <= 50 // Sell 50 cups at most."
```

When the rule is false the refusal gives those words where it would have quoted the rule: `rule: Sell 50 cups at most. (from stand)`. The same reason is recorded on the refused commit and shown to a model in the note before its one retry ([decision 0063](../decisions/0063-a-rule-says-why-in-its-own-words.md)). A rule with no words is refused as `rule: EXPRESSION (from stand) is false`.

- Remarks on several lines are joined in order with a space. A `//` inside a text literal, as in `'http://'`, is part of the text.
- A rule that cannot be evaluated is still shown whole, remark included, with what went wrong: the words say what to do when the rule is false.
- A rule with `//` and no words after it, or with words and no condition, is refused when written with reason `shape`.
- Only rules are read this way. A remark in a watch `when`, a `set` value or a `first` is a comment.
- Not built: the instruction a model is given for writing pages does not teach the form.

### Text functions

An expression can take text apart with these functions. All but `captures` and `capturesAll` take their names and shapes from the strings extension of the CEL project ([cel-go `ext/README.md`](https://github.com/google/cel-go/blob/master/ext/README.md#strings), read 2026-11-20). Each can be called as a method (`text.split(',')`) or as a function (`split(text, ',')`). Positions count characters from zero.

| Function | Gives | Example |
|---|---|---|
| `split(text, sep)`, `split(text, sep, limit)` | A list of text. A limit of 0 gives an empty list. | `'a,b,c'.split(',')` is `['a', 'b', 'c']` |
| `substring(text, start)`, `substring(text, start, end)` | The characters from `start` up to `end`. A position out of range is an error. | `'tacocat'.substring(0, 4)` is `'taco'` |
| `indexOf(text, find)`, `indexOf(text, find, start)` | The position of the first match from `start`, or -1. | `'hello mellow'.indexOf('ello', 2)` is `7` |
| `trim(text)` | The text without leading and trailing whitespace. | `'  x '.trim()` is `'x'` |
| `lowerAscii(text)` | The text with ASCII letters in lower case. | `'TacoCÆt'.lowerAscii()` is `'tacocÆt'` |
| `replace(text, find, by)`, `replace(text, find, by, limit)` | The text with matches replaced. A limit of 0 replaces none. | `'hello hello'.replace('he', 'we', 1)` is `'wello hello'` |
| `join(list)`, `join(list, sep)` | The list of text as one text. | `['a', 'b'].join('/')` is `'a/b'` |
| `captures(text, pattern)` | The groups of the first match of a Python regular expression as a list of text, or the whole match when the pattern has no group, or an empty list when it does not match. Not in the standard. | `'x=1 y=2'.captures('x=(\\d+) y=(\\d+)')` is `['1', '2']` |
| `capturesAll(text, pattern)` | The first group of every match of a Python regular expression as a list of text, or the whole match when the pattern has no group, or an empty list when nothing matches. Not in the standard. | `'**a** and **b**'.capturesAll('\\*\\*(.+?)\\*\\*')` is `['a', 'b']` |

One more function reads the vault. `terms(text)` gives the sorted names of the pages whose `aka` phrases the text uses, as a list of text ([decision 0044](../decisions/0044-a-page-is-known-by-its-phrases.md)). It is usable in rules, in watch `when` and `set` and in `shows.first`, and it reads the pages that exist when the expression is evaluated. So does `within(name, space)`, which is true when the page `name` exists and lies within `space` ([Who may write](#who-may-write)). A phrase is recognised as whole words, without regard to case, with runs of whitespace as one space and a trailing `'s` allowed. `terms(space.heard).filter(t, terms(text).contains(t)).size()` is how many terms a member shares with what a space heard.

The standard has no `captures`. Its regular-expression extension has `regex.extract` and `regex.extractAll`, which need optional values, allow one group and carry a namespaced name that cel-python cannot register as a method, so `captures` and `capturesAll` stand in until a need for the standard form is shown. The standard `int('12')` and `double('1.5')` already turn captured text into a number, so `int(line.captures('n=(\\d+)')[0])` reads a number out of a line. A pattern that does not match gives an empty list, and indexing it is an evaluation error, so a rule that reads such a number refuses a line without one.

Every function is pure. Text over 65536 characters, a result over 65536 characters, or a pattern over 256 characters is an evaluation error, handled like any other failing expression ([Refusals](#refusals)). The limits bound the cost of a call but do not make every pattern fast: a pattern can still backtrack for a long time on an input under the limit.

## Variables in scope

| Where | Name | Meaning |
|---|---|---|
| Rule | `page` | The fields of the page as it would be after the write. Reserved keys are not fields. |
| Rule | `space` | The fields handed down by the spaces the page is within, nearest winning (see [Context from spaces](#context-from-spaces)). |
| Rule | `size` | The byte length of the serialised page as it would be after the write. |
| Rule | `text` | The body of the page as it would be after the write, empty when the page has none. |
| Rule | `event` | The write being judged, with the fields a watch sees: `kind` is `write`, `by` is the actor, `reason` is empty text and `id` is empty text, because the commit does not exist yet. |
| Rule | `asks` | The asks of the page, `asks.spent` and `asks.left`, as they stand before the write (see [A budget](#a-budget)). |
| Watch | `page` | The fields of the watching page as it is now. |
| Watch | `space` | The same, for the watching page. |
| Watch | `size` | The byte length of the watching page as it is now. |
| Watch | `text` | The body of the watching page as it is now. |
| Watch | `other_text` | The body of the page that was just written. |
| Watch | `other` | The fields of the page that was just written. |
| Watch | `other_size` | The byte length of the page that was just written. |
| Watch | `other_name` | The name of the page that was just written. |
| Watch | `asks` | `asks.spent` and `asks.left` of the watching page. |
| Watch | `event` | A map describing the event being reacted to, for every kind of watch. |
| Watch | `event.id` | The id of the commit being reacted to. A case can keep it in a field to mark what it has met, then test `page.met != event.id`. |
| Watch | `event.kind` | `write` for a kept write, `refused` for a refusal, the words of the `Kind` trailer. |
| Watch | `event.by` | The actor of the write or the refused write. |
| Watch | `event.reason` | The one-line reason of a refusal, and empty text for a kept write. |

A field is read as `page.cups`. The runtime has no size limit of its own: `size <= 2000` is an ordinary rule ([decision 0006](../decisions/0006-size-is-a-rule.md)).

## Rules and spaces

A page may carry a list of rules in `rules`. A space is a page that other pages name in `within`, as one name or as a list of names ([decision 0045](../decisions/0045-a-page-may-be-within-several-spaces.md)). A write is checked against the page's own plain rules, then the `each` rules of every space above it, nearest first, and each space is judged once however many paths lead to it. A write is kept only if all hold, so being within one more space only ever tightens.

A rule entry is a condition as text, or a mapping with the one key `each` whose value is a condition. A plain condition applies to the page that carries it and to no other, so it states an invariant of that page's own state in one line. An `each` condition applies to every page within the space, at any depth, and never to the space itself, so a space can bind a whole kind of act without carrying the field ([decision 0036](../decisions/0036-a-plain-rule-stays-with-its-page.md)):

```yaml
rules:
  - page.cash >= 0                          # this page only
  - each: page.amount <= space.cash - 20    # every page within this one, not this one
```

A rule is proven when it is written. Every rule and every watch `when` and `set` expression is parsed at the write, and a syntax error is refused for shape. A rule may read only `page`, `space`, `size`, `text` and `event`, and a watch entry those and `other`, `other_text`, `other_size` and `other_name`; `event` is a map with `id`, `kind`, `by` and `reason`, and a field of it other than those is refused too; any other name is refused for shape, and the reason lists the names allowed there. The names are found from the structure of the parsed expression, so nothing is evaluated, and a variable bound by `all`, `exists`, `exists_one`, `map` or `filter` is not a name read from outside. An `each` rule that is added is also tried against every page already within the space, at any depth, and the write is refused for rule, naming the page, if it is false or cannot be evaluated for one ([decision 0038](../decisions/0038-a-rule-is-proven-when-written.md)). The names are judged by the shape of the expression and the fields by the pages, so a rule that reads a field some page lacks lands when the pages within it already have the field.

Every page within the space is judged, including a space page that lies within it, so a page that lacks the field fails the rule as any missing field does. Any other mapping is refused for shape, and the reason says what is allowed. A refusal names the condition and the space it came from, whichever form it had ([decision 0034](../decisions/0034-a-rule-for-the-pages-within.md), the key renamed by [decision 0035](../decisions/0035-a-character-binds-its-own-space.md)).

A write that changes the `within` of a page that already exists is judged twice: by the page's own rules and the `each` rules of the spaces it will be in, as above, and by the `each` rules of every space it was in before and is not in now, evaluated against the page as it would be after the write ([decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md)). A space that says nothing about leaving lets its members go. A space that wants to bind states it as a rule. A refusal by a space the page is leaving names that space, as any refusal from a space does.

An `each` rule speaks only of the pages that have the fields it reads off `page`. A rule about payments reads `page.amount`; a page within the same space that has no `amount` is not a payment, and the rule is not judged against it, when the rule is written or afterwards. A field read off `space` must exist, and a plain rule must be able to read every field it names on its own page.

### Who may write

A rule can see who is writing. `event.by` is the name of the actor of the write being judged, and `within(NAME, SPACE)` says whether a page called NAME exists and lies within SPACE, by any path and including the theatre when that page exists. A name that is not a page is within nothing. So a space can say who may write in it, and the answer is read from the pages, not from a list kept beside them.

In plain words: "only the owner changes the price" is a rule on the shop, and "staff may write here" is a rule on the shop that asks whether the writer lies within `staff`.

```yaml
rules:
  - each: "event.by == 'owner' || !has(page.price)"   # only the owner writes a price
  - each: "within(event.by, 'staff')"                 # only staff write here
```

The first speaks only of pages that have a `price`, as any `each` rule speaks only of the pages that have the fields it reads. A write that breaks either is refused for rule and recorded as a refusal. A member who leaves `staff` stops being admitted at its next write, since the rule reads the pages as they are. A rule on the `theatre` page speaks for the whole vault, and a plain rule on it says who may write the theatre itself. A name is bound to its key by `verify` ([decision 0053](../decisions/0053-a-rule-sees-who-acts-and-a-name-cannot-be-borrowed.md)), so `event.by` is the name the signature carries; within one machine the key folder is the credential.

### The theatre

A vault may have a page named `theatre`, the outermost space. Every other page lies within it implicitly, after every space it names and every space above those, so the theatre's `each` rules judge every write, its fields are context at the lowest precedence, its body is the last block of `![[page#context]]`, its `on: within` and `on: refusal` entries hear every write and refusal, and `![[theatre#members]]` lists every other page. It lies within nothing, and naming it in `within` changes nothing. An answer with `writes: theatre` may add rules and reflex watch entries to it, so a character can tighten the whole house and never loosen it. A vault with no such page has no outermost space ([decision 0051](../decisions/0051-the-theatre-is-a-page.md)).

## Context from spaces

A space hands down its fields as `space`. For a page, the runtime starts from the farthest space above it and overlays the fields of each nearer space in turn, ending with the nearest, so the nearest space wins a field of the same name. A page within several spaces gets the fields of all of them with this precedence: nearer beats farther; among a page's own spaces the one listed first beats those listed after, since the first is its home; a space reached by two paths counts at its nearest distance; and spaces at one distance are ordered by the order they are reached, breadth first from the page's list. Reserved keys are not included, and a page within no space reads an empty map. `space` is available in rules (the page's own and the `each` rules of the spaces above, so a space's rule can speak about context set further in), in watch `when` conditions and in `set` values, where it is the watcher's.

Reading a field no space has is an error, as `page` is: the rule is refused as failing to evaluate, and the reason says which field was read on which thing. When another thing in scope has a field of that name, the reason says to read it there: `space.cash does not exist here: this page has cash, read it as page.cash`. A rule that may run where the context is missing guards it, as in `!has(space.limit) || page.cups <= space.limit`.

A write is judged only when its page is written. Changing a field of a space does not re-judge the pages within it; their next write meets the new value. A missing space is passed over, and the walk of rules refuses it, as it refuses a loop back to the page. Reactions handed down and embeds of context are not built.

## Refusals

A write that cannot hold is refused and recorded as an empty signed commit that changes no page ([vault format](vault-format.md#a-refusal)). The reason starts with one of these:

| Reason | When |
|---|---|
| `shape` | A reserved key or field is malformed: `within` is not a page name, `rules` is not a list of conditions and `each` mappings, `watch` is not a list of entries with `on`, `when` and exactly one of `set` or `ask` (an `ask` has a `prompt` and `into`, `writes` or both, and no keys beyond those in [Asking a model](#asking-a-model)), or a field name is not text. A rule or a watch expression does not parse or reads a name its place does not have (see [Rules and spaces](#rules-and-spaces)). |
| `rule` | A rule is false, fails to evaluate, or cannot be reached, or an `each` rule being added breaks a page already within the space: the `within` chain loops back on itself, or names a space that does not exist. The reason names the rule and the space it came from, or gives the rule's own words in place of the rule ([a rule that says why](#a-rule-that-says-why)). |
| `cycle` | Reactions are nested deeper than 12. |
| `watch` | A watch condition or value failed to evaluate. The refusal is recorded against the watching page. |
| `model` | A question to a model could not be asked or was not answered. The refusal is recorded against the asking page. See [Asking a model](#asking-a-model). |
| `limit` | A write bound to a space broke a limit of that space, whether it is a page of an answer or a letter from another theatre ([connectors](connectors.md#the-post-connector)): it is outside that space, or it names a secret or a command, or one of its watch entries would write outside the space. See [An answer that is pages](#an-answer-that-is-pages). Also an ask that the budget of the page does not allow: see [A budget](#a-budget). |

Values given to a write must be plain data: text, numbers, booleans, lists and maps. Anything else is rejected before any commit is made.

## Reactions

A page watches another page, or itself, through entries in `watch`. Each entry has a page to watch (`on`), a condition (`when`) and one action, `set` or `ask`. An entry with `set` looks like this:

```yaml
watch:
- on: cooler                   # the page watched
  when: other.cups < 10        # a condition
  set:                         # fields to set, each a value expression
    ordered: "true"
```

`on` can also name a relation instead of a page ([decision 0037](../decisions/0037-a-watch-can-fire-on-a-relation.md)). `on: within` reacts to a write of any page within the watching page, at any depth. `on: link` reacts to a write of a page whose body or text fields contain a link `[[NAME]]` to the watching page, or whose body uses a phrase the watching page is known by in `aka` ([decision 0044](../decisions/0044-a-page-is-known-by-its-phrases.md)). `on: refusal` reacts to a refused write ([below](#noticing-a-refusal)). A page never reacts to its own write through a relation, and a page may not be named `within`, `link` or `refusal`, which is refused with reason `shape`. `other_name` says which page was written.

After a write is committed, the runtime visits every page in order of name, looking for entries whose `on` is the page just written or names a relation that the write satisfies. For each one whose `when` is true it evaluates the `set` expressions and writes the results to the watching page. That write:

- is signed by the watching page's own key, created on first use;
- carries `Cause`, the id of the commit that triggered it;
- is checked against rules like any other write, and can be refused;
- triggers the pages that watch the watching page in turn.

Watchers are visited in order of name, and the reactions to one reaction finish before the next watcher is visited, so the order of the commits is the same on every run. A page that watches both `a-first` and `z-last`, which both watch one page, always meets `a-first` first.

A reaction that would leave the watching page unchanged is skipped, which is what ends a stable state. Reactions nest to a depth of 12, and a deeper one is refused with reason `cycle`. A refused write changes no page, so it triggers only the entries that name a refusal.

### Reactions handed down

A space may hand a reaction down as it hands down rules. A watch entry written `each: ENTRY`, where ENTRY is an ordinary entry with `on`, `when` and `set`, is carried by every page within the space as if the page had written it, at any depth and by any path, including every page when the entry is on the `theatre`. `page` is the member, `space` the fields of its spaces, and `other`, `event` and `text` are as for any entry of that member.

```yaml
watch:
  - each:
      on: bell
      when: has(page.cups)        # only a page that has cups
      set:
        rang: other.n
```

- The space does not carry what it hands down, and a page carries an entry from each space once however many paths lead to the space.
- A page reacts by its own entries first, in the order written, then by those handed down, from the nearest space outward in the order of the spaces above it (see [context from spaces](#context-from-spaces)), the theatre last. Each reaction is written by the member, signed by the member, with `Cause` the commit it answered, and the reactions to it finish before the next begins.
- `on` means what it means for the member: a page name, or `within`, `link` or `refusal` relative to the member. A handed-down entry cannot say "when this page itself is written": no word names the member, and a space cannot name a page it does not know.
- Like an `each` rule, the entry speaks only of members that have the fields it reads off `page`. For a member without one, the entry does nothing and nothing is refused.
- Only `set` is handed down. An entry with `ask` is refused for `limit`, because nothing meters an ask yet, and a character that gives its space reflexes may add `each` entries with `set` only.
- The cost is one evaluation of each entry per member per event, and one write for each member whose `when` holds. The depth limit of 12 applies to the whole chain, so a handed-down entry that feeds itself ends in a refusal for `cycle`.
- To find which entry fired for a write in the history, read the commit's `Cause` and the `watch` of the spaces the page lies within; the commit is the member's, and the entry is the space's.

### Noticing a refusal

An entry with `on: refusal` reacts to a refused write of any kind, after the refusal commit is recorded ([decision 0039](../decisions/0039-an-event-can-be-noticed.md)). A page is told when the refused write was to it and it exists, when it was the actor, or when the page written lies within it, by its kept `within` or else the one the write attempted, at any depth. In the entry, `event.kind` is `refused`, `event.reason` is the reason on one line, `event.by` is the actor, `other_name` is the page the write was to and `other` is the changes attempted, with no body. The reaction is an ordinary write by the watching page, caused by the refusal, one level deeper. A refusal recorded past the depth limit tells nobody, and a reaction that is itself refused may tell others within the same limit. The refused write returns the same result as before.

The entry says what picks the refusal up. A `set` that counts refusals is a reflex and asks no model. An `ask` to a small provider is a faculty. An `ask` to the character's own provider is the character. A second entry on the same page can read what the first counted, so the cheapest layer that can deal with a refusal does, and only a count past a threshold reaches the character.

## Asking a model

A watch entry may carry `ask` in place of `set`. It puts to a model a question that state cannot answer and writes the answer back as an ordinary change ([decision 0019](../decisions/0019-providers-are-pages.md)).

```yaml
watch:
- on: ticket
  when: "other.status == 'new'"
  ask:
    provider: helper        # optional: the name of a provider page
    otherwise: "Nobody has looked at this yet."   # optional: the sentence to write with no model
    prompt: "Summarise this request in one sentence: ![[ticket#text]]"
    into: summary           # the field on this page that receives the answer
    writes: den             # optional: a space the answer may write pages into
```

An entry has `set` or `ask`, never both. An `ask` has `prompt`, and `into` or `writes` or both, and may have `provider` and `otherwise`. All are text, and `provider` and `writes` are page names. Anything else is refused with reason `shape`. Without `provider` a model is detected from the environment ([detection](providers.md#detection)).

When the entry fires, in order:

1. Embeds in `prompt` are resolved as when a page is read ([vault format](vault-format.md#pages)): `![[page#field]]` reads one field and `![[page]]` reads a whole body, and `![[space#members]]` lists the pages within a space, in the order and to the length the space's `shows` states, and `![[page#context]]` gives what the spaces above the page say, nearest first. A change to any of them changes the resolved prompt, so the skip rule asks again.
2. With `writes`, the fixed instruction for pages ([An answer that is pages](#an-answer-that-is-pages)) is placed ahead of the resolved prompt, so the author's question is the last thing the model reads. The skip rule applies. The watching page keeps a field `<into>_asked` holding the SHA-256 hex digest of the resolved prompt together with the answer it got, or `writes_asked` when the entry has no `into` (the digest then covers the prompt alone). If `into` is present (or the entry has none) and the field matches the resolved prompt and the answer now in `into`, nothing is asked and nothing is written. A question is settled only while its answer is still in place: when another entry or a write has changed `into`, the same prompt is asked again. Otherwise a settled question is never asked twice, so a loop settles. The depth limit of 12 still applies, checked before the model is called.
3. The provider page, if one is named, is read ([providers](providers.md)) and the model is called once. Without one, or when it fails, detected models are tried in order.
4. If no model answered, the `otherwise` text or a built-in sentence is written to `into` and `<into>_asked` is left out, so a later ask with a model replaces it ([when no model answers](providers.md#when-no-model-answers)).
5. The trimmed answer is written to `into`, together with `<into>_asked`, in one write by the watching page. It carries `Cause` like any reaction and is checked against the page's rules and its spaces' rules. A refused answer is recorded as a refusal and the field keeps its value, and when a rule refused it the question is asked again ([When an answer is refused](#when-an-answer-is-refused)).

The commit records the question and the model ([vault format](vault-format.md#a-model-answer)). Reading the history needs no model call.

### An answer that is pages

With `writes`, the answer may hold pages as well as text, so that a character can organise itself: make notes, other characters, spaces and rules. The key names a space, and the character may write only inside it. `writes` is the verb for what a page does to a space, as `watch` is for what it does to another page. Without the key an answer is text, as before.

**The format.** The reply is cut into lines. A line that reads exactly `=== page: <name> ===` starts a page and names it. The page is Markdown with frontmatter, as in [vault format](vault-format.md#pages), and runs to the next header line or to a line that reads exactly `=== end ===`. Text before the first header, and text after an `=== end ===`, is the plain answer. If the entry has `into`, the plain text goes there, with the empty string when there is none. Leading and trailing blank lines of a page are ignored. This instruction is placed ahead of the prompt, so authors do not restate it. It is built from the same constants the parser cuts on, so the example page in it is one the parser accepts. The runtime is nobody, so these lines are narrated in the third person and shown in italics as stage directions: a page's own words, with their "I" and "you", always come from a page. The words live in `src/conky/voice.md`. `<page>` is the asking page, and the sentence about what the space holds is present only when the prompt itself embeds `![[<space>#members]]`:

```
*<page> can keep pages in <space>. Whatever <page> writes outside a page is its reply. A page is kept when it is written like this:*

=== page: <name> ===
---
within: <space>
---
what is worth keeping
=== end ===

*A page can be a note. It can also carry a rule that must stay true from now on. A rule is a line under `rules:` that says when the page is fine. It reads the page as page.FIELD and the space as space.FIELD.*

*To bind every page in <space> but not <space> itself, or to have <space> count what it turns away, <space> gets `each` rules and `watch` entries and nothing else. A watch entry sets a field when something happens. It is written like this:*

=== page: <space> ===
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

*Each time <page> is asked, it is shown what <space> holds, so it sees what it kept.*

*<page> cannot write anywhere else. Writing nothing more is fine.*
```

**How a page is applied.** The answer is written first, as today. If that write held, each page is applied in the order given as an ordinary write, one commit per page, by the actor that asked (the asking page, when a watch entry asked) and so signed by its key. Each carries `Cause`, the id of the commit of the answer. A page sets the keys its frontmatter names, and its body replaces the body when it has any text, as `conky write` does. A key it leaves out stays as it is, so a page can change its own `watch` and keep its `within`. If the answer write was refused nothing is applied, because the answer did not settle.

**The limits.** The runtime enforces each, and none depends on the prompt.

1. A page must be within the named space, directly or through spaces inside it, after the write. A page that already exists must be within it before the write too, so an answer cannot take hold of a page outside the space by naming it. The space page itself is outside, with one exception: a block that names it is allowed when it holds `rules`, `watch` or both and nothing else, no other field and no body. Its entries are added to what the space has, one that is already there is ignored, and nothing the space has is removed or changed ([decision 0035](../decisions/0035-a-character-binds-its-own-space.md)). An added watch entry must be a reflex, a `set`: one that carries `ask` is refused with reason `limit`, because nothing meters an ask yet ([decision 0041](../decisions/0041-a-character-gives-its-space-reflexes.md)). Any other block that names the space is refused. Otherwise the write is refused with reason `limit`. A character may create spaces inside the named space, and a page written after one may lie within it.
2. Every write is judged by the rules of every space involved, exactly as any write is, including the spaces a page leaves ([Rules and spaces](#rules-and-spaces)). A rule a character adds to a space it made binds the writes that follow.
3. A page written by an answer may not carry a field `secret` or `command`, which are the fields a provider page uses to name a secret and a program ([providers](providers.md)). Those stay with the person who sets the provider up, and a provider page that has them cannot be changed by an answer. Page names are checked as any page name is, so a name cannot reach outside the vault.
4. A watch entry of a page written by an answer may not write into a space outside the named space, so a character cannot widen its own reach, or the reach of what it makes, by rewriting a `writes` value. Such a page is refused with reason `limit`.
5. Each page is written one level deeper than the answer, and every reaction to it one level deeper again. The cap of 12 applies as to any chain of reactions, so a page whose watch entry asks again, and writes pages whose entries ask again, stops with a `cycle` refusal.
6. A malformed block is one recorded refusal with reason `shape` that says what was wrong: a header that names no page, a page with no frontmatter or an unclosed one, frontmatter that is not valid YAML or not keys with values, a value that is not plain data, or a reserved key of the wrong shape. A header with no valid name is recorded against the asking page. The blocks before and after still apply. An answer with no pages is fine.

When no model answers, the plain sentence goes to `into` as today and no pages are written. An entry with `writes` and no `into` has nowhere to put the sentence, so the failure is one `model` refusal. `conky ask` takes the same ability through `--writes` ([command line](cli.md#ask)).

### When an answer is refused

When a rule refuses the write of an answer, or the answer is refused for its shape, whether in the write to `into` or in a page the answer holds, the same question is sent once more. The second prompt is the first followed by a blank line and one fixed stage direction, so it is the last thing the model reads:

```
*<page>'s last answer was turned away: <reason> <page> may answer again so that it holds.*
```

`<page>` is the asking page. `<reason>` is the reason recorded on the refusal, ended with a full stop when it has none, for example `rule: page.said != 'no' (from camp) is false` or `shape: page block Mrs Okafor's parcel: The header ... does not name a page.` The history of a retried answer reads in this order: the write that triggered the entry, the refusal of the first answer, then the second answer, whose `Cause` is the refusal. The second ask is an ordinary recorded ask, and its prompt, which differs from the first, is a different moment for the cache, so it never hits the first answer. The field `<into>_asked` holds the digest of the entry's own prompt, so the question settles as if it had been asked once.

The retry is one, and no more. When the second answer is refused for a rule or its shape too, the entry's `otherwise` text is written to `into` as an ordinary write that the rules judge, and when that is refused it is recorded and the asking stops. With no `otherwise` text, or no `into`, the asking stops with the second refusal recorded and the field keeps its value. A refusal with reason `limit` or `cycle` is not retried, and neither is a failure to ask, which is covered below.

### When asking fails

Each of these, for a named provider page, is recorded as a refusal on the asking page, and the question then falls through to detection and the plain sentence: a missing or malformed provider page, a secret that cannot be found, a failed connection, an HTTP error, a reply with no answer text, and no reply within 60 seconds. The reason starts with `model:` and says what to do next, for example `model: secret 'openrouter' not found: set CONKY_SECRET_OPENROUTER or put it in openrouter.secret in the key directory`. A failure to ask is not retried. The write that triggered the entry stands and every other reaction runs, so everything that needs no model works with no network.

## A budget

A page may carry `budget: {asks: 5}`, the most times it may ask a model since the budget was last written ([decision 0058](../decisions/0058-a-budget-the-runtime-holds.md)).

- **Counted from the history.** An ask is spent when a commit of the page, kept or refused, records a model's answer: a `Model` trailer that is not `none`, and no `Cache` trailer. An answer refused for a rule or its shape is spent, and so is the ask repeated after it. A replayed answer, a plain sentence, a failed provider and a `limit` refusal are not. Nothing is stored for the count.
- **Refilled by a write.** The count starts again at the last write that set `budget`, on the page or on the space that holds the budget it lives under, even to the same value. Such a write carries the trailer `Budget`. A write that leaves `budget` alone changes nothing. No clock is involved: a clock page, when there is one, refills by writing.
- **Past it, a refusal.** When the asks spent have reached `asks`, no model is called, and a refusal for `limit` is recorded on the page, saying how many asks were allowed and that writing the budget again refills it. A cached answer is not looked for. An entry with `on: refusal` hears it like any refusal.
- **Handed down.** A member with no `budget` of its own takes that of the nearest space above it that has one, the theatre last. It is a default for each member and not a pool: two members of a space with `asks: 1` ask once each. A shared pool is not built.
- **Read.** A condition reads `asks.spent` and `asks.left`. With no budget, `asks.spent` is 0 and `asks.left` is 1000000. A prompt embeds `![[PAGE#asks]]`, which says `3 of 5 asks left`, and for a page with no budget reads the field called `asks` as before. The embed resolves in a prompt, not when a page is read.
- **Not lowered.** An answer may not set `budget` on a page it writes, and may still not add an `ask` to its space; a space still may not hand down an `ask`.

```yaml
budget: {asks: 20}
watch:
  - on: ticket
    when: "asks.left > 0"
    ask: {prompt: "Summarise ![[ticket#text]]. ![[scribe#asks]].", into: summary}
```

## Measures

A measure is a page watching itself: an entry whose `on` is the page's own name, with a `set` expression computed from the page's state. It is no separate concept ([decision 0008](../decisions/0008-measures-are-self-watches.md)). In a self-watch, `size` and `other_size` are equal.

The computed value is committed like any write, so reading history never evaluates an expression. Unchanged reactions are skipped and the depth limit applies, so a self-watch settles when its fields stop changing.

Pressure is the first use. A page with no size rule takes a large write, and a self-watch such as `{on: <itself>, when: "true", set: {pressure: "size / 400"}}` records a rising number as its own commit. A second entry with `when: "page.pressure >= 2"` can set a state that other pages watch. Walls stay for what must never happen. Nothing yet acts to relieve the pressure.
