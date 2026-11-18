---
crest: "[[guard-pnl-notebook]]"
engine: "guard"
target: "[[pnl-notebook]]"
fuel: 3000
proof: "cert:smt:88812cfa09b"
code: |
  cel:
    post.sql.startsWith("SELECT") &&
    !post.sql.contains("DROP") &&
    !post.sql.contains("DELETE")
seal: "sig:ed25519:1b7a998124b"
---
# Validator Port: `[[pnl-notebook]]`
Read-only query guard ensuring SQL queries cannot mutate or drop tables.
