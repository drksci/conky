<h3 align="center"><img src="docs/assets/conky-mark.png" alt="" width="48" height="48" align="absmiddle">&nbsp;<picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/name.dark.svg"><img src="docs/assets/figures/name.light.svg" alt="Conky" height="48" align="absmiddle"></picture></h3>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/tagline.dark.svg"><img src="docs/assets/figures/tagline.light.svg" alt="The unharnessed harness" height="30" align="absmiddle"></picture></p>

<p><img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="100%"><br><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

### Copy pasta

```
🍋 user@lemonstand ❯ uvx --from git+https://github.com/drksci/conky conky demo lemonade
```

```
🛸 user@thething ❯ uvx --from git+https://github.com/drksci/conky conky assimilate
```

<h3 align="center">Delete the harness. Keep the agents.</h3>

<p align="center">Agents, rules and data are all pages in one Git folder.<br>The pages notice each other and act. There is nothing else.</p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/demo.dark.svg"><img src="docs/assets/figures/demo.light.svg" alt="Left, a terminal playing the demo: Maya sets up a lemonade stand with one house rule, fills the cooler, a cup count below zero is refused, a busy hour empties the cooler and the supplier orders lemons by itself. Right, a wireframe of the same thing as a screen, in the pages' own words: the house rule, the cooler's count, the supplier's order and lines from the daybook, updating in step." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-oregon-trail.dark.svg"><img src="docs/assets/figures/fig-oregon-trail.light.svg" alt="A schematic in three panels. The game: Oregon Trail asks whether to stop at the next fort, hunt or continue. Conky: the screen changed, Ma read a pattern, Jed wants to hunt, a house rule refuses it, Ma says to push on, and the hands type 3. A2UI: the same moment as a screen, with the four travellers, the supplies and a note that Ma read The Art of War." width="800"></picture></p>

<p align="center"><sub>Four strangers, one wagon and a BASIC game from 1978. A schematic: the <a href="docs/guide/playing-a-program.md">connector</a> that plays a program works today, the party is next.</sub></p>


<br>


### tl;dr

Most agent systems are a model with machinery around it: prompts, orchestration code and a database, each holding part of the truth where nobody can read it.

Conky takes the machinery away. The system is its own documents. Pages notice each other and act, rules are enforced on every change, and the history of those changes is the only record. What is left for the model is the part worth having a model for: judgement, character and conversation.

It is plain files in Git, so you can read all of it, and you can take it and leave.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-0-folder.dark.svg"><img src="docs/assets/figures/fig-0-folder.light.svg" alt="An early Macintosh folder window titled Lemonade stand, in black and white. Inside are six page icons named stand, cooler, supplier, daybook, maya and sam. Dashed arrows run from stand to cooler to supplier, and the daybook has an arrow looping back to itself. The status line reads: 6 pages, running itself." width="800"></picture></p>

<br>

### Not another harness

Five places where the usual approach and Conky part ways. Left is the usual way, right is Conky, and the small print names the real parts, each sourced in the <a href="docs/research/harnesses.md">comparison</a>.

<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-1-truth.dark.svg"><img src="docs/assets/figures/row-1-truth.light.svg" alt="Usually the truth is spread across code, prompts, a database, and Dave. With Conky the truth is the pages, and there is nowhere else to look." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-2-rules.dark.svg"><img src="docs/assets/figures/row-2-rules.light.svg" alt="Usually rules are a strongly worded prompt, and hope. With Conky rules are checked on every change, and a model cannot talk its way past one." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-3-in-charge.dark.svg"><img src="docs/assets/figures/row-3-in-charge.light.svg" alt="Usually one loop runs everything and calls the model for all of it. With Conky nothing is in charge: pages notice each other and respond." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-4-history.dark.svg"><img src="docs/assets/figures/row-4-history.light.svg" alt="Usually, to learn why it did that, you grep the logs and pray. With Conky every change is signed and says what caused it, so you can blame an agent." width="800"></picture></a></p>
<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/row-5-leaving.dark.svg"><img src="docs/assets/figures/row-5-leaving.light.svg" alt="Usually it grew until it could not be moved. With Conky it is a folder and its history: pick it up and go." width="800"></picture></a></p>


<br>

<p align="center"><a href="docs/guide/concepts.md">Concepts</a> &nbsp;·&nbsp; <a href="docs/guide/getting-started.md">Getting started</a> &nbsp;·&nbsp; <a href="docs/reference/vault-format.md">Reference</a> &nbsp;·&nbsp; <a href="docs/design.md">Design</a> &nbsp;·&nbsp; <a href="docs/decisions/0001-objective.md">Decisions</a> &nbsp;·&nbsp; <a href="docs/research/harnesses.md">Research</a> &nbsp;·&nbsp; <a href="CONTRIBUTING.md">Contributing</a></p>

<p align="center"><sub>Early days: the <a href="docs/project/roadmap.md">roadmap</a> says what works and what is still to come.<br><a href="LICENSE-MIT">MIT</a> or <a href="LICENSE-APACHE">Apache-2.0</a>, your pick. The puppet pictures belong to other people.</sub></p>

<p align="center"><a href="https://github.com/drksci/conky/actions/workflows/ci.yml"><img src="https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg" alt="CI"></a></p>

<br>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-tri.dark.svg"><img src="docs/assets/figures/mark-tri.light.svg" alt="" width="60"></picture></p>

<p align="center"><sub>Brought to you by</sub><br><a href="https://drksci.com"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-drksci.dark.svg"><img src="docs/assets/figures/mark-drksci.light.svg" alt="d/rksci" width="110"></picture></a></p>
