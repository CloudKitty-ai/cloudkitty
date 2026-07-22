//! The long-run welfare gate (specs 004/006; moved here by spec 014 T033):
//! 20,000 default-world ticks held to the trusted bounds, scored by the
//! shared `cloudkitty_rl::welfare` module — the same code the evaluation
//! harness reports with, so the gate and the scorecard can never drift.
//!
//! Runs on the budgetless headless driver (FR-017), which the parity suite
//! proves byte-identical to the served tick.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::welfare::WelfareAccumulator;

const TICKS: u64 = 20_000;

#[test]
fn twenty_thousand_ticks_stay_within_the_welfare_bounds() {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);

    for _ in 0..TICKS {
        drive_tick(&mut world, &registry, &config);
        accumulator.observe(&world);
    }

    let report = accumulator.report();
    for kitty in &report.kitties {
        println!(
            "{}: mean {:.1}, below-45 {:.1}% (longest streak {}), floor touches {}",
            kitty.name,
            kitty.mean_happiness,
            kitty.low_share * 100.0,
            kitty.max_low_streak,
            kitty.floor_touches,
        );
    }
    println!("max distress age {}", report.max_distress_age);

    let violations = report.violations();
    assert!(
        violations.is_empty(),
        "welfare bounds violated:\n{}",
        violations.join("\n")
    );
}
