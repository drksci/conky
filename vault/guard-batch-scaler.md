---
crest: "[[guard-batch-scaler]]"
engine: "guard"
target: "[[batch-scaler]]"
fuel: 5000
proof: "cert:smt:7ed1fc05c23822d0801e9217183e8f245a1fcba89cb5241d30b8cf6dfc1079b0"
code: |
  cel: size(post.raw_markdown) <= 4096
seal: "sig:ed25519:forge_batch-scaler"
---
# Validator Port: `[[batch-scaler]]`
Ensures bounded execution and strict sprawl limits.
