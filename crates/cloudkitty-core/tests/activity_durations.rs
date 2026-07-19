//! Spec 006 (action durations): the success criteria as permanent guards.
//!
//! A 20,000-tick default-config run is instrumented from served state alone
//! (kitty `activity` + `activity_clock`), reconstructing every activity
//! instance and holding it to the configured bounds:
//!
//! - SC-001: no instance shorter than its minimum (except the documented
//!   counterpart-loss ends: a critter that vanished or scurried off, a
//!   groomed friend who walked away, a water source that dried up) and none
//!   longer than its maximum -- checked both while running and at the end.
//! - SC-002 (sampled): eat and drink instances end promptly -- never past the
//!   ticks their starting pressure could possibly justify.
//! - SC-004: every activity kind is observed lasting at least 2 ticks.
//! - SC-006: a snapshot saved mid-activity resumes to the identical future.
//!
//! SC-005 (same-seed determinism, activity timelines included) is guarded by
//! `welfare_longrun::the_same_seed_replays_the_same_five_thousand_ticks_exactly`,
//! whose full-JSON comparison covers the new fields automatically.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use cloudkitty_core::config::{Config, DurationBounds};
use cloudkitty_core::kitty::{Activity, Kitty};
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{BehaviorRegistry, World};

const TICKS: u64 = 20_000;

/// The `[actions.durations]` key an activity is governed by.
fn kind_key(activity: &Activity) -> Option<&'static str> {
    match activity {
        Activity::Idle => None,
        Activity::Eating => Some("eat"),
        Activity::Drinking => Some("drink"),
        Activity::Playing { .. } => Some("play"),
        Activity::Grooming { .. } => Some("bath"),
        Activity::Sleeping { .. } => Some("sleep"),
        Activity::Resting { .. } => Some("cuddle"),
    }
}

fn bounds_for(config: &Config, key: &str) -> DurationBounds {
    let d = &config.actions.durations;
    match key {
        "eat" => d.eat,
        "drink" => d.drink,
        "play" => d.play,
        "bath" => d.bath,
        "sleep" => d.sleep,
        "cuddle" => d.cuddle,
        other => unreachable!("unknown duration key {other}"),
    }
}

/// Whether this activity's counterpart can leave mid-scene, lawfully ending
/// it below the minimum (FR-010). Duet partners cannot leave (they are bound
/// and never move mid-activity), so duets are not in this list.
fn counterpart_can_leave(activity: &Activity) -> bool {
    use cloudkitty_core::action::TargetRef;
    matches!(
        activity,
        Activity::Drinking
            | Activity::Playing {
                target: Some(TargetRef::Element { .. })
            }
            | Activity::Grooming { target: Some(_) }
    )
}

#[derive(Debug, Clone)]
struct OpenInstance {
    kind: &'static str,
    short_end_allowed: bool,
    /// The action that continues this activity. The tick an activity ends on
    /// clears its clock *after* servicing it, so that final tick is invisible
    /// in the clock -- but `last_action` truthfully records the continuation,
    /// and the tracker credits it from there.
    continuation: cloudkitty_core::action::Action,
    /// Pressure of the governed need just before the first bite/sip -- the
    /// promptness budget for SC-002.
    starting_pressure: Option<f32>,
    last_elapsed: u64,
}

#[tokio::test]
async fn twenty_thousand_ticks_of_activities_respect_their_bounds() {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    // (kitty id, clock.started) uniquely names an instance.
    let mut open: BTreeMap<(u32, u64), OpenInstance> = BTreeMap::new();
    let mut observed_two_plus: BTreeSet<&'static str> = BTreeSet::new();
    let mut completed = 0u64;
    let mut prev_needs: BTreeMap<u32, (f32, f32)> = BTreeMap::new(); // (eat, drink)

    let finalize = |inst: OpenInstance,
                    config: &Config,
                    completed: &mut u64,
                    observed_two_plus: &mut BTreeSet<&'static str>| {
        if inst.last_elapsed >= 2 {
            observed_two_plus.insert(inst.kind);
        }
        let bounds = bounds_for(config, inst.kind);
        assert!(
            inst.last_elapsed <= bounds.max,
            "SC-001: a {} ran {} ticks, past its maximum {}",
            inst.kind,
            inst.last_elapsed,
            bounds.max
        );
        if !inst.short_end_allowed {
            assert!(
                inst.last_elapsed >= bounds.min,
                "SC-001: a {} ended after {} ticks, below its minimum {} \
                 (and its counterpart could not have left)",
                inst.kind,
                inst.last_elapsed,
                bounds.min
            );
        }
        // SC-002 (sampled on eat/drink): the scene never outlives what its
        // starting pressure could justify. Relief is full per tick; growth
        // (< 1/tick) is absorbed by the -1.0 margin.
        if let Some(pressure) = inst.starting_pressure {
            let relief = match inst.kind {
                "eat" => config.actions.eat_relief,
                "drink" => config.actions.drink_relief,
                _ => unreachable!(),
            };
            let justified = (pressure / (relief - 1.0)).ceil() as u64;
            let budget = justified.max(bounds.min);
            assert!(
                inst.last_elapsed <= budget,
                "SC-002: a {} with starting pressure {:.1} ran {} ticks \
                 (budget {budget})",
                inst.kind,
                pressure,
                inst.last_elapsed
            );
        }
        *completed += 1;
    };

    for _ in 0..TICKS {
        world.tick(&registry, &config).await;
        let closed_tick = world.tick - 1; // the tick that just resolved

        for kitty in &world.kitties {
            let current_key = kitty.activity_clock.map(|clock| (kitty.id, clock.started));

            // Any open instance for this kitty that is not the current one
            // has ended (clock cleared, or a new scene began).
            let stale: Vec<(u32, u64)> = open
                .keys()
                .filter(|(id, started)| *id == kitty.id && current_key != Some((*id, *started)))
                .copied()
                .collect();
            for key in stale {
                let mut inst = open.remove(&key).expect("key just listed");
                // Credit the invisible final tick: if this kitty's recorded
                // action this tick was the scene's continuation, the scene
                // was serviced once more before its clock cleared.
                if kitty.last_action == Some(inst.continuation) {
                    inst.last_elapsed += 1;
                }
                finalize(inst, &config, &mut completed, &mut observed_two_plus);
            }

            let Some(clock) = kitty.activity_clock else {
                continue;
            };
            let elapsed = clock.elapsed(closed_tick);
            let key = (kitty.id, clock.started);
            let entry = open.entry(key).or_insert_with(|| OpenInstance {
                kind: kind_key(&kitty.activity).expect("clocked activity is in progress"),
                short_end_allowed: counterpart_can_leave(&kitty.activity),
                continuation: kitty
                    .activity
                    .continuation()
                    .expect("an in-progress activity has a continuation"),
                starting_pressure: match kitty.activity {
                    Activity::Eating => prev_needs.get(&kitty.id).map(|(eat, _)| *eat),
                    Activity::Drinking => prev_needs.get(&kitty.id).map(|(_, drink)| *drink),
                    _ => None,
                },
                last_elapsed: 0,
            });
            entry.last_elapsed = elapsed;
            let bounds = bounds_for(&config, entry.kind);
            assert!(
                elapsed <= bounds.max,
                "SC-001: a {} is {elapsed} ticks old, past its maximum {} while still running",
                entry.kind,
                bounds.max
            );
        }

        prev_needs = world
            .kitties
            .iter()
            .map(|k: &Kitty| {
                (
                    k.id,
                    (k.needs.get(NeedKind::Eat), k.needs.get(NeedKind::Drink)),
                )
            })
            .collect();
    }
    for (_, mut inst) in std::mem::take(&mut open) {
        // Scenes still running when the curtain falls haven't ended short --
        // only their maximum is checkable.
        inst.short_end_allowed = true;
        inst.starting_pressure = None;
        finalize(inst, &config, &mut completed, &mut observed_two_plus);
    }

    println!("completed activity instances: {completed}");
    println!("kinds observed at 2+ ticks: {observed_two_plus:?}");
    assert!(
        completed > 1_000,
        "the run should be full of scenes; something is off if it is not"
    );
    // SC-004: every kind is watchable -- at least 2 consecutive ticks each.
    for kind in ["eat", "drink", "play", "bath", "sleep", "cuddle"] {
        assert!(
            observed_two_plus.contains(kind),
            "SC-004: no {kind} was ever observed lasting 2+ ticks in {TICKS} ticks"
        );
    }
}

#[tokio::test]
async fn a_mid_activity_save_resumes_to_the_identical_future() {
    // SC-006: saving mid-scene loses nothing -- the resumed world walks the
    // exact same future as the one that never stopped.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    for _ in 0..300 {
        world.tick(&registry, &config).await;
    }
    // Make sure the save actually catches a scene in progress.
    let mut guard = 0;
    while !world.kitties.iter().any(|k| k.activity_clock.is_some()) {
        world.tick(&registry, &config).await;
        guard += 1;
        assert!(
            guard < 500,
            "no activity in 500 ticks? durations are broken"
        );
    }

    let saved = serde_json::to_string(&world).expect("worlds serialize");
    let mut resumed: World = serde_json::from_str(&saved).expect("snapshots load");

    for _ in 0..500 {
        world.tick(&registry, &config).await;
        resumed.tick(&registry, &config).await;
    }
    assert_eq!(
        serde_json::to_string(&world).unwrap(),
        serde_json::to_string(&resumed).unwrap(),
        "a mid-activity resume diverged from the uninterrupted run"
    );
}
