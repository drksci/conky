---
crest: "[[guard-warehouse]]"
engine: "guard"
target: "[[warehouse]]"
fuel: 5000
proof: "cert:smt:c2978e68dca9cac621efb5a730b3c2a49cf0b3275522c2d23e629a14f54049b8"
code: |
  cel: size(post.raw_markdown) <= 4096
seal: "sig:ed25519:forge_warehouse"
---
# Validator Port: `[[warehouse]]`
Ensures bounded execution and strict sprawl limits.
