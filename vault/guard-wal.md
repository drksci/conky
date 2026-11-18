---
crest: "[[guard-wal]]"
engine: "guard"
target: "[[wal]]"
inherits: ["[[realm]]"]
fuel: 5000
proof: "cert:smt:89f3c104e2b7a91d"
code: |
  cel:
    post.vaults.usd >= 0.0 &&
    post.vaults.oz >= 0.0 &&
    post.vaults.lb >= 0.0 &&
    post.vaults.cpu >= 0.0 &&
    size(post.raw_markdown) <= 4096 &&
    wal.is_balanced_parity == true
seal: "sig:ed25519:55b108e1"
---
# Validator Port: `[[wal]]`
Formally verified pre-commit guard proving non-negative vaults, $\le 4\text{KB}$ HUD compliance, and strict zero-sum `parity`.
