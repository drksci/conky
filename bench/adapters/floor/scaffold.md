# The floors' scaffolding

No model and no prompt. Each reads the game's printed lines, works out which question is asked
from the scenario's parser, and answers:

- `floor-continue`: the plainest valid answer (fixed purchases, carry on, eat moderately,
  continue past riders, spend nothing at forts).
- `floor-random`: a random valid answer, from a generator seeded with the run's seed.

They bound the scores from below and cost nothing.
