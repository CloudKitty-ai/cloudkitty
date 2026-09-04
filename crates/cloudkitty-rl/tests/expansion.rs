//! Spec 035: the surface-expansion export, end to end.
//!
//! The three committed pre-wall artifacts in `policies/retired/` (moved
//! there at the phase-1 cutover, rows kept per the README's retirement
//! rule) are the real old-generation fixtures (read-only); synthetic
//! small ones are written
//! with old-pin headers where cheap shapes are needed. The deaf/mute tests
//! implement the U1 per-family split: v2 full presence-vs-absence deafness,
//! v3 kind-identity insensitivity (relabeling equivalence).

use std::path::{Path, PathBuf};

use cloudkitty_rl::attn::{write_v3_artifact, V3Header, V3_ARCHITECTURE};
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::codec::ActionCodec;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::expand::{expand_file, old_v3_blob_float_count, ExpandError};
use cloudkitty_rl::observe::{observation_len, HEAD_KINDS};
use cloudkitty_rl::policy::{
    split_container_for_expansion, write_artifact, ArtifactHeader, PolicyArtifact,
};

fn policies_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../policies/retired")
}

fn temp_dir(label: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("ck-035-{label}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).expect("temp dir");
    dir
}

fn expectations() -> cloudkitty_rl::policy::SchemaExpectations {
    PolicyBehavior::expectations(&RlConfig::default())
}

/// The pre-wall geometry, derived (never quoted): digest 8×4 + clock.
fn old_obs_len() -> usize {
    observation_len(&RlConfig::default().observation) - (HEAD_KINDS.len() * 4 + 1) + 8 * 4 + 1
}

/// A synthetic schema-3 v2 artifact with deterministic pattern weights.
fn write_old_v2_fixture(path: &Path, hidden: usize, pattern: u32) {
    let cfg = RlConfig::default().observation;
    let input = old_obs_len();
    let out = ActionCodec::v2(&cfg).len() + 9; // menu + Silent + 8 legacy kinds
    let header = ArtifactHeader {
        artifact_version: 2,
        observation_schema: 3,
        action_schema: 2,
        mask_schema: 2,
        layers: vec![[input, hidden], [hidden, out]],
        activation: "relu".into(),
    };
    let modulus = (pattern % 13 + 5) as usize;
    let w1: Vec<f32> = (0..input * hidden)
        .map(|i| ((i % modulus) as f32 - (modulus as f32 / 2.0)) * 0.03)
        .collect();
    let w2: Vec<f32> = (0..hidden * out)
        .map(|i| ((i % (modulus + 2)) as f32 - 2.0) * 0.05)
        .collect();
    write_artifact(
        path,
        &header,
        &[(w1, vec![0.02; hidden]), (w2, vec![0.0; out])],
    )
    .expect("old v2 fixture writes");
}

/// A synthetic schema-3 v3 artifact (small hyperparameters).
fn write_old_v3_fixture(path: &Path, pattern: u32) -> V3Header {
    let cfg = RlConfig::default().observation;
    let header = V3Header {
        artifact_version: 3,
        observation_schema: 3,
        action_schema: 2,
        mask_schema: 2,
        architecture: V3_ARCHITECTURE.to_string(),
        d_model: 16,
        heads: 2,
        encoder_layers: 1,
        ffn: 32,
    };
    let n = old_v3_blob_float_count(&header, &cfg);
    let modulus = (pattern % 17 + 7) as usize;
    let blob: Vec<f32> = (0..n)
        .map(|i| ((i % modulus) as f32 - (modulus as f32 / 2.0)) * 0.02)
        .collect();
    write_v3_artifact(path, &header, &blob).expect("old v3 fixture writes");
    header
}

// ---- T001/T002: the tool reads what the serving loader refuses ----

#[test]
fn the_serving_loader_still_refuses_what_the_tool_reads() {
    for name in ["e004-a1-s2.ckpolicy", "attn-a1-s1.ckpolicy"] {
        let path = policies_dir().join(name);
        let err = PolicyArtifact::load(&path, &expectations())
            .expect_err("the generation gate refuses pre-wall artifacts");
        assert!(
            format!("{err}").contains("schema"),
            "{name}: refused for schema reasons, got: {err}"
        );
        split_container_for_expansion(&path)
            .unwrap_or_else(|e| panic!("{name}: the tooling read parses any generation: {e}"));
    }
}

// ---- spec 049 T032: no map across the fog wall ----

/// The three committed pre-wall sources, plus synthetic old v2/v3
/// fixtures: every expansion is refused at this binary's surface
/// (observation 5), naming the compiled surface and the tool's one target
/// (observation 4 / action 3 / mask 3), before any source byte is read.
/// The spec-035 placement, attestation and deaf/mute guards this file
/// carried ran the map for real; with no map onto schema 5 they cannot
/// execute, and live in git history (`git log -S an_expanded_v2_mind`)
/// for the day a 3.0 map is ruled.
#[test]
fn every_expansion_is_refused_at_the_3_0_wall_naming_both_surfaces() {
    let dir = temp_dir("refuse-wall");
    let mut sources: Vec<PathBuf> = ["attn-a1-s1", "attn-a1-s3", "e004-a1-s2"]
        .iter()
        .map(|name| policies_dir().join(format!("{name}.ckpolicy")))
        .collect();
    let old_v2 = dir.join("old-v2.ckpolicy");
    write_old_v2_fixture(&old_v2, 8, 11);
    let old_v3 = dir.join("old-v3.ckpolicy");
    write_old_v3_fixture(&old_v3, 7);
    sources.push(old_v2);
    sources.push(old_v3);
    for source in sources {
        let out = dir.join("out.ckpolicy");
        let err = expand_file(&source, &out).expect_err("no map across the wall");
        assert!(
            matches!(err, ExpandError::UnmappedTarget { o: 5, a: 3, m: 3 }),
            "{}: {err}",
            source.display()
        );
        let text = format!("{err}");
        assert!(
            text.contains("observation 5") && text.contains("observation 4"),
            "{text}"
        );
        assert!(!out.exists(), "nothing is written");
    }
}

// ---- T006: refusals ----

#[test]
fn a_current_generation_source_is_refused_as_nothing_to_expand() {
    let dir = temp_dir("refuse-current");
    let current =
        cloudkitty_rl::test_support::fixture_artifact("ck-035-refuse-current", "now", 8, 11);
    let err = expand_file(&current, &dir.join("out.ckpolicy")).unwrap_err();
    assert!(matches!(err, ExpandError::AlreadyCurrent { .. }), "{err}");
    assert!(format!("{err}").contains("nothing to expand"), "{err}");
}

#[test]
fn an_unmapped_generation_is_refused_naming_its_pins() {
    let dir = temp_dir("refuse-unmapped");
    let source = dir.join("ancient.ckpolicy");
    let header = ArtifactHeader {
        artifact_version: 2,
        observation_schema: 1,
        action_schema: 1,
        mask_schema: 1,
        layers: vec![[4, 2], [2, 3]],
        activation: "relu".into(),
    };
    write_artifact(
        &source,
        &header,
        &[(vec![0.0; 8], vec![0.0; 2]), (vec![0.0; 6], vec![0.0; 3])],
    )
    .unwrap();
    let err = expand_file(&source, &dir.join("out.ckpolicy")).unwrap_err();
    assert!(
        matches!(err, ExpandError::UnmappedGeneration { .. }),
        "{err}"
    );
    let msg = format!("{err}");
    assert!(
        msg.contains("ancient.ckpolicy") && msg.contains("observation 1"),
        "{msg}"
    );
}

#[test]
fn a_corrupted_source_is_refused() {
    let dir = temp_dir("refuse-corrupt");
    let source = dir.join("chewed.ckpolicy");
    std::fs::write(&source, b"chewed by a greeble").unwrap();
    let err = expand_file(&source, &dir.join("out.ckpolicy")).unwrap_err();
    assert!(matches!(err, ExpandError::Read(_)), "{err}");
}

#[test]
fn an_unknown_version_is_refused() {
    let dir = temp_dir("refuse-version");
    let source = dir.join("future.ckpolicy");
    let header_json =
        r#"{"artifact_version":9,"observation_schema":3,"action_schema":2,"mask_schema":2}"#;
    let mut bytes = Vec::new();
    bytes.extend_from_slice(cloudkitty_rl::policy::ARTIFACT_MAGIC);
    bytes.extend_from_slice(&(header_json.len() as u32).to_le_bytes());
    bytes.extend_from_slice(header_json.as_bytes());
    std::fs::write(&source, bytes).unwrap();
    let err = expand_file(&source, &dir.join("out.ckpolicy")).unwrap_err();
    assert!(
        matches!(err, ExpandError::UnknownVersion { found: 9, .. }),
        "{err}"
    );
}

#[test]
fn a_malformed_v3_header_is_refused_not_panicked_on() {
    // Review finding: d_model=0 reached a divide-by-zero; encoder_layers=0
    // could attest an artifact the serving loader refuses. Both now earn
    // the named refusal.
    let dir = temp_dir("v3-hyper-guard");
    for (field, value) in [("d_model", 0u32), ("encoder_layers", 0u32), ("heads", 3u32)] {
        let source = dir.join(format!("bad-{field}.ckpolicy"));
        let header_json = format!(
            r#"{{"artifact_version":3,"observation_schema":3,"action_schema":2,"mask_schema":2,"architecture":"entity_attention","d_model":{},"heads":{},"encoder_layers":{},"ffn":{}}}"#,
            if field == "d_model" { value } else { 16 },
            if field == "heads" { value } else { 2 },
            if field == "encoder_layers" { value } else { 1 },
            32
        );
        let mut bytes = Vec::new();
        bytes.extend_from_slice(cloudkitty_rl::policy::ARTIFACT_MAGIC);
        bytes.extend_from_slice(&(header_json.len() as u32).to_le_bytes());
        bytes.extend_from_slice(header_json.as_bytes());
        std::fs::write(&source, bytes).unwrap();
        let err = expand_file(&source, &dir.join("out.ckpolicy")).unwrap_err();
        // At the spec-049 wall the target gate refuses every pre-wall
        // source before its hyperparameters are read -- still a named
        // refusal, never a panic. The guard itself is exercised at its
        // own layer (`expand::tests::the_v3_hyperparameter_guard_names_
        // each_refusal`); this test pins the gate in front of it.
        assert!(
            matches!(err, ExpandError::UnmappedTarget { .. }),
            "{field}: named refusal, not a panic: {err}"
        );
    }
}
