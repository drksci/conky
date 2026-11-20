<h1><img src="docs/assets/conky-mark.png" alt="" width="40" height="40" align="absmiddle">&nbsp;Conky: the unharnessed harness</h1>

<img src="docs/assets/figures/chip-lemonade.svg" alt="Lemonade stand:" height="26" align="left" vspace="13" hspace="6">

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

<img src="docs/assets/figures/chip-assimilate.svg" alt="The thing:" height="26" align="left" vspace="13" hspace="6">

```bash
uvx --from git+https://github.com/drksci/conky conky assimilate
```

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">A folder where everything is somebody.</h3>

<p align="center">An open-source agent harness where the whole AI system is Markdown pages in a Git repository.<br>Every page is a character with its own name and voice. Every change is signed. Every rule holds.<br>The dull parts are reflexes, so the thinking can go into being someone.</p>

<p align="center"><a href="docs/guide/concepts.md">Concepts</a> &nbsp;·&nbsp; <a href="docs/guide/getting-started.md">Getting started</a> &nbsp;·&nbsp; <a href="docs/reference/vault-format.md">Reference</a> &nbsp;·&nbsp; <a href="docs/project/roadmap.md">Roadmap</a></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/demo.dark.svg"><img src="docs/assets/figures/demo.light.svg" alt="Left, a terminal playing the demo: Maya sets up a lemonade stand with one house rule, fills the cooler, a cup count below zero is refused, a busy hour empties the cooler and the supplier orders lemons by itself. Right, a wireframe of the same thing as a screen, in the pages' own words: the house rule, the cooler's count, the supplier's order and lines from the daybook, updating in step." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-oregon-trail.dark.svg"><img src="docs/assets/figures/fig-oregon-trail.light.svg" alt="A schematic in three panels. The game: Oregon Trail asks whether to stop at the next fort, hunt or continue. Conky: the screen changed, Ma read a pattern, Jed wants to hunt, a house rule refuses it, Ma says to push on, and the hands type 3. A2UI: the same moment as a screen, with the four travellers, the supplies and a note that Ma read The Art of War." width="800"></picture></p>


<br>


### tl;dr

Every AI agent project turns into the same thing eventually: a pile of prompts, some glue code and a database nobody wants to touch. Six months in, nobody can tell you why it did what it did, and moving it anywhere is a project of its own.

Conky does it backwards. The whole system is a folder of Markdown files in Git, and every file is somebody: the owner, the cooler, the supplier, the daybook, each with its own name and voice. The dull parts are reflexes. Changes are signed, rules are checked on every write, and pages notice each other, so nobody has to think about any of that. The thinking is saved for being someone.

That's it. Files and Git. If you ever hate it, clone the folder and leave.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-0-folder.dark.svg"><img src="docs/assets/figures/fig-0-folder.light.svg" alt="An early Macintosh folder window titled Lemonade stand, in black and white. Inside are six page icons named stand, cooler, supplier, daybook, maya and sam. Dashed arrows run from stand to cooler to supplier, and the daybook has an arrow looping back to itself. The status line reads: 6 pages, running itself." width="800"></picture></p>

<br>

### Not another harness

Most agent setups keep what is true in four places: the prompt, the config, the database and the code. When they disagree, somebody has to work out which one wins.

Conky keeps one place. Each row shows the usual way on the left and Conky on the right, with the actual parts named. Every name is sourced in the <a href="docs/research/harnesses.md">comparison</a>.

<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-1-truth.dark.svg"><img src="docs/assets/figures/row-1-truth.light.svg" alt="Usually the truth is spread across code, prompts, a database, and Dave. With Conky the truth is the pages, and there is nowhere else to look." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-2-rules.dark.svg"><img src="docs/assets/figures/row-2-rules.light.svg" alt="Usually rules are a strongly worded prompt, and hope. With Conky rules are checked on every change, and a model cannot talk its way past one." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-3-in-charge.dark.svg"><img src="docs/assets/figures/row-3-in-charge.light.svg" alt="Usually one loop runs everything and calls the model for all of it. With Conky nothing is in charge: pages notice each other and respond." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-4-history.dark.svg"><img src="docs/assets/figures/row-4-history.light.svg" alt="Usually, to learn why it did that, you grep the logs and pray. With Conky every change is signed and says what caused it, so you can blame an agent." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-5-leaving.dark.svg"><img src="docs/assets/figures/row-5-leaving.light.svg" alt="Usually it grew until it could not be moved. With Conky it is a folder and its history: pick it up and go." width="800"></picture></a></p>

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
