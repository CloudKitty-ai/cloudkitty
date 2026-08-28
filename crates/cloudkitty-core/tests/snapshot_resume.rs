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
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/pre-028-world.json");
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
        world.recent_meows.iter().all(|m| m.intensity == 0.0),
        "a pre-028 meow (no intensity field) reads 0.0"
    );
    assert!(
        world.kitties.iter().any(|k| !k.meow_cooldowns.is_empty()),
        "per-kind cooldown stamps survived the reinterpretation"
    );
    // ...and the new state defaulted honestly.
    assert!(
        world.kitties.iter().all(|k| k.announce_armed.is_empty()),
        "pre-028 kitties resume disarmed; the first needs phase re-arms"
    );

    // And it RUNS: 200 ticks under the shipped config with the builtin
    // registry -- policy seats lawfully fall back when their behavior is
    // unregistered (core cannot open artifacts), which is itself the
    // wall's point: the old world runs whatever the seats say. The
    // invariants assert inside every tick.
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
            || world.kitties.iter().all(|k| k.needs.highest_pressure().1
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

/// Spec 041 FR-009 / US1 AC-5: a snapshot recorded on the pre-041 engine
/// carrying a BOUND rest duet (both partners in `Resting` naming each
/// other, one shared clock) loads and resumes lawfully as two synchronized
/// resters, each paying the mutual tier from its own slot -- no error
/// state, no reshaping. The fixture was serialized by the pre-041 build
/// (2026-08-28), not hand-written.
///
/// 3.0 config-hygiene wall: this tolerance (fixture + test) is marked for
/// deletion there, alongside the inert `cuddle_relief` key -- after the
/// wall's --fresh cutover no pre-041 world can resume.
#[tokio::test(flavor = "current_thread")]
async fn a_pre_041_bound_rest_duet_resumes_as_synchronized_resters() {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/pre-041-bound-duet.json");
    let text = std::fs::read_to_string(path).expect("the committed fixture is readable");
    let mut world: World = serde_json::from_str(&text).expect("a pre-041 world deserializes");

    // The bound-duet shape arrived intact: mutual references, live clocks.
    let k1 = world.kitty(1).unwrap();
    let k2 = world.kitty(2).unwrap();
    assert_eq!(k1.activity.partner(), Some(2), "the fixture's duet");
    assert_eq!(k2.activity.partner(), Some(1));
    assert!(k1.activity_clock.is_some() && k2.activity_clock.is_some());
    let cuddle_before_1 = k1.needs.get(cloudkitty_core::NeedKind::Cuddle);
    let cuddle_before_2 = k2.needs.get(cloudkitty_core::NeedKind::Cuddle);

    // One tick under the default config: both scenes continue lawfully
    // (the invariants assert inside the tick), and each pays the mutual
    // tier TWICE -- once from its own slot, once as the other's partner --
    // the synchronized-resters shape the spec promises.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    // Two ticks: the fixture's scene was already serviced on its capture
    // tick (spec 006's effects-due rule), so the first resumed tick stamps
    // without paying; the second pays.
    world.tick(&registry, &config).await;
    world.tick(&registry, &config).await;

    let k1 = world.kitty(1).unwrap();
    let k2 = world.kitty(2).unwrap();
    assert_eq!(
        k1.activity.partner(),
        Some(2),
        "the scene continues, un-reshaped"
    );
    assert_eq!(k2.activity.partner(), Some(1));
    let rate = config.actions.rest_mutual_relief;
    for (before, kitty) in [(cuddle_before_1, k1), (cuddle_before_2, k2)] {
        let got = kitty.needs.get(cloudkitty_core::NeedKind::Cuddle);
        assert!(
            got < before - (2.0 * rate - 1.0),
            "each rester collects mutual from both slots, got {got} from {before}"
        );
        // Counters resumed at zero (serde default) and count from the
        // resume: the one paying tick bumped mutual on each owner's scene.
        assert_eq!(kitty.activity_clock.unwrap().mutual_ticks, 1);
        assert_eq!(kitty.activity_clock.unwrap().drip_ticks, 0);
    }
}
