use conky_airlock::types::{Crest, Patch};
use git2::{Oid, Repository, Signature};
use std::path::Path;

pub struct GitBackend {
    repo: Repository,
}

impl GitBackend {
    pub fn open_or_init<P: AsRef<Path>>(path: P) -> Result<Self, git2::Error> {
        let repo = match Repository::open(&path) {
            Ok(r) => r,
            Err(_) => Repository::init(&path)?,
        };
        Ok(Self { repo })
    }

    pub fn commit_file(
        &self,
        rel_path: &Path,
        author: &str,
        message: &str,
    ) -> Result<Oid, git2::Error> {
        let mut index = self.repo.index()?;
        index.add_path(rel_path)?;
        index.write()?;

        let tree_id = index.write_tree()?;
        let tree = self.repo.find_tree(tree_id)?;

        let sig = Signature::now(author, "conky@sunnyside.internal")?;

        let head = self.repo.head();
        let parents = match head {
            Ok(ref h) => {
                if let Some(target) = h.target() {
                    vec![self.repo.find_commit(target)?]
                } else {
                    vec![]
                }
            }
            Err(_) => vec![],
        };

        let parent_refs: Vec<&git2::Commit> = parents.iter().collect();

        self.repo.commit(
            Some("HEAD"),
            &sig,
            &sig,
            message,
            &tree,
            &parent_refs,
        )
    }

    pub fn commit_etch(&self, patch: &Patch, identity: &Crest) -> Result<Oid, git2::Error> {
        self.commit_sealed_etch(patch, identity, "flux:quiescent")
    }

    pub fn commit_sealed_etch(
        &self,
        patch: &Patch,
        crest: &str,
        pulse_root: &str,
    ) -> Result<Oid, git2::Error> {
        let mut index = self.repo.index()?;
        let clean_target = patch.target.trim_matches(|c| c == '[' || c == ']');
        index.add_path(Path::new(&format!("{}.md", clean_target)))?;
        index.write()?;

        let tree_id = index.write_tree()?;
        let tree = self.repo.find_tree(tree_id)?;

        let sig = Signature::now(
            crest,
            &format!("purpose:{}|pulse:{}", patch.purpose, pulse_root),
        )?;

        let mut parents = Vec::new();
        if !patch.base.is_empty() {
            if let Ok(base_oid) = Oid::from_str(&patch.base) {
                if let Ok(commit) = self.repo.find_commit(base_oid) {
                    parents.push(commit);
                }
            }
        }

        if parents.is_empty() {
            if let Ok(head) = self.repo.head() {
                if let Some(target) = head.target() {
                    if let Ok(commit) = self.repo.find_commit(target) {
                        parents.push(commit);
                    }
                }
            }
        }

        let parent_refs: Vec<&git2::Commit> = parents.iter().collect();

        self.repo.commit(
            Some("HEAD"),
            &sig,
            &sig,
            &format!("seal: {} -> {}", crest, patch.target),
            &tree,
            &parent_refs,
        )
    }

    pub fn head_oid(&self) -> Result<Option<Oid>, git2::Error> {
        match self.repo.head() {
            Ok(h) => Ok(h.target()),
            Err(_) => Ok(None),
        }
    }
}
