---
crest: "[[view-pitcher]]"
engine: "view"
target: "[[pitcher]]"
guard: "[[guard-pitcher]]"
stream: "pulse://[[pitcher]]"
a2ui:
  version: "0.8"
  surfaceId: "pitcher-gauge"
  components:
    - id: "root"
      component: { ProgressGauge: { label: "Pitcher Level", value: { path: "/level_oz" }, max: 160.0, unit: "oz" } }
seal: "sig:ed25519:pitcher_init"
---
# A2UI View Port: `[[pitcher]]`
Streams real-time 20Hz pour gauge updates.
