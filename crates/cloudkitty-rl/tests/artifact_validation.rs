//! Artifact validation (spec 014 FR-016, T041): missing, truncated,
//! corrupt, and schema-mismatched artifacts each produce an error the
//! caller can attribute to its config field; the content hash is stable
//! across loads.

use std::path::PathBuf;

use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::policy::{ArtifactError, PolicyArtifact};

fn scratch_dir(name: &str) -> PathBuf {
    let dir = std::env::temp_dir()
        .join("ck-artifact-validation")
        .join(name);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// A valid artifact shaped for the default schemas: obs → 16 → 40.
fn valid_artifact(path: &std::path::Path) {
    cloudkitty_rl::test_support::write_fixture_artifact(path, 16, 5);
}

#[test]
fn a_valid_artifact_loads_with_a_stable_hash() {
    let path = scratch_dir("valid").join("policy.ckpolicy");
    valid_artifact(&path);
    let rl = RlConfig::default();

    let a = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    let b = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();
    assert_eq!(a.content_hash(), b.content_hash(), "same file, same hash");
    assert_eq!(a.content_hash().len(), 64);
}

#[test]
fn missing_truncated_corrupt_and_mismatched_artifacts_each_fail_by_name() {
    let rl = RlConfig::default();
    let expectations = PolicyBehavior::expectations(&rl);

    // Missing.
    let missing = scratch_dir("missing").join("nope.ckpolicy");
    assert!(matches!(
        PolicyArtifact::load(&missing, &expectations),
        Err(ArtifactError::Io(_))
    ));

    // Corrupt: not our file at all.
    let corrupt = scratch_dir("corrupt").join("garbage.ckpolicy");
    std::fs::write(&corrupt, b"not a policy, just bytes").unwrap();
    assert!(matches!(
        PolicyArtifact::load(&corrupt, &expectations),
        Err(ArtifactError::BadMagic)
    ));

    // Truncated: a valid file with its tail cut off.
    let truncated = scratch_dir("truncated").join("short.ckpolicy");
    valid_artifact(&truncated);
    let bytes = std::fs::read(&truncated).unwrap();
    std::fs::write(&truncated, &bytes[..bytes.len() - 100]).unwrap();
    assert!(matches!(
        PolicyArtifact::load(&truncated, &expectations),
        Err(ArtifactError::BlobSize { .. })
    ));

    // Schema-mismatched: an artifact one generation OLDER than the binary
    // (relative offset, so the test names a mismatch in every generation).
    // The message is the whole diagnosis on the day this fires (spec 026
    // contract C3): both generation numbers and the re-train remedy.
    let mismatched = scratch_dir("mismatch").join("old-schema.ckpolicy");
    valid_artifact(&mismatched);
    let mut wrong = expectations;
    wrong.observation_schema += 1;
    let err = PolicyArtifact::load(&mismatched, &wrong).unwrap_err();
    assert!(
        matches!(
            err,
            ArtifactError::SchemaMismatch {
                schema: "observation",
                ..
            }
        ),
        "{err}"
    );
    let msg = err.to_string();
    assert!(
        msg.contains(&format!("v{}", expectations.observation_schema))
            && msg.contains(&format!("v{}", wrong.observation_schema)),
        "names found and expected generations: {msg}"
    );
    assert!(msg.contains("re-trained"), "carries the remedy: {msg}");

    // The symmetric direction: an artifact one generation NEWER than the
    // binary (a schema-2 file met by a schema-1 server) refuses just as
    // legibly, numbers reversed.
    let mut older_binary = expectations;
    older_binary.observation_schema -= 1;
    let err = PolicyArtifact::load(&mismatched, &older_binary).unwrap_err();
    let msg = err.to_string();
    assert!(
        matches!(
            err,
            ArtifactError::SchemaMismatch {
                schema: "observation",
                ..
            }
        ) && msg.contains("re-trained"),
        "symmetric refusal, same remedy: {msg}"
    );

    // Shape-mismatched: input width for a different slot configuration.
    // Both widths and the predates-the-generation hint must be in the text
    // (the width gate fires independently of the schema gate).
    let mut small = RlConfig::default();
    small.observation.kitty_slots = 1;
    let small_expect = PolicyBehavior::expectations(&small);
    let err = PolicyArtifact::load(&mismatched, &small_expect).unwrap_err();
    assert!(matches!(err, ArtifactError::Shape(_)), "{err}");
    let msg = err.to_string();
    assert!(
        msg.contains(&expectations.observation_len.to_string())
            && msg.contains(&small_expect.observation_len.to_string()),
        "names both widths: {msg}"
    );
    assert!(
        msg.contains("generation") && msg.contains("re-trained"),
        "hints at the generation wall and the remedy: {msg}"
    );
}
