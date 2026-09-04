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
use cloudkitty_core::test_support::assert_orthogonal_scenes;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::welfare::WelfareAccumulator;

const TICKS: u64 = 20_000;

#[test]
fn twenty_thousand_ticks_stay_within_the_welfare_bounds() {
    // Spec 049 T080: these bounds were baselined under global vision (specs
    // 004/006), so the gate pins a world-covering radius (64 = 32 + 32 on
    // the compiled world) and keeps measuring what it always measured. At
    // the served placeholder r = 5 the same run reads 13 violations (means
    // 77.6 / 69.3 / 77.9, below-45 shares 2.6-4.7%, an eat distress of
    // 3,477 ticks): the ruled heading rule sweeps only a ring within r of
    // the inner square, so on a 32x32 world the centre and the corner
    // pockets are never seen and the existence-based safeguard never puts
    // food in view -- OWNER FLAG (spec 049 report), the reading below.
    let mut config = Config::default();
    config.vision.radius = 64;
    config
        .validate()
        .expect("the default config under global vision is valid");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);

    for _ in 0..TICKS {
        drive_tick(&mut world, &registry, &config);
        // Spec 009 SC-001 rides the long run, exactly as it did before the
        // gate moved here (spec 014 review): the spatial scene assertions
        // historically caught edge cases that only long default-world
        // dynamics surface.
        assert_orthogonal_scenes(&world);
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

/// Spec 049 T060: the same 20,000-tick run at the Gen 1 vision radius --
/// every built-in cat blind beyond five tiles, exploring for what it
/// cannot see. A READING, not a gate: the 2.x bounds were baselined under
/// global vision and the Gen 1 welfare bar is the step-5 pre-registration's
/// to set, so this prints the report and asserts only the invariants that
/// hold at any radius (orthogonal scenes, the run completing). Run it with
/// `cargo test -p cloudkitty-rl --test welfare_longrun -- --ignored fog_r5`.
#[test]
#[ignore]
fn fog_r5_twenty_thousand_ticks_welfare_reading() {
    let mut config = Config::default();
    config.vision.radius = 5;
    config
        .validate()
        .expect("the default config at r = 5 is valid");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);

    for _ in 0..TICKS {
        drive_tick(&mut world, &registry, &config);
        assert_orthogonal_scenes(&world);
        accumulator.observe(&world);
    }

    let report = accumulator.report();
    for kitty in &report.kitties {
        println!(
            "r=5 {}: mean {:.1}, below-45 {:.1}% (longest streak {}), floor touches {}",
            kitty.name,
            kitty.mean_happiness,
            kitty.low_share * 100.0,
            kitty.max_low_streak,
            kitty.floor_touches,
        );
    }
    println!("r=5 max distress age {}", report.max_distress_age);
    println!("r=5 distress census {:?}", report.distress_census);
    println!("r=5 pinned {:?}", report.pinned);
    let violations = report.violations();
    println!(
        "r=5 against the 2.x global-vision bounds: {} violation(s){}{}",
        violations.len(),
        if violations.is_empty() { "" } else { "\n" },
        violations.join("\n")
    );
}
