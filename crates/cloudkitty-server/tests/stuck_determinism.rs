//! Spec 061 SC-004 / US3-AC2: replays of the same seed, configuration,
//! and deterministic seats reproduce the identical fire sequence and
//! identical substitutes, end to end — the `determinism.rs` fingerprint
//! pattern, budgetless (`drive_tick`), with the detector enforcing.

use std::sync::Arc;

use cloudkitty_core::action::Action;
use cloudkitty_core::config::KittyConfig;
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{
    Behavior, BehaviorRegistry, Config, Decision, DecisionContext, Direction, NeedKind, World,
};
use cloudkitty_server::stuck::{FireRecord, StuckConfig, StuckDetector, StuckMode, StuckShared};

/// The deterministic firing seat: dithers on its home row, idles
/// elsewhere, draws nothing from the decision stream.
struct HomeDither {
    home_y: u32,
}

#[async_trait::async_trait]
impl Behavior for HomeDither {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        if ctx.me.pos.y == self.home_y {
            let direction = if ctx.me.pos.x % 2 == 0 {
                Direction::East
            } else {
                Direction::West
            };
            Decision::silent(Action::move_to(direction))
        } else {
            Decision::silent(Action::Idle)
        }
    }
}

fn firing_config() -> Config {
    let mut config = test_config();
    config.kitties = vec![
        KittyConfig::new(1, "Pacer", 3, 3, "policy:dither"),
        KittyConfig::new(2, "Biscuit", 12, 12, "needs_driven"),
    ];
    config
}

/// One full budgetless run: wrapped registry, enforcing detector,
/// observer in the loop exactly as sim_task wires it. Returns the fire
/// records and the final world's serialization.
fn run(ticks: u64) -> (Vec<FireRecord>, String) {
    let config = Arc::new(firing_config());
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("policy:dither", Arc::new(HomeDither { home_y: 3 }));
    let shared = StuckShared::new(StuckConfig {
        mode: StuckMode::Enforce,
        window: 20,
        ..StuckConfig::default()
    });
    let (registry, mind_plugins) =
        cloudkitty_server::wrap_mind_seats(registry, &Default::default(), &shared);
    let mut detector = StuckDetector::new(shared.clone(), mind_plugins);

    let mut world = World::generate(&config);
    world.kitties[0].needs.add(NeedKind::Eat, 200.0);
    for _ in 0..ticks {
        drive_tick(&mut world, &registry, &config);
        detector.observe(&world);
    }
    let records = detector.observe(&world).recent;
    (
        records,
        serde_json::to_string(&world).expect("worlds serialize"),
    )
}

#[test]
fn two_replays_produce_identical_fire_records_and_worlds_end_to_end() {
    let (records_a, world_a) = run(70);
    let (records_b, world_b) = run(70);

    assert!(
        !records_a.is_empty(),
        "the fixture fires, or this determinism read is vacuous"
    );
    assert_eq!(
        records_a, records_b,
        "same seed, config, deterministic seat: the fire sequence is identical, substitutes included (SC-004)"
    );
    assert_eq!(world_a, world_b, "and the worlds are fingerprint-identical");

    // The sequence respects FR-007 in both replays: no consecutive-tick
    // refires anywhere in the record.
    for pair in records_a.windows(2) {
        assert!(
            pair[1].tick - pair[0].tick >= 20,
            "refire gap under one window: {} -> {}",
            pair[0].tick,
            pair[1].tick
        );
    }
}
