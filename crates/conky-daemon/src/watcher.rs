use notify::{Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::{Path, PathBuf};
use std::sync::mpsc::{channel, Receiver};
use std::time::Duration;

pub struct VaultWatcher {
    _watcher: RecommendedWatcher,
    rx: Receiver<notify::Result<Event>>,
    vault_path: PathBuf,
}

impl VaultWatcher {
    pub fn new<P: AsRef<Path>>(vault_path: P) -> notify::Result<Self> {
        let (tx, rx) = channel();

        let mut watcher = RecommendedWatcher::new(
            move |res| {
                let _ = tx.send(res);
            },
            notify::Config::default().with_poll_interval(Duration::from_millis(200)),
        )?;

        watcher.watch(vault_path.as_ref(), RecursiveMode::Recursive)?;

        Ok(Self {
            _watcher: watcher,
            rx,
            vault_path: vault_path.as_ref().to_path_buf(),
        })
    }

    pub fn next_event(&self) -> Option<PathBuf> {
        while let Ok(Ok(event)) = self.rx.try_recv() {
            match event.kind {
                EventKind::Modify(_) | EventKind::Create(_) => {
                    for path in event.paths {
                        if path.extension().and_then(|s| s.to_str()) == Some("md") {
                            return Some(path);
                        }
                    }
                }
                _ => {}
            }
        }
        None
    }

    pub fn vault_path(&self) -> &Path {
        &self.vault_path
    }
}
