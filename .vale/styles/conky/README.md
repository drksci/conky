# The conky house style

Vale rules for the published prose: README, CONTRIBUTING, CHANGELOG, SECURITY, CLAUDE.md and `docs/`. They name the habits that make writing read as padded or generated: stock phrases, hype, first person plural, dashes as punctuation, rhetorical questions, hedges and long sentences.

- `error` rules fail `scripts/check`. `warning` and `suggestion` rules are reported by `vale .` and read by a person.
- Each file holds one rule and starts with a comment saying why.
- To add a term, append it to `tokens` in `StockPhrases.yml` (errors) or `Hedges.yml` (warnings). Matching ignores case. Run `vale .` to see the effect.
- To exempt a file or block, add a section to `.vale.ini` at the repository root, for example `conky.Questions = NO`.
