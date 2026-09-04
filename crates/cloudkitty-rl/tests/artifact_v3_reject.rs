//! Spec 030 US2 (T015): each incompatible v3 artifact fails load naming the
//! field and reason, before any tick (FR-006, SC-003). One case per class.

use std::path::{Path, PathBuf};

use cloudkitty_rl::attn::blob_float_count;
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::policy::{ArtifactError, PolicyArtifact, ARTIFACT_MAGIC};
use cloudkitty_rl::test_support::default_v3_header;

fn scratch_dir(name: &str) -> PathBuf {
    let dir = std::env::temp_dir()
        .join("ck-artifact-v3-reject")
        .join(name);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// Writes a raw artifact from a header JSON string and a zero blob of
/// `floats` values — so a test can inject a defect the typed writer would not
/// allow (an unknown key, a wrong version, a short blob).
fn craft(path: &Path, header_json: &str, floats: usize) {
    let json = format!("{header_json}\n");
    let mut bytes = Vec::new();
    bytes.extend_from_slice(ARTIFACT_MAGIC);
    bytes.extend_from_slice(&(json.len() as u32).to_le_bytes());
    bytes.extend_from_slice(json.as_bytes());
    for _ in 0..floats {
        bytes.extend_from_slice(&0.0f32.to_le_bytes());
    }
    std::fs::write(path, bytes).unwrap();
}

fn valid_floats() -> usize {
    let rl = RlConfig::default();
    blob_float_count(&default_v3_header(), &rl.observation)
}

fn header_json_with(mutate: impl FnOnce(&mut serde_json::Value)) -> String {
    let mut v = serde_json::to_value(default_v3_header()).unwrap();
    mutate(&mut v);
    serde_json::to_string(&v).unwrap()
}

#[test]
fn each_rejection_class_fails_by_name_before_any_tick() {
    let rl = RlConfig::default();
    let expect = PolicyBehavior::expectations(&rl);
    let floats = valid_floats();
    let dir = scratch_dir("cases");

    // Version not in the supported set: rejected by version, not by shape.
    let p = dir.join("version.ckpolicy");
    craft(
        &p,
        &header_json_with(|v| v["artifact_version"] = 4.into()),
        floats,
    );
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
    assert!(
        matches!(err, ArtifactError::UnsupportedVersion { found: 4, .. }),
        "{err}"
    );
    assert!(
        err.to_string().contains("2, 3"),
        "lists the supported set: {err}"
    );

    // Unknown / misspelled header key: strict parse names the field.
    let p = dir.join("unknown-key.ckpolicy");
    craft(&p, &header_json_with(|v| v["d_modell"] = 64.into()), floats);
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
    assert!(matches!(err, ArtifactError::Header(_)), "{err}");
    assert!(
        err.to_string().contains("d_modell"),
        "names the stray key: {err}"
    );

    // Schema pin mismatch.
    let p = dir.join("schema.ckpolicy");
    craft(
        &p,
        &header_json_with(|v| v["observation_schema"] = 99.into()),
        floats,
    );
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
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

    // Spec 033 (T019): the GENERATION gate, pin by pin -- an artifact from
    // the pre-wall generation carries observation 3 / action 2 / mask 2,
    // and each stale pin is refused independently, naming itself. This is
    // how the wall refuses by version and never by shape accident.
    for (key, stale, schema) in [
        ("observation_schema", 3, "observation"),
        ("action_schema", 2, "action"),
        ("mask_schema", 2, "mask"),
    ] {
        let p = dir.join(format!("stale-{schema}.ckpolicy"));
        craft(&p, &header_json_with(|v| v[key] = stale.into()), floats);
        let err = PolicyArtifact::load(&p, &expect).unwrap_err();
        match err {
            ArtifactError::SchemaMismatch { schema: named, .. } => assert_eq!(
                named, schema,
                "the pre-wall {schema} pin is refused naming its own schema"
            ),
            other => panic!("stale {schema} pin: wrong error class: {other}"),
        }
    }

    // Unrecognized architecture.
    let p = dir.join("arch.ckpolicy");
    craft(
        &p,
        &header_json_with(|v| v["architecture"] = "mlp".into()),
        floats,
    );
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
    assert!(matches!(err, ArtifactError::Architecture(_)), "{err}");
    assert!(
        err.to_string().contains("mlp"),
        "names the bad architecture: {err}"
    );

    // Bad hyperparameter: d_model not divisible by heads.
    let p = dir.join("hyper.ckpolicy");
    craft(&p, &header_json_with(|v| v["d_model"] = 63.into()), floats);
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
    assert!(matches!(err, ArtifactError::Hyperparameter(_)), "{err}");
    assert!(err.to_string().contains("divisible"), "{err}");

    // Non-positive hyperparameter.
    let p = dir.join("zero.ckpolicy");
    craft(&p, &header_json_with(|v| v["ffn"] = 0.into()), floats);
    assert!(matches!(
        PolicyArtifact::load(&p, &expect),
        Err(ArtifactError::Hyperparameter(_))
    ));

    // Blob length inconsistent with the hyperparameters.
    let p = dir.join("blob.ckpolicy");
    craft(
        &p,
        &serde_json::to_string(&default_v3_header()).unwrap(),
        floats - 1,
    );
    let err = PolicyArtifact::load(&p, &expect).unwrap_err();
    assert!(matches!(err, ArtifactError::BlobSize { .. }), "{err}");
}

#[test]
fn a_v3_artifact_on_a_v2_only_supported_set_is_rejected_by_version() {
    // The version gate keys on the loader's supported set; a header the build
    // does not support is refused at the version check, not downstream. Here
    // we assert the symmetric guarantee with a made-up future version: it is
    // an UnsupportedVersion, never a shape/blob error.
    let rl = RlConfig::default();
    let expect = PolicyBehavior::expectations(&rl);
    let dir = scratch_dir("future");
    let p = dir.join("v9.ckpolicy");
    let json = header_json_with(|v| v["artifact_version"] = 9.into());
    craft(&p, &json, valid_floats());
    assert!(matches!(
        PolicyArtifact::load(&p, &expect),
        Err(ArtifactError::UnsupportedVersion { found: 9, .. })
    ));
}

/// Spec 049 FR-025 / SC-008: a REAL schema-4 artifact -- the spec-033
/// oracle, kept beside its schema-5 successor as this witness -- is
/// refused at load naming the observation schema and both versions,
/// before any tick.
#[test]
fn schema_four_artifact_is_refused() {
    let rl = RlConfig::default();
    let expect = PolicyBehavior::expectations(&rl);
    let old =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/oracle-schema4.ckpolicy");
    let err = PolicyArtifact::load(&old, &expect).expect_err("schema 4 cannot cross the wall");
    match err {
        ArtifactError::SchemaMismatch {
            schema,
            found,
            expected,
        } => {
            assert_eq!(schema, "observation");
            assert_eq!((found, expected), (4, 5));
        }
        other => panic!("wrong error class: {other}"),
    }
}
