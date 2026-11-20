# Probe: overhead with the model held fixed

Class: mechanism.

- Asked of a harness: nothing beyond the scenario.
- The backend is `fixed`: each screen is answered with the answer recorded earlier for the same
  screen (`python -m bench.backends record RUN_DIR... --out answers.json`), the same for every
  arm, so the game unfolds the same way and only the harness differs.
- Score per input: model calls, tokens and bytes sent (pack, screen, scaffolding), wall time.
- A recording made from a stand-in backend is never used for a reported number.
- Run: `python -m bench.run --probe overhead --recording answers.json --arms conky,loop --out DIR`
