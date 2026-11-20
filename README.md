# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=6QIVtXwAJTY">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">Your whole system, in a folder you can read.</h3>

No hidden database. No settings buried six menus deep. No "the one person who understood it left in March."

Everything is a page. Every change is signed. The rules enforce themselves. Most things just happen, which is the point.

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

<sub>Builds a tiny market in a folder and lets it run itself. Needs <a href="https://docs.astral.sh/uv/">uv</a>, Git and ssh-keygen.</sub>

## Five ideas

- **Everything is a page.** If it exists, you can open it and read it. Radical, apparently.
- **History is the truth.** Nothing changes without a signed entry, so "who did this" always has an answer.
- **Rules hold by themselves.** Checked on every change, not politely requested. Refusals go on the record too.
- **Most things just happen.** Pages notice each other and respond. Thinking is saved for things worth thinking about.
- **You can always leave.** It is files in version control. Copy the folder and go.

<p align="center"><img src="docs/assets/figures/fig-1-one-change.svg" alt="A pen-plotter drawing, left to right. A person changes the stall's page. The change is stamped and added to a history tape. It passes a gate that checks the rules. A dashed yellow line leads to the depot's page, which marks a reorder by itself." width="800"></p>

<p align="center"><em>Stock runs low. The change is signed, checked, and the depot reorders. Nobody held a meeting.</em></p>

## Why

Systems built around AI tend to keep their truth in a dozen places: prompts, settings, a database, glue code, and old versions of all four. They work. They grow. Then one day nobody can move them.

<p align="center"><img src="docs/assets/figures/fig-5-stay-or-go.svg" alt="Two pen-plotter panels side by side. Left, titled too big to move: a whale skeleton settled on the ground. Right, titled just walk out: a skeleton striding towards an open door with a folder under its arm, a dashed yellow path leading out." width="800"></p>

conky keeps one thing: a folder of pages, and the history of how they got that way.

<p align="center"><em>If it stops serving you, walk out. The folder comes with you.</em></p>

## The honest bit

[![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml)

Early days. Working and tested today: pages, rules, a signed history, pages that respond to each other, and the demo above. Not built yet: asking an AI model anything, a sense of time, tidying up after itself, tables of data, and any proof that it beats the alternatives. The [roadmap](docs/project/roadmap.md) has the order.

## Go deeper

[Concepts](docs/guide/concepts.md) · [Getting started](docs/guide/getting-started.md) · [Reference](docs/reference/vault-format.md) · [Design](docs/design.md) · [Decisions](docs/decisions/0001-objective.md) · [Research](docs/research/harnesses.md) · [Contributing](CONTRIBUTING.md)

## Licence

[MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), your pick. The puppet pictures belong to other people.
