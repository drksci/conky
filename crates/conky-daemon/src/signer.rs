use ed25519_dalek::{Signer, SigningKey, VerifyingKey};
use rand::rngs::OsRng;
use std::collections::HashMap;

pub struct CrestSigner {
    keys: HashMap<String, SigningKey>,
}

impl CrestSigner {
    pub fn new() -> Self {
        Self {
            keys: HashMap::new(),
        }
    }

    pub fn get_or_create_key(&mut self, crest: &str) -> &SigningKey {
        self.keys.entry(crest.to_string()).or_insert_with(|| {
            SigningKey::generate(&mut OsRng)
        })
    }

    pub fn sign_content(&mut self, crest: &str, content: &[u8]) -> String {
        let key = self.get_or_create_key(crest);
        let signature = key.sign(content);
        format!("sig:ed25519:{}", hex::encode(signature.to_bytes()))
    }

    pub fn verifying_key(&mut self, crest: &str) -> VerifyingKey {
        self.get_or_create_key(crest).verifying_key()
    }
}

impl Default for CrestSigner {
    fn default() -> Self {
        Self::new()
    }
}

// Simple hex helper to avoid extra crate if needed
mod hex {
    pub fn encode(data: [u8; 64]) -> String {
        let mut s = String::with_capacity(128);
        for byte in data {
            s.push_str(&format!("{:02x}", byte));
        }
        s
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crest_signing() {
        let mut signer = CrestSigner::new();
        let sig = signer.sign_content("[[a19f4c881b]]", b"test transaction");
        assert!(sig.starts_with("sig:ed25519:"));
        assert_eq!(sig.len(), "sig:ed25519:".len() + 128);
    }
}
