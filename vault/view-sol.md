---
crest: "[[view-sol]]"
engine: "view"
target: "[[sol]]"
stream: "pulse://sol"
a2ui:
  version: "0.8"
  surfaceId: "winter-sol-hud"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["kpi-row", "steamer-gauge", "winter-notebook"] } } }
    - id: "kpi-row"
      component: { MetricCard: { label: "Winter Cash Flow", value: { path: "/vaults/usd" } } }
    - id: "steamer-gauge"
      component: { ProgressGauge: { label: "Cider Kettle Stock", value: { path: "/cider_oz" }, max: 200.0, unit: "oz" } }
    - id: "winter-notebook"
      component: { Table: { label: "Hot Beverage Performance", source: "[[pnl-hot-beverages]]" } }
seal: "sig:ed25519:view_winter"
---
# Sol Winter Operations Cockpit
Reconfigured for hot cider and artisan tea delivery.
