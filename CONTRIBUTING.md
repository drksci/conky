# Contributing

conky is pre-alpha. Small, focused contributions are welcome.

## Prerequisites

- Stable Rust (with `rustfmt` and `clippy`).

## Checks

Run all three before opening a pull request:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
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
