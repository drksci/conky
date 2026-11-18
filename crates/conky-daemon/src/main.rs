use conky_daemon::git_backend::GitBackend;
use conky_daemon::signer::CrestSigner;
use conky_daemon::watcher::VaultWatcher;
use conky_daemon::LocalVault;
use conky_graph::BacklinkIndex;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Duration;
use tracing::{error, info};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    let vault_dir = PathBuf::from("./vault");
    if !vault_dir.exists() {
        fs::create_dir_all(&vault_dir)?;
    }

    info!("Initializing conky runtime...");
    info!("Vault directory: {}", vault_dir.display());

    let git = GitBackend::open_or_init(".")?;
    let mut signer = CrestSigner::new();
    let mut index = BacklinkIndex::new();
    let _local_vault = LocalVault::new(&vault_dir);

    // Initial indexing
    info!("Building initial vault index...");
    if let Ok(entries) = fs::read_dir(&vault_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("md") {
                if let Ok(content) = fs::read_to_string(&path) {
                    let node_name = path
                        .file_stem()
                        .and_then(|s| s.to_str())
                        .unwrap_or_default();
                    index.update_node(node_name, &content);
                    info!("Indexed node: [[{}]]", node_name);
                }
            }
        }
    }

    let watcher = match VaultWatcher::new(&vault_dir) {
        Ok(w) => w,
        Err(e) => {
            error!("Failed to create watcher on {}: {}", vault_dir.display(), e);
            return Err(e.into());
        }
    };

    info!("conky-daemon is alive and watching vault. Press Ctrl+C to terminate.");

    loop {
        if let Some(changed_path) = watcher.next_event() {
            let stem = changed_path
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("");
            info!("Detected change in node: [[{}]]", stem);

            if let Ok(content) = fs::read_to_string(&changed_path) {
                index.update_node(stem, &content);
                let dependents = index.get_dependents(stem);
                info!("Dependents of [[{}]]: {:?}", stem, dependents);

                // Commit change with deterministic crest signature
                let crest_id = format!("[[{}]]", stem);
                let sig = signer.sign_content(&crest_id, content.as_bytes());
                info!("Generated seal: {}", sig);

                if let Ok(rel) = changed_path.strip_prefix(Path::new(".")) {
                    if let Ok(oid) = git.commit_file(
                        rel,
                        &crest_id,
                        &format!("sync: {} [{}]", crest_id, &sig[..24]),
                    ) {
                        info!("Committed state {} to Git: {}", crest_id, oid);
                    }
                }
            }
        }

        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}
