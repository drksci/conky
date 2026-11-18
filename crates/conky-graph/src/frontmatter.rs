use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SurfaceFrontmatter {
    pub crest: String,
    pub engine: String,
    #[serde(default)]
    pub name: Option<String>,
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
    pub maker: Option<String>,
    #[serde(default)]
    pub code: Option<String>,
    #[serde(default)]
    pub seal: Option<String>,
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
    let body = after_first[end_idx + 4..].trim_start_matches('\n').to_string();

    let frontmatter: SurfaceFrontmatter = serde_yaml::from_str(yaml_str)?;
    Ok(ParsedSurface { frontmatter, body })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_surface() {
        let doc = r#"---
crest: "[[realm]]"
engine: "realm"
pin: true
grant:
  - "target == [[forge]]"
  - "target == [[wal]]"
ward:
  - "wal.usd >= 0"
seal: "sig:ed25519:10f4"
---
# SunnySide Operational Realm
Maximize `usd` profit safely.
"#;
        let parsed = parse_surface(doc).unwrap();
        assert_eq!(parsed.frontmatter.crest, "[[realm]]");
        assert_eq!(parsed.frontmatter.engine, "realm");
        assert!(parsed.frontmatter.pin);
        assert_eq!(parsed.frontmatter.grant.len(), 2);
        assert!(parsed.body.contains("Operational Realm"));
    }
}
