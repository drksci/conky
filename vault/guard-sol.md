---
crest: "[[guard-sol]]"
engine: "guard"
target: "[[sol]]"
inherits: ["[[realm]]"]
fuel: 5000
proof: "cert:smt:4312fa89b1c7"
code: |
  cel:
    post.state.price >= 2.00 &&
    post.state.price <= 6.00 &&
    size(post.raw_markdown) <= 4096
seal: "sig:ed25519:c92d54e1987ba"
---
# Validator Port: `[[sol]]`
Guards Sol's autonomous actions: bounds price within realm bounds [$2.00..$6.00] and prevents prompt sprawl.
