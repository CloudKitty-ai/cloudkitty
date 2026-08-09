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

fn fixture_artifact(name: &str) -> PathBuf {
    test_support::fixture_artifact("ck-server-policy", name, 8, 11)
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
"#,
        artifact.display()
    )
}

#[test]
fn startup_validates_and_registers_the_policy_before_any_tick() {
    let artifact = fixture_artifact("good");
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
fn the_shipped_config_seats_a_policy_this_binary_can_open() {
    // Second tour, restored per the generation-gap test's own instruction
    // (spec 028): a generation-3 artifact certified (e004-a1-s2, grid
    // 15/15 on the settled §9.2 gate) and took the seats back on
    // 2026-08-09, so the parked assertion has expired by its own terms
    // exactly as it did on 2026-08-07.
    //
    // What this proves is strictly stronger than the parked version: not
    // just that unreferenced blocks are never opened, but that the
    // referenced artifact IS opened and survives the schema gate. It
    // catches a seat naming a missing artifact, a stale-generation
    // artifact, or a policy with no `[rl.policy.*]` block. If the seats
    // ever park again, restore the generation-gap test
    // (`the_shipped_config_boots_scripted_across_the_generation_gap`,
    // last at git d261888) instead of deleting this one.
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../cloudkitty.toml");
    let text = std::fs::read_to_string(&root).expect("the shipped config is readable");
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().expect("the shipped config validates");
    assert!(
        config
            .kitties
            .iter()
            .any(|k| k.behavior.starts_with("policy:")),
        "the shipped config seats at least one policy now that a certified \
         generation-3 winner exists; if the seats are parked again, restore \
         the generation-gap test instead of deleting this one"
    );
    let mut rl = RlConfig::from_toml_str(&text).unwrap();
    // Artifact paths in the shipped config are relative to the repo root (the
    // server's working directory); a test's is the crate root, so resolve them
    // before opening anything.
    let repo = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    for policy in rl.policy.values_mut() {
        policy.artifact = repo.join(&policy.artifact).to_string_lossy().into_owned();
    }
    let mut registry = BehaviorRegistry::with_builtins();
    // The proof: registration opens every named artifact and runs it through
    // the schema gate. A stale-generation artifact would be refused here.
    register_policy_behaviors(&mut registry, &config, &rl)
        .expect("every seated policy resolves to an artifact this binary can open");
    config.validate_behavior_names(&registry.names()).unwrap();
}

#[tokio::test]
async fn a_policy_kitty_is_viewer_indistinguishable_from_a_built_in() {
    let artifact = fixture_artifact("served");
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
