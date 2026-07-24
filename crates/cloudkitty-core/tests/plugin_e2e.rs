//! End-to-end plugin tests (spec 016 US2): real `ScriptBehavior` instances
//! driving real child processes through whole constitutional ticks, hostile
//! and friendly alike. The fixtures under `tests/fixtures/` are the
//! adversaries and the model citizen; `seam::drive_tick` is the driver, so
//! every tick runs the full applied phases -- invariants asserted -- and
//! comes back with provenance-marked records.
//!
//! These tests spawn `python3` (present on dev machines and CI alike; the
//! repo already carries a Python test surface).

use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::behavior::{BehaviorRegistry, ScriptBehavior};
use cloudkitty_core::config::Config;
use cloudkitty_core::seam::{drive_tick, Provenance};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;

fn fixture(name: &str) -> String {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name)
        .to_string_lossy()
        .into_owned()
}

fn plugin(fixture_name: &str, extra_args: &[&str]) -> ScriptBehavior {
    let mut args = vec![fixture(fixture_name)];
    args.extend(extra_args.iter().map(|s| s.to_string()));
    ScriptBehavior::new("test_plugin", "python3", args)
}

fn world_with_plugin(
    behavior: ScriptBehavior,
    plugged_kitties: &[usize],
    tune: impl FnOnce(&mut Config),
) -> (World, BehaviorRegistry, Arc<Config>) {
    let mut config = test_config();
    for &index in plugged_kitties {
        config.kitties[index].behavior = "test_plugin".into();
    }
    tune(&mut config);
    let config = Arc::new(config);
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("test_plugin", Arc::new(behavior));
    let world = World::generate(&config);
    (world, registry, config)
}

/// SC-004: a well-behaved plugin drives its kitty for a full in-world day
/// (600 ticks), every decision applied and attributed to the advisor -- and
/// a second kitty sharing the same process is attributed correctly too
/// (the envelope's kitty_id echo at work).
#[test]
fn a_well_behaved_plugin_drives_kitties_for_a_full_day() {
    let (mut world, registry, config) =
        world_with_plugin(plugin("well_behaved.py", &[]), &[0, 1], |_| {});
    let (first, second) = (config.kitties[0].id, config.kitties[1].id);

    for _ in 0..600 {
        let driven = drive_tick(&mut world, &registry, &config);
        for id in [first, second] {
            let record = driven.report.record(id).expect("every kitty decides");
            assert_eq!(
                record.provenance,
                Provenance::PolicyMade,
                "tick {}: the plugin's decision is attributed to it",
                world.tick
            );
        }
    }
    assert_eq!(world.tick, 600, "a full in-world day, zero missed ticks");
}

/// SC-003: a hostile plugin emitting malformed output every decision for
/// 1,000 ticks. Every tick completes, the constitutional invariants hold
/// (asserted inside the applied phases every tick), and every affected
/// decision is the fallback's -- the process is never killed for mere
/// garbage, and no malformed proposal is ever reshaped into a legal one.
#[test]
fn a_hostile_plugin_costs_cleverness_and_nothing_else() {
    let (mut world, registry, config) = world_with_plugin(plugin("hostile.py", &[]), &[0], |_| {});
    let advised = config.kitties[0].id;

    for _ in 0..1000 {
        let driven = drive_tick(&mut world, &registry, &config);
        let record = driven.report.record(advised).expect("the kitty decides");
        assert_eq!(
            record.provenance,
            Provenance::FallbackTaken,
            "tick {}: garbage resolves to the fallback",
            world.tick
        );
    }
    assert_eq!(world.tick, 1000);
}

/// SC-005: the advisor dies mid-run. Zero missed ticks, fallback from the
/// first affected decision, relaunch only after `relaunch_cooldown_ticks`,
/// recovery automatic.
#[test]
fn a_plugin_that_dies_mid_run_falls_back_and_relaunches_after_the_cooldown() {
    let (mut world, registry, config) = world_with_plugin(
        plugin("well_behaved.py", &["--die-after", "5"]),
        &[0],
        |c| c.behavior.relaunch_cooldown_ticks = 3,
    );
    let advised = config.kitties[0].id;

    let mut provenances = Vec::new();
    for _ in 0..9 {
        let driven = drive_tick(&mut world, &registry, &config);
        provenances.push(driven.report.record(advised).unwrap().provenance);
    }

    use Provenance::{FallbackTaken as F, PolicyMade as P};
    assert_eq!(
        provenances,
        vec![P, P, P, P, P, F, F, F, P],
        "five advised ticks, death at tick 5, cooldown ticks 6-7, \
         automatic relaunch at tick 8"
    );
    assert_eq!(world.tick, 9, "zero missed ticks throughout");
}

/// FR-010: an oversized reply is a failed proposal and kills the process --
/// no relaunch inside the cooldown window.
#[test]
fn an_oversized_reply_fails_the_proposal_and_kills_the_process() {
    let (mut world, registry, config) =
        world_with_plugin(plugin("oversized.py", &[]), &[0], |_| {});
    let advised = config.kitties[0].id;

    for _ in 0..5 {
        let driven = drive_tick(&mut world, &registry, &config);
        assert_eq!(
            driven.report.record(advised).unwrap().provenance,
            Provenance::FallbackTaken,
            "tick {}: oversized replies never become decisions",
            world.tick
        );
    }
}

/// Review 2026-07-23: the silent wedge — a plugin that reads each request,
/// never answers, and keeps stdout open. This runs on the BUDGETLESS path
/// (drive_tick has no wall-clock budget), so only the transport's own
/// exchange deadline can contain it: every tick must complete, bounded by
/// `exchange_timeout_ms`, with the fallback deciding and the wedged process
/// killed and re-tried after the cooldown. Before the deadline existed this
/// exact scenario hung the driver forever.
#[test]
fn a_silently_wedged_plugin_cannot_stall_the_budgetless_driver() {
    let (mut world, registry, config) = world_with_plugin(plugin("wedged.py", &[]), &[0], |c| {
        c.behavior.exchange_timeout_ms = 150;
        c.behavior.relaunch_cooldown_ticks = 1;
    });
    let advised = config.kitties[0].id;

    let started = std::time::Instant::now();
    for _ in 0..3 {
        let driven = drive_tick(&mut world, &registry, &config);
        assert_eq!(
            driven.report.record(advised).unwrap().provenance,
            Provenance::FallbackTaken,
            "tick {}: a wedged plugin costs cleverness, never the tick",
            world.tick
        );
    }
    assert_eq!(world.tick, 3, "zero missed ticks");
    // Generous bound: 3 ticks x 150ms deadline plus process churn. The
    // point is bounded-at-all — the pre-fix behavior was an infinite hang.
    assert!(
        started.elapsed() < std::time::Duration::from_secs(30),
        "each tick is bounded by the exchange deadline"
    );
}

/// Analysis finding I1: a plugin that replies twice per request. The stale
/// second line -- a perfectly valid envelope for an earlier decision -- must
/// never be applied: the correlation check fails it and restarts the
/// process, so provenance alternates advisor/fallback with a 1-tick cooldown
/// and no stale proposal ever lands.
#[test]
fn a_desynced_reply_stream_is_caught_by_correlation_never_applied_stale() {
    let (mut world, registry, config) = world_with_plugin(plugin("desync.py", &[]), &[0], |c| {
        c.behavior.relaunch_cooldown_ticks = 1
    });
    let advised = config.kitties[0].id;

    for step in 0..8u64 {
        let driven = drive_tick(&mut world, &registry, &config);
        let record = driven.report.record(advised).unwrap();
        let expected = if step % 2 == 0 {
            // Fresh process: the first reply correlates and is applied.
            Provenance::PolicyMade
        } else {
            // The buffered stale line answers the wrong tick: rejected,
            // process restarted -- never a stale action applied as fresh.
            Provenance::FallbackTaken
        };
        assert_eq!(record.provenance, expected, "step {step}");
    }
}
