use regex::Regex;
use std::collections::{HashMap, HashSet};

#[derive(Debug, Default, Clone)]
pub struct BacklinkIndex {
    // node -> set of nodes that link to it
    pub backlinks: HashMap<String, HashSet<String>>,
    // node -> set of nodes that it links to
    pub forward_links: HashMap<String, HashSet<String>>,
}

impl BacklinkIndex {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn extract_links(content: &str) -> HashSet<String> {
        let re = Regex::new(r"\[\[(.*?)\]\]").unwrap();
        let mut links = HashSet::new();
        for cap in re.captures_iter(content) {
            let full = &cap[1];
            let target = full.split('#').next().unwrap_or(full).trim();
            links.insert(target.to_string());
        }
        links
    }

    pub fn update_node(&mut self, node: &str, content: &str) {
        // Clear previous forward links
        if let Some(old_forwards) = self.forward_links.remove(node) {
            for target in old_forwards {
                if let Some(bl) = self.backlinks.get_mut(&target) {
                    bl.remove(node);
                }
            }
        }

        let links = Self::extract_links(content);
        for target in &links {
            self.backlinks
                .entry(target.clone())
                .or_default()
                .insert(node.to_string());
        }
        self.forward_links.insert(node.to_string(), links);
    }

    pub fn get_dependents(&self, node: &str) -> Vec<String> {
        self.backlinks
            .get(node)
            .map(|set| set.iter().cloned().collect())
            .unwrap_or_default()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_backlink_indexing() {
        let mut index = BacklinkIndex::new();
        index.update_node("sol", "Watch [[kiosk]] and check [[weather#heat]]");
        index.update_node("kiosk", "Customer placed order for [[sol]]");

        let kiosk_deps = index.get_dependents("kiosk");
        assert!(kiosk_deps.contains(&"sol".to_string()));

        let weather_deps = index.get_dependents("weather");
        assert!(weather_deps.contains(&"sol".to_string()));
    }
}
