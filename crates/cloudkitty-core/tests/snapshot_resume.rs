//! The generation wall, engine side (spec 028 FR-022/SC-006): pre-028
//! world snapshots load and RUN on this engine. The committed fixture was
//! serialized at the last pre-028 commit — populated meows (no intensity
//! field), per-kind cooldowns, live purr state — and this suite is the
//! wall's witness that the break is policy-side only.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::config::Config;
use cloudkitty_core::world::World;

fn fixture() -> World {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/pre-028-world.json");
    let text = std::fs::read_to_string(path).expect("the committed fixture is readable");
    serde_json::from_str(&text).expect("a pre-028 world deserializes on this engine")
}

#[tokio::test(flavor = "current_thread")]
async fn a_pre_028_world_resumes_and_runs() {
    let mut world = fixture();

    // The old-generation state arrived intact...
    assert_eq!(world.tick, 3000, "the fixture's clock");
    assert!(
        !world.recent_meows.is_empty(),
        "old-kind meows are still audible"
    );
    assert!(
        world
            .recent_meows
            .iter()
            .all(|m| m.intensity == 0.0),
        "a pre-028 meow (no intensity field) reads 0.0"
    );
    assert!(
        world
            .kitties
            .iter()
            .any(|k| !k.meow_cooldowns.is_empty()),
        "per-kind cooldown stamps survived the reinterpretation"
    );
    // ...and the new state defaulted honestly.
    assert!(
        world.kitties.iter().all(|k| k.announce_armed.is_empty()),
        "pre-028 kitties resume disarmed; the first needs phase re-arms"
    );

    // And it RUNS: 200 ticks under the shipped config, scripted-only (the
    // shipped seats are parked scripted across the generation gap), with
    // the invariants asserting inside every tick.
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let text = std::fs::read_to_string(root.join("cloudkitty.toml")).unwrap();
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().expect("the shipped config validates");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    for _ in 0..200 {
        world.tick(&registry, &config).await;
    }
    assert_eq!(world.tick, 3200, "two hundred lawful ticks later");
    assert!(
        world.kitties.iter().any(|k| !k.announce_armed.is_empty())
            || world
                .kitties
                .iter()
                .all(|k| k.needs.highest_pressure().1
                    < config.meow.announce_threshold - config.meow.announce_hysteresis),
        "arming state is live again (or honestly nothing is armable)"
    );
}

#[test]
fn a_pre_028_meow_entry_reads_zero_intensity() {
    // The Meow-level compat case, isolated from the world fixture: the
    // exact JSON a pre-028 recent_meows entry carries.
    let json = r#"{"kitty_id": 3, "kind": "want_play", "tick": 42}"#;
    let meow: cloudkitty_core::Meow = serde_json::from_str(json).unwrap();
    assert_eq!(meow.intensity, 0.0);
    assert_eq!(meow.kind, cloudkitty_core::MessageKind::WantPlay);
}
