//! Golden parity (spec 014 US1, SC-001, FR-004): a run driven by built-in
//! behaviors and a run externally fed those same decisions serialize
//! byte-identically — RNG state included — over ≥ 5,000 ticks.
//!
//! This is the Article VI guard on the joint-action seam: the seam is a
//! different *source* of proposals, never a different law.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;

const PARITY_TICKS: u64 = 5_000;
const CHECKPOINT_EVERY: u64 = 500;

fn serialize(world: &World) -> String {
    serde_json::to_string(world).expect("worlds serialize")
}

#[test]
fn golden_parity_over_five_thousand_ticks() {
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();

    // World A: behavior-driven, budgetless, collecting each tick's dispatched
    // proposals (the parity capture, research.md R4).
    // World B: fed exactly those proposals through the joint-action seam.
    let mut driven = World::generate(&config);
    let mut joint = World::generate(&config);

    for tick in 0..PARITY_TICKS {
        let outcome = drive_tick(&mut driven, &registry, &config);
        joint.tick_with_proposals(&outcome.proposals, &config);

        if tick % CHECKPOINT_EVERY == 0 || tick == PARITY_TICKS - 1 {
            assert_eq!(
                serialize(&driven),
                serialize(&joint),
                "worlds diverged at tick {tick}"
            );
        }
    }

    assert_eq!(driven.tick, PARITY_TICKS);
    assert_eq!(joint.tick, PARITY_TICKS);
}

#[test]
fn the_budgetless_driver_matches_the_served_tick() {
    // drive_tick is the same law as World::tick: from the same seed, one
    // budgetless behavior-driven tick and one served (async, budgeted) tick
    // produce byte-identical worlds. Built-ins never feel the budget, so the
    // only difference between the paths is machinery — which must not show.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();

    let mut served = World::generate(&config);
    let mut headless = World::generate(&config);

    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_time()
        .build()
        .unwrap();
    for _ in 0..200 {
        runtime.block_on(served.tick(&registry, &config));
        drive_tick(&mut headless, &registry, &config);
    }

    assert_eq!(serialize(&served), serialize(&headless));
}

#[test]
fn the_joint_tick_consumes_the_identical_rng_draw_shape() {
    // T012: RNG state after a joint-action tick equals RNG state after the
    // equivalent behavior-driven tick — the draw-shape assertion (FR-002).
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();

    let mut driven = World::generate(&config);
    let mut joint = World::generate(&config);

    for _ in 0..50 {
        let outcome = drive_tick(&mut driven, &registry, &config);
        joint.tick_with_proposals(&outcome.proposals, &config);
        assert_eq!(
            serde_json::to_string(&driven.rng).unwrap(),
            serde_json::to_string(&joint.rng).unwrap(),
            "RNG streams diverged at tick {}",
            driven.tick
        );
    }
}

#[test]
fn the_tick_report_is_total_and_carries_the_dealt_seeds() {
    // FR-003: every kitty appears exactly once per report, with the decision
    // seed it was dealt; the driven report's seeds match the proposals'
    // decisions (replaying a seed reproduces the choice is covered by the
    // resolver's own unit tests).
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let outcome = drive_tick(&mut world, &registry, &config);
    let ids: Vec<_> = outcome.report.records.iter().map(|r| r.kitty_id).collect();
    let mut expected: Vec<_> = config.kitties.iter().map(|k| k.id).collect();
    expected.sort_unstable();
    assert_eq!(ids, expected, "one record per kitty, stable id order");

    let mut joint = World::generate(&config);
    let report = joint.tick_with_proposals(&outcome.proposals, &config);
    let joint_ids: Vec<_> = report.records.iter().map(|r| r.kitty_id).collect();
    assert_eq!(joint_ids, expected);
    // Same seed, same draw shape: the two paths deal the same seeds.
    for (a, b) in outcome.report.records.iter().zip(report.records.iter()) {
        assert_eq!(a.decision_seed, b.decision_seed);
    }
}
