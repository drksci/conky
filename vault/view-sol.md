---
crest: "[[view-sol]]"
engine: "view"
target: "[[sol]]"
guard: "[[guard-view-sol]]"
stream: "pulse://[[sol]]"
a2ui:
  version: "0.8"
  surfaceId: "sunnyside-sol-cockpit"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["operator-header", "state-row", "chat-stream"] } } }
    - id: "operator-header"
      component: { MetricCard: { label: "Operator", value: { path: "/name" } } }
    - id: "state-row"
      component: { Row: { children: { explicitList: ["price-gauge", "focus-gauge", "drive-gauge"] } } }
    - id: "price-gauge"
      component: { MetricCard: { label: "Price / Cup", value: { path: "/state/price" }, prefix: "$" } }
    - id: "focus-gauge"
      component: { ProgressGauge: { label: "Focus Tier", value: { path: "/focus" }, max: 1.0 } }
    - id: "drive-gauge"
      component: { MetricCard: { label: "Drive Strain", value: { path: "/drive/strain" } } }
    - id: "chat-stream"
      component: { Table: { label: "Recent Transmissions", source: "[[chat#window]]" } }
seal: "sig:ed25519:c92d54e1987ba"
---
# A2UI View Port: `[[sol]]`
Operator cockpit view projecting Sol's cognitive state and pricing posture.
