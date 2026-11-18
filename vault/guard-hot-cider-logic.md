---
crest: "[[guard-hot-cider-logic]]"
engine: "guard"
target: "[[hot-cider-logic]]"
fuel: 5000
proof: "cert:smt:cf6a86504146bbad22729372170bfeb73059d94963416c5f19729d0e53a8fc3d"
code: |
  cel: size(post.raw_markdown) <= 4096
seal: "sig:ed25519:forge_hot-cider-logic"
---
# Validator Port: `[[hot-cider-logic]]`
Ensures bounded execution and strict sprawl limits.
