---
crest: "[[view-plug]]"
engine: "view"
target: "[[plug]]"
guard: "[[guard-plug]]"
stream: "pulse://plug"
a2ui:
  version: "0.8"
  surfaceId: "external-plug-hud"
  components:
    - id: "root"
      component: { MetricCard: { label: "Harness Adapter Status", value: { path: "/protocol" } } }
seal: "sig:ed25519:plug_view"
---
# A2UI View Port: Harness Bridges
Shows bridge activity and throughput.
