//! Article V: the same seed always produces the same world.
//!
//! This is what makes the property suite's failures reproducible and what lets a
//! restart continue the same future rather than merely the same positions.

use std::sync::Arc;

use cloudkitty_core::behavior::test_behaviors::{AlwaysInvalid, Chaos};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, Config, World};

fn registry() -> BehaviorRegistry {
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("always_invalid", Arc::new(AlwaysInvalid));
    registry.register("chaos", Arc::new(Chaos));
    registry
}

async fn run(config: &Arc<Config>, ticks: u64) -> World {
    let registry = registry();
    let mut world = World::generate(config);
    for _ in 0..ticks {
        world.tick(&registry, config).await;
    }
    world
}

fn fingerprint(world: &World) -> String {
    serde_json::to_string(world).expect("worlds serialize")
}

#[tokio::test(flavor = "current_thread")]
async fn the_same_seed_produces_the_same_world() {
    let config = Arc::new(test_config());

    let a = run(&config, 500).await;
    let b = run(&config, 500).await;

    assert_eq!(
        fingerprint(&a),
        fingerprint(&b),
        "two runs with the same seed diverged"
    );
}

#[tokio::test(flavor = "current_thread")]
async fn a_different_seed_produces_a_different_world() {
    let config_a = Arc::new(test_config());
    let mut other = test_config();
    other.world.seed += 1;
    let config_b = Arc::new(other);

    let a = run(&config_a, 300).await;
    let b = run(&config_b, 300).await;

    assert_ne!(
        fingerprint(&a),
        fingerprint(&b),
        "different seeds should tell different stories"
    );
}

#[tokio::test(flavor = "current_thread")]
async fn saving_and_resuming_continues_the_same_future() {
    let config = Arc::new(test_config());
    let registry = registry();

    // The uninterrupted run.
    let straight_through = run(&config, 400).await;

    // The interrupted one: stop at 150, serialize, restore, carry on to 400.
    let mut world = World::generate(&config);
    for _ in 0..150 {
        world.tick(&registry, &config).await;
    }
    let saved = serde_json::to_string(&world).expect("save");
    let mut resumed: World = serde_json::from_str(&saved).expect("load");
    for _ in 0..250 {
        resumed.tick(&registry, &config).await;
    }

    assert_eq!(
        fingerprint(&straight_through),
        fingerprint(&resumed),
        "a restart changed the world's future -- the RNG state did not survive"
    );
}

#[tokio::test(flavor = "current_thread")]
async fn determinism_holds_with_misbehaving_advisors() {
    // Hostile behaviors draw from their own per-kitty streams; that must not make
    // the world unpredictable.
    let mut config = test_config();
    config.kitties[0].behavior = "chaos".into();
    config.kitties[1].behavior = "always_invalid".into();
    let config = Arc::new(config);

    let a = run(&config, 400).await;
    let b = run(&config, 400).await;

    assert_eq!(fingerprint(&a), fingerprint(&b));
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn concurrency_does_not_change_the_outcome() {
    // Decisions are gathered concurrently. On a multi-threaded runtime they may
    // complete in any order -- and the world must come out identical anyway,
    // because each kitty's randomness was drawn before any of them ran.
    let config = Arc::new(test_config());

    let a = run(&config, 300).await;
    let b = run(&config, 300).await;

    assert_eq!(
        fingerprint(&a),
        fingerprint(&b),
        "completion order leaked into the simulation"
    );
}

/// Spec 049 SC-006: same seed + config + ticks → identical memory on every
/// kitty, under a real fog (the world fingerprint already covers it; this
/// names the field so a memory that drifted would say so).
#[tokio::test]
async fn the_same_seed_produces_the_same_memory_under_fog() {
    let mut config = test_config();
    config.vision.radius = 4;
    config.validate().unwrap();
    let config = Arc::new(config);
    let a = run(&config, 400).await;
    let b = run(&config, 400).await;
    let populated = a
        .kitties
        .iter()
        .flat_map(|k| k.memory.iter())
        .filter(|s| s.is_some())
        .count();
    assert!(populated >= 2, "memory fills under fog: {populated}");
    for (x, y) in a.kitties.iter().zip(b.kitties.iter()) {
        assert_eq!(x.memory, y.memory, "kitty {}", x.id);
        assert_eq!(x.explore_heading, y.explore_heading, "kitty {}", x.id);
    }
}
