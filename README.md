# conky

<p align="center">
  <img src="docs/assets/conky-hero.jpg" alt="A ventriloquist puppet in a sweater that reads conky, with the caption: You just remember I call the shots here, Bubbles." width="800">
</p>
<p align="center"><sub><a href="https://www.youtube.com/watch?v=Z1xFvF7zFBY">Trailer Park Boys: Conky</a></sub></p>

<h3 align="center">Your whole system, in a folder you can read.</h3>

Every person, team, tool and rule is a page. Every change is signed and kept. The rules enforce themselves. Most things happen by themselves, and nobody has to think about them.

```bash
uvx --from git+https://github.com/drksci/conky conky demo
```

That builds a small market in a folder and lets it run itself. It needs [uv](https://docs.astral.sh/uv/), Git and ssh-keygen.

[![CI](https://github.com/drksci/conky/actions/workflows/ci.yml/badge.svg)](https://github.com/drksci/conky/actions/workflows/ci.yml) *Early days. The core works and is tested. Most of the plan is still ahead.*

## Five ideas

- **Everything is a page.** If it exists, you can open it and read it.
- **History is the truth.** Nothing changes without a signed entry, so anything can be traced and anything can be put back.
- **Rules hold by themselves.** They are checked on every change. A change that breaks one is refused, and the refusal is kept too.
- **Most things just happen.** Pages notice each other and respond. Thinking is saved for what needs it.
- **You can always leave.** It is ordinary files in ordinary version control. Copy the folder and go.

<p align="center"><img src="docs/assets/figures/fig-1-one-change.svg" alt="A pen-plotter drawing, left to right. A person changes the stall's page. The change is stamped and added to a history tape. It passes a gate that checks the rules. A dashed yellow line leads to the depot's page, which marks a reorder by itself." width="800"></p>

<p align="center"><em>Stock runs low. The change is signed, checked, and the depot reorders. Nobody decided to.</em></p>

## Why

Most systems built around AI keep their truth in a dozen places at once: prompts, settings, a database, glue code, old versions of all four. They work, and they grow, and one day nobody can move them.

<p align="center"><img src="docs/assets/figures/fig-5-too-big-to-move.svg" alt="A pen-plotter plate of a whale skeleton settled on the ground. Leader lines name the places state gets stuck: settings, a hidden database, glue code, old versions and private formats. Beside it, much smaller, a folder of papers with a carry handle and a dashed yellow path leading off the frame." width="800"></p>

<p align="center"><em>It grew until it could not be moved.</em></p>

conky keeps one thing: a folder of pages and the history of how they came to say what they say. Any tool that reads files can read it. Any place that holds a folder can hold it.

<p align="center"><img src="docs/assets/figures/fig-6-walk-out.svg" alt="A pen-plotter drawing of a cheerful skeleton striding towards an open exit door, carrying a folder of papers by its handle. A pinned checklist reads: you can leave the tool, the host, the model, the runtime, even this one. A dashed yellow path leads out through the door." width="800"></p>

<p align="center"><em>So if it stops serving you, walk out. The folder comes with you.</em></p>

## Where it stands

Working today, with tests:

- Pages, grouped into spaces that hand their rules down.
- Rules checked on every change, with refusals kept.
- A signed history that can be verified and used to restore everything.
- Pages that respond to each other, and pages that watch themselves.
- A command line, and the demo above.

Not built yet:

- Pages that put a question to an AI model, with a choice of provider.
- Time, as something pages can respond to.
- Tidying up what has grown crowded or gone quiet.
- Tables of data beside the pages.
- Any measured comparison with other systems.

The order of work is in the [roadmap](docs/project/roadmap.md).

## Go deeper

| If you want | Read |
|---|---|
| The ideas, in plain language | [Concepts](docs/guide/concepts.md) |
| To try it by hand | [Getting started](docs/guide/getting-started.md) |
| The technical detail | [Reference](docs/reference/vault-format.md), [command line](docs/reference/cli.md), [rules and reactions](docs/reference/rules-and-reactions.md) |
| Why it is built this way | [Design](docs/design.md) and the [decision records](docs/decisions/0001-objective.md) |
| How it compares | [Research and comparisons](docs/research/harnesses.md) |
| To take part | [Contributing](CONTRIBUTING.md) |

## Licence

[MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), whichever you prefer. The pictures of the puppet are not covered by either.
