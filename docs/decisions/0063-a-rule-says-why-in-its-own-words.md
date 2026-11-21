---
kind: decision
title: A rule says why in its own words
status: accepted
date: 2026-11-21
source: maintainers
arch:
  covers:
  - law.rule.says
---

# 0063 A rule says why in its own words

## Context

- A refusal by a rule that is false gives the rule back: `rule: !has(page.cups) || page.cups <= 50 (from stand) is false`. That says what was checked. It does not say what to do, and whoever is turned away, a small model on its one retry for one, has to work the answer out of an expression.
- [Decision 0038](0038-a-rule-is-proven-when-written.md) made the reasons for a rule that cannot be evaluated plain, and the trials behind it showed that a reason with the right words in it is what a small model recovers from. A rule that is merely false had no such words, because only its author knows them.
- The rule language already has a place for words. CEL has line comments, `//` to the end of the line, and cel-python reads them. A rule is stored as written, so a rule with a comment was already accepted, kept and quoted whole in its refusal.

## The walk

1. **The image.** A sign on a door. "No entry" is the rule; "deliveries round the back" is what makes it kind. The second line is written by whoever put up the sign, on the sign.
2. **The general case.** A check that carries its own message: a limit with the words for whoever meets it.
3. **Existing words.** A rule, its expression and a refusal's reason all exist. `otherwise` exists on an ask, as what is written when no answer holds, and `when` exists on a watch entry; a rule that took `otherwise` would need a mapping for the plain rule too, with a key for its condition, which is two new forms. A comment in the expression needs none: no key, no name, no form. What is left over is one behaviour, that the reason prefers the words.
4. **The natural gesture.** A person writing a condition puts a remark beside it. `page.cups <= 50 // Sell 50 cups at most.` is what would be typed untaught.
5. **Par.** Kubernetes validation rules, which are CEL, pair each `rule` with a `message` field beside it ([Kubernetes, "Validation rules"](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules), read 2026-11-21). JSON Schema validators carry an error message beside a constraint in the same way, and a SQL check constraint has a name that the error reports. The convention is a sibling field. This decision goes against it: see the bet below.
6. **Who does it.** A character can already do half for itself: it may write the comment today, and the refusal quotes it. It cannot make the refusal lead with the words. The runtime builds that and nothing else.
7. **The trial.** One dial: the same `each` rule on a space, with words and without. A small model is asked for something the rule refuses and gets its one retry. Forecast, written before any run: with words the second answer holds in at least four draws of five, and without them in fewer. A miss would mean the words are not what a model recovers from, and the form should be reconsidered. The trial has not been run.
8. **How it is seen.** `conky log` shows `refused cooler rule: Sell 50 cups at most. (from stand)`, a line a person reads without knowing the rule language. The retry note a model is shown carries the same words.
9. **The smallest step.** Built now: the words lead the reason of a rule that is false. Waiting: teaching the form in the page instruction of `voice.md`, which changes what every model is shown and wants the trial first; words chosen by an expression, as Kubernetes has in `messageExpression`. Not closed off: a sibling key can still be added if the bet is lost, since a comment stays a comment.

Said once more: a rule's remark is its reason. That is shorter than the request, and it adds no word.

## Decision

The words after `//` in a rule are what a refusal says when the rule is false.

- A rule entry, plain or `each`, may end a line with `//` and words. Several remarks are joined in order with a space. A `//` inside a text literal, as in `'http://'`, is part of the text.
- When such a rule is false the reason is `rule: WORDS (from OWNER)`, in the result, in the `Reason` trailer of the refused commit and in the retry note shown to a model. For an `each` rule that a page already within breaks when the rule is added, `for PAGE, within it` follows as before.
- A rule with no words is refused as before: `rule: EXPRESSION (from OWNER) is false`.
- A rule with words that cannot be evaluated keeps the form `rule: EXPRESSION (from OWNER) failed to evaluate: WHY`. The words say what to do when the rule is false, and here something else is wrong; the expression, remark included, is shown.
- Refused when written, with reason `shape` and the sentence `rule-words` of `voice.md`: a rule with `//` and no words after it, and a rule that is words and no condition.
- Only rules are read this way. A remark in a watch `when`, a `set` value or a `first` is a comment and nothing more.

## The bet

Against the convention of a message field beside the rule, the bet is that a remark in the expression is written more readily, by people and by models, and misread no more often. It is lost if the trial of step 7 shows models writing rules without remarks where a key would have been filled, or remarks that describe the rule and do not say what to do, at a rate a key would not have.

## What the old behaviour guaranteed

- A reason for a false rule quoted the rule, so the rule could be found from the reason alone. Given up for a rule with words: the reason names the owner, the `From` trailer names it for a space, and the rule is read on that page. A rule with no words keeps the quote, held by `test_a_rule_without_words_is_refused_as_before`.
- Every such reason ended `is false`, and the trial pictures in `bench/dynamics.py` matched on it. Kept for rules with no words; the pictures now read both forms, held by `test_the_trial_picture_reads_a_refusal_that_carries_words`.
- By accident: a rule with a bare `//` was accepted. Given up; it is refused with what to write.

## Consequences

- Whoever writes a limit can say what to do about it, in the place the limit is written, and the record of a refusal reads as a sentence.
- Nothing is added to the vocabulary and no stored form changes: a vault written before reads the same, and a rule with a remark written before now leads its refusals with the remark.
- Not built: the page instruction does not teach the form, so a character learns it from a rule it is shown or not at all. No trial has been run.
