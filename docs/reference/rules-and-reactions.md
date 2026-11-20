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

### Text functions

An expression can take text apart with these functions. All but `captures` take their names and shapes from the strings extension of the CEL project ([cel-go `ext/README.md`](https://github.com/google/cel-go/blob/master/ext/README.md#strings), read 2026-11-20). Each can be called as a method (`text.split(',')`) or as a function (`split(text, ',')`). Positions count characters from zero.

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

The standard has no `captures`. Its regular-expression extension has `regex.extract`, which needs optional values and allows one group, so `captures` stands in until a need for the standard form is shown. The standard `int('12')` and `double('1.5')` already turn captured text into a number, so `int(line.captures('n=(\\d+)')[0])` reads a number out of a line. A pattern that does not match gives an empty list, and indexing it is an evaluation error, so a rule that reads such a number refuses a line without one.

Every function is pure. Text over 65536 characters, a result over 65536 characters, or a pattern over 256 characters is an evaluation error, handled like any other failing expression ([Refusals](#refusals)). The limits bound the cost of a call but do not make every pattern fast: a pattern can still backtrack for a long time on an input under the limit.

## Variables in scope

| Where | Name | Meaning |
|---|---|---|
| Rule | `page` | The fields of the page as it would be after the write. Reserved keys are not fields. |
| Rule | `space` | The fields handed down by the spaces the page is within, nearest winning (see [Context from spaces](#context-from-spaces)). |
| Rule | `size` | The byte length of the serialised page as it would be after the write. |
| Watch | `page` | The fields of the watching page as it is now. |
| Watch | `space` | The same, for the watching page. |
| Watch | `size` | The byte length of the watching page as it is now. |
| Watch | `other` | The fields of the page that was just written. |
| Watch | `other_size` | The byte length of the page that was just written. |
| Watch | `event` | The id of the change being reacted to. A case can keep it in a field to mark what it has met, then test `page.met != event`. |

A field is read as `page.cups`. The runtime has no size limit of its own: `size <= 2000` is an ordinary rule ([decision 0006](../decisions/0006-size-is-a-rule.md)).

## Rules and spaces

A page may carry a list of rules in `rules`. A space is a page that other pages name in `within`. A write is checked against the page's own rules, then those of the space named by its `within`, then that space's own `within`, and so on up the chain, so a page inherits the rules of every space above it.

The rules of a space therefore also apply to the space page itself, and a space whose rule mentions a field must carry that field. This is a known gap ([open questions](../project/open-questions.md)).

A write that changes the `within` of a page that already exists is judged twice: by the page's own rules and the spaces it will be in, as above, and by the rules of every space it was in before, evaluated against the page as it would be after the write ([decision 0022](../decisions/0022-leaving-a-space-is-a-write-the-space-can-refuse.md)). A space that says nothing about leaving lets its members go. A space that wants to bind states it as a rule. A refusal by a space the page is leaving names that space, as any refusal from a space does.

## Context from spaces

A space hands down its fields as `space`. For a page, the runtime starts from the outermost space it is within and overlays the fields of each inner space in turn, ending with the nearest, so the nearest space wins a field of the same name. Reserved keys are not included, and a page within no space reads an empty map. `space` is available in rules (the page's own and those handed down, so a space's rule can speak about context set further in), in watch `when` conditions and in `set` values, where it is the watcher's.

Reading a field no space has is an error, as `page` is: the rule is refused as failing to evaluate. A rule that may run where the context is missing guards it, as in `!has(space.limit) || page.cups <= space.limit`.

A write is judged only when its page is written. Changing a field of a space does not re-judge the pages within it; their next write meets the new value. A missing space or a loop in the chain ends the climb, and the walk of rules refuses it as before. Several spaces for one page, reactions handed down and embeds of context are not built.

## Refusals

A write that cannot hold is refused and recorded as an empty signed commit that changes no page ([vault format](vault-format.md#a-refusal)). The reason starts with one of these:

| Reason | When |
|---|---|
| `shape` | A reserved key or field is malformed: `within` is not a page name, `rules` is not a list of text, `watch` is not a list of entries with `on`, `when` and exactly one of `set` or `ask` (an `ask` has a `prompt` and `into`, `writes` or both, and no keys beyond those in [Asking a model](#asking-a-model)), or a field name is not text. |
| `rule` | A rule is false, fails to evaluate, or cannot be reached: the `within` chain loops back on itself, or names a space that does not exist. The reason names the rule and the space it came from. |
| `cycle` | Reactions are nested deeper than 12. |
| `watch` | A watch condition or value failed to evaluate. The refusal is recorded against the watching page. |
| `model` | A question to a model could not be asked or was not answered. The refusal is recorded against the asking page. See [Asking a model](#asking-a-model). |
| `limit` | A page written by an answer broke a limit of the space it was given: it is outside that space, or it names a secret or a command, or one of its watch entries would write outside the space. See [An answer that is pages](#an-answer-that-is-pages). |

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

After a write is committed, the runtime visits every page in order of name, looking for entries whose `on` is the page just written. For each one whose `when` is true it evaluates the `set` expressions and writes the results to the watching page. That write:

- is signed by the watching page's own key, created on first use;
- carries `Cause`, the id of the commit that triggered it;
- is checked against rules like any other write, and can be refused;
- triggers the pages that watch the watching page in turn.

A reaction that would leave the watching page unchanged is skipped, which is what ends a stable state. Reactions nest to a depth of 12, and a deeper one is refused with reason `cycle`. A refused write triggers no reactions, because nothing changed.

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

1. Embeds in `prompt` are resolved as when a page is read ([vault format](vault-format.md#pages)): `![[page#field]]` reads one field and `![[page]]` reads a whole body, and `![[space#members]]` lists the pages within a space. A change to either changes the resolved prompt, so the skip rule asks again.
2. With `writes`, the fixed instruction for pages ([An answer that is pages](#an-answer-that-is-pages)) is placed ahead of the resolved prompt, so the author's question is the last thing the model reads. The skip rule applies. The watching page keeps a field `<into>_asked` holding the SHA-256 hex digest of the resolved prompt together with the answer it got, or `writes_asked` when the entry has no `into` (the digest then covers the prompt alone). If `into` is present (or the entry has none) and the field matches the resolved prompt and the answer now in `into`, nothing is asked and nothing is written. A question is settled only while its answer is still in place: when another entry or a write has changed `into`, the same prompt is asked again. Otherwise a settled question is never asked twice, so a loop settles. The depth limit of 12 still applies, checked before the model is called.
3. The provider page, if one is named, is read ([providers](providers.md)) and the model is called once. Without one, or when it fails, detected models are tried in order.
4. If no model answered, the `otherwise` text or a built-in sentence is written to `into` and `<into>_asked` is left out, so a later ask with a model replaces it ([when no model answers](providers.md#when-no-model-answers)).
5. The trimmed answer is written to `into`, together with `<into>_asked`, in one write by the watching page. It carries `Cause` like any reaction and is checked against the page's rules and its spaces' rules. A refused answer is recorded as a refusal and the field keeps its value.

The commit records the question and the model ([vault format](vault-format.md#a-model-answer)). Reading the history needs no model call.

### An answer that is pages

With `writes`, the answer may hold pages as well as text, so that a character can organise itself: make notes, other characters, spaces and rules. The key names a space, and the character may write only inside it. `writes` is the verb for what a page does to a space, as `watch` is for what it does to another page. Without the key an answer is text, as before.

**The format.** The reply is cut into lines. A line that reads exactly `=== page: <name> ===` starts a page and names it. The page is Markdown with frontmatter, as in [vault format](vault-format.md#pages), and runs to the next header line or to a line that reads exactly `=== end ===`. Text before the first header, and text after an `=== end ===`, is the plain answer. If the entry has `into`, the plain text goes there, with the empty string when there is none. Leading and trailing blank lines of a page are ignored. This instruction is placed ahead of the prompt, so authors do not restate it. It is built from the same constants the parser cuts on, so the example page in it is one the parser accepts. `<page>` is the asking page, and the sentence about what the space holds is present only when the prompt itself embeds `![[<space>#members]]`:

```
You are a page called <page>, and <space> is a space you can write into. Your reply is whatever you write outside a page. You may write pages into <space>, and they are kept. Write one like this:

=== page: <name> ===
---
within: <space>
---
what you want to keep
=== end ===

A page can be a note to yourself, or it can carry a rule that must stay true from now on: a line under `rules:`, a CEL condition on `page.FIELD`. Each time you are asked, you are shown what <space> holds, so you will see what you kept. You cannot write anywhere else. Writing nothing more is fine.
```

**How a page is applied.** The answer is written first, as today. If that write held, each page is applied in the order given as an ordinary write, one commit per page, by the actor that asked (the asking page, when a watch entry asked) and so signed by its key. Each carries `Cause`, the id of the commit of the answer. A page sets the keys its frontmatter names, and its body replaces the body when it has any text, as `conky write` does. A key it leaves out stays as it is, so a page can change its own `watch` and keep its `within`. If the answer write was refused nothing is applied, because the answer did not settle.

**The limits.** The runtime enforces each, and none depends on the prompt.

1. A page must be within the named space, directly or through spaces inside it, after the write. A page that already exists must be within it before the write too, so an answer cannot take hold of a page outside the space by naming it. The space page itself is outside. Otherwise the write is refused with reason `limit`. A character may create spaces inside the named space, and a page written after one may lie within it.
2. Every write is judged by the rules of every space involved, exactly as any write is, including the spaces a page leaves ([Rules and spaces](#rules-and-spaces)). A rule a character adds to a space it made binds the writes that follow.
3. A page written by an answer may not carry a field `secret` or `command`, which are the fields a provider page uses to name a secret and a program ([providers](providers.md)). Those stay with the person who sets the provider up, and a provider page that has them cannot be changed by an answer. Page names are checked as any page name is, so a name cannot reach outside the vault.
4. A watch entry of a page written by an answer may not write into a space outside the named space, so a character cannot widen its own reach, or the reach of what it makes, by rewriting a `writes` value. Such a page is refused with reason `limit`.
5. Each page is written one level deeper than the answer, and every reaction to it one level deeper again. The cap of 12 applies as to any chain of reactions, so a page whose watch entry asks again, and writes pages whose entries ask again, stops with a `cycle` refusal.
6. A malformed block is one recorded refusal with reason `shape` that says what was wrong: a header that names no page, a page with no frontmatter or an unclosed one, frontmatter that is not valid YAML or not keys with values, a value that is not plain data, or a reserved key of the wrong shape. A header with no valid name is recorded against the asking page. The blocks before and after still apply. An answer with no pages is fine.

When no model answers, the plain sentence goes to `into` as today and no pages are written. An entry with `writes` and no `into` has nowhere to put the sentence, so the failure is one `model` refusal. `conky ask` takes the same ability through `--writes` ([command line](cli.md#ask)).

### When asking fails

Each of these, for a named provider page, is recorded as a refusal on the asking page, and the question then falls through to detection and the plain sentence: a missing or malformed provider page, a secret that cannot be found, a failed connection, an HTTP error, a reply with no answer text, and no reply within 60 seconds. The reason starts with `model:` and says what to do next, for example `model: secret 'openrouter' not found: set CONKY_SECRET_OPENROUTER or put it in openrouter.secret in the key directory`. There are no retries. The write that triggered the entry stands and every other reaction runs, so everything that needs no model works with no network.

## Measures

A measure is a page watching itself: an entry whose `on` is the page's own name, with a `set` expression computed from the page's state. It is no separate concept ([decision 0008](../decisions/0008-measures-are-self-watches.md)). In a self-watch, `size` and `other_size` are equal.

The computed value is committed like any write, so reading history never evaluates an expression. Unchanged reactions are skipped and the depth limit applies, so a self-watch settles when its fields stop changing.

Pressure is the first use. A page with no size rule takes a large write, and a self-watch such as `{on: <itself>, when: "true", set: {pressure: "size / 400"}}` records a rising number as its own commit. A second entry with `when: "page.pressure >= 2"` can set a state that other pages watch. Walls stay for what must never happen. Nothing yet acts to relieve the pressure.
