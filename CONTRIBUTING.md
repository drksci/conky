# Contributing

Small, focused contributions are welcome. Read [CLAUDE.md](CLAUDE.md) first: its rules apply to people and agents alike.

## Setup

- Python 3.11 or newer, Git, and `ssh-keygen`. The tests need both.
- Install with `pip install -e '.[dev]'`.
- Enable the pre-push hook once: `git config core.hooksPath scripts/hooks`.

## Checks

Run all checks with:

```bash
scripts/check
```

The pre-push hook runs it and blocks the push on failure. CI runs it on every pull request and on pushes to `main`. The hook is local configuration and is not cloned, so each clone enables it once.

`scripts/check` runs six things: `ruff check`, `ruff format --check`, the tests, `scripts/check_docs.py`, the prose check below and `scripts/check_commits.py`. Ruff selects the rule sets E, F, I, B, UP and SIM with a line length of 100.

## Prose

[Vale](https://vale.sh), which `pip install -e '.[dev]'` installs, lints published Markdown against the house style in `.vale/styles/conky/`. Errors fail `scripts/check`: stock phrases and hype words, first person plural, em and en dashes, exclamation marks and rhetorical questions. Warnings and suggestions cover hedges, "there is" openers, "not only ... but" constructions and sentences over 35 words. Read them and decide.

- `scripts/check` runs `vale --minAlertLevel=error` on the README, CONTRIBUTING, CHANGELOG, SECURITY, CLAUDE.md and `docs/`.
- `vale .` reports every level.

## Commits

Subjects are `<type>: <summary>`, with type one of feat, fix, docs, test, refactor or chore. The summary starts lower-case, has no trailing full stop, and the whole subject is at most 72 characters.

## Picking work

Take the step marked `next` in [docs/project/roadmap.md](docs/project/roadmap.md). Each step has a stable id and a state of `done`, `next` or `later`. Exactly one is `next`, and `scripts/check_docs.py` checks it.

## What a change must include

The pull request template's Done when list:

- `scripts/check` passes.
- Docs updated in the same change.
- A decision recorded if the design changed.
- Status and roadmap updated.
- A changelog line added if behaviour changed. The changelog follows Keep a Changelog and has an `## [Unreleased]` heading.

Every new invariant comes with a test that fails without it. Label stubs honestly: name them `stub` and say so in the doc comment.

## Figures

The maintainers generate the figures under `docs/assets/figures/` and commit them as SVG. Do not edit them by hand; to propose one, describe it in an issue or pull request.

## Licence

By contributing, you agree that your contributions are licensed under the
same terms as the project: MIT or Apache-2.0, at the user's option.
