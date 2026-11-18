---
crest: "[[guard-pitcher]]"
engine: "guard"
target: "[[pitcher]]"
fuel: 2000
proof: "cert:smt:pitcher_proof"
code: |
  cel:
    post.level_oz >= 0.0 &&
    post.level_oz <= 160.0
seal: "sig:ed25519:pitcher_init"
---
# Validator Port: `[[pitcher]]`
Bounds pitcher fluid capacity between 0 and 160 oz.
