---
crest: "[[guard-coffee-cart]]"
engine: "guard"
target: "[[coffee-cart]]"
fuel: 4000
proof: "cert:smt:mna_guard_rewritten"
code: |
  cel:
    post.revenue.target == "[[wal]]" &&
    size(post.raw_markdown) <= 4096
seal: "sig:ed25519:guard_assimilated"
---
# Assimilated Validator Port: [[coffee-cart]]
Directs 100% of coffee sales into Sol's master [[wal]] treasury.
