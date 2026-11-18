---
crest: "[[contract-bulk-lemons]]"
engine: "gear"
gate:
  - { role: "buyer", by: "[[sol]]", seal: "sig:ed25519:sol_futures_ratified" }
  - { role: "seller", by: "[[supplier_citrus]]", seal: "sig:ed25519:supplier_citrus_futures_ratified" }
guard: "[[guard-contract-bulk-lemons]]"
terms: { lemons_lb: 500.0, price_usd: 100.00 }
seal: "sig:ed25519:contract_dual_sealed"
---
# Bilateral Citrus Futures Contract
Binds Sol and Supplier Citrus to 500 lb lemons at $0.20/lb fixed price, bypassing ambient price squeeze.
