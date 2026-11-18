use conky_airlock::types::Fault;
use regex::Regex;

pub trait VaultReader {
    fn read(&self, link_or_path: &str) -> Result<String, anyhow::Error>;
}

pub fn extract_section(content: &str, heading_or_block: &str) -> Result<String, anyhow::Error> {
    // Check for markdown heading: `# <heading>` or `## <heading>`
    let target = heading_or_block.trim().to_lowercase();
    let mut capturing = false;
    let mut captured_lines = Vec::new();

    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with('#') {
            let heading_text = trimmed.trim_start_matches('#').trim().to_lowercase();
            if heading_text == target {
                capturing = true;
                continue;
            } else if capturing {
                break;
            }
        } else if capturing {
            captured_lines.push(line);
        }
    }

    if capturing {
        Ok(captured_lines.join("\n").trim().to_string())
    } else {
        // Fallback: search key-value or raw block if not heading
        for line in content.lines() {
            if let Some((k, v)) = line.split_once(':') {
                if k.trim().to_lowercase() == target {
                    return Ok(v.trim().to_string());
                }
            }
        }
        // If not found as section, return empty or content
        Ok(content.to_string())
    }
}

pub fn compile_slots<V: VaultReader>(content: &str, vault: &V, depth: u8) -> Result<String, Fault> {
    if depth > 3 {
        return Err(Fault::Sprawl(4097));
    }

    let re = Regex::new(r"!\[\[(.*?)\]\]").unwrap();
    let mut resolved_content = content.to_string();

    for cap in re.captures_iter(content) {
        let link = &cap[1];
        let parts: Vec<&str> = link.split('#').collect();
        let target_file = parts[0];

        let target_content = match vault.read(target_file) {
            Ok(c) => c,
            Err(e) => {
                tracing::warn!("Failed to transclude {}: {}", target_file, e);
                continue;
            }
        };

        let extracted = if parts.len() > 1 {
            extract_section(&target_content, parts[1]).unwrap_or(target_content)
        } else {
            target_content
        };

        // Recursively resolve slots within the transcluded content
        let flattened = compile_slots(&extracted, vault, depth + 1)?;
        resolved_content = resolved_content.replace(&cap[0], &flattened);
    }

    // Enforce 4KB HUD law pre-inference
    if resolved_content.len() > 4096 {
        return Err(Fault::Sprawl(resolved_content.len() as u32));
    }

    Ok(resolved_content)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    struct MockVault {
        files: HashMap<String, String>,
    }

    impl VaultReader for MockVault {
        fn read(&self, path: &str) -> Result<String, anyhow::Error> {
            self.files
                .get(path)
                .cloned()
                .ok_or_else(|| anyhow::anyhow!("File not found: {}", path))
        }
    }

    #[test]
    fn test_transclusion_flattening() {
        let mut files = HashMap::new();
        files.insert("wal".into(), "usd: 42.50\noz: 160".into());
        let vault = MockVault { files };

        let template = "Treasury: $![[wal#usd]] | Inventory: ![[wal#oz]] oz";
        let compiled = compile_slots(template, &vault, 0).unwrap();
        assert_eq!(compiled, "Treasury: $42.50 | Inventory: 160 oz");
    }
}
