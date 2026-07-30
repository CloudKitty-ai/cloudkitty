//! Fixtures shared by this crate's integration tests and downstream
//! crates' (the server's policy tests) — the same doctrine as
//! `cloudkitty_core::test_support`. One fixture-artifact writer instead of
//! five hand-rolled copies (spec 014 review): an artifact-format change is
//! made here once, and every suite follows.

use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use crate::codec::ActionCodec;
use crate::config::RlConfig;
use crate::observe::observation_len;
use crate::policy::{write_artifact, ArtifactHeader, ARTIFACT_VERSION};

/// Writes a valid fixture policy artifact shaped for the default schemas
/// (observation → `hidden` ReLU units → menu logits, both lengths derived
/// from the schemas' own single sources) with deterministic pseudo-weights
/// derived from `pattern` (no RNG: reproducible bytes).
pub fn write_fixture_artifact(path: &Path, hidden: usize, pattern: u32) {
    write_fixture_artifact_with_output(path, hidden, pattern, None);
}

/// [`write_fixture_artifact`], with the output layer optionally flooded by
/// one constant (its bias scaled per index) — the shape the garbage-logits
/// tests need (NaN, ±inf, all-equal logits still select a masked-in
/// action).
pub fn write_fixture_artifact_with_output(
    path: &Path,
    hidden: usize,
    pattern: u32,
    output_fill: Option<f32>,
) {
    let rl = RlConfig::default();
    let input = observation_len(&rl.observation);
    let menu = ActionCodec::v1(&rl.observation).len();
    let header = ArtifactHeader {
        artifact_version: ARTIFACT_VERSION,
        observation_schema: 1,
        action_schema: 1,
        mask_schema: 1,
        layers: vec![[input, hidden], [hidden, menu]],
        activation: "relu".into(),
    };
    let modulus = (pattern % 13 + 5) as usize;
    let w1: Vec<f32> = (0..input * hidden)
        .map(|i| ((i % modulus) as f32 - (modulus as f32 / 2.0)) * 0.03)
        .collect();
    let (w2, b2): (Vec<f32>, Vec<f32>) = match output_fill {
        Some(fill) => (
            vec![fill; hidden * menu],
            (0..menu).map(|i| fill * i as f32 * 0.01).collect(),
        ),
        None => (
            (0..hidden * menu)
                .map(|i| ((i % (modulus + 2)) as f32 - 2.0) * 0.05)
                .collect(),
            vec![0.0; menu],
        ),
    };
    write_artifact(path, &header, &[(w1, vec![0.02; hidden]), (w2, b2)])
        .expect("fixture artifacts write");
}

/// [`write_fixture_artifact`] into a namespaced temp directory; returns the
/// artifact path.
///
/// Parallel tests may share a `(dir_name, file_name)` pair, so the artifact
/// is written to a private scratch name and renamed into place: rename is
/// atomic, and the bytes are deterministic for the same parameters, so a
/// concurrent reader always sees a complete, correct artifact — never a
/// half-written one (the `BadMagic` flake this replaces).
pub fn fixture_artifact(dir_name: &str, file_name: &str, hidden: usize, pattern: u32) -> PathBuf {
    fixture_artifact_with_output(dir_name, file_name, hidden, pattern, None)
}

/// [`fixture_artifact`] with the output layer optionally flooded (see
/// [`write_fixture_artifact_with_output`]) — the constant-logit shape the
/// --sample tests need — under the same atomic rename discipline.
pub fn fixture_artifact_with_output(
    dir_name: &str,
    file_name: &str,
    hidden: usize,
    pattern: u32,
    output_fill: Option<f32>,
) -> PathBuf {
    static SCRATCH: AtomicU64 = AtomicU64::new(0);
    let dir = std::env::temp_dir().join(dir_name);
    std::fs::create_dir_all(&dir).expect("temp dir");
    let path = dir.join(format!("{file_name}.ckpolicy"));
    let scratch = dir.join(format!(
        "{file_name}.{}.{}.scratch",
        std::process::id(),
        SCRATCH.fetch_add(1, Ordering::Relaxed)
    ));
    write_fixture_artifact_with_output(&scratch, hidden, pattern, output_fill);
    std::fs::rename(&scratch, &path).expect("fixture artifacts land");
    path
}
