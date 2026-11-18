---
crest: "[[view-wal]]"
engine: "view"
target: "[[wal]]"
guard: "[[guard-view-wal]]"
gate:
  - { role: "owner", by: "[[@owner]]", seal: "sig:ed25519:99e412c0" }
stream: "pulse://[[wal]]"
a2ui:
  version: "0.8"
  surfaceId: "sunnyside-wal-hud"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["kpi-row", "margin-spark", "inject-btn"] } } }
    - id: "kpi-row"
      component: { Row: { children: { explicitList: ["cash-gauge", "oz-gauge", "cpu-gauge"] } } }
    - id: "cash-gauge"
      component: { MetricCard: { label: "Net Cash", value: { path: "/vaults/usd" }, prefix: "$", trend: "stream" } }
    - id: "oz-gauge"
      component: { ProgressGauge: { label: "Pitcher Stock", value: { path: "/vaults/oz" }, max: 160.0, unit: "oz" } }
    - id: "cpu-gauge"
      component: { MetricCard: { label: "AI Compute Left", value: { path: "/vaults/cpu" }, prefix: "$" } }
    - id: "margin-spark"
      component: { Sparkline: { label: "Hourly Net Margin", source: "[[pnl-notebook#hourly_series]]" } }
    - id: "inject-btn"
      component: { ActionButton: { label: "Inject $25 Float", action: "etch:[[wal]]/float", requireGate: "[[@owner]]" } }
seal: "sig:ed25519:71d209ab"
---
# A2UI View Port: `[[wal]]`
Streams real-time treasury, pitcher volume, and inference spend widgets to Obsidian and mobile `voice` clients.
