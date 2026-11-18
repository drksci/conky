---
crest: "[[realm-southbank]]"
engine: "realm"
inherits: ["[[realm]]"]
parent: "[[sol]]"
ward: ["wal.usd >= 0", "spend <= 50.00"]
gate:
  - { role: "ceo", by: "[[sol]]", threshold: 100.00 }
seal: "sig:ed25519:realm_southbank"
---
# South Bank Child Operational Realm
Tightly bounded sub-realm. Any expenditure > $100 requires Sol's CEO gate signature.
