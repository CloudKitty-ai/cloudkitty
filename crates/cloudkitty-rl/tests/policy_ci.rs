//! The full-suite-with-policy-kitty guard (spec 014 SC-005's suite clause,
//! T045): with a fixture policy kitty rostered, determinism holds
//! bit-exactly, the constitutional invariants hold across a long run
//! (Articles I-III assert inside every tick), no decision ever needs the
//! fallback, and the welfare accounting machinery works.
//!
//! The welfare *bounds* are deliberately not asserted here: they are the
//! quality bar for shipped brains (SC-004), gated by `kitty-eval` against a
//! trained artifact — a random-weight fixture has never been taught to walk
//! to a bowl, and holding it to a trained policy's bar would gate CI on an
//! untrained brain. The engine's own guarantees (clamps, safeguard spawner,
//! floor) are what CI holds every brain to, and they assert per tick below.

use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::seam::{drive_tick, Provenance};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::test_support;
use cloudkitty_rl::welfare::WelfareAccumulator;

fn fixture_artifact() -> PathBuf {
    test_support::fixture_artifact("ck-policy-ci", "fixture", 12, 7)
}

fn policy_registry(rl: &RlConfig) -> BehaviorRegistry {
    let path = fixture_artifact();
    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), rl, false).unwrap();
    registry.register("policy:fixture", Arc::new(behavior));
    registry
}

fn policy_config() -> Config {
    let mut config = Config::default();
    // Pumpkin gets the trained-mind seat; the others keep their built-ins.
    config.kitties[2].behavior = "policy:fixture".into();
    config
}

#[test]
fn determinism_holds_with_a_policy_kitty_rostered() {
    let rl = RlConfig::default();
    let registry = policy_registry(&rl);
    let config = Arc::new(policy_config());

    let run = || {
        let mut world = World::generate(&config);
        for _ in 0..2_000 {
            drive_tick(&mut world, &registry, &config);
        }
        serde_json::to_string(&world).expect("worlds serialize")
    };
    assert_eq!(run(), run(), "same seed, same future (Article V)");
}

#[test]
fn a_long_run_with_a_policy_kitty_upholds_the_invariants_without_fallbacks() {
    let rl = RlConfig::default();
    let registry = policy_registry(&rl);
    let config = Arc::new(policy_config());
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);
    let policy_kitty = config.kitties[2].id;

    for _ in 0..5_000 {
        // Every tick asserts Articles I-III internally; completing the run
        // is the invariant pass.
        let driven = drive_tick(&mut world, &registry, &config);
        for record in &driven.report.records {
            assert_ne!(
                record.provenance,
                Provenance::FallbackTaken,
                "kitty {} needed the fallback",
                record.kitty_id
            );
        }
        accumulator.observe(&world);
    }

    // The scorecard machinery reports the policy kitty like any other.
    let report = accumulator.report();
    assert_eq!(report.ticks, 5_000);
    assert!(report
        .kitties
        .iter()
        .any(|k| k.kitty_id == policy_kitty && k.mean_happiness > 0.0));
    assert_eq!(
        world.kitties.len(),
        config.kitties.len(),
        "no kitty ever leaves the world (Article II)"
    );
}

/// The p99 decision-latency check (SC-005: p99 < 10% of the decision
/// budget), `#[ignore]`d by default and run explicitly on the reference
/// machine:
///
/// ```text
/// cargo test -p cloudkitty-rl --release --test policy_ci -- --ignored
/// ```
///
/// Method: 2,000 policy decisions against live default-world snapshots
/// (the world advances between decisions, so observations vary), each
/// timed individually with `Instant`; p99 is the 20th-largest sample. The
/// budget is the default config's: `budget_fraction_of_tick` (0.5) x
/// `tick_ms` (800) = 400ms, so the bar is 40ms per decision.
#[test]
#[ignore = "latency measurement: run explicitly on the reference machine (release)"]
fn p99_decision_latency_is_under_a_tenth_of_the_budget() {
    let rl = RlConfig::default();
    let registry = policy_registry(&rl);
    let config = Arc::new(policy_config());
    let mut world = World::generate(&config);
    let policy = registry.get("policy:fixture").unwrap();
    let policy_kitty = config.kitties[2].id;

    let mut samples = Vec::with_capacity(2_000);
    for _ in 0..2_000 {
        drive_tick(&mut world, &registry, &config);
        let snapshot = Arc::new(world.snapshot());
        let dealt = world.deal_decision_seeds();
        let kitty_seed = dealt
            .seed_for(policy_kitty)
            .expect("the policy kitty is rostered");
        let ctx = cloudkitty_core::behavior::DecisionContext {
            me: snapshot.kitty(policy_kitty).unwrap().clone(),
            world: snapshot.clone(),
            rng: cloudkitty_core::rng::DecisionRng::from_seed(kitty_seed),
            config: config.clone(),
        };
        let start = std::time::Instant::now();
        let _ = cloudkitty_core::behavior::resolve_one(Some(policy.clone()), &ctx, kitty_seed);
        samples.push(start.elapsed());
    }
    samples.sort();
    let p99 = samples[samples.len() - samples.len() / 100 - 1];
    let budget_ms = config.behavior.budget_ms(config.world.tick_ms);
    let bar = std::time::Duration::from_millis(budget_ms / 10);
    println!("p99 decision latency: {p99:?} (bar: {bar:?})");
    assert!(
        p99 < bar,
        "p99 {p99:?} is not under 10% of the {budget_ms}ms budget"
    );
}
