use blake3::Hasher;
use conky_airlock::types::{Fault, PulseFrame};
use std::collections::HashMap;

pub struct StreamMultiplexer {
    // source link -> rolling hash chain
    chains: HashMap<String, String>,
    buffered_frames: HashMap<String, Vec<PulseFrame>>,
}

impl StreamMultiplexer {
    pub fn new() -> Self {
        Self {
            chains: HashMap::new(),
            buffered_frames: HashMap::new(),
        }
    }

    pub fn emit_pulse(&mut self, mut frame: PulseFrame) -> Result<u64, Fault> {
        // Enforce max depth 12
        if frame.depth > 12 {
            return Err(Fault::Cycle(frame.depth));
        }

        // Update rolling blake3 hash chain
        let prev_hash = self
            .chains
            .get(&frame.source)
            .cloned()
            .unwrap_or_else(|| "flux:init".to_string());

        let mut hasher = Hasher::new();
        hasher.update(prev_hash.as_bytes());
        hasher.update(frame.patch_json.as_bytes());
        hasher.update(&frame.seq.to_le_bytes());

        let new_hash = format!("flux:{}", hasher.finalize().to_hex());
        frame.rolling_hash = new_hash.clone();
        self.chains.insert(frame.source.clone(), new_hash);

        let frames = self.buffered_frames.entry(frame.source.clone()).or_default();
        frames.push(frame);

        Ok(frames.len() as u64)
    }

    pub fn get_rolling_root(&self, source: &str) -> String {
        self.chains
            .get(source)
            .cloned()
            .unwrap_or_else(|| "flux:quiescent".to_string())
    }

    pub fn flush_quiescence(&mut self, source: &str) -> (String, usize) {
        let root = self.get_rolling_root(source);
        let count = self.buffered_frames.remove(source).map(|v| v.len()).unwrap_or(0);
        (root, count)
    }
}

impl Default for StreamMultiplexer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pulse_stream_coalescence() {
        let mut mux = StreamMultiplexer::new();
        for i in 1..=50 {
            let frame = PulseFrame {
                source: "[[pitcher]]".into(),
                seq: i,
                rolling_hash: String::new(),
                patch_json: format!(r#"{{"oz_left": {}}}"#, 160.0 - (i as f64 * 0.96)),
                depth: 1,
            };
            mux.emit_pulse(frame).unwrap();
        }

        let (root_hash, count) = mux.flush_quiescence("[[pitcher]]");
        assert_eq!(count, 50);
        assert!(root_hash.starts_with("flux:"));
    }

    #[test]
    fn test_cycle_breaker() {
        let mut mux = StreamMultiplexer::new();
        let frame = PulseFrame {
            source: "[[loop]]".into(),
            seq: 1,
            rolling_hash: String::new(),
            patch_json: "{}".into(),
            depth: 13,
        };
        assert_eq!(mux.emit_pulse(frame), Err(Fault::Cycle(13)));
    }
}
