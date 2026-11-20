use crate::types::Fault;
use std::process::Command;

pub struct ShadowExecution;

impl ShadowExecution {
    /// Executes a closure in an ephemeral git worktree, ensuring no changes hit main
    pub fn run_shadow<F, T>(repo_path: &str, worktree_name: &str, f: F) -> Result<T, Fault>
    where
        F: FnOnce(&str) -> Result<T, Fault>,
    {
        let wt_path = format!("{}/.shadow_{}", repo_path, worktree_name);

        // 1. git worktree add
        let add_status = Command::new("git")
            .args(["worktree", "add", "--detach", &wt_path, "HEAD"])
            .current_dir(repo_path)
            .output();

        if let Err(e) = add_status {
            return Err(Fault::Ward(format!(
                "Failed creating shadow worktree: {}",
                e
            )));
        }

        // 2. Execute inner logic inside worktree
        let result = f(&wt_path);

        // 3. git worktree remove --force
        let _ = Command::new("git")
            .args(["worktree", "remove", "--force", &wt_path])
            .current_dir(repo_path)
            .output();

        result
    }
}
