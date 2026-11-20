# Golden vault

`v1.bundle` is a Git bundle of a small vault made with this version of conky: a space with rules, a member page, a refused write, a reaction, a measure and an embed, all at fixed instants. `v1.pages.json` maps each page name to the exact text of its file.

This is a deliberate fixture, not runtime output. `tests/test_laws.py` clones the bundle, runs `verify` and compares every page. Future versions must keep reading it; if one cannot, the change is a break in the vault format and needs a decision record first. Do not regenerate the bundle to make a test pass.
