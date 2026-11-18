---
crest: "[[view-realm]]"
engine: "view"
target: "[[realm]]"
guard: "[[guard-realm]]"
stream: "pulse://[[realm]]"
a2ui:
  version: "0.8"
  surfaceId: "sunnyside-realm-governance"
  components:
    - id: "root"
      component: { Column: { children: { explicitList: ["realm-title", "grants-card", "wards-card"] } } }
    - id: "realm-title"
      component: { MetricCard: { label: "Realm Policy", value: { path: "/engine" } } }
    - id: "grants-card"
      component: { Table: { label: "Active Grants", source: "[[realm#grant]]" } }
    - id: "wards-card"
      component: { Table: { label: "Constitutional Wards", source: "[[realm#ward]]" } }
seal: "sig:ed25519:10f4b39178ae9"
---
# A2UI View Port: `[[realm]]`
Governance and policy dashboard for `@owner`.
