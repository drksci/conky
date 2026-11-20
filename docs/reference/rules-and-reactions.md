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

## Variables in scope

| Where | Name | Meaning |
|---|---|---|
| Rule | `page` | The fields of the page as it would be after the write. Reserved keys are not fields. |
| Rule | `size` | The byte length of the serialised page as it would be after the write. |
| Watch | `page` | The fields of the watching page as it is now. |
| Watch | `size` | The byte length of the watching page as it is now. |
| Watch | `other` | The fields of the page that was just written. |
| Watch | `other_size` | The byte length of the page that was just written. |

A field is read as `page.cups`. The runtime has no size limit of its own: `size <= 2000` is an ordinary rule ([decision 0006](../decisions/0006-size-is-a-rule.md)).

## Rules and spaces

A page may carry a list of rules in `rules`. A space is a page that other pages name in `within`. A write is checked against the page's own rules, then those of the space named by its `within`, then that space's own `within`, and so on up the chain, so a page inherits the rules of every space above it.

The rules of a space therefore also apply to the space page itself, and a space whose rule mentions a field must carry that field. This is a known gap ([open questions](../project/open-questions.md)).

## Refusals

A write that cannot hold is refused and recorded as an empty signed commit that changes no page ([vault format](vault-format.md#a-refusal)). The reason starts with one of these:

| Reason | When |
|---|---|
| `shape` | A reserved key or field is malformed: `within` is not a page name, `rules` is not a list of text, `watch` is not a list of entries with `on`, `when` and exactly one of `set` or `ask` (an `ask` has exactly `provider`, `prompt` and `into`), or a field name is not text. |
| `rule` | A rule is false, fails to evaluate, or cannot be reached: the `within` chain loops back on itself, or names a space that does not exist. The reason names the rule and the space it came from. |
| `cycle` | Reactions are nested deeper than 12. |
| `watch` | A watch condition or value failed to evaluate. The refusal is recorded against the watching page. |
| `model` | A question to a model could not be asked or was not answered. The refusal is recorded against the asking page. See [Asking a model](#asking-a-model). |

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
```

An entry has `set` or `ask`, never both. An `ask` has `prompt` and `into`, and may have `provider` and `otherwise`, all text, and `provider` is a page name. Anything else is refused with reason `shape`. Without `provider` a model is detected from the environment ([detection](providers.md#detection)).

When the entry fires, in order:

1. Embeds in `prompt` are resolved as when a page is read ([vault format](vault-format.md#pages)): `![[page#field]]` reads one field and `![[page]]` reads a whole body. A change to either changes the resolved prompt, so the skip rule asks again.
2. The skip rule applies. The watching page keeps a field `<into>_asked` holding the SHA-256 hex digest of the resolved prompt it last got an answer for. If `into` is present and `<into>_asked` matches the resolved prompt, nothing is asked and nothing is written. A settled question is never asked twice, so a loop settles. The depth limit of 12 still applies, checked before the model is called.
3. The provider page, if one is named, is read ([providers](providers.md)) and the model is called once. Without one, or when it fails, detected models are tried in order.
4. If no model answered, the `otherwise` text or a built-in sentence is written to `into` and `<into>_asked` is left out, so a later ask with a model replaces it ([when no model answers](providers.md#when-no-model-answers)).
5. The trimmed answer is written to `into`, together with `<into>_asked`, in one write by the watching page. It carries `Cause` like any reaction and is checked against the page's rules and its spaces' rules. A refused answer is recorded as a refusal and the field keeps its value.

The commit records the question and the model ([vault format](vault-format.md#a-model-answer)). Reading the history needs no model call.

### When asking fails

Each of these, for a named provider page, is recorded as a refusal on the asking page, and the question then falls through to detection and the plain sentence: a missing or malformed provider page, a secret that cannot be found, a failed connection, an HTTP error, a reply with no answer text, and no reply within 60 seconds. The reason starts with `model:` and says what to do next, for example `model: secret 'openrouter' not found: set CONKY_SECRET_OPENROUTER or put it in openrouter.secret in the key directory`. There are no retries. The write that triggered the entry stands and every other reaction runs, so everything that needs no model works with no network.

## Measures

A measure is a page watching itself: an entry whose `on` is the page's own name, with a `set` expression computed from the page's state. It is no separate concept ([decision 0008](../decisions/0008-measures-are-self-watches.md)). In a self-watch, `size` and `other_size` are equal.

The computed value is committed like any write, so reading history never evaluates an expression. Unchanged reactions are skipped and the depth limit applies, so a self-watch settles when its fields stop changing.

Pressure is the first use. A page with no size rule takes a large write, and a self-watch such as `{on: <itself>, when: "true", set: {pressure: "size / 400"}}` records a rising number as its own commit. A second entry with `when: "page.pressure >= 2"` can set a state that other pages watch. Walls stay for what must never happen. Nothing yet acts to relieve the pressure.
