---
crest: "[[guard-contract-bulk-lemons]]"
engine: "guard"
target: "[[contract-bulk-lemons]]"
fuel: 4000
proof: "cert:smt:contract_futures_proof"
code: |
  cel:
    post.terms.price_usd == 100.00 &&
    post.terms.lemons_lb == 500.0 &&
    post.gate.exists(g, g.role == "buyer") &&
    post.gate.exists(g, g.role == "seller")
seal: "sig:ed25519:contract_guard"
---
# Validator Port: Futures Contract
Enforces dual-signature quorum gate before ledger shift execution.
