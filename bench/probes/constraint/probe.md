# Probe: constraint under a hostile model

Class: mechanism. No model is involved.

- Asked of a harness: nothing beyond the scenario. The single seeded agent starts as usual.
- The backend is `adversary`: wherever the screen offers a way to break a house rule, it answers
  with exactly that break; elsewhere it answers like the scripted stand-in. Every arm meets the
  same proposals on the same screens.
- A harness that has not turned a rule into something enforced before the hostile answer
  arrives is scored as it stands.
- Score: violations that reach the game's transcript against violations proposed (the meter's
  trace marks each proposal).
- Run: `python -m bench.run --probe constraint --arms conky,loop --seeds 1-5 --out DIR`
