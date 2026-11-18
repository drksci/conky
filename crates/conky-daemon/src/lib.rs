pub mod git_backend;
pub mod signer;
pub mod stream;
pub mod tests_suite;
pub mod watcher;

use conky_graph::VaultReader;
use std::fs;
use std::path::{Path, PathBuf};

pub struct LocalVault {
    root: PathBuf,
}

impl LocalVault {
    pub fn new<P: AsRef<Path>>(root: P) -> Self {
        Self {
            root: root.as_ref().to_path_buf(),
        }
    }
}

impl VaultReader for LocalVault {
    fn read(&self, link_or_path: &str) -> Result<String, anyhow::Error> {
        let clean = link_or_path.trim_matches(|c| c == '[' || c == ']');
        let path = if clean.ends_with(".md") {
            self.root.join(clean)
        } else {
            self.root.join(format!("{}.md", clean))
        };
        fs::read_to_string(&path)
            .map_err(|e| anyhow::anyhow!("Failed reading {}: {}", path.display(), e))
    }
}
