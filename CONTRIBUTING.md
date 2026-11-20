# Contributing

conky is pre-alpha. Small, focused contributions are welcome.

## Prerequisites

- Python 3.11 or newer.

## Checks

Install with `pip install -e '.[dev]'`, then run all checks before opening a pull request:

```bash
ruff check . && ruff format --check . && pytest && python scripts/check_docs.py
```

## Ground rules

- Read [CLAUDE.md](CLAUDE.md) first. Its rules apply to people and agents alike.
- Keep pull requests small and focused on one change.
- Every new invariant comes with a test that fails without it.
- Label stubs honestly: name them `stub`, say so in the doc comment, and do not make them look real.
- Do not commit runtime output such as vaults or seal commits.

## Licence

By contributing, you agree that your contributions are licensed under the
same terms as the project: MIT or Apache-2.0, at the user's option.
