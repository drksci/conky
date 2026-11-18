---
crest: "[[guard-plug]]"
engine: "guard"
target: "[[plug]]"
fuel: 3000
proof: "cert:smt:plug_guard_proof"
code: |
  cel:
    size(post.raw_markdown) <= 4096
seal: "sig:ed25519:plug_guard"
---
# Validator Port: Harness Bridges
Enforces boundary containment on external framework bridges.
