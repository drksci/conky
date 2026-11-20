<h3 align="center"><img src="docs/assets/conky-mark.png" alt="" width="32" height="32" align="absmiddle">&nbsp;&nbsp;Conky&nbsp;&nbsp;&nbsp;<picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/slogan.dark.svg"><img src="docs/assets/figures/slogan.light.svg" alt="The unharnessed harness" height="20" align="absmiddle"></picture></h3>

<p><img src="docs/assets/figures/chip-stall.svg" alt="Market stall demo" height="22" align="absmiddle">&nbsp;&nbsp;<code>uvx --from git+https://github.com/drksci/conky conky demo</code></p>

<p><img src="docs/assets/figures/chip-assimilate.svg" alt="Assimilation" height="22" align="absmiddle">&nbsp;&nbsp;<code>uvx --from git+https://github.com/drksci/conky conky assimilate</code></p>

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">A folder that runs itself.</h3>

<p align="center">An open-source agent harness where the whole AI system is Markdown pages in a Git repository.<br>People, teams, tools and rules, as pages you can read. Every change signed. Every rule enforced.<br>Most of the work done by nobody in particular.</p>

<p align="center"><a href="docs/guide/concepts.md">Concepts</a> &nbsp;·&nbsp; <a href="docs/guide/getting-started.md">Getting started</a> &nbsp;·&nbsp; <a href="docs/reference/vault-format.md">Reference</a> &nbsp;·&nbsp; <a href="docs/project/roadmap.md">Roadmap</a></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/demo.dark.svg"><img src="docs/assets/figures/demo.light.svg" alt="Left, a terminal playing the demo: a market gets one rule, a stall joins, a change that breaks the rule is refused, stock runs low and the depot reorders by itself. Right, a wireframe of the same thing as a screen: a stock level, a reorder indicator flipping to yes, the rule, a pressure gauge and a history list, updating in step." width="800"></picture></p>

<p align="center"><sub>Both need <a href="https://docs.astral.sh/uv/">uv</a>, Git and ssh-keygen. The first builds a tiny market and leaves it to run itself. The second hands a stopped one to a stranger and watches it carry on.</sub></p>

<br>


### tl;dr

Every AI agent project turns into the same thing eventually: a pile of prompts, some glue code and a database nobody wants to touch. Six months in, nobody can tell you why it did what it did, and moving it anywhere is a project of its own.

Conky does it backwards. The whole system is a folder of Markdown files in Git. Every change is a signed commit. The rules get checked on every write, so they hold whether or not anyone remembers them. Pages react to each other without calling a model, and the model only gets asked when the files cannot answer.

That's it. Files and Git. If you ever hate it, clone the folder and leave.

<br>

### Not another harness

You have seen the bug. The prompt says one thing, the config says another, the database remembers a third, and the agent does a fourth. Everyone asks which one is right. Conky asks why there were four.

So there is one. The state, the rules and the instructions are the same living pages, and nothing else gets a vote.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-1-truth.dark.svg"><img src="docs/assets/figures/row-1-truth.light.svg" alt="Usually the truth is spread across code, prompts, a database, and Dave. With Conky the truth is the pages, and there is nowhere else to look." width="800"></picture></p>
<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-2-rules.dark.svg"><img src="docs/assets/figures/row-2-rules.light.svg" alt="Usually rules are a strongly worded prompt, and hope. With Conky rules are checked on every change, and a model cannot talk its way past one." width="800"></picture></p>
<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-3-in-charge.dark.svg"><img src="docs/assets/figures/row-3-in-charge.light.svg" alt="Usually one loop runs everything and calls the model for all of it. With Conky nothing is in charge: pages notice each other and respond." width="800"></picture></p>
<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-4-history.dark.svg"><img src="docs/assets/figures/row-4-history.light.svg" alt="Usually, to learn why it did that, you grep the logs and pray. With Conky every change is signed and says what caused it, so you can blame an agent." width="800"></picture></p>
<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-5-leaving.dark.svg"><img src="docs/assets/figures/row-5-leaving.light.svg" alt="Usually it grew until it could not be moved. With Conky it is a folder and its history: pick it up and go." width="800"></picture></p>

<details>
<summary>The ten parts, with what works today</summary>
<br>

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

</details>

<br>

[Concepts](docs/guide/concepts.md) &nbsp;·&nbsp; [Getting started](docs/guide/getting-started.md) &nbsp;·&nbsp; [Reference](docs/reference/vault-format.md) &nbsp;·&nbsp; [Design](docs/design.md) &nbsp;·&nbsp; [Decisions](docs/decisions/0001-objective.md) &nbsp;·&nbsp; [Research](docs/research/harnesses.md) &nbsp;·&nbsp; [Contributing](CONTRIBUTING.md)

<sub>Early days: the [roadmap](docs/project/roadmap.md) says what works and what is still to come. &nbsp; [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), your pick. The puppet pictures belong to other people. &nbsp; [![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)</sub>

<br>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-tri.dark.svg"><img src="docs/assets/figures/mark-tri.light.svg" alt="" width="60"></picture></p>

<p align="center"><sub>Brought to you by</sub><br><a href="https://drksci.com"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-drksci.dark.svg"><img src="docs/assets/figures/mark-drksci.light.svg" alt="d/rksci" width="110"></picture></a></p>
