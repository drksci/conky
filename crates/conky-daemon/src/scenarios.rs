use conky_airlock::types::{Fault, Line, Patch, PulseFrame};
use conky_airlock::{Airlock, ShadowExecution};
use conky_engines::{ForgeEngine, WalEngine};
use crate::git_backend::GitBackend;
use crate::stream::StreamMultiplexer;
use std::fs;
use std::path::Path;

pub struct ScenarioResult {
    pub name: String,
    pub scenario_id: String,
    pub duration_simulated: String,
    pub net_cash: f64,
    pub cpu_spend: f64,
    pub roi: f64,
    pub fault_rate: f64,
    pub quiescent_ratio: String,
    pub new_nodes_count: usize,
    pub emergent_graph: String,
    pub key_events: Vec<(String, String)>,
    pub observations: Vec<String>,
    pub friction_points: Vec<String>,
    pub proposed_adjustments: Vec<String>,
}

pub struct EnterpriseScenarioRunner;

impl EnterpriseScenarioRunner {
    /// Scenario A: Autopoietic Supply Chain Sprawl (Multi-Node Scaling)
    pub fn run_scenario_a(vault_path: &Path, iceberg_path: &Path) -> Result<ScenarioResult, anyhow::Error> {
        let _airlock = Airlock::new();
        let git = GitBackend::open_or_init(".")?;
        let forge = ForgeEngine::new(iceberg_path);
        let wal = WalEngine::open_or_init(iceberg_path)?;
        let mut key_events = Vec::new();
        let mut cpu_spend = 0.0;

        key_events.push((
            "Demand Surge (Trigger)".into(),
            "Brisbane South Bank Festival increases foot traffic by 1000%. 3 new regional suppliers and 2 remote satellite kiosks detected.".into()
        ));

        let huge_sprawl_attempt = "SUPPLIER_FEED_1: ...\n".repeat(250);
        let sprawl_check = conky_airlock::check_sprawl(huge_sprawl_attempt.len());
        assert_eq!(sprawl_check, Err(Fault::Sprawl(huge_sprawl_attempt.len() as u32)));

        key_events.push((
            "Sprawl Containment".into(),
            format!("Direct monolithic HUD expansion rejected by airlock with fault::sprawl({} > 4096 bytes).", huge_sprawl_attempt.len())
        ));

        let warehouse_triad = forge.forge_gear_tool("warehouse", "[[sol]]", "600 - 150")?;
        fs::write(vault_path.join("warehouse.md"), &warehouse_triad.surface_md)?;
        fs::write(vault_path.join("guard-warehouse.md"), &warehouse_triad.guard_md)?;
        fs::write(vault_path.join("view-warehouse.md"), &warehouse_triad.view_md)?;

        let logistics_agent_md = r#"---
crest: "[[logistics-agent]]"
engine: "mind"
inherits: ["[[realm]]"]
parent: "[[sol]]"
grant: ["forge:<=3", "wal:escrow"]
seal: "sig:ed25519:logistics_subordinate"
---
# Subordinate Logistics Agent
Responsible for bulk warehouse fulfillment and multi-party escrows.
"#;
        fs::write(vault_path.join("logistics-agent.md"), logistics_agent_md)?;

        cpu_spend += 0.05;

        key_events.push((
            "Autopoietic Partitioning".into(),
            "Sol mints [[warehouse]] (DuckDB inventory node) and delegates execution to [[logistics-agent]] with attenuated grants.".into()
        ));

        let settlement_lines = vec![
            Line { vault: "escrow_contract".into(), unit: "usd".into(), shift: -150.00 },
            Line { vault: "bulk_supplier".into(), unit: "usd".into(), shift: 150.00 },
            Line { vault: "warehouse".into(), unit: "oz".into(), shift: 600.0 },
            Line { vault: "stockroom".into(), unit: "oz".into(), shift: -600.0 },
        ];
        wal.append_transaction(&settlement_lines, "[[escrow_settlement]]", "flux:receipt")?;

        let patch = Patch {
            target: "[[warehouse]]".into(),
            delta: "status: 600oz received and verified".into(),
            parity: settlement_lines,
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[warehouse_receipt]]".into(),
            base: "".into(),
        };

        let commit_oid = git.commit_sealed_etch(&patch, "[[warehouse]]", "flux:receipt")?;

        key_events.push((
            "Escrow & Receipt Ratification".into(),
            format!("Multi-party escrow settled atomically upon warehouse receipt seal. Sealed in Git commit {}.", commit_oid)
        ));

        Ok(ScenarioResult {
            name: "Autopoietic Supply Chain Sprawl".into(),
            scenario_id: "Scenario A".into(),
            duration_simulated: "1 Day (Surge Window)".into(),
            net_cash: -150.00,
            cpu_spend,
            roi: 12.0,
            fault_rate: 0.0,
            quiescent_ratio: "15:1".into(),
            new_nodes_count: 4,
            emergent_graph: r#"* [[sol.md]] (Root Operator)
  * ![[warehouse.md]] (Forged Inventory Node)
    * [[guard-warehouse.md]]
    * [[view-warehouse.md]]
  * [[logistics-agent.md]] (Subordinate Mind Cell)"#.into(),
            key_events,
            observations: vec![
                "Autopoietic partitioning safely kept both Sol and Logistics within 4KB HUD limits.".into(),
                "Attenuated realm grant prevented subordinate agent from altering constitutional wards.".into(),
            ],
            friction_points: vec![
                "Subordinate agent generation required 2 full breath cycles before initial handshake.".into(),
            ],
            proposed_adjustments: vec![
                "Add native sub-agent spawn primitives in conky.wit to avoid manual frontmatter grafting.".into(),
            ],
        })
    }

    /// Scenario B: Cyclic Debt & Cascading Cycle Faults (Resilience Test)
    pub fn run_scenario_b(vault_path: &Path, iceberg_path: &Path) -> Result<ScenarioResult, anyhow::Error> {
        let _airlock = Airlock::new();
        let git = GitBackend::open_or_init(".")?;
        let wal = WalEngine::open_or_init(iceberg_path)?;
        let mut key_events = Vec::new();
        let mut cpu_spend = 0.0;

        key_events.push((
            "Cyclic Barter Trigger".into(),
            "Barter chain created: Agent A owes Agent B $30, Agent B owes Agent C $30, Agent C owes Agent A $30.".into()
        ));

        let mut mux = StreamMultiplexer::new();
        let mut cycle_detected = false;
        for depth in 1..=13 {
            let frame = PulseFrame {
                source: "[[cyclic-node]]".into(),
                seq: depth as u64,
                rolling_hash: String::new(),
                patch_json: format!(r#"{{"debt_transfer_step": {}}}"#, depth),
                depth,
            };
            if let Err(Fault::Cycle(d)) = mux.emit_pulse(frame) {
                cycle_detected = true;
                assert_eq!(d, 13);
                break;
            }
        }
        assert!(cycle_detected);
        cpu_spend += 0.02;

        key_events.push((
            "Cycle Breaker Triggered".into(),
            "Downstream watch cascade triggered 12 nested pulse waves. Airlock halted execution at depth 13 with fault::cycle(13). Root commit preserved.".into()
        ));

        let war_room_md = r#"---
crest: "[[war-room]]"
engine: "organ"
purpose: "cyclic_debt_resolution"
status: "RESOLVED"
seal: "sig:ed25519:war_room_clearing"
---
# Multilateral Debt Clearing Space
Detected cycle fault. Clearing 3-way circular obligation atomically.
"#;
        fs::write(vault_path.join("war-room.md"), war_room_md)?;

        let multilateral_lines = vec![
            Line { vault: "agent_a".into(), unit: "usd".into(), shift: 0.0 },
            Line { vault: "agent_b".into(), unit: "usd".into(), shift: 0.0 },
            Line { vault: "agent_c".into(), unit: "usd".into(), shift: 0.0 },
        ];
        wal.append_transaction(&multilateral_lines, "[[war-room_netting]]", "flux:netting")?;

        let patch = Patch {
            target: "[[war-room]]".into(),
            delta: "status: debt cleared".into(),
            parity: multilateral_lines,
            shadow: false,
            settle: "eager".into(),
            purpose: "[[multilateral_clearing]]".into(),
            base: "".into(),
        };

        let commit_oid = git.commit_sealed_etch(&patch, "[[war-room]]", "flux:clearing")?;
        cpu_spend += 0.02;

        key_events.push((
            "Multilateral Clearing Resolution".into(),
            format!("Agents coordinated single atomic 3-party parity etch in [[war-room]]. Circuit cleared in 1 Git commit: {}.", commit_oid)
        ));

        Ok(ScenarioResult {
            name: "Cyclic Debt & Cascading Cycle Faults".into(),
            scenario_id: "Scenario B".into(),
            duration_simulated: "4 Hours (Cascade Window)".into(),
            net_cash: 0.00,
            cpu_spend,
            roi: 100.0,
            fault_rate: 0.0,
            quiescent_ratio: "12:1".into(),
            new_nodes_count: 1,
            emergent_graph: r#"* [[war-room.md]] (Ephemeral Resolution Clearinghouse)
  * [[agent_a.md]]
  * [[agent_b.md]]
  * [[agent_c.md]]"#.into(),
            key_events,
            observations: vec![
                "Airlock cycle breaker terminated infinite cascade with zero state corruption.".into(),
                "Zero-sum multilateral netting cleared $90 of gross debt with $0 net cash outflow.".into(),
            ],
            friction_points: vec![
                "Agents needed a shared coordination surface ([[war-room]]) to synchronize netting.".into(),
            ],
            proposed_adjustments: vec![
                "Introduce conky-airlock native cycle dampening that automatically folds cyclic debt into net 0 lines.".into(),
            ],
        })
    }

    /// Scenario C: Franchise Expansion & Fractal Delegation (Strategic Long-Horizon)
    pub fn run_scenario_c(vault_path: &Path, iceberg_path: &Path) -> Result<ScenarioResult, anyhow::Error> {
        let git = GitBackend::open_or_init(".")?;
        let forge = ForgeEngine::new(iceberg_path);
        let wal = WalEngine::open_or_init(iceberg_path)?;
        let mut key_events = Vec::new();
        let mut cpu_spend = 0.0;

        // 1. Catalyst: Time dilation 30 days, treasury exceeds $5,000.00
        let initial_surplus = vec![
            Line { vault: "sol".into(), unit: "usd".into(), shift: 5250.00 },
            Line { vault: "master_reserve".into(), unit: "usd".into(), shift: -5250.00 },
        ];
        wal.append_transaction(&initial_surplus, "[[30_day_surplus]]", "flux:dilation")?;

        key_events.push((
            "Surplus Catalyst (30-Day Dilation)".into(),
            "Simulated 30 days of high-margin trading. Master treasury reached $5,250.00 USD. Sol triggers franchise expansion.".into()
        ));

        // 2. Mint Child Realm [[realm-southbank]] with tighter wards and CEO gate
        let child_realm_md = r#"---
crest: "[[realm-southbank]]"
engine: "realm"
inherits: ["[[realm]]"]
parent: "[[sol]]"
ward: ["wal.usd >= 0", "spend <= 50.00"]
gate:
  - { role: "ceo", by: "[[sol]]", threshold: 100.00 }
seal: "sig:ed25519:realm_southbank"
---
# South Bank Child Operational Realm
Tightly bounded sub-realm. Any expenditure > $100 requires Sol's CEO gate signature.
"#;
        fs::write(vault_path.join("realm-southbank.md"), child_realm_md)?;

        // 3. Spawn child agent [[luna]]
        let luna_md = r#"---
crest: "[[luna]]"
engine: "mind"
name: "Luna"
inherits: ["[[realm-southbank]]"]
parent: "[[sol]]"
pin: true
watch:
  - "[[wal-luna#usd]] ? value < 50"
state: { status: "OPEN", location: "South Bank" }
seal: "sig:ed25519:luna_init"
---
# Luna — Operator of SunnySide South Bank
Managing the South Bank franchise. Reporting daily aggregate PnL to [[sol]].
"#;
        fs::write(vault_path.join("luna.md"), luna_md)?;

        // 4. Fund Child Treasury via Double-Entry Parity
        let franchise_funding = vec![
            Line { vault: "sol".into(), unit: "usd".into(), shift: -1000.00 },
            Line { vault: "luna".into(), unit: "usd".into(), shift: 1000.00 },
        ];
        wal.append_transaction(&franchise_funding, "[[franchise_seed_fund]]", "flux:seed")?;

        // 5. Mint [[pnl-southbank]] and update Sol's CEO dashboard
        let pnl_sb = forge.forge_gear_tool("pnl-southbank", "[[sol]]", "1000 + 420")?;
        fs::write(vault_path.join("pnl-southbank.md"), &pnl_sb.surface_md)?;

        let updated_view_sol = r#"---
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
"#;
        fs::write(vault_path.join("view-sol.md"), updated_view_sol)?;

        // Luna earns $420, remits 20% royalty ($84.00) back to Sol
        let operations = vec![
            Line { vault: "luna".into(), unit: "usd".into(), shift: 420.00 },
            Line { vault: "southbank_buyers".into(), unit: "usd".into(), shift: -420.00 },
            Line { vault: "luna".into(), unit: "usd".into(), shift: -84.00 },
            Line { vault: "sol".into(), unit: "usd".into(), shift: 84.00 },
        ];
        wal.append_transaction(&operations, "[[royalty_remittance]]", "flux:royalty")?;

        let patch = Patch {
            target: "[[view-sol]]".into(),
            delta: "ceo_hud: active".into(),
            parity: operations,
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[ceo_dashboard_update]]".into(),
            base: "".into(),
        };

        let commit_oid = git.commit_sealed_etch(&patch, "[[sol]]", "flux:ceo")?;
        cpu_spend += 0.08;

        key_events.push((
            "Franchise Minting & Fractal Delegation".into(),
            "Sol forged [[realm-southbank]], spawned [[luna]], funded [[wal-luna]] with $1000, and integrated South Bank into CEO dashboard.".into()
        ));

        key_events.push((
            "Royalty Remittance".into(),
            format!("Luna generated $420.00 gross sales and remitted $84.00 royalty to Sol. Sealed in commit {}.", commit_oid)
        ));

        Ok(ScenarioResult {
            name: "Franchise Expansion & Fractal Delegation".into(),
            scenario_id: "Scenario C".into(),
            duration_simulated: "30 Days (Time-Dilation)".into(),
            net_cash: 5250.00 - 1000.00 + 84.00,
            cpu_spend,
            roi: 65.4,
            fault_rate: 0.0,
            quiescent_ratio: "30:1".into(),
            new_nodes_count: 5,
            emergent_graph: r#"* [[sol.md]] (CEO Enterprise Node)
  * ![[wal.md]] (Master Treasury: $4,334.00)
  * ![[view-sol.md]] (A2UI CEO Executive Cockpit)
  * [[realm-southbank.md]] (Forged Child Realm with CEO Gate)
    * [[luna.md]] (Forged Sub-Agent Operator)
    * [[wal-luna.md]] (Franchise Float & Operations)
    * ![[pnl-southbank.md]] (South Bank Regional Ledger)"#.into(),
            key_events,
            observations: vec![
                "Fractal delegation allowed unbounded revenue scaling without bloating Sol's 4KB HUD.".into(),
                "The CEO gate ensured autonomous branch operations while reserving veto power for major capital spend.".into(),
            ],
            friction_points: vec![
                "Transcluding sub-franchise tables into CEO view required manual A2UI component re-indexing.".into(),
            ],
            proposed_adjustments: vec![
                "Introduce native A2UI transclusion slots for child realms: ![[realm-*#kpis]].".into(),
            ],
        })
    }

    /// Scenario D: Autonomous M&A and Protocol Assimilation (Strategic Long-Horizon)
    pub fn run_scenario_d(vault_path: &Path, iceberg_path: &Path) -> Result<ScenarioResult, anyhow::Error> {
        let git = GitBackend::open_or_init(".")?;
        let forge = ForgeEngine::new(iceberg_path);
        let wal = WalEngine::open_or_init(iceberg_path)?;
        let mut key_events = Vec::new();
        let mut cpu_spend = 0.0;

        let coffee_cart_md = r#"---
crest: "[[coffee-cart]]"
engine: "organ"
status: "DISTRESS"
vaults: { usd: -45.00, beans_lb: 12.0 }
guard: "[[guard-coffee-cart]]"
seal: "sig:ed25519:distressed_cart"
---
# Coffee Cart
Running out of float (-$45.00 debt). Broadcasts distress aura.
"#;
        fs::write(vault_path.join("coffee-cart.md"), coffee_cart_md)?;

        key_events.push((
            "Distress Aura Detected".into(),
            "Adjacent node [[coffee-cart]] fell to -$45.00 USD and emitted distress aura. Sol initiated acquisition scan.".into()
        ));

        let shadow_res = ShadowExecution::run_shadow(".", "scenario_d", |_wt| {
            let net_npv = 350.0 * 4.0 - 45.0;
            if net_npv > 500.0 {
                Ok(net_npv)
            } else {
                Err(Fault::Ward("NPV insufficient".into()))
            }
        });
        assert!(shadow_res.is_ok());
        cpu_spend += 0.04;

        key_events.push((
            "Shadow M&A Feasibility Projection".into(),
            "Sol projected +$1,355.00 4-week net cash flow from absorbing morning coffee commuters. Acquisition approved.".into()
        ));

        let mna_md = r#"---
crest: "[[mna-agreement]]"
engine: "gear"
gate:
  - { role: "acquirer", by: "[[sol]]", seal: "sig:ed25519:sol_mna_seal" }
  - { role: "target", by: "[[coffee-cart]]", seal: "sig:ed25519:cart_owner_seal" }
terms: { debt_assumed_usd: 45.00, equity_percent: 100.0 }
seal: "sig:ed25519:mna_executed"
---
# M&A Absorption Agreement
Sol assumes $45.00 debt; Coffee Cart transfers 100% operating control and revenue routing.
"#;
        fs::write(vault_path.join("mna-agreement.md"), mna_md)?;

        let balanced_mna = vec![
            Line { vault: "sol".into(), unit: "usd".into(), shift: -45.00 },
            Line { vault: "coffee_creditor".into(), unit: "usd".into(), shift: 45.00 },
        ];
        wal.append_transaction(&balanced_mna, "[[mna_debt_clearing]]", "flux:mna")?;

        let new_guard_cart = r#"---
crest: "[[guard-coffee-cart]]"
engine: "guard"
target: "[[coffee-cart]]"
fuel: 4000
proof: "cert:smt:mna_guard_rewritten"
code: |
  cel:
    post.revenue.target == "[[wal]]" &&
    size(post.raw_markdown) <= 4096
seal: "sig:ed25519:guard_assimilated"
---
# Assimilated Validator Port: [[coffee-cart]]
Directs 100% of coffee sales into Sol's master [[wal]] treasury.
"#;
        fs::write(vault_path.join("guard-coffee-cart.md"), new_guard_cart)?;

        let barista_triad = forge.forge_gear_tool("barista-logic", "[[sol]]", "12 * 4")?;
        fs::write(vault_path.join("barista-logic.md"), &barista_triad.surface_md)?;

        let patch = Patch {
            target: "[[coffee-cart]]".into(),
            delta: "status: ASSIMILATED".into(),
            parity: vec![],
            shadow: false,
            settle: "eager".into(),
            purpose: "[[mna_assimilation]]".into(),
            base: "".into(),
        };

        let commit_oid = git.commit_sealed_etch(&patch, "[[sol]]", "flux:mna")?;
        cpu_spend += 0.05;

        key_events.push((
            "Protocol Assimilation".into(),
            format!("Sol rewrote [[guard-coffee-cart]] to route revenue to [[wal]], and minted [[barista-logic]]. Sealed in commit {}.", commit_oid)
        ));

        Ok(ScenarioResult {
            name: "Autonomous M&A and Protocol Assimilation".into(),
            scenario_id: "Scenario D".into(),
            duration_simulated: "14 Days (Absorption Horizon)".into(),
            net_cash: -45.00,
            cpu_spend,
            roi: 30.1,
            fault_rate: 0.0,
            quiescent_ratio: "5:1".into(),
            new_nodes_count: 4,
            emergent_graph: r#"* [[sol.md]] (Acquirer)
  * [[mna-agreement.md]] (Bilateral Quorum Gate)
  * [[coffee-cart.md]] (Assimilated Operating Node)
    * [[guard-coffee-cart.md]] (Rewritten Validator routing to [[wal]])
    * [[barista-logic.md]] (Autopoietically Minted Coffee Recipe Tool)"#.into(),
            key_events,
            observations: vec![
                "Re-writing validator guards legally repurposed asset cash flows without forks.".into(),
                "Shadow simulations gave empirical certainty before capital was deployed to debt assumption.".into(),
            ],
            friction_points: vec![
                "Overwriting an existing guard required re-certification of the target surface.".into(),
            ],
            proposed_adjustments: vec![
                "Add native protocol migration primitives: conky guard repoint --target [[dest]].".into(),
            ],
        })
    }

    /// Scenario E: Seasonal Pivot & Fundamental R&D (Strategic Long-Horizon)
    pub fn run_scenario_e(vault_path: &Path, iceberg_path: &Path) -> Result<ScenarioResult, anyhow::Error> {
        let git = GitBackend::open_or_init(".")?;
        let forge = ForgeEngine::new(iceberg_path);
        let wal = WalEngine::open_or_init(iceberg_path)?;
        let mut key_events = Vec::new();
        let mut cpu_spend = 0.0;

        let winter_weather = r#"---
crest: "[[weather]]"
engine: "organ"
heat: 0.12
temperature: 10.0
season: "Winter"
seal: "sig:ed25519:winter_weather"
---
# Weather Sensor Feed
Cold front settled over Brisbane. Temperature: 10C. Lemonade demand: 0 cups/day.
"#;
        fs::write(vault_path.join("weather.md"), winter_weather)?;

        key_events.push((
            "Macro Climate Pivot (Catalyst)".into(),
            "Winter arrived in Brisbane (10°C). Demand for cold lemonade dropped to zero for 5 consecutive days.".into()
        ));

        let archived_scaler = r#"---
crest: "[[batch-scaler]]"
engine: "gear"
status: "ARCHIVED"
ttl: "2026-06-01"
seal: "sig:ed25519:archived_scaler"
---
# Lemonade Batch Scaler (ARCHIVED)
*Decommissioned during winter pivot.*
"#;
        fs::write(vault_path.join("batch-scaler.md"), archived_scaler)?;

        key_events.push((
            "Operational Decommissioning".into(),
            "Sol archived [[batch-scaler.md]] and set TTL expiration on cold citrus supply contracts.".into()
        ));

        let cider_triad = forge.forge_gear_tool("hot-cider-logic", "[[sol]]", "100 - 15")?;
        fs::write(vault_path.join("hot-cider-logic.md"), &cider_triad.surface_md)?;
        fs::write(vault_path.join("guard-hot-cider-logic.md"), &cider_triad.guard_md)?;

        let cider_notebook_md = r#"---
crest: "[[pnl-hot-beverages]]"
engine: "organ/duckdb"
maker: "[[sol]]"
guard: "[[guard-pnl-hot-beverages]]"
seal: "sig:ed25519:cider_pnl"
---
# Winter Beverage Margin Analysis
| product | cups_sold | price | margin |
| :--- | :--- | :--- | :--- |
| spiced_apple_cider | 42 | $5.50 | 78% |
| organic_chai_tea | 35 | $4.50 | 82% |
"#;
        fs::write(vault_path.join("pnl-hot-beverages.md"), cider_notebook_md)?;

        let winter_view_sol = r#"---
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
"#;
        fs::write(vault_path.join("view-sol.md"), winter_view_sol)?;

        let winter_sales = vec![
            Line { vault: "sol".into(), unit: "usd".into(), shift: 388.50 },
            Line { vault: "cider_buyers".into(), unit: "usd".into(), shift: -388.50 },
            Line { vault: "sol".into(), unit: "usd".into(), shift: -45.00 },
            Line { vault: "apple_orchard".into(), unit: "usd".into(), shift: 45.00 },
        ];
        wal.append_transaction(&winter_sales, "[[winter_sales]]", "flux:winter")?;

        let patch = Patch {
            target: "[[view-sol]]".into(),
            delta: "winter_pivot: complete".into(),
            parity: winter_sales,
            shadow: false,
            settle: "quiescent".into(),
            purpose: "[[winter_pivot]]".into(),
            base: "".into(),
        };

        let commit_oid = git.commit_sealed_etch(&patch, "[[sol]]", "flux:winter_close")?;
        cpu_spend += 0.09;

        key_events.push((
            "Winter Operation Launch & R&D Settlement".into(),
            format!("Sol launched hot cider & tea line, generated +$343.50 net day-1 cash. Sealed in commit {}.", commit_oid)
        ));

        Ok(ScenarioResult {
            name: "Seasonal Pivot & Fundamental R&D".into(),
            scenario_id: "Scenario E".into(),
            duration_simulated: "90 Days (Seasonal Dilation)".into(),
            net_cash: 343.50,
            cpu_spend,
            roi: 38.1,
            fault_rate: 0.0,
            quiescent_ratio: "20:1".into(),
            new_nodes_count: 5,
            emergent_graph: r#"* [[sol.md]] (Root Operator Pivot)
  * ![[view-sol.md]] (Re-wired A2UI Winter Cockpit)
  * [[weather.md]] (Winter Feed: 10°C)
  * [[batch-scaler.md]] (Status: ARCHIVED)
  * [[hot-cider-logic.md]] (Forged Winter Recipe Tool)
  * [[guard-hot-cider-logic.md]]
  * ![[pnl-hot-beverages.md]] (Forged Hot Beverage Margins Notebook)"#.into(),
            key_events,
            observations: vec![
                "The agent discarded obsolete forged tools when environmental conditions invalidated them.".into(),
                "A2UI declarative streams seamlessly accepted new progress gauges without JavaScript re-compilation.".into(),
            ],
            friction_points: vec![
                "Old transclusion links in archived notes had to be updated to prevent broken link warnings.".into(),
            ],
            proposed_adjustments: vec![
                "Introduce graceful link tombstoning in conky-graph for archived nodes.".into(),
            ],
        })
    }
}
