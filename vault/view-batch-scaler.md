---
crest: "[[view-batch-scaler]]"
engine: "view"
target: "[[batch-scaler]]"
guard: "[[guard-batch-scaler]]"
stream: "pulse://batch-scaler"
a2ui:
  version: "0.8"
  surfaceId: "batch-scaler-widget"
  components:
    - id: "root"
      component: { MetricCard: { label: "batch-scaler Status", value: { path: "/engine" } } }
seal: "sig:ed25519:forge_batch-scaler"
---
# A2UI View Port: `[[batch-scaler]]`
Live telemetry for batch-scaler.
