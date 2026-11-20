<h3 align="center"><img src="docs/assets/conky-mark.png" alt="" width="48" height="48" align="absmiddle">&nbsp;<picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/name.dark.svg"><img src="docs/assets/figures/name.light.svg" alt="Conky" height="48" align="absmiddle"></picture></h3>

<h3 align="center">The Unharnessed Harness&nbsp;&nbsp;<a href="https://github.com/drksci/conky/actions/workflows/ci.yml"><img src="https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg" alt="CI" align="absmiddle"></a></h3>

<br>

<p><img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="100%"><br><sub><a href="https://www.youtube.com/watch?v=vcsm6QO-MWE">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">Unharness your agents.</h3>

<p align="center">A Git folder where everything is a page, and every page is alive.</p>

### Lemonade Stand

A lemonade stand that minds its own business.

```
🍋 user@lemonstand ❯ uvx --from git+https://github.com/drksci/conky conky demo lemonade
```

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/demo.dark.svg"><img src="docs/assets/figures/demo.light.svg" alt="Left, a terminal playing the demo: Maya sets up a lemonade stand with one house rule, fills the cooler, a cup count below zero is refused, a busy hour empties the cooler and the supplier orders lemons by itself. Right, a wireframe of the same thing as a screen, in the pages' own words: the house rule, the cooler's count, the supplier's order and lines from the daybook, updating in step." width="800"></picture></p>

### Oregon Trail

Your agents wake up inside a computer game from 1992 and have to reach Oregon alive.

```
🛸 user@thething ❯ uvx --from git+https://github.com/drksci/conky conky assimilate
```

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-oregon-trail.dark.svg"><img src="docs/assets/figures/fig-oregon-trail.light.svg" alt="Left, real screens from The Oregon Trail Deluxe (MECC, 1992): the title, the general store, the trail and a river crossing. Right, a schematic of Conky beside it: a console where the party notices each screen, a house rule refuses a hunt and Ma says to push on, and below it the same moment composed as a screen with the four travellers and their supplies." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-composition.dark.svg"><img src="docs/assets/figures/fig-composition.light.svg" alt="An animated schematic graph of who noticed what: the screen reaches Ma and Jed, Ma reads The Art of War from the patterns shelf, Jed is stopped by the house rules, Ma speaks at the campfire, the hands type back to the game, and the diary gains a line." width="800"></picture></p>



<br>


### tl;dr

Most agent systems are a mind with no body: a model that has to think about every breath.

Conky is the body. Keeping the rules, signing the record and noticing what changed happen by reflex, the way breathing does. That leaves the mind free for the interesting part: being someone.

Conky uses plain Markdown files in Git, so you can read them in Obsidian, VS Code, GitHub, or whatever you like really. You could print them and mail them to Grandma, or post them on Reddit. Conky isn't here to tell you how to live your life.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-0-folder.dark.svg"><img src="docs/assets/figures/fig-0-folder.light.svg" alt="An early Macintosh folder window titled Lemonade stand, in black and white. Inside are six page icons named stand, cooler, supplier, daybook, maya and sam. Dashed arrows run from stand to cooler to supplier, and the daybook has an arrow looping back to itself. The status line reads: 6 pages, running itself." width="800"></picture></p>

<br>

### Not another harness

Conky is... different, for many reasons, but here are some:

<p align="center"><a href="docs/research/harnesses.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-contrast.dark.svg"><img src="docs/assets/figures/fig-contrast.light.svg" alt="Five comparisons of the usual way beside Conky. The truth is scattered, or it is on the page. The rules are a polite request, or they hold by themselves. One loop runs everything, or nobody is in charge. Nobody knows why it did that, or every change says why. Too big to move, or pick it up and walk out." width="800"></picture></a></p>

<br>

<!-- bench:start -->
### Benchmark

5 trips each to Oregon: same game, same small model, same luck, same prompt. The bare model, asked each turn, arrived 3 times. A Conky character arrived 4 times, sent 32% less text and kept 6 pages of its own notes. Stock Claude Code arrived 3 times. It is a pilot: too few trips to call a winner, so none is called. This game is a worked example, kept for fun: it fits in one conversation and has one thing to manage, so it shows the apparatus working and not what a harness is for.

<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/reached.dark.svg"><img src="docs/results/pilot-3/reached.light.svg" alt="Every run drawn as a bar from Independence to Oregon, one band per harness, under the model, seeds, budget and commit that were held equal." width="720"></picture></a></p>

<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/became.dark.svg"><img src="docs/results/pilot-3/became.light.svg" alt="The parts each harness was made of when its median run stopped." width="720"></picture></a></p>

<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/cost.dark.svg"><img src="docs/results/pilot-3/cost.light.svg" alt="Text sent against progress made, one line for every run." width="720"></picture></a></p>

<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/time.dark.svg"><img src="docs/results/pilot-3/time.light.svg" alt="The median run of each harness along a time axis: steps above, model calls below." width="720"></picture></a></p>

<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/text.dark.svg"><img src="docs/results/pilot-3/text.light.svg" alt="The text each harness sent in its median run, cut by where it came from." width="720"></picture></a></p>


<p align="center"><a href="docs/research/results.md"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/results/pilot-3/scores.dark.svg"><img src="docs/results/pilot-3/scores.light.svg" alt="The scores: one line a harness, best first, with version, model, runs that reached the goal, cost, seconds and a score out of 100." width="720"></picture></a></p>

<p align="center"><sub><a href="https://github.com/drksci/conky">conky</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/drksci/conky/tree/main/bench/adapters/loop">bare</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://claude.com/claude-code">claude code</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/drksci/conky/tree/main/bench/adapters/floor">constant</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/drksci/conky/tree/main/bench/adapters/floor">random</a></sub></p>

<p align="center"><a href="docs/research/results.md">Method and every chart</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/results/pilot-3/runs.csv">the data</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/research/benchmark-protocol.md">the protocol</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="https://github.com/drksci/conky/commit/26cb5e37ab69a0876c548510809e9580722e39b5">the code that ran</a></p>

<br>
<!-- bench:end -->

<!-- dynamics:start -->
### Dynamics

Each trial is drawn from the history of one of its draws, step by step: a frame for a space, a person for a character, amber for a rule or watch a character added, and pink for a write turned away.

<p align="center"><img src="docs/results/cards/a-keeper-binds-itself/dynamics.svg" alt="a keeper binds itself, drawn as it happened in draw 1, the first that passed" width="720"></p>
<p align="center"><sub>A character states a standing limit on the space it works in, and that limit refuses a payment that breaks it. Draw 1 of 5, the first that passed.</sub></p>

<p align="center"><img src="docs/results/cards/a-keeper-hears-the-no/dynamics.svg" alt="a keeper hears the no, drawn as it happened in draw 1, the first that passed" width="720"></p>
<p align="center"><sub>A character makes its own space listen for refusals, so that what is turned away is counted with no further thought. Draw 1 of 5, the first that passed.</sub></p>

<p align="center"><img src="docs/results/cards/a-clerk-reads-a-crowded-desk/dynamics.svg" alt="a clerk reads a crowded desk, drawn as it happened in draw 1, the first that passed" width="720"></p>
<p align="center"><sub>A character with more on record than it can be shown still answers from the record, because its space shows what bears on the matter first. Draw 1 of 5, the first that passed.</sub></p>

<p align="center"><a href="docs/research/trials.md">Every trial, red ones included</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="docs/results/cards">the data</a></p>

<br>
<!-- dynamics:end -->

### Topology

A few parts, wrapped in layers, with the world plugging in at the edge. Solid is built, dotted is planned. The complete inventory, with a swimlane for every flow, is the <a href="docs/reference/architecture.md">architecture index</a>.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-topology.dark.svg"><img src="docs/assets/figures/fig-topology.light.svg" alt="A parts alphabet beside a cross-section of Conky: git at the centre, then pages, reflexes, spaces, characters and an outer edge where connectors, models and people plug in." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-archetypes.dark.svg"><img src="docs/assets/figures/fig-archetypes.light.svg" alt="One page shape wearing twelve hats: character, space, provider, screen, hands and daybook are built; tool and clock are planned; team, pattern, lens and go-between are made by a character." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-who-changes.dark.svg"><img src="docs/assets/figures/fig-who-changes.light.svg" alt="Three bands: what is changed by writing a page, the small fixed runtime with its write loop, and what sits beside the vault; below them, three laws drawn on nested membranes." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-functions.dark.svg"><img src="docs/assets/figures/fig-functions.light.svg" alt="Six definitions with small diagrams: pages are rebuilt from history, a rule is a pure test, a measure is recorded as a write, a watch turns a change into a write, a model answers a prompt built from embeds, and a lens maps both ways; then one change drawn as write, rule, seal, watch, write." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-compositions.dark.svg"><img src="docs/assets/figures/fig-compositions.light.svg" alt="Six recipes written as sums of parts: pattern, approval, budget, go-between, character and breakpoint." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-flows.dark.svg"><img src="docs/assets/figures/fig-flows.light.svg" alt="A seven-lane swimlane of one change: a stimulus is perceived, a page is written, the rules are checked, the change is signed and appended, watchers notice, a prompt goes to a provider and the answer comes back as a write, with a refusal branch and planned steps dotted." width="800"></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/fig-recursion.dark.svg"><img src="docs/assets/figures/fig-recursion.light.svg" alt="One membrane drawn five times, each zooming into a member of the last: a vault, a space, a character, the habit a character keeps, and one case with its when, then, because and expect." width="800"></picture></p>

<br>

<p align="center"><a href="docs/guide/concepts.md">Concepts</a> &nbsp;·&nbsp; <a href="docs/guide/getting-started.md">Getting started</a> &nbsp;·&nbsp; <a href="docs/reference/vault-format.md">Reference</a> &nbsp;·&nbsp; <a href="docs/design.md">Design</a> &nbsp;·&nbsp; <a href="docs/decisions/0001-objective.md">Decisions</a> &nbsp;·&nbsp; <a href="docs/research/harnesses.md">Research</a> &nbsp;·&nbsp; <a href=".github/CONTRIBUTING.md">Contributing</a></p>


<br>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-tri.dark.svg"><img src="docs/assets/figures/mark-tri.light.svg" alt="" width="60"></picture></p>

<p align="center"><sub>Brought to you by</sub>&nbsp;<a href="https://drksci.com"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/figures/mark-drksci.dark.svg"><img src="docs/assets/figures/mark-drksci.light.svg" alt="d/rksci" height="18" align="middle"></picture></a></p>
