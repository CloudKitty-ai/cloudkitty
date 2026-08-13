//! Server integration for spec 030 US1 (T011): a config seating a v3
//! entity-attention policy beside a v2 policy boots with both artifacts
//! validated and hash-logged before any tick, and the served world ticks
//! without error (SC-001). A v3 artifact whose schema predates the binary
//! fails startup naming its config field (T017).

use std::sync::Arc;

use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::test_support;
use cloudkitty_server::register_policy_behaviors;

fn config_text(v3: &std::path::Path, v2: &std::path::Path) -> String {
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
behavior = "policy:attn"

[[kitty]]
id = 3
name = "Pumpkin"
x = 16
y = 8
behavior = "policy:mlp"

[rl.policy.attn]
artifact = "{}"

[rl.policy.mlp]
artifact = "{}"
"#,
        v3.display(),
        v2.display()
    )
}

#[test]
fn a_v3_and_a_v2_policy_seat_boot_together_before_any_tick() {
    let v3 = test_support::fixture_v3_artifact("ck-server-policy-v3", "attn", 3);
    let v2 = test_support::fixture_artifact("ck-server-policy-v3", "mlp", 8, 11);
    let text = config_text(&v3, &v2);
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();

    let mut registry = BehaviorRegistry::with_builtins();
    register_policy_behaviors(&mut registry, &config, &rl)
        .expect("both a v3 and a v2 artifact register");
    config.validate_behavior_names(&registry.names()).unwrap();
    assert!(
        registry.get("policy:attn").is_some(),
        "the v3 seat registered"
    );
    assert!(
        registry.get("policy:mlp").is_some(),
        "the v2 seat registered"
    );
}

#[tokio::test]
async fn the_world_ticks_with_a_v3_and_a_v2_seat() {
    let v3 = test_support::fixture_v3_artifact("ck-server-policy-v3", "attn-served", 5);
    let v2 = test_support::fixture_artifact("ck-server-policy-v3", "mlp-served", 8, 11);
    let text = config_text(&v3, &v2);
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    register_policy_behaviors(&mut registry, &config, &rl).unwrap();
    let config = Arc::new(config);

    let mut world = World::generate(&config);
    for _ in 0..30 {
        world.tick(&registry, &config).await;
    }
    assert_eq!(world.kitties.len(), 3, "everyone still here (Article II)");
}

#[test]
fn a_stale_generation_v3_artifact_fails_startup_naming_its_field() {
    // A v3 artifact whose observation schema predates the binary is refused
    // at startup, named to its config field — the same fail-loud contract the
    // v2 loader holds (T017, FR-006). We simulate the stale generation by
    // hand-writing a v3 header with a bumped observation schema.
    let dir = std::env::temp_dir().join("ck-server-policy-v3");
    std::fs::create_dir_all(&dir).unwrap();
    let stale = dir.join("stale.ckpolicy");
    let mut header = serde_json::to_value(test_support::default_v3_header()).unwrap();
    header["observation_schema"] = 99.into();
    let json = serde_json::to_string(&header).unwrap() + "\n";
    let mut bytes = Vec::new();
    bytes.extend_from_slice(cloudkitty_rl::policy::ARTIFACT_MAGIC);
    bytes.extend_from_slice(&(json.len() as u32).to_le_bytes());
    bytes.extend_from_slice(json.as_bytes());
    std::fs::write(&stale, bytes).unwrap();

    let v2 = test_support::fixture_artifact("ck-server-policy-v3", "mlp-stale", 8, 11);
    let text = config_text(&stale, &v2);
    let config: Config = toml::from_str(&text).unwrap();
    let rl = RlConfig::from_toml_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    let err = register_policy_behaviors(&mut registry, &config, &rl).unwrap_err();
    let message = format!("{err:#}");
    assert!(
        message.contains("[rl.policy.attn].artifact"),
        "the error names the v3 seat's config field: {message}"
    );
}
