---
crest: "[[view-pnl-notebook]]"
engine: "view"
target: "[[pnl-notebook]]"
guard: "[[guard-pnl-notebook]]"
stream: "pulse://[[pnl-notebook]]"
a2ui:
  version: "0.8"
  surfaceId: "sunnyside-pnl-widget"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["pnl-table"] } } }
    - id: "pnl-table"
      component: { Table: { label: "Real-Time Unit PnL", source: "[[pnl-notebook]]" } }
seal: "sig:ed25519:1b7a998124b"
---
# A2UI View Port: `[[pnl-notebook]]`
Live DuckDB-projected profit and loss widget.
