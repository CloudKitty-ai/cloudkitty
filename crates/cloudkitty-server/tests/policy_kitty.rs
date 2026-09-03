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
    format!(
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
    )
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
fn the_shipped_config_parks_every_seat_at_the_3_0_wall_and_refuses_the_2_x_minds() {
    // The fourth tour (spec 049, the fog wall). This restores the
    // generation-gap posture the third-tour test (`…seats_a_policy_this
    // _binary_can_open`) said to restore "if the seats ever park again":
    // observation schema 5 refuses every schema-4 artifact at load
    // (FR-025 / SC-008), so the served roster is scripted until the Gen 1
    // minds seat at the step-7 cutover. Two proofs: no seat names a
    // policy, and every [rl.policy.*] artifact the config still lists --
    // the 2.x registry, never opened for an unreferenced block -- IS
    // refused by this binary, naming the observation schema and both
    // versions, before any tick.
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../cloudkitty.toml");
    let text = std::fs::read_to_string(&root).expect("the shipped config is readable");
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().expect("the shipped config validates");
    assert!(
        config
            .kitties
            .iter()
            .all(|k| !k.behavior.starts_with("policy:")),
        "at the 3.0 wall every served seat is scripted; a policy seat means Gen 1 minds \
         landed -- then restore the seats-open test from git history"
    );
    let mut rl = RlConfig::from_toml_str(&text).unwrap();
    let repo = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    for policy in rl.policy.values_mut() {
        policy.artifact = repo.join(&policy.artifact).to_string_lossy().into_owned();
    }
    assert!(
        !rl.policy.is_empty(),
        "the 2.x registry blocks stay as the record of what was seated"
    );
    let expectations = cloudkitty_rl::behavior::PolicyBehavior::expectations(&rl);
    for (name, policy) in &rl.policy {
        let err = cloudkitty_rl::policy::PolicyArtifact::load(
            std::path::Path::new(&policy.artifact),
            &expectations,
        )
        .expect_err(&format!(
            "[rl.policy.{name}]: a 2.x (schema-4) artifact must not cross the wall"
        ));
        let text = format!("{err}");
        assert!(
            text.contains("observation"),
            "[rl.policy.{name}]: the refusal names the observation schema: {text}"
        );
        assert!(
            text.contains('4') && text.contains('5'),
            "[rl.policy.{name}]: found 4 / expected 5 are both named: {text}"
        );
    }
    // And a registry with no seated policy registers nothing -- boot
    // proceeds scripted.
    let mut registry = BehaviorRegistry::with_builtins();
    let displays = register_policy_behaviors(&mut registry, &config, &rl).unwrap();
    assert!(displays.is_empty());
    config.validate_behavior_names(&registry.names()).unwrap();
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
