# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub>The name comes from Conky, the puppet in the television series <em>Trailer Park Boys</em>. The still and the quote belong to the show's owners and are not covered by this repository's licence.</sub></p>

Try it. One command, nothing to set up beyond uv and Git:

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

It builds a small market in a folder and shows it running itself. It needs uv, Git 2.34 or newer and ssh-keygen.

*Early days: the core works and is tested; much is still to be built.*

[![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)

**A folder of plain documents that behaves like a living system: every change is recorded and signed, the rules are enforced for you, and most things simply happen without anyone having to think about them.**

## The idea in five lines

- **Everything is a page.** If it exists, it can be opened and read: a person, a team, a tool, a process, a rule.
- **History is the truth.** Nothing changes without a signed entry saying who changed what, so anything can be traced and put back.
- **Rules hold by themselves.** They are checked on every change, not left to good behaviour, and a refused change is recorded too.
- **Most things just happen.** Pages notice each other and respond; thinking, by a person or an AI model, is kept for what truly needs it.
- **It goes anywhere.** The whole thing is ordinary files in ordinary version control, with nothing to migrate and nothing to be locked into.

<p align="center"><img src="docs/assets/figures/fig-1-one-change.svg" alt="A pen-plotter drawing in five steps, left to right. A person changes the stall's page. The change is stamped and added to the history tape. It passes a gate that checks the rules. A dashed yellow line then leads to the depot's page, which marks a reorder by itself. Notes read: signed and recorded, checked every time, nobody had to decide." width="800"></p>

<p align="center"><em>Fig. 1. One change: signed and recorded, checked against the rules, and answered by another page with nobody deciding. Schematic, not data.</em></p>

## What it is

Pages are grouped into spaces, and a page follows the rules of the space it belongs to. Nothing is hidden in a program or a database.

Take a market stall that is running low on stock. Its page records the new level, a page for the depot is watching it, and the depot's page marks a reorder, with nobody deciding to. If someone tried to set the stock below zero, the market's rule would refuse the change, and the refusal would be kept in the history.

## Where it stands

Working and tested today:

- Pages, grouped into spaces that pass their rules down.
- Rules that are checked on every change, with refusals recorded.
- A signed history of every change, which can be checked and used to restore the pages.
- Pages that respond to each other without anyone being asked.
- Pages that keep track of their own size and growth.
- A command line to try all of this, and a demo that builds a small market and tells its story step by step.

Not built yet:

- Tables of data kept beside the pages.
- Anything that acts when a page becomes crowded.
- Pages that put a question to an AI model.
- Rules that look at several pages changed together.
- Measured comparisons with other systems. No measurements have been made.

The order of the remaining work is in the [roadmap](docs/project/roadmap.md).

## Go deeper

- [Concepts](docs/guide/concepts.md): the ideas in plain language.
- [Getting started](docs/guide/getting-started.md): a hands-on walkthrough.
- [Reference](docs/reference/vault-format.md): the technical detail, with the [command line](docs/reference/cli.md) and [rules and reactions](docs/reference/rules-and-reactions.md).
- [Design and decisions](docs/design.md): the overview and the [decision records](docs/decisions/0001-objective.md).
- [Research and comparisons](docs/research/harnesses.md): how conky relates to other systems and to published work.
- [Contributing](CONTRIBUTING.md): how to take part.

## The name

The name comes from a puppet who reminds the man holding him who calls the shots.

## Licence

Dual licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. The hero still and its quote are not covered by either.
