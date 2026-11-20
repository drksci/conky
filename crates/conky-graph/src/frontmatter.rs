use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, Default)]
pub struct SurfaceFrontmatter {
    pub crest: String,
    pub engine: String,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub guard: Option<String>,
    #[serde(default)]
    pub view: Option<String>,
    #[serde(default)]
    pub inherits: Vec<String>,
    #[serde(default)]
    pub pin: bool,
    #[serde(default)]
    pub watch: Vec<String>,
    #[serde(default)]
    pub ward: Vec<String>,
    #[serde(default)]
    pub grant: Vec<String>,
    #[serde(default)]
    pub target: Option<String>,
    #[serde(default)]
    pub fuel: Option<u64>,
    #[serde(default)]
    pub proof: Option<String>,
    #[serde(default)]
    pub settle: Option<String>,
    #[serde(default)]
    pub maker: Option<String>,
    #[serde(default)]
    pub code: Option<String>,
    #[serde(default)]
    pub seal: Option<String>,
    #[serde(default)]
    pub escalate: Option<String>,
    #[serde(default)]
    pub shard: Option<String>,
    #[serde(default)]
    pub vaults: Option<serde_yaml::Value>,
    #[serde(default)]
    pub gate: Option<serde_yaml::Value>,
    #[serde(default)]
    pub stream: Option<String>,
    #[serde(default)]
    pub a2ui: Option<serde_yaml::Value>,
    #[serde(default)]
    pub traits: Option<serde_yaml::Value>,
    #[serde(default)]
    pub drive: Option<serde_yaml::Value>,
    #[serde(default)]
    pub focus: Option<f64>,
    #[serde(default)]
    pub state: Option<serde_yaml::Value>,
    #[serde(default)]
    pub source: Option<String>,
    #[serde(default)]
    pub sql: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ParsedSurface {
    pub frontmatter: SurfaceFrontmatter,
    pub body: String,
}

pub fn parse_surface(content: &str) -> Result<ParsedSurface, anyhow::Error> {
    let trimmed = content.trim_start();
    if !trimmed.starts_with("---") {
        anyhow::bail!("Missing frontmatter delimiter '---'");
    }

    let after_first = &trimmed[3..];
    let end_idx = after_first
        .find("\n---")
        .ok_or_else(|| anyhow::anyhow!("Unterminated frontmatter"))?;

    let yaml_str = &after_first[..end_idx];
    let body = after_first[end_idx + 4..]
        .trim_start_matches('\n')
        .to_string();

    let frontmatter: SurfaceFrontmatter = serde_yaml::from_str(yaml_str)?;
    Ok(ParsedSurface { frontmatter, body })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_surface_triad() {
        let doc = r#"---
crest: "[[realm]]"
engine: "realm"
guard: "[[guard-realm]]"
view: "[[view-realm]]"
pin: true
grant:
  - "watch:*"
ward:
  - "wal.usd >= 0"
seal: "sig:ed25519:10f4"
---
# Operational Realm
Maximize `usd` profit safely.
"#;
        let parsed = parse_surface(doc).unwrap();
        assert_eq!(parsed.frontmatter.crest, "[[realm]]");
        assert_eq!(parsed.frontmatter.engine, "realm");
        assert_eq!(parsed.frontmatter.guard.as_deref(), Some("[[guard-realm]]"));
        assert_eq!(parsed.frontmatter.view.as_deref(), Some("[[view-realm]]"));
        assert!(parsed.frontmatter.pin);
    }
}
