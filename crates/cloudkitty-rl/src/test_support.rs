//! Fixtures shared by this crate's integration tests and downstream
//! crates' (the server's policy tests) — the same doctrine as
//! `cloudkitty_core::test_support`. One fixture-artifact writer instead of
//! five hand-rolled copies (spec 014 review): an artifact-format change is
//! made here once, and every suite follows.

use std::path::{Path, PathBuf};

use crate::config::RlConfig;
use crate::observe::observation_len;
use crate::policy::{write_artifact, ArtifactHeader, ARTIFACT_VERSION};

/// Writes a valid fixture policy artifact shaped for the default schemas
/// (observation → `hidden` ReLU units → 40 logits) with deterministic
/// pseudo-weights derived from `pattern` (no RNG: reproducible bytes).
pub fn write_fixture_artifact(path: &Path, hidden: usize, pattern: u32) {
    let rl = RlConfig::default();
    let input = observation_len(&rl.observation);
    let header = ArtifactHeader {
        artifact_version: ARTIFACT_VERSION,
        observation_schema: 1,
        action_schema: 1,
        mask_schema: 1,
        layers: vec![[input, hidden], [hidden, 40]],
        activation: "relu".into(),
    };
    let modulus = (pattern % 13 + 5) as usize;
    let w1: Vec<f32> = (0..input * hidden)
        .map(|i| ((i % modulus) as f32 - (modulus as f32 / 2.0)) * 0.03)
        .collect();
    let w2: Vec<f32> = (0..hidden * 40)
        .map(|i| ((i % (modulus + 2)) as f32 - 2.0) * 0.05)
        .collect();
    write_artifact(
        path,
        &header,
        &[(w1, vec![0.02; hidden]), (w2, vec![0.0; 40])],
    )
    .expect("fixture artifacts write");
}

/// [`write_fixture_artifact`] into a namespaced temp directory; returns the
/// artifact path.
pub fn fixture_artifact(dir_name: &str, file_name: &str, hidden: usize, pattern: u32) -> PathBuf {
    let dir = std::env::temp_dir().join(dir_name);
    std::fs::create_dir_all(&dir).expect("temp dir");
    let path = dir.join(format!("{file_name}.ckpolicy"));
    write_fixture_artifact(&path, hidden, pattern);
    path
}
