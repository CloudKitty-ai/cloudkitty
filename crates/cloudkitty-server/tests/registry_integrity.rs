//! The model registry's release-honest gate (spec 034 FR-008): every
//! `.ckpolicy` at `policies/` top level has a row in `policies/registry.toml`
//! keyed by the file's actual sha256, and the registry itself parses
//! strictly (unknown fields refused, all fields required and non-empty —
//! enforced inside the loader this test goes through, the same code path
//! the server refuses startup with).
//!
//! The row→file direction is deliberately unchecked: rows are history —
//! sha is identity, so retirement and renames keep their rows (US2
//! scenarios 2–3). A row for a sha that never existed is a review concern,
//! not a machine check.

use std::path::PathBuf;

use sha2::{Digest, Sha256};

#[test]
fn every_top_level_artifact_has_a_registry_row() {
    let policies = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../policies");
    // The loader resolves registry.toml beside its argument; the probe name
    // itself never needs to exist.
    let rows = cloudkitty_server::load_registry_beside(&policies.join("_probe.ckpolicy"))
        .expect("policies/registry.toml parses strictly with every field present");
    assert!(
        !rows.is_empty(),
        "the registry ships rows for the certified artifacts"
    );

    let mut checked = 0usize;
    for entry in std::fs::read_dir(&policies).expect("policies/ is readable") {
        let path = entry.expect("dir entry").path();
        // Top level only: retired/ keeps its rows but is out of scope here.
        if path.extension().and_then(|e| e.to_str()) != Some("ckpolicy") {
            continue;
        }
        let bytes = std::fs::read(&path).expect("artifact readable");
        let sha = format!("{:x}", Sha256::digest(&bytes));
        assert!(
            rows.contains_key(&sha),
            "policies/{} (sha256 {sha}) has no row in policies/registry.toml — \
             the row lands in the same PR as the artifact (spec 034 FR-003/FR-008)",
            path.file_name().unwrap().to_string_lossy()
        );
        checked += 1;
    }
    assert!(
        checked > 0,
        "the walk found the committed artifacts (wrong path anchor?)"
    );
}
