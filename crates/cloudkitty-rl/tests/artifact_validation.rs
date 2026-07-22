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

    let a = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl).unwrap();
    let b = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl).unwrap();
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

    // Schema-mismatched: trained against a different observation schema.
    let mismatched = scratch_dir("mismatch").join("old-schema.ckpolicy");
    valid_artifact(&mismatched);
    let mut wrong = expectations;
    wrong.observation_schema = 2;
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
    assert!(err.to_string().contains("observation"), "{err}");

    // Shape-mismatched: input width for a different slot configuration.
    let mut small = RlConfig::default();
    small.observation.kitty_slots = 1;
    let err = PolicyArtifact::load(&mismatched, &PolicyBehavior::expectations(&small)).unwrap_err();
    assert!(matches!(err, ArtifactError::Shape(_)), "{err}");
}
