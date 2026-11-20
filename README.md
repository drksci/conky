<p align="center"><img src="docs/assets/conky-mark.png" alt="" width="72" height="72"></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/masthead.dark.svg"><img src="docs/assets/figures/masthead.light.svg" alt="Conky, the unharnessed harness" width="560"></picture></p>

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">A folder that runs itself.</h3>

<p align="center">People, teams, tools and rules, as pages you can read.<br>Every change signed. Every rule enforced. Most of the work done by nobody in particular.</p>

<p align="center"><a href="docs/guide/concepts.md">Concepts</a> &nbsp;·&nbsp; <a href="docs/guide/getting-started.md">Getting started</a> &nbsp;·&nbsp; <a href="docs/reference/vault-format.md">Reference</a> &nbsp;·&nbsp; <a href="docs/project/roadmap.md">Roadmap</a></p>

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

<p align="center"><img src="docs/assets/figures/demo.svg" alt="A terminal playing the demo: a market is set up with one rule, a stall joins, a change that breaks the rule is refused, stock runs low and the depot reorders by itself." width="800"></p>

<p align="center"><sub>Needs <a href="https://docs.astral.sh/uv/">uv</a>, Git and ssh-keygen. Builds a tiny market in a folder and leaves it to get on with things.</sub></p>

<br>


### tl;dr

Every AI agent project turns into the same thing eventually: a pile of prompts, some glue code and a database nobody wants to touch. Six months in, nobody can tell you why it did what it did, and moving it anywhere is a project of its own.

Conky does it backwards. The whole system is a folder of Markdown files in Git. Every change is a signed commit. The rules get checked on every write, so they hold whether or not anyone remembers them. Pages react to each other without calling a model, and the model only gets asked when the files cannot answer.

That's it. Files and Git. If you ever hate it, clone the folder and leave.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-1-one-change.dark.svg"><img src="docs/assets/figures/fig-1-one-change.light.svg" alt="A flat line drawing, left to right: the stall's page, a stamp, a strip of history, a gate marked rules, then a dashed yellow arrow to the depot's page, which has marked a reorder." width="800"></picture></p>

<p align="center"><sub><i>Stock runs low. The change is signed, recorded and checked, and the depot reorders. Nobody decided to.</i></sub></p>

<br>


### What a folder can do

<sub>● works today &nbsp;&nbsp; ○ on the way</sub>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-page.dark.svg"><img src="docs/assets/figures/ico-page.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Pages</b> &nbsp;<sub>●</sub><br>Everything is one: a person, a team, a tool, a rule, a pile of data. If it exists, you can open it and read it.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-space.dark.svg"><img src="docs/assets/figures/ico-space.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Spaces</b> &nbsp;<sub>●</sub><br>Pages live in spaces, and spaces hand their rules down. Structure, without buying a tool to draw the org chart.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-rule.dark.svg"><img src="docs/assets/figures/ico-rule.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Rules that hold</b> &nbsp;<sub>●</sub><br>Checked on every change, not politely requested in a prompt. A refused change goes on the record too.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-reaction.dark.svg"><img src="docs/assets/figures/ico-reaction.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Things that just happen</b> &nbsp;<sub>●</sub><br>Pages notice each other and respond. Stock runs low, the depot reorders. Nobody held a meeting.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-measure.dark.svg"><img src="docs/assets/figures/ico-measure.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Pages that feel their weight</b> &nbsp;<sub>● &nbsp;tidying up ○</sub><br>A page can watch itself. Pressure builds as it grows, and things get noticed before they rot.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-history.dark.svg"><img src="docs/assets/figures/ico-history.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>A signed history</b> &nbsp;<sub>●</sub><br>Every change says who made it and what caused it. "Why did it do that" has an answer. Undo is a checkout.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-model.dark.svg"><img src="docs/assets/figures/ico-model.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Models, on request</b> &nbsp;<sub>● &nbsp;background minds ○</sub><br>A page asks a model only when the pages run out of answers. The provider is a page too, so switching is one edit.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-pattern.dark.svg"><img src="docs/assets/figures/ico-pattern.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Patterns, not features</b> &nbsp;<sub>○</sub><br>No built-in ledger, CRM or workflow engine. Recipes compose the same few parts into whatever the job needs.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-direction.dark.svg"><img src="docs/assets/figures/ico-direction.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>A sense of direction</b> &nbsp;<sub>○</sub><br>A goal is a page. Drifting from it shows up as a quiet reading and a small correction, not an alarm.</p>

<p><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/ico-leave.dark.svg"><img src="docs/assets/figures/ico-leave.light.svg" alt="" width="30" align="absmiddle"></picture>&nbsp;&nbsp;<b>Leave any time</b> &nbsp;<sub>●</sub><br>It is a Git repository. Clone it, bundle it, take it somewhere better. No export wizard.</p>

<br>


### The whale and the door

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-5-stay-or-go.dark.svg"><img src="docs/assets/figures/fig-5-stay-or-go.light.svg" alt="Two drawings side by side. Left, too big to move: a whale skeleton settled on the ground. Right, just walk out: a skeleton striding to an open door with a folder under its arm." width="800"></picture></p>

Every system ends up as one of these two.

**Where the truth lives.** Usually in code, prompts, a database, and Dave. Here, in pages.

**How rules are kept.** Usually with a strongly worded prompt. Here, checked on every change.

**"Why did it do that."** Usually you grep the logs and pray. Here there is a signed history, with causes.

**When a model gets called.** Usually constantly, for everything. Here, when the pages run out of answers.

**What leaving costs.** Usually a migration project and a quarter. Here, `git clone`.

<br>


### How far along

**Now.** Pages, spaces, rules, reactions, measures, a signed history, asking a model, and the demo.

**Next.** A sense of time, tidying up what has gone quiet, trying a change before making it, approvals, and renames that fix their own links.

**Later.** Background minds, direction and drift, patterns, tables, a core that runs in a browser, and the assimilation test.

The assimilation test is the one to watch. Stop a running system, hand a stranger nothing but the folder, and see whether it carries on as the original. Unlike in a certain Antarctic film, every copy gets the blood test.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-6-blood-test.dark.svg"><img src="docs/assets/figures/fig-6-blood-test.light.svg" alt="A row of four dishes on a bench, tagged original, copy, copy, copy, with a hot wire reaching towards them and a yellow tick above each copy." width="800"></picture></p>

<p align="center"><sub><i>Every copy gets tested. Every copy has to pass.</i></sub></p>

The parts marked as working are real and tested. The model part has only met stand-in servers so far, not a live provider, and nothing here has been measured against anything else yet. The [roadmap](docs/project/roadmap.md) has the order, and the [evaluation plan](docs/research/evaluation-plan.md) says how the measuring will be done.

<br>


[Concepts](docs/guide/concepts.md) &nbsp;·&nbsp; [Getting started](docs/guide/getting-started.md) &nbsp;·&nbsp; [Reference](docs/reference/vault-format.md) &nbsp;·&nbsp; [Design](docs/design.md) &nbsp;·&nbsp; [Decisions](docs/decisions/0001-objective.md) &nbsp;·&nbsp; [Research](docs/research/harnesses.md) &nbsp;·&nbsp; [Contributing](CONTRIBUTING.md)

<sub>[MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), your pick. The puppet pictures belong to other people. &nbsp; [![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)</sub>

<br>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-tri.dark.svg"><img src="docs/assets/figures/mark-tri.light.svg" alt="" width="60"></picture></p>

<p align="center"><sub>Brought to you by</sub><br><a href="https://drksci.com"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-drksci.dark.svg"><img src="docs/assets/figures/mark-drksci.light.svg" alt="d/rksci" width="110"></picture></a></p>
