---
crest: "[[guard-realm]]"
engine: "guard"
target: "[[realm]]"
fuel: 10000
proof: "cert:smt:0000000000000000"
code: |
  cel:
    post.ward.exists(w, w == "wal.usd >= 0") &&
    post.ward.exists(w, w == "wal.oz >= 0")
seal: "sig:ed25519:10f4b39178ae9"
---
# Validator Port: `[[realm]]`
Constitutional root validator. Ensures invariants and escalation paths cannot be abolished.
