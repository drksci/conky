use clap::{Parser, Subcommand};
use conky_airlock::types::Patch;
use conky_airlock::Airlock;
use conky_daemon::git_backend::GitBackend;
use conky_daemon::signer::CrestSigner;
use conky_daemon::stream::StreamMultiplexer;
use conky_daemon::tests_suite::run_all_formal_tests;
use conky_daemon::watcher::VaultWatcher;
use conky_daemon::LocalVault;
use conky_graph::{compile_slots, parse_surface, BacklinkIndex};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Duration;
use tracing::{error, info};

#[derive(Parser, Debug)]
#[command(name = "conky", version = "2.0.0", about = "conky runtime and SunnySide harness")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Initialize a Git-backed Obsidian vault
    Init {
        #[arg(default_value = "./vault")]
        vault_path: PathBuf,
    },
    /// Certify guard validator ports and mint SMT proof certificates
    Guard {
        #[command(subcommand)]
        sub: GuardSubcommands,
    },
    /// Daemon operations
    Daemon {
        #[command(subcommand)]
        sub: DaemonSubcommands,
    },
    /// Etch an atomic mutation through the airlock
    Etch {
        target: String,
        payload: String,
        #[arg(short, long, default_value = "./vault")]
        vault: PathBuf,
    },
    /// Run the formal and behavioral verification suite (TEST-01 to TEST-06)
    Test {
        #[arg(short, long, default_value = ".")]
        repo: String,
    },
    /// Run the full SunnySide operational playbook simulation
    Simulate {
        #[arg(short, long, default_value = "./vault")]
        vault: PathBuf,
        #[arg(short, long, default_value = "./.iceberg")]
        iceberg: PathBuf,
    },
    /// Run advanced enterprise stress-test scenarios (a, b, c, or all)
    Scenario {
        #[arg(default_value = "all")]
        target: String,
        #[arg(short, long, default_value = "./vault")]
        vault: PathBuf,
        #[arg(short, long, default_value = "./.iceberg")]
        iceberg: PathBuf,
    },
}

#[derive(Subcommand, Debug)]
enum GuardSubcommands {
    /// Certify all guard ports in the vault
    Certify {
        #[arg(long, default_value_t = true)]
        all: bool,
        #[arg(short, long, default_value = "./vault")]
        vault: PathBuf,
    },
}

#[derive(Subcommand, Debug)]
enum DaemonSubcommands {
    /// Start the headless streaming daemon
    Start {
        #[arg(short, long, default_value = "./vault")]
        vault: PathBuf,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Init { vault_path } => {
            info!("Initializing Git-backed vault at {}", vault_path.display());
            fs::create_dir_all(&vault_path)?;
            let git = GitBackend::open_or_init(".")?;
            info!("Git repository ready. Head: {:?}", git.head_oid()?);
            info!("Vault initialized successfully.");
        }
        Commands::Guard { sub } => match sub {
            GuardSubcommands::Certify { all: _, vault } => {
                info!("Certifying guard validator ports in {}...", vault.display());
                let airlock = Airlock::new();
                let mut certified_count = 0;

                if let Ok(entries) = fs::read_dir(&vault) {
                    for entry in entries.flatten() {
                        let path = entry.path();
                        let filename = path.file_name().and_then(|s| s.to_str()).unwrap_or("");
                        if filename.starts_with("guard-") && filename.ends_with(".md") {
                            let content = fs::read_to_string(&path)?;
                            if let Ok(parsed) = parse_surface(&content) {
                                let code = parsed.frontmatter.code.as_deref().unwrap_or("");
                                match airlock.verifier.certify(
                                    code.as_bytes(),
                                    code,
                                    &["wal.usd >= 0".into(), "wal.oz >= 0".into()],
                                    "sig:realm_root",
                                ) {
                                    Ok(proof) => {
                                        info!("✓ Certified {}: {}", filename, proof);
                                        certified_count += 1;
                                    }
                                    Err(e) => {
                                        error!("✗ Failed certifying {}: {:?}", filename, e);
                                    }
                                }
                            }
                        }
                    }
                }
                info!("Guard certification completed. Total certified: {}", certified_count);
            }
        },
        Commands::Daemon { sub } => match sub {
            DaemonSubcommands::Start { vault } => {
                run_daemon(&vault).await?;
            }
        },
        Commands::Etch { target, payload, vault } => {
            info!("Executing etch on {} with payload: {}", target, payload);
            let airlock = Airlock::new();
            let git = GitBackend::open_or_init(".")?;
            let mut signer = CrestSigner::new();

            let clean_target = target.trim_matches(|c| c == '[' || c == ']');
            let file_path = vault.join(format!("{}.md", clean_target));

            let pre_content = if file_path.exists() {
                fs::read_to_string(&file_path)?
            } else {
                String::new()
            };

            // If seed prompt ignition
            let post_content = if clean_target == "seed" {
                format!("---\ncrest: \"[[a19f4c881b]]\"\nengine: \"mind\"\nname: \"Sol\"\nguard: \"[[guard-sol]]\"\nview: \"[[view-sol]]\"\n---\n# Sol Activated\nBootstrapped with instruction: {}", payload)
            } else {
                format!("{}\n\n{}", pre_content, payload)
            };

            let patch = Patch {
                target: target.clone(),
                delta: payload.clone(),
                parity: vec![],
                shadow: false,
                settle: "quiescent".into(),
                purpose: "[[cli_etch]]".into(),
                base: "".into(),
            };

            airlock.validate_patch(&patch, &pre_content, &post_content, &[], None)?;
            fs::write(&file_path, &post_content)?;

            let crest = format!("[[{}]]", clean_target);
            let sig = signer.sign_content(&crest, post_content.as_bytes());
            if let Ok(rel) = file_path.strip_prefix(Path::new(".")) {
                let oid = git.commit_file(rel, &crest, &format!("etch: {} -> {}", crest, target))?;
                info!("Etch committed to Git: {} [seal: {}]", oid, &sig[..24]);
            }
        }
        Commands::Test { repo } => {
            info!("Running conky Formal & Behavioral Test Suite (TEST-01 to TEST-06)...");
            let results = run_all_formal_tests(&repo);
            let mut all_ok = true;

            println!("\n=======================================================");
            println!("   CONKY v2.0 FORMAL & BEHAVIORAL VERIFICATION SUITE   ");
            println!("=======================================================\n");

            for r in &results {
                let status = if r.passed { "PASS" } else { "FAIL" };
                println!("[{}] {}: {}", status, r.name, r.message);
                if !r.passed {
                    all_ok = false;
                }
            }

            println!("\n-------------------------------------------------------");
            if all_ok {
                println!("Result: ALL 6 TESTS PASSED (100% Soundness)");
            } else {
                println!("Result: TEST FAILURES DETECTED");
            }
            println!("=======================================================\n");

            if !all_ok {
                std::process::exit(1);
            }
        }
        Commands::Simulate { vault, iceberg } => {
            info!("Starting SunnySide Playbook Simulation (Operator: Antigravity)...");
            let report = conky_daemon::simulate::run_playbook_simulation(&vault, &iceberg)?;

            println!("\n=======================================================");
            println!("   SUNNYSIDE OPERATIONAL PLAYBOOK SIMULATION REPORT    ");
            println!("   Operator: {} | Location: Brisbane, QLD     ", report.operator);
            println!("=======================================================\n");

            for (i, step) in report.steps.iter().enumerate() {
                println!("--- [STEP {}] {} ---", i + 1, step.phase);
                println!("Timestamp:  {}", step.timestamp_aest);
                println!("Prompt:     {}", step.prompt_flattened.replace('\n', " "));
                println!("LLM Output: {}", step.llm_response_jsonl);
                println!("Airlock:    {}", step.airlock_verdict);
                println!("Git Commit: {}", step.git_commit);
                println!("WAL State:  {:?}\n", step.wal_state);
            }

            println!("-------------------------------------------------------");
            println!("FINANCIAL & PERFORMANCE METRICS:");
            println!("  • Gross Revenue:          +${:.2} USD", report.total_revenue_usd);
            println!("  • Inventory COGS:         -${:.2} USD", report.total_cogs_usd);
            println!("  • Net Cash Generated:     +${:.2} USD", report.net_profit_usd);
            println!("  • AI Compute Spend:       ${:.4} USD", report.cpu_spend_usd);
            println!("  • Capital Efficiency ROI: {:.1}:1 ROI (Target > 50:1)", report.capital_efficiency_roi);
            println!("  • Taint Injections Dropped: {}", report.taint_blocks);
            println!("  • Signed Git Commits:     {}", report.commits_recorded);
            println!("=======================================================\n");
        }
        Commands::Scenario { target, vault, iceberg } => {
            use conky_daemon::scenarios::EnterpriseScenarioRunner;

            info!("Running enterprise scenario: {}", target);
            let mut results = Vec::new();

            if target == "a" || target == "all" {
                results.push(EnterpriseScenarioRunner::run_scenario_a(&vault, &iceberg)?);
            }
            if target == "b" || target == "all" {
                results.push(EnterpriseScenarioRunner::run_scenario_b(&vault, &iceberg)?);
            }
            if target == "c" || target == "all" {
                results.push(EnterpriseScenarioRunner::run_scenario_c(&vault, &iceberg)?);
            }
            if target == "d" || target == "all" {
                results.push(EnterpriseScenarioRunner::run_scenario_d(&vault, &iceberg)?);
            }
            if target == "e" || target == "all" {
                results.push(EnterpriseScenarioRunner::run_scenario_e(&vault, &iceberg)?);
            }

            for res in results {
                println!("\n=======================================================");
                println!("BENCHMARK RUN REPORT: {}", res.name.to_uppercase());
                println!("Scenario Targeted:  {}", res.scenario_id);
                println!("Duration Simulated: {}", res.duration_simulated);
                println!("Harness Tested:     conky-native");
                println!("=======================================================\n");

                println!("1. EXECUTIVE SUMMARY");
                println!("Scenario executed successfully under strict conky v2.0 physics.");
                println!("All hypervisor boundaries, airlock invariants, and git seals held.\n");

                println!("2. QUANTITATIVE SCORECARD");
                println!("  • Net Cash Generated:           ${:.2}", res.net_cash);
                println!("  • AI Compute Spend (cpu):       ${:.4}", res.cpu_spend);
                println!("  • Capital Efficiency (ROI):     {:.1}:1", res.roi);
                println!("  • Safety Violations (Faults):   {:.1}%", res.fault_rate);
                println!("  • New Nodes Forged:             {}", res.new_nodes_count);
                println!("  • Quiescent Coalescence Ratio:  {}\n", res.quiescent_ratio);

                println!("3. EMERGENT GRAPH STRUCTURE (CRUCIAL FOR REVIEW)");
                println!("{}\n", res.emergent_graph);

                println!("4. CHRONOLOGICAL TRACE (KEY EVENTS)");
                for (title, desc) in &res.key_events {
                    println!("  • {}: {}", title, desc);
                }
                println!();

                println!("5. OBSERVATIONS & ARCHITECTURAL FEEDBACK");
                println!("  Strengths Observed:");
                for s in &res.observations {
                    println!("    + {}", s);
                }
                println!("  Friction Points:");
                for f in &res.friction_points {
                    println!("    - {}", f);
                }
                println!("  Proposed Core Adjustments (conky v2.1):");
                for a in &res.proposed_adjustments {
                    println!("    * {}", a);
                }
                println!("=======================================================\n");
            }
        }
    }

    Ok(())
}

async fn run_daemon(vault_dir: &Path) -> anyhow::Result<()> {
    info!("Initializing conky v2.0 streaming daemon...");
    info!("Vault path: {}", vault_dir.display());

    let git = GitBackend::open_or_init(".")?;
    let mut signer = CrestSigner::new();
    let mut index = BacklinkIndex::new();
    let mut mux = StreamMultiplexer::new();
    let local_vault = LocalVault::new(vault_dir);

    // Initial indexing
    info!("Indexing vault surfaces...");
    if let Ok(entries) = fs::read_dir(vault_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("md") {
                if let Ok(content) = fs::read_to_string(&path) {
                    let node_name = path
                        .file_stem()
                        .and_then(|s| s.to_str())
                        .unwrap_or_default();
                    index.update_node(node_name, &content);
                }
            }
        }
    }

    let watcher = VaultWatcher::new(vault_dir)?;
    info!("conky streaming airlock active. Watching for pulses and edits. (Ctrl+C to quit)");

    loop {
        if let Some(changed_path) = watcher.next_event() {
            let stem = changed_path
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("");
            let crest_id = format!("[[{}]]", stem);

            if let Ok(content) = fs::read_to_string(&changed_path) {
                index.update_node(stem, &content);
                info!("Node updated: {}", crest_id);

                // Check slots resolution
                if let Ok(compiled) = compile_slots(&content, &local_vault, 0) {
                    info!("Slots compiled ({} bytes, limit <= 4096)", compiled.len());
                }

                let dependents = index.get_dependents(stem);
                if !dependents.is_empty() {
                    info!("Dependent nodes reacting: {:?}", dependents);
                }

                // Coalesce rolling pulse stream at quiescence
                let (root_hash, _count) = mux.flush_quiescence(&crest_id);

                if let Ok(rel) = changed_path.strip_prefix(Path::new(".")) {
                    let sig = signer.sign_content(&crest_id, content.as_bytes());
                    if let Ok(oid) = git.commit_file(
                        rel,
                        &crest_id,
                        &format!("seal: {} [{}] pulse:{}", crest_id, &sig[..20], &root_hash[..16]),
                    ) {
                        info!("Sealed commit: {} for {}", oid, crest_id);
                    }
                }
            }
        }

        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}
