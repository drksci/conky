//! Wasmtime host bindings for conky.wit
//! Sandsboxed capsule execution runtime.

pub struct CapsuleHost {
    // Wasmtime engine and linker will be configured in Sprint 2
}

impl CapsuleHost {
    pub fn new() -> Self {
        Self {}
    }
}

impl Default for CapsuleHost {
    fn default() -> Self {
        Self::new()
    }
}
