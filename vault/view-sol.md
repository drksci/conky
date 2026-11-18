---
crest: "[[view-sol]]"
engine: "view"
target: "[[sol]]"
stream: "pulse://sol"
a2ui:
  version: "0.8"
  surfaceId: "ceo-master-hud"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["kpi-row", "franchise-feed"] } } }
    - id: "kpi-row"
      component: { MetricCard: { label: "Enterprise Cash", value: { path: "/vaults/usd" } } }
    - id: "franchise-feed"
      component: { Table: { label: "South Bank Subsidiary", source: "[[pnl-southbank]]" } }
seal: "sig:ed25519:view_ceo"
---
# Sol CEO Enterprise Dashboard
Aggregates master treasury and South Bank franchise performance.
