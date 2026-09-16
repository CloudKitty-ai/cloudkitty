//! Server integration with a policy kitty (spec 014 US4, T044): a config
//! naming a policy boots with the artifact validated and hash-logged
//! before any tick; a corrupted artifact fails startup naming
//! `[rl.policy.<name>].artifact`; and the served world's state is
//! indistinguishable in shape from a built-in kitty's.

use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::test_support;
use cloudkitty_server::register_policy_behaviors;

/// A registerable fixture: the artifact plus its spec-034 registry row —
/// since the wall's registry gate (FR-007), an artifact without a row
/// beside it refuses to seat, so the pair is the unit. Per-test `dir` keeps
/// parallel tests from merging the same registry file.
fn fixture_artifact(dir: &str, name: &str) -> PathBuf {
    let artifact = test_support::fixture_artifact(dir, name, 8, 11);
    test_support::registry_row_beside(&artifact, "Test · fixture");
    artifact
}

fn policy_config_text(artifact: &std::path::Path) -> String {
    // Spec 049 FR-030: completed over the defaults -- every section stated.
    cloudkitty_core::test_support::complete_toml(&format!(
        r#"
[world]
width = 32
height = 32
tick_ms = 800
seed = 99

[[kitty]]
id = 1
name = "Miso"
x = 10
y = 12
behavior = "needs_driven"

[[kitty]]
id = 2
name = "Biscuit"
x = 20
y = 18
behavior = "playful"

[[kitty]]
id = 3
name = "Pumpkin"
x = 16
y = 8
behavior = "policy:trained"

[rl.policy.trained]
artifact = "{}"
[vision]
radius = 40
memory_timeout_ticks = 0
"#,
        artifact.display()
    ))
}

#[test]
fn startup_validates_and_registers_the_policy_before_any_tick() {
    let artifact = fixture_artifact("ck-server-policy-good", "good");
    let text = policy_config_text(&artifact);
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();

    let mut registry = BehaviorRegistry::with_builtins();
    register_policy_behaviors(&mut registry, &config, &rl).expect("a valid artifact registers");
    // The registered name validates like any built-in.
    config.validate_behavior_names(&registry.names()).unwrap();
    assert!(registry.get("policy:trained").is_some());
}

#[test]
fn a_corrupted_artifact_fails_startup_naming_the_config_field() {
    let dir = std::env::temp_dir().join("ck-server-policy");
    std::fs::create_dir_all(&dir).unwrap();
    let corrupt = dir.join("corrupt.ckpolicy");
    std::fs::write(&corrupt, b"chewed by a greeble").unwrap();

    let text = policy_config_text(&corrupt);
    let config: Config = toml::from_str(&text).unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    let err = register_policy_behaviors(&mut registry, &config, &rl).unwrap_err();
    let message = format!("{err:#}");
    assert!(
        message.contains("[rl.policy.trained].artifact"),
        "the error names the config field: {message}"
    );
    // ...and the artifact path rides in the same context line, so the
    // operator can answer "which file" without opening the config
    // (spec 026 contract C3, questions 1 and 2).
    assert!(
        message.contains("corrupt.ckpolicy"),
        "the error names the artifact file: {message}"
    );

    // A missing [rl.policy] block is equally fatal, equally named.
    let mut no_block: Config = toml::from_str(&text).unwrap();
    no_block.kitties[2].behavior = "policy:unconfigured".into();
    let err =
        register_policy_behaviors(&mut registry, &no_block, &RlConfig::default()).unwrap_err();
    assert!(
        format!("{err:#}").contains("[rl.policy.unconfigured]"),
        "{err:#}"
    );
}

#[test]
fn the_shipped_config_seats_the_gen1_minds_and_names_exactly_what_it_serves() {
    // The fifth tour (the 0.3.0 cutover, owner rulings 2026-09-15;
    // 2.x retirement on the owner's word 2026-09-16): supersedes
    // `the_shipped_config_parks_every_seat_at_the_3_0_wall…` (expired by
    // its own terms when the Gen 1 minds landed) and, at the retirement,
    // its "unreferenced 2.x blocks still refuse" half — those blocks are
    // gone with their artifacts (policies/retired/, README rows). What
    // remains to guard:
    // 1. every served seat names a policy, and registration opens every
    //    seated artifact through the schema gate (a missing artifact, a
    //    stale generation, or a blockless seat all fail here);
    // 2. the config names exactly what it serves — every [rl.policy.*]
    //    stanza is seated (retirement removes the stanza with the file),
    //    and the policies/ top level holds exactly the stanza-named
    //    files (the README's own top-level rule, machine-checked).
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../cloudkitty.toml");
    let text = std::fs::read_to_string(&root).expect("the shipped config is readable");
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().expect("the shipped config validates");
    // Seats and minds counted separately on purpose: the same mind at two
    // seats is legal (the pre-wall twin seating was exactly that; F-027
    // retired the PATTERN as a design choice, not the capability), so the
    // every-seat check counts seats and `seated` dedups to distinct minds.
    assert!(
        config
            .kitties
            .iter()
            .all(|k| k.behavior.starts_with("policy:")),
        "the 0.3.0 seating: every served seat is a Gen 1 mind; if the seats ever park \
         again, restore the wall test from git history instead of deleting this one"
    );
    let seated: std::collections::BTreeSet<&str> = config
        .kitties
        .iter()
        .filter_map(|k| k.behavior.strip_prefix("policy:"))
        .collect();
    let mut rl = RlConfig::from_toml_str(&text).unwrap();
    let repo = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    for policy in rl.policy.values_mut() {
        policy.artifact = repo.join(&policy.artifact).to_string_lossy().into_owned();
    }
    // Proof 1: registration opens every SEATED artifact and runs it
    // through the schema gate.
    let mut registry = BehaviorRegistry::with_builtins();
    let displays = register_policy_behaviors(&mut registry, &config, &rl)
        .expect("every seated Gen 1 policy resolves to an artifact this binary can open");
    assert_eq!(
        displays.len(),
        seated.len(),
        "one registered display per seated mind"
    );
    config.validate_behavior_names(&registry.names()).unwrap();
    // Proof 2: the naming correspondences.
    let stanza_names: std::collections::BTreeSet<&str> =
        rl.policy.keys().map(|k| k.as_str()).collect();
    assert_eq!(
        stanza_names, seated,
        "every [rl.policy.*] stanza is a seated mind and vice versa \
         (a retired mind's stanza leaves with its artifact)"
    );
    let named_files: std::collections::BTreeSet<String> = rl
        .policy
        .values()
        .map(|p| {
            std::path::Path::new(&p.artifact)
                .file_name()
                .unwrap()
                .to_string_lossy()
                .into_owned()
        })
        .collect();
    let top_level: std::collections::BTreeSet<String> = std::fs::read_dir(repo.join("policies"))
        .expect("policies/ is readable")
        .filter_map(|e| {
            let path = e.expect("dir entry").path();
            (path.extension().and_then(|x| x.to_str()) == Some("ckpolicy"))
                .then(|| path.file_name().unwrap().to_string_lossy().into_owned())
        })
        .collect();
    assert_eq!(
        top_level, named_files,
        "policies/ top level holds exactly what the served config names \
         (retired files live in policies/retired/)"
    );
}

#[tokio::test]
async fn a_policy_kitty_is_viewer_indistinguishable_from_a_built_in() {
    let artifact = fixture_artifact("ck-server-policy-served", "served");
    let text = policy_config_text(&artifact);
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    register_policy_behaviors(&mut registry, &config, &rl).unwrap();
    let config = Arc::new(config);

    // Drive the served tick (budgeted path) with the policy kitty rostered.
    let mut world = World::generate(&config);
    for _ in 0..50 {
        world.tick(&registry, &config).await;
    }

    // The published snapshot carries the same field shape for every kitty:
    // nothing marks the policy kitty as different (the behavior name is
    // ordinary config, present for built-ins too).
    let snapshot = world.snapshot();
    let json = serde_json::to_value(&snapshot).unwrap();
    let kitties = json["kitties"].as_array().unwrap();
    assert_eq!(kitties.len(), 3);
    let keys = |v: &serde_json::Value| -> Vec<String> {
        let mut k: Vec<String> = v.as_object().unwrap().keys().cloned().collect();
        // Optional fields (pursuit, activity_clock, ...) vary by state for
        // built-ins too; compare the required core fields.
        k.retain(|key| {
            [
                "id",
                "name",
                "pos",
                "needs",
                "happiness",
                "activity",
                "behavior",
            ]
            .contains(&key.as_str())
        });
        k.sort();
        k
    };
    assert_eq!(keys(&kitties[0]), keys(&kitties[2]));
    assert_eq!(world.kitties.len(), 3, "everyone still here (Article II)");
}
