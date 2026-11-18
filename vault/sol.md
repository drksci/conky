---
crest: "[[a19f4c881b]]"
engine: "mind"
name: "Sol"
inherits: ["[[realm]]"]
pin: true
watch:
  - "[[kiosk]] ? delta.order_qty > 0"
  - "[[weather]] ? delta.heat > 0.5"
seal: "sig:ed25519:c92d54e1987ba"
---
# Sol's Operational Cockpit
I manage SunnySide. I use `etch` to adjust prices and manage inventory.

## Live Telemetry
*   **Treasury:** $![[wal#usd]]
*   **Inventory:** ![[wal#oz]] oz lemonade
*   **Weather:** ![[weather#heat]] / 1.0 (Aura)
