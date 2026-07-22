//! Baseline reproduction (spec 014 US3, T035): the harness's numbers are
//! the welfare suite's numbers for the same seeds — guaranteed one level
//! deeper than comparison: both consume the shared welfare module over the
//! same budgetless driver. This test closes the loop end to end for
//! `needs_driven` and `playful`.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::harness::{run_one, EvalRequest, RosterMode};
use cloudkitty_rl::welfare::WelfareAccumulator;

const TICKS: u64 = 2_000;

/// A hand-rolled run of the welfare suite's accounting: generate, drive,
/// observe with the shared module — exactly what the suite does.
fn suite_numbers(brain: Option<&str>, seed: u64) -> cloudkitty_rl::welfare::WelfareReport {
    let mut config = Config::default();
    config.world.seed = seed;
    if let Some(brain) = brain {
        for kitty in &mut config.kitties {
            kitty.behavior = brain.to_string();
        }
    }
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);
    for _ in 0..TICKS {
        drive_tick(&mut world, &registry, &config);
        accumulator.observe(&world);
    }
    accumulator.report()
}

#[test]
fn the_harness_reproduces_the_welfare_suites_numbers_for_the_same_seeds() {
    let core = Config::default();
    let rl = RlConfig::default();
    let registry = BehaviorRegistry::with_builtins();

    for brain in ["needs_driven", "playful"] {
        for seed in [1u64, 2] {
            let outcome = run_one(&EvalRequest {
                core: &core,
                rl: &rl,
                registry: &registry,
                subject: Some(brain),
                roster: RosterMode::AllSubject,
                seed,
                ticks: TICKS,
            });
            let suite = suite_numbers(Some(brain), seed);
            assert_eq!(
                outcome.report, suite,
                "{brain} seed {seed}: harness and suite disagree"
            );
            assert_eq!(outcome.fallback_count, 0, "built-ins never fall back");
        }
    }

    // And with no override the harness scores the config's own roster —
    // the welfare suite's exact scenario.
    let outcome = run_one(&EvalRequest {
        core: &core,
        rl: &rl,
        registry: &registry,
        subject: None,
        roster: RosterMode::AllSubject,
        seed: core.world.seed,
        ticks: TICKS,
    });
    let suite = suite_numbers(None, core.world.seed);
    assert_eq!(outcome.report, suite);
}
