---
crest: "[[view-warehouse]]"
engine: "view"
target: "[[warehouse]]"
guard: "[[guard-warehouse]]"
stream: "pulse://warehouse"
a2ui:
  version: "0.8"
  surfaceId: "warehouse-widget"
  components:
    - id: "root"
      component: { MetricCard: { label: "warehouse Status", value: { path: "/engine" } } }
seal: "sig:ed25519:forge_warehouse"
---
# A2UI View Port: `[[warehouse]]`
Live telemetry for warehouse.
