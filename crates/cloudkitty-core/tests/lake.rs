//! The lake guarantee through the tick path (spec 027 FR-002, US1
//! scenario 5).
//!
//! The unit tests in spawn.rs construct damaged states by hand; this
//! suite reaches the same law through `World::tick` — timed water
//! expires mid-life, and the very next environment phase re-forms the
//! square. That pins the expire → restock ordering inside a phase, not
//! just the restock function's own behavior.

use std::sync::Arc;

use cloudkitty_core::element::ElementType;
use cloudkitty_core::{BehaviorRegistry, Config, World};

fn has_lake(world: &World) -> bool {
    let waters: Vec<_> = world
        .elements
        .iter()
        .filter(|e| e.element_type() == ElementType::Water)
        .map(|e| e.pos)
        .collect();
    waters.iter().any(|p| {
        [(1u32, 0u32), (0, 1), (1, 1)]
            .iter()
            .all(|(dx, dy)| waters.iter().any(|q| q.x == p.x + dx && q.y == p.y + dy))
    })
}

#[tokio::test]
async fn a_timed_lake_re_forms_within_the_next_phase_after_expiry() {
    // Short-lived water in a small world: lake tiles expire constantly,
    // and every break must heal by the end of the following tick's
    // environment phase (expiry and restock share a phase, so the same
    // tick usually re-forms it; one tick of grace covers the
    // carried-over case when a critter squats on the gap).
    // Default geometry (the roster's positions constrain it); only the
    // water rule changes: minimum at the lake threshold, short TTL.
    let mut config = Config::default();
    config.world.seed = 7;
    config.elements.water.min = 4;
    config.elements.water.max = 6;
    config.elements.water.ttl = Some(40); // jitter 100 floors draws at 1..141
    config.validate().expect("timed-water config validates");

    let registry = BehaviorRegistry::with_builtins();
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    assert!(has_lake(&world), "generation installs the lake");

    let mut lakeless_streak = 0u32;
    let mut breaks_seen = 0u32;
    let mut waters_over_run = 0u64;
    for _ in 0..600 {
        world.tick(&registry, &config).await;
        waters_over_run += world.count_of(ElementType::Water) as u64;
        if has_lake(&world) {
            lakeless_streak = 0;
        } else {
            lakeless_streak += 1;
            breaks_seen += 1;
            assert!(
                lakeless_streak <= 1,
                "a broken lake must re-form by the end of the next tick's \
                 environment phase (tick {})",
                world.tick
            );
        }
    }
    // The scenario must actually exercise expiry: with a 1..141-tick TTL
    // over 600 ticks, water certainly cycled — assert the water count
    // stayed live (the minimum is honored on average) so a silent
    // stop-spawning bug cannot pass as "no breaks".
    assert!(waters_over_run >= 4 * 600, "water population went slack");
    let _ = breaks_seen; // informational; zero breaks is legal (same-phase heals)
}
