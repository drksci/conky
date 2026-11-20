# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">A folder that runs itself.</h3>

<p align="center">People, teams, tools and rules, as pages you can read.<br>Every change signed. Every rule enforced. Most of the work done by nobody in particular.</p>

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

<p align="center"><img src="docs/assets/figures/demo.svg" alt="A terminal playing the demo: a market is set up with one rule, a stall joins, a change that breaks the rule is refused, stock runs low and the depot reorders by itself." width="800"></p>

<p align="center"><sub>Needs <a href="https://docs.astral.sh/uv/">uv</a>, Git and ssh-keygen. Builds a tiny market in a folder and leaves it to get on with things.</sub></p>

## The pitch

Most AI systems are a model in a trench coat made of prompts, glue code and a database nobody dares open. They demo beautifully. Then they grow, and one day nobody can say why the thing did what it did, or move it anywhere else.

conky starts from the other end. The system is a folder of pages, and the folder is the whole truth. The software has two jobs: enforce the rules and keep the history. A model is a guest who gets asked a question when the pages cannot answer it.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-1-one-change.dark.svg"><img src="docs/assets/figures/fig-1-one-change.light.svg" alt="A flat line drawing, left to right: the stall's page, a stamp, a strip of history, a gate marked rules, then a dashed yellow arrow to the depot's page, which has marked a reorder. Under the depot: nobody decided." width="800"></picture></p>

## What is in the box

<sub>● works today &nbsp; ○ on the way</sub>

<table>
<tr><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-page.dark.svg"><img src="docs/assets/figures/ico-page.light.svg" alt="" width="44"></picture><br><b>Pages</b> <sub>●</sub><br>Everything is one: a person, a team, a tool, a rule, a pile of data. If it exists, you can open it and read it.</td><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-space.dark.svg"><img src="docs/assets/figures/ico-space.light.svg" alt="" width="44"></picture><br><b>Spaces</b> <sub>●</sub><br>Pages live in spaces, and spaces hand their rules down. Structure without buying a tool to draw the org chart.</td></tr>
<tr><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-rule.dark.svg"><img src="docs/assets/figures/ico-rule.light.svg" alt="" width="44"></picture><br><b>Rules that hold</b> <sub>●</sub><br>Checked on every change, not politely requested in a prompt. A refused change goes on the record too.</td><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-reaction.dark.svg"><img src="docs/assets/figures/ico-reaction.light.svg" alt="" width="44"></picture><br><b>Things that just happen</b> <sub>●</sub><br>Pages notice each other and respond. Stock runs low, the depot reorders. Nobody held a meeting.</td></tr>
<tr><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-measure.dark.svg"><img src="docs/assets/figures/ico-measure.light.svg" alt="" width="44"></picture><br><b>Pages that feel their weight</b> <sub>● pressure &nbsp; ○ tidying up</sub><br>A page can watch itself. Pressure builds as it grows, and things get noticed before they rot.</td><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-history.dark.svg"><img src="docs/assets/figures/ico-history.light.svg" alt="" width="44"></picture><br><b>A signed history</b> <sub>●</sub><br>Every change says who made it and what caused it. "Why did it do that" has an answer. Undo is a checkout.</td></tr>
<tr><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-model.dark.svg"><img src="docs/assets/figures/ico-model.light.svg" alt="" width="44"></picture><br><b>Models, on request</b> <sub>● &nbsp; ○ background minds</sub><br>A page asks a model only when the pages run out of answers. The provider is a page too, so switching is one edit.</td><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-pattern.dark.svg"><img src="docs/assets/figures/ico-pattern.light.svg" alt="" width="44"></picture><br><b>Patterns, not features</b> <sub>○</sub><br>No built-in ledger, CRM or workflow engine. Recipes compose the same few parts into whatever the job needs.</td></tr>
<tr><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-direction.dark.svg"><img src="docs/assets/figures/ico-direction.light.svg" alt="" width="44"></picture><br><b>A sense of direction</b> <sub>○</sub><br>A goal is a page. Drifting from it shows up as a quiet reading and a small correction, not an alarm.</td><td width="50%" valign="top"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-leave.dark.svg"><img src="docs/assets/figures/ico-leave.light.svg" alt="" width="44"></picture><br><b>Leave any time</b> <sub>●</sub><br>It is a Git repository. Clone it, bundle it, take it somewhere better. No export wizard.</td></tr>
</table>

## Stay or go

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-5-stay-or-go.dark.svg"><img src="docs/assets/figures/fig-5-stay-or-go.light.svg" alt="Two panels side by side. Left, too big to move: a whale skeleton settled on the ground. Right, just walk out: a skeleton striding to an open door with a folder under its arm." width="800"></picture></p>

Every system ends up as one of these two.

| | The usual way | conky |
|---|---|---|
| The truth lives in | code, prompts, a database, and Dave | pages |
| Rules are | a strongly worded prompt | checked, every time |
| "Why did it do that" | grep the logs and pray | signed history, with causes |
| A model gets called | constantly, for everything | when the pages run out of answers |
| Leaving costs | a migration project and a quarter | `git clone` |

## Now, next, later

| Now | Next | Later |
|---|---|---|
| Pages, spaces, rules, reactions, measures, signed history, asking a model, the demo | A sense of time, tidying up what has gone quiet, trying a change before making it, approvals, renames that fix their own links | Background minds, direction and drift, patterns, tables, a core that runs in a browser, and the assimilation test |

The assimilation test is the one to watch: stop a running system, hand a stranger nothing but the folder, and see whether it carries on as the original. Unlike in a certain Antarctic film, every copy gets the blood test.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-6-blood-test.dark.svg"><img src="docs/assets/figures/fig-6-blood-test.light.svg" alt="A row of four dishes on a bench, tagged original, copy, copy, copy, with a hot wire reaching towards them and a yellow tick above each copy. Every copy gets tested. Every copy has to pass." width="800"></picture></p>

Early days, in other words. The parts marked as working are real and tested. The model part has only met stand-in servers so far, not a live provider, and nothing here has been measured against anything else yet. The [roadmap](docs/project/roadmap.md) has the order and the [evaluation plan](docs/research/evaluation-plan.md) says how the measuring will be done.

## Read on

[Concepts](docs/guide/concepts.md) · [Getting started](docs/guide/getting-started.md) · [Reference](docs/reference/vault-format.md) · [Design](docs/design.md) · [Decisions](docs/decisions/0001-objective.md) · [Research](docs/research/harnesses.md) · [Contributing](CONTRIBUTING.md)

[![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)

## Licence

[MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), your pick. The puppet pictures belong to other people.
