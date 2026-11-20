# Contributing

conky is pre-alpha. Small, focused contributions are welcome. Read [CLAUDE.md](CLAUDE.md) first: its rules apply to people and agents alike.

## Setup

- Python 3.11 or newer, Git, and `ssh-keygen` (the tests need both Git and `ssh-keygen`).
- Install with `pip install -e '.[dev]'`.
- Enable the pre-push hook once: `git config core.hooksPath scripts/hooks`.

## Checks

Run all checks with:

```bash
scripts/check
```

The pre-push hook runs the same command and blocks the push if it fails. There is no hosted CI.

## Commits

Subjects are `<type>: <summary>` with type one of feat, fix, docs, test, refactor or chore. The summary starts lower-case, has no trailing full stop, and the whole subject is at most 72 characters.

## Picking work

Take the step marked `next` in [docs/project/roadmap.md](docs/project/roadmap.md). There is exactly one.

## What a change must include

The pull request template's Done when list:

- `scripts/check` passes.
- Docs updated in the same change.
- A decision recorded if the design changed.
- Status and roadmap updated.
- A changelog line added if behaviour changed.

Every new invariant comes with a test that fails without it. Label stubs honestly: name them `stub` and say so in the doc comment.

## Licence

By contributing, you agree that your contributions are licensed under the
same terms as the project: MIT or Apache-2.0, at the user's option.
