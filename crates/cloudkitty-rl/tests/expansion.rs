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

use cloudkitty_core::rng::SimRng;
use cloudkitty_rl::attn::{write_v3_artifact, V3Header, V3_ARCHITECTURE};
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::expand::{
    expand_file, old_v3_blob_float_count, verify_expansion, ExpandError, NEW_HEAD_FLOOR,
};
use cloudkitty_rl::observe::{observation_len, HEAD_KINDS};
use cloudkitty_rl::policy::{
    split_container_for_expansion, write_artifact, ArtifactHeader, PolicyArtifact, Scratch,
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

// ---- T007 + convergence T013/T014: all three committed artifacts ----

/// The three phase-1 candidates' output shas, pinned (convergence T014,
/// SC-002's across-machines clause): CI — a different machine — must
/// reproduce these exact bytes from the committed sources, or determinism
/// is broken. Mechanically-checked duplication per the policies/README
/// doctrine; an `EXPANSION_TOOL_VERSION` bump moves these in the same
/// change, which is precisely what keying determinism to the version means.
const EXPECTED_O4_SHAS: [(&str, &str); 3] = [
    (
        "attn-a1-s1",
        "61d6d7cc699f1de303b4fb661a77380bf56b5d69e76db3eac5bd316b38ed604a",
    ),
    (
        "attn-a1-s3",
        "d6f60818ad0516445367a3cdbca2a7df24a36886ed457e3ee1c8fe06004569ad",
    ),
    (
        "e004-a1-s2",
        "b6293849a63bd2f8b915080e74a20a5dd5f539eb48911bece3d4e23876588b09",
    ),
];

#[tokio::test]
async fn all_three_committed_artifacts_expand_load_and_drive_a_kitty() {
    let dir = temp_dir("roundtrip");
    for (name, expected_sha) in EXPECTED_O4_SHAS {
        let source = policies_dir().join(format!("{name}.ckpolicy"));
        let output = dir.join(format!("{name}-o4.ckpolicy"));
        let attestation =
            expand_file(&source, &output).unwrap_or_else(|e| panic!("{name} expands: {e}"));
        assert_eq!(
            attestation.mapped, attestation.total_source,
            "{name}: bijective"
        );
        assert_eq!(
            attestation.mapped + attestation.zeroed + attestation.floored,
            attestation.total_output,
            "{name}: counts partition the output"
        );
        assert_eq!(
            attestation.output_sha256, expected_sha,
            "{name}: SC-002 across machines — this machine reproduced \
             different bytes than the pinned expansion"
        );
        // First-class: the UNTOUCHED serving loader opens the output.
        let loaded = PolicyArtifact::load(&output, &expectations())
            .unwrap_or_else(|e| panic!("{name}-o4 loads first-class: {e}"));
        assert_eq!(loaded.sha256, attestation.output_sha256);

        // ...and DRIVES a kitty (convergence T013, SC-001/US1-AC2): the
        // real expanded mind decides in a ticking world, not just a loader.
        let mut config = cloudkitty_core::test_support::test_config();
        config.kitties[0].behavior = "policy:crossed".into();
        let config = std::sync::Arc::new(config);
        let mut registry = cloudkitty_core::BehaviorRegistry::with_builtins();
        registry.register(
            "policy:crossed",
            std::sync::Arc::new(PolicyBehavior::new(
                loaded.clone(),
                RlConfig::default(),
                false,
            )),
        );
        let mut world = cloudkitty_core::World::generate(&config);
        for _ in 0..10 {
            world.tick(&registry, &config).await;
        }
        assert_eq!(
            world.kitties.len(),
            config.kitties.len(),
            "{name}-o4 drove its kitty for 10 ticks (Article II intact)"
        );
        assert_eq!(world.tick, 10, "{name}-o4: the world really ticked");
    }
}

#[test]
fn expansion_is_deterministic_byte_for_byte() {
    let dir = temp_dir("determinism");
    let source = policies_dir().join("attn-a1-s1.ckpolicy");
    let a = dir.join("a-o4.ckpolicy");
    let b = dir.join("b-o4.ckpolicy");
    let sha_a = expand_file(&source, &a).expect("first run").output_sha256;
    let sha_b = expand_file(&source, &b).expect("second run").output_sha256;
    assert_eq!(sha_a, sha_b, "same source + tool version -> same bytes");
    assert_eq!(
        std::fs::read(&a).unwrap(),
        std::fs::read(&b).unwrap(),
        "byte-identical, not merely same-hash"
    );
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

// ---- T008: deaf and mute, per the U1 family split ----

/// New-kind digest offsets in the current observation: rows 8..15 of the
/// digest block, derived from the layout.
fn new_digest_range() -> std::ops::Range<usize> {
    let cfg = RlConfig::default().observation;
    let new_len = observation_len(&cfg);
    let digest_start = new_len - (HEAD_KINDS.len() * 4 + 1);
    digest_start + 8 * 4..new_len - 1
}

#[test]
fn an_expanded_v2_mind_is_fully_deaf_and_mute() {
    let dir = temp_dir("v2-deaf-mute");
    let source = dir.join("old.ckpolicy");
    write_old_v2_fixture(&source, 8, 11);
    let output = dir.join("old-o4.ckpolicy");
    expand_file(&source, &output).expect("expands");
    let artifact = PolicyArtifact::load(&output, &expectations()).expect("loads");

    let cfg = RlConfig::default().observation;
    let obs_len = observation_len(&cfg);
    let menu = ActionCodec::v2(&cfg).len();
    let new_range = new_digest_range();
    let mut rng = SimRng::from_seed(0x2026_0817);
    let mut scratch = Scratch::default();
    for _ in 0..200 {
        let mut obs: Vec<f32> = (0..obs_len)
            .map(|_| (rng.gen_range_u32(0, 200) as f32 / 100.0) - 1.0)
            .collect();
        // Mute: every new-kind head logit is the constant floor, exactly.
        let with: Vec<f32> = artifact.forward(&obs, &mut scratch).to_vec();
        for (k, logit) in with[menu + 9..menu + MessageCodec::LEN].iter().enumerate() {
            assert_eq!(
                logit.to_bits(),
                NEW_HEAD_FLOOR.to_bits(),
                "new head logit {k} is the constant floor"
            );
        }
        // Deaf (v2 full form): zeroing the new digest columns changes no bit.
        for i in new_range.clone() {
            obs[i] = 0.0;
        }
        let without: Vec<f32> = artifact.forward(&obs, &mut scratch).to_vec();
        assert_eq!(
            with.iter().map(|f| f.to_bits()).collect::<Vec<_>>(),
            without.iter().map(|f| f.to_bits()).collect::<Vec<_>>(),
            "v2 deafness is presence-vs-absence bit-identity"
        );
    }
}

#[test]
fn an_expanded_v3_mind_is_mute_and_kind_identity_insensitive() {
    let dir = temp_dir("v3-deaf-mute");
    let source = dir.join("old.ckpolicy");
    write_old_v3_fixture(&source, 5);
    let output = dir.join("old-o4.ckpolicy");
    expand_file(&source, &output).expect("expands");
    let artifact = PolicyArtifact::load(&output, &expectations()).expect("loads");

    let cfg = RlConfig::default().observation;
    let obs_len = observation_len(&cfg);
    let menu = ActionCodec::v2(&cfg).len();
    let digest_start = obs_len - (HEAD_KINDS.len() * 4 + 1);
    let mut rng = SimRng::from_seed(0x2026_0818);
    let mut scratch = Scratch::default();
    for _ in 0..50 {
        let base: Vec<f32> = (0..obs_len)
            .map(|_| (rng.gen_range_u32(0, 200) as f32 / 100.0) - 1.0)
            .collect();
        // One audible new-kind tuple, injected as kind A then as kind B
        // (rows 8..15 are the new kinds); everything else identical.
        let tuple = [0.8f32, 0.1, -0.2, 0.0];
        let mut kinds = [
            8 + rng.gen_range_u32(0, 7) as usize,
            8 + rng.gen_range_u32(0, 7) as usize,
        ];
        if kinds[0] == kinds[1] {
            kinds[1] = 8 + (kinds[0] - 8 + 1) % 7;
        }
        let mut logits = Vec::new();
        for kind in kinds {
            let mut obs = base.clone();
            // Silence every new-kind row, then speak exactly one.
            for row in 8..HEAD_KINDS.len() {
                for f in 0..4 {
                    obs[digest_start + row * 4 + f] = 0.0;
                }
            }
            for (f, v) in tuple.iter().enumerate() {
                obs[digest_start + kind * 4 + f] = *v;
            }
            let out: Vec<f32> = artifact.forward(&obs, &mut scratch).to_vec();
            // Mute: constant floor on every new head output.
            for logit in &out[menu + 9..menu + MessageCodec::LEN] {
                assert_eq!(logit.to_bits(), NEW_HEAD_FLOOR.to_bits());
            }
            logits.push(out);
        }
        // Kind-identity insensitivity (U1): which new kind carried the
        // tuple must not matter. Zeroed type rows make the tokens
        // identical; attention and the masked mean pool are
        // permutation-invariant over identical token values.
        assert_eq!(
            logits[0].iter().map(|f| f.to_bits()).collect::<Vec<_>>(),
            logits[1].iter().map(|f| f.to_bits()).collect::<Vec<_>>(),
            "relabeling a new kind changed the forward"
        );
    }
}

// ---- T009: the attestation cannot pass by accident ----

#[test]
fn a_corrupted_expansion_fails_verification_naming_the_class() {
    let dir = temp_dir("mutations");
    let source = dir.join("old.ckpolicy");
    write_old_v2_fixture(&source, 8, 11);
    let output = dir.join("old-o4.ckpolicy");
    expand_file(&source, &output).expect("expands");

    let (header, blob, _) = split_container_for_expansion(&source).unwrap();
    let good = std::fs::read(&output).unwrap();
    let cfg = RlConfig::default().observation;
    verify_expansion(&header, &blob, &good, &cfg).expect("the honest output verifies");

    let hlen = u32::from_le_bytes([good[8], good[9], good[10], good[11]]) as usize;
    let body = 12 + hlen;
    let put = |bytes: &mut Vec<u8>, float_index: usize, value: f32| {
        let at = body + float_index * 4;
        bytes[at..at + 4].copy_from_slice(&value.to_le_bytes());
    };

    // (i) A new head bias flattened to 0.0 -> "not the floor".
    let mut mutated = good.clone();
    let total_floats = (good.len() - body) / 4;
    put(&mut mutated, total_floats - 1, 0.0);
    let err = verify_expansion(&header, &blob, &mutated, &cfg).unwrap_err();
    assert!(err.contains("floor"), "{err}");

    // (ii) A new input column made nonzero -> "not 0.0".
    let mut mutated = good.clone();
    let new_len = observation_len(&cfg);
    put(&mut mutated, new_len - 2, 1.0); // row 0, a new digest column
    let err = verify_expansion(&header, &blob, &mutated, &cfg).unwrap_err();
    assert!(err.contains("not 0.0"), "{err}");

    // (iii) A mapped value shifted -> "differs from source".
    let mut mutated = good.clone();
    put(&mut mutated, 0, 42.0);
    let err = verify_expansion(&header, &blob, &mutated, &cfg).unwrap_err();
    assert!(err.contains("differs"), "{err}");
}

// ---- T008(b): world-level — seated, full vocabulary, speaking neighbor ----

#[tokio::test]
async fn a_seated_expanded_v2_mind_stays_mute_and_deaf_in_a_running_world() {
    use cloudkitty_core::meow::{Meow, MessageKind};
    use cloudkitty_core::{BehaviorRegistry, World};

    let dir = temp_dir("world-mute");
    let source = dir.join("old.ckpolicy");
    write_old_v2_fixture(&source, 8, 11);
    let output = dir.join("old-o4.ckpolicy");
    expand_file(&source, &output).expect("expands");
    let artifact = PolicyArtifact::load(&output, &expectations()).expect("loads");

    let mut config = cloudkitty_core::test_support::test_config();
    // Every vocabulary flag on — the reserves included. The mask cannot be
    // the silencer here; only the floored head keeps the expanded mind mute.
    config.meow.vocabulary.trill = true;
    config.meow.vocabulary.ekekek = true;
    config.kitties[0].behavior = "policy:expanded".into();
    let config = std::sync::Arc::new(config);

    let rl = RlConfig::default();
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register(
        "policy:expanded",
        std::sync::Arc::new(PolicyBehavior::new(artifact, rl, false)),
    );

    let new_kinds = [
        MessageKind::HereFood,
        MessageKind::HereWater,
        MessageKind::HereCritter,
        MessageKind::HereSunbeam,
        MessageKind::Chirp,
        MessageKind::Trill,
        MessageKind::Ekekek,
        MessageKind::Mew, // mew is legacy (renamed follow_me) — NOT asserted absent
    ];
    let speaker = config.kitties[1].id;
    let subject = config.kitties[0].id;

    // Twin worlds from the same seed: one hears a neighbor speak a new
    // kind, one does not. The v2 mind is fully deaf, so the subject's
    // trajectory must match exactly (the scripted neighbor never reads
    // the free register, so its trajectory matches too).
    let mut heard = World::generate(&config);
    let mut silent = World::generate(&config);
    heard.recent_meows.push(Meow {
        kitty_id: speaker,
        kind: MessageKind::Chirp,
        tick: heard.tick,
        intensity: 0.0,
    });
    for _ in 0..40 {
        heard.tick(&registry, &config).await;
        silent.tick(&registry, &config).await;
    }

    // Mute: the expanded mind spoke no post-wall kind (mew excluded — it
    // is the legacy word under a new name and stays speakable).
    for meow in &heard.recent_meows {
        if meow.kitty_id == subject {
            assert!(
                !new_kinds[..7].contains(&meow.kind),
                "the expanded mind spoke a word it never learned: {:?}",
                meow.kind
            );
        }
    }
    // Deaf: the injected chirp changed nothing about the subject.
    let h = heard.kitty(subject).unwrap();
    let s = silent.kitty(subject).unwrap();
    assert_eq!(h.pos, s.pos, "position unchanged by an unheard word");
    assert_eq!(h.activity, s.activity, "activity unchanged");
    assert_eq!(
        h.needs, s.needs,
        "needs trajectory unchanged — full v2 deafness at world level"
    );
}

// ---- 035-review remediation: the verifier's independence, proven ----

#[test]
fn the_verifier_rejects_what_construction_never_produces() {
    // The medium review's empirical finding: the verifier must be
    // independent of construction. Each scenario here is a "regressed
    // tool" output that the old verifier blessed or panicked on.
    let dir = temp_dir("verifier-independence");
    let source = dir.join("old.ckpolicy");
    write_old_v2_fixture(&source, 8, 11);
    let output = dir.join("old-o4.ckpolicy");
    expand_file(&source, &output).expect("expands");
    let (header, blob, _) = split_container_for_expansion(&source).unwrap();
    let good = std::fs::read(&output).unwrap();
    let cfg = RlConfig::default().observation;

    // (a) The source itself claimed as "output": old pins, never-widened
    // head — the exact regression the review confirmed attesting PASS.
    let source_bytes = std::fs::read(&source).unwrap();
    let err = verify_expansion(&header, &blob, &source_bytes, &cfg).unwrap_err();
    assert!(
        err.contains("not the current surface"),
        "an unexpanded output must fail on its pins: {err}"
    );

    // (b) A truncated output names the corruption instead of panicking.
    let err = verify_expansion(&header, &blob, &good[..good.len() / 2], &cfg).unwrap_err();
    assert!(
        err.contains("truncated") || err.contains("floats"),
        "truncation is named, not panicked on: {err}"
    );
    let err = verify_expansion(&header, &blob, &good[..10], &cfg).unwrap_err();
    assert!(err.contains("container"), "{err}");

    // (c) A sign-flipped -0.0 in a zeroed position is different bytes and
    // must fail the bit-exact zero check.
    let hlen = u32::from_le_bytes([good[8], good[9], good[10], good[11]]) as usize;
    let body = 12 + hlen;
    let mut negzero = good.clone();
    let new_len = observation_len(&cfg);
    let at = body + (new_len - 2) * 4; // row 0, a new digest column
    negzero[at..at + 4].copy_from_slice(&(-0.0f32).to_le_bytes());
    let err = verify_expansion(&header, &blob, &negzero, &cfg).unwrap_err();
    assert!(err.contains("not 0.0"), "-0.0 is not provably zero: {err}");

    // (d) A dropped source parameter cannot attest (T009's restored
    // criterion): shorten the source blob by one float.
    let err = verify_expansion(&header, &blob[..blob.len() - 4], &good, &cfg).unwrap_err();
    assert!(
        err.contains("dropped or extra source parameter"),
        "a dropped source parameter is named: {err}"
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
        let msg = format!("{err}");
        assert!(
            msg.contains("positive") || msg.contains("divisible"),
            "{field}: named refusal, not a panic: {msg}"
        );
    }
}
