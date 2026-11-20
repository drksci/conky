---
kind: research
title: "Anxiety kernels: warnings that reach someone who will act"
status: current
date: 2026-11-20
source: "https://drksci.com/research-anxiety-kernels"
---

# Anxiety kernels: warnings that reach someone who will act

## How to read this

The page was fetched on 2026-11-20 as raw HTML and its full text was read, from the first section to the method and sources list. Its interactive parts (two seeded simulations, a toggle of competing worries, a forecast chart) did not render in the fetch, so only their captions and the numbers printed beside them were read. The forecast table was read but not checked. None of the cited sources was fetched: not the independent review of the outage, not the Google SRE Workbook, FAIR, ISO/TS 22317 or the other items in its list, and not the sibling page "Too Much World", which the page says it builds on. Every number below is the page's own claim. Only short phrases are quoted.

## What the page says

Most warnings "arrive in time, and reach nobody with a reason to act." The page's case is the Optus Triple Zero outage of 18 September 2025, reconstructed from an independent review for the Optus board. By the page's account two alerts fired, post-change graphs showed call failures rising, and five callers described the fault correctly, and none of it reached anyone with the authority and a reason to act. The outage lasted 14 hours, 605 callers were affected and only 150 connected.

An **anxiety kernel** is "a small written rule that prices the harm, names an owner and keeps the warning open until someone has handled it." It decides in advance who must act and how fast. It has four parts, none of them new: watch one stream the organisation already has, price the harm as a cost of delay in a shared unit with the source of the figure beside it, route to a named owner at a severity the price sets, and hold one episode on that person's desk until it is handled. The page says a kernel would not have prevented the mistakes made before any alert fired. It applies to alerts that fired and went nowhere.

## Key concepts

- **Why nobody acts.** Anxiety here means holding a warning when acting on it gets a person refused or blamed. People stop acting, and "from outside the unanswered warnings look like nobody noticed." A kernel makes acting the default and keeps it cheap. The page shows this with a simulation: three synthetic personas work the same bad night twice, once where every action is refused or blamed and once where every action is backed.
- **A kernel is a few lines anyone can read and argue with.** The page gives three illustrative kernels for an emergency-call service, each with a detector, a `when` condition and an `action`, written for the article and not as the operator's configuration. One watches completion by region against that region's own baseline, one pauses a planned change when an alarm fires on a service the change was declared not to affect, and one opens a triage when two or more reports arrive within two hours. Detection has to match the grain of the failure, in space, in time, and in activity without progress.
- **Pricing.** Alerts are ranked by what an hour of delay costs, not by how often they fire. A severity ladder maps cost of delay to who is told, within what time and how often it repeats, for example "SEV1" at $100 an hour or more, with the executive on call told within five minutes. Pricing lets people argue precisely, such as raising $100 an hour to $250 and giving the reason.
- **Holding.** Most alerting fires afresh on every repeat "until people stop seeing a red light that is always on." A kernel keeps one episode open until it is handled.
- **Rules go stale.** Every alert rule is a ready-made conclusion that somebody decided in advance. A well-kept rule and a stale one look the same on a dashboard. A rule becomes prejudice "when nobody remembers who set it, on what evidence, or when it was last tested." On the night, the rule that alerts during planned work are expected was applied to the two alerts that mattered most. The guard the page gives is a sourced cost and a date on each rule, and agreement in advance on how it will be judged.
- **Finite attention, a baseline.** Well-kept rules still add up until the open warnings exceed what one person can attend to. The page proposes a "bedrock baseline", the smallest set of costed rules that stays on, cheap enough that removing it would be a deliberate decision.
- **Priorities from the accounts.** Kernel prices could be summed into rolling scenario estimates in a forecast profit and loss: each kernel's median cost lands in a named account in the months it is likely to fall, and its P10 to P90 band widens the forecast. The page says nothing in this section "has been tested on a real P&L" and that the organisation shown is invented.

## What recurs, and what is forecast or checked

- Recurrence in the page is of a situation, an alert class, not of a thought. The kernel is decided once, in advance, and applied each time the condition holds. That is a rule written ahead, with no step in which a repeated thought is noticed and compiled into it. The page does cite clustering repeat incidents by class and fixing the class, as postmortem practice it drew on.
- The forecast the page uses is a price: a cost of delay, entered as a range with a median and a P10 to P90 band, and summed across kernels. It is a forecast of loss, not a forecast of what the next stimulus will be.
- The checks the page asks for are on the rule, not on its predictions: a source and a date for each cost, a test date for each rule, and agreement in advance on how it will be judged. Nothing in the page compares a forecast with what happened and revises the rule from the gap.
- The nearest resemblance to making repeated thought cheaper is its own account of why the decision must be made early: "the decision to act has to be written down before the night", so that nobody decides at two in the morning whether a warning is worth someone's sleep. The stale-rule section is the nearest it comes to a check that a kept conclusion still holds.

## What it establishes

As reported:

- A timeline of what the independent review recorded about the night, with times. It is a secondary account of the review and was not checked against it here.
- Nothing measured about kernels. The simulation is labelled "seeded, not measured": three synthetic personas, one run per arm, one seed, the model not recorded. The runs show the effect the author set up, that refused action lowers initiative and raises avoidance, and they are illustration and not evidence.
- The kernels, the severity ladder and the forecast are illustrations written for the article.

## What it does not establish

The page says so itself:

- None of the kernels "would have fixed the fault", and most of the mistakes found were made before any alert could fire.
- The simulation is "not a measurement".
- Nothing in the profit and loss section has been tested on a real one. The claim there that risk was never managed properly because it took too much attention is a conjecture, and the organisation is invented.
- A comment from an anonymous source is used "as a lens", not as evidence, and its claims are unchecked.
- No claim is made that a kernel changes behaviour in a real organisation.

## What a Conky design must supply

The source leaves these open. A Conky use of the idea has to build them, or say it does not:

- **A shared unit of price.** The page prices harm in dollars per hour with the source recorded. A vault has no such unit built, and an energy unit is only an idea ([energy unit](../ideas/energy-unit.md)).
- **An owner and a hold.** Routing to a named owner and keeping one episode open until handled needs an owner on a page and a state that persists. Neither is built as a pattern.
- **Reading of each rule's age and source.** The stale-rule guard needs a date and a source on each rule, which a signed history already holds for every page.
- **Evidence in place of testimony.** The page's numbers are illustrations. A Conky pattern would have to show on a real run that a held, priced warning is handled sooner than a repeated one.
- **Anything about changing a rule from its own results.** The source does not do this, so the design cannot take it from there.
