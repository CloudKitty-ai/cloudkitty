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
fn the_shipped_config_seats_the_gen1_minds_and_still_refuses_the_2_x_minds() {
    // The fifth tour (the 0.3.0 cutover, owner rulings 2026-09-15):
    // supersedes `the_shipped_config_parks_every_seat_at_the_3_0_wall…`,
    // whose parked assertion expired by its own terms when the Gen 1
    // minds landed. This is the seats-open posture of the third tour
    // (restored from 8c3db07, as that test instructed) plus the wall
    // test's surviving half: every 2.x block the config still lists is
    // schema-4 and refused by this binary. Two proofs:
    // 1. every served seat names a policy, and registration opens every
    //    seated artifact through the schema gate (a missing artifact, a
    //    stale generation, or a blockless seat all fail here);
    // 2. the UNREFERENCED [rl.policy.*] blocks -- the 2.x registry of
    //    what WAS seated, never opened at boot -- still refuse at load,
    //    naming the observation schema and both versions.
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
    // Proof 2: the 2.x registry blocks stay, and stay unservable here.
    let retired: Vec<_> = rl
        .policy
        .iter()
        .filter(|(name, _)| !seated.contains(name.as_str()))
        .collect();
    assert!(
        !retired.is_empty(),
        "the 2.x registry blocks stay as the record of what was seated"
    );
    let expectations = cloudkitty_rl::behavior::PolicyBehavior::expectations(&rl);
    for (name, policy) in retired {
        let err = cloudkitty_rl::policy::PolicyArtifact::load(
            std::path::Path::new(&policy.artifact),
            &expectations,
        )
        .expect_err(&format!(
            "[rl.policy.{name}]: a 2.x (schema-4) artifact must not cross the wall"
        ));
        let text = format!("{err}");
        assert!(
            text.contains("observation schema mismatch")
                && text.contains("schema v4")
                && text.contains("speaks v5"),
            "[rl.policy.{name}]: the schema gate's own words -- found 4, expected 5: {text}"
        );
    }
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
