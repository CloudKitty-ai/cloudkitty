//! Spec 006 (action durations): the success criteria as permanent guards.
//!
//! A 20,000-tick default-config run is held to the configured bounds using
//! the engine's own record: every activity that ends emits an
//! [`ActivityEnd`] event carrying the exact tick span it ran (the served
//! snapshots alone cannot show a scene's final tick, which clears the clock
//! it stamped). Bounds come from `Activity::bounds` -- the same mapping the
//! engine enforces -- so the test cannot drift against a re-governed kind.
//!
//! - SC-001: no instance shorter than its minimum (except the documented
//!   counterpart-loss ends: a critter that vanished or scurried off, a
//!   groomed friend who walked away, a water source that dried up, and --
//!   spec 060 -- a meal whose bowl drained or vanished, which ends at that
//!   resolution) and none longer than its maximum -- checked on every ended
//!   event, and against still-running clocks each tick.
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

use cloudkitty_core::config::Config;
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::world::adjacent_stocked_chow_in;
use cloudkitty_core::{ActivityEnd, BehaviorRegistry, Element, ElementKind, Position, World};

const TICKS: u64 = 20_000;

/// The `[actions.durations]` key an activity is governed by -- labels for
/// assertion messages and the SC-004 coverage set. (Bounds themselves come
/// from `Activity::bounds`, never from this label.)
fn kind_key(activity: &Activity) -> &'static str {
    match activity {
        Activity::Idle => "idle",
        Activity::Eating => "eat",
        Activity::Drinking => "drink",
        Activity::Playing { .. } => "play",
        Activity::Grooming { .. } => "bath",
        Activity::Sleeping { .. } => "sleep",
        Activity::Resting { .. } => "cuddle",
    }
}

/// Whether this activity's counterpart can leave mid-scene, lawfully ending
/// it below the minimum (FR-010, and spec 060 for meals: a bowl that drains
/// or vanishes fails the feeding condition and ends the scene at that
/// resolution). Duet partners cannot leave (they are bound and never move
/// mid-activity), so duets are not in this list. Eating does not get a
/// blanket pass: every below-minimum Eating end is further held to a
/// failed feeding condition in the event loop below (review 2026-10-12).
fn counterpart_can_leave(activity: &Activity) -> bool {
    use cloudkitty_core::action::TargetRef;
    matches!(
        activity,
        Activity::Eating
            | Activity::Drinking
            | Activity::Playing {
                target: Some(TargetRef::Element { .. })
            }
            | Activity::Grooming { target: Some(_) }
    )
}

#[tokio::test]
async fn twenty_thousand_ticks_of_activities_respect_their_bounds() {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    // (kitty id, started tick) uniquely names an instance across its life.
    let mut seen: BTreeSet<(u32, u64)> = BTreeSet::new();
    let mut starting_pressure: BTreeMap<(u32, u64), f32> = BTreeMap::new();
    let mut observed_two_plus: BTreeSet<&'static str> = BTreeSet::new();
    let mut completed = 0u64;
    let mut prev_needs: BTreeMap<u32, (f32, f32)> = BTreeMap::new(); // (eat, drink)
    // Every bowl on the books at the previous boundary, for the spec-060
    // feeding-condition check: the environment phase (the element vec's
    // only writer) runs after resolution, so this is the bowl set the
    // resolutions of the CURRENT tick read.
    let mut prev_chow: BTreeMap<u32, Position> = BTreeMap::new();

    let check_ended = |ev: &ActivityEnd,
                       starting_pressure: &BTreeMap<(u32, u64), f32>,
                       observed_two_plus: &mut BTreeSet<&'static str>| {
        let kind = kind_key(&ev.activity);
        let span = ev.span();
        if span >= 2 {
            observed_two_plus.insert(kind);
        }
        let bounds = ev
            .activity
            .bounds(&config.actions.durations)
            .expect("an ended activity was in progress, so it has bounds");
        assert!(
            span <= bounds.max,
            "SC-001: a {kind} ran {span} ticks, past its maximum {}",
            bounds.max
        );
        if !counterpart_can_leave(&ev.activity) {
            assert!(
                span >= bounds.min,
                "SC-001: a {kind} ended after {span} ticks, below its minimum {} \
                 (and its counterpart could not have left)",
                bounds.min
            );
        }
        // SC-002 (sampled on eat/drink): the scene never outlives what its
        // starting pressure could justify. Relief is full per tick; growth
        // (< 1/tick) is absorbed by the -1.0 margin.
        if let Some(pressure) = starting_pressure.get(&(ev.kitty_id, ev.started)) {
            let relief = match ev.activity {
                Activity::Eating => config.actions.eat_relief,
                Activity::Drinking => config.actions.drink_relief,
                _ => unreachable!("starting pressure is only recorded for meals and drinks"),
            };
            let justified = (pressure / (relief - 1.0)).ceil() as u64;
            let budget = justified.max(bounds.min);
            assert!(
                span <= budget,
                "SC-002: a {kind} with starting pressure {pressure:.1} ran {span} ticks \
                 (budget {budget})"
            );
        }
    };

    for _ in 0..TICKS {
        world.tick(&registry, &config).await;
        let closed_tick = world.tick - 1; // the tick that just resolved

        // Every scene longer than one tick is observed open here at least
        // once (counterpart pruning runs in the owner's next slot) -- the
        // moment its starting pressure is on the books and its running age
        // checkable. A meal started on a bowl's last serving ends at its
        // own start tick's resolution (spec 060) and is never seen open, so
        // SC-002's pressure sampling skips such one-tick meals; their spans
        // are still bounds-checked through the activity log below.
        for kitty in &world.kitties {
            let Some(clock) = kitty.activity_clock else {
                continue;
            };
            let elapsed = clock.elapsed(closed_tick);
            if elapsed == 1 {
                if let Some(&(eat, drink)) = prev_needs.get(&kitty.id) {
                    match kitty.activity {
                        Activity::Eating => {
                            starting_pressure.insert((kitty.id, clock.started), eat);
                        }
                        Activity::Drinking => {
                            starting_pressure.insert((kitty.id, clock.started), drink);
                        }
                        _ => {}
                    }
                }
            }
            let bounds = kitty
                .activity
                .bounds(&config.actions.durations)
                .expect("a clocked activity is in progress");
            assert!(
                elapsed <= bounds.max,
                "SC-001: a {} is {elapsed} ticks old, past its maximum {} while still running",
                kind_key(&kitty.activity),
                bounds.max
            );
        }

        // The engine's own record of everything that ended: exact spans, no
        // reconstruction. The log holds far more than one tick's worth of
        // events, so reading it every tick misses nothing.
        for ev in world.activity_log.events() {
            if !seen.insert((ev.kitty_id, ev.started)) {
                continue;
            }
            check_ended(ev, &starting_pressure, &mut observed_two_plus);
            // Spec 060 (review 2026-10-12): an Eating end below its minimum
            // is lawful ONLY on a failed feeding condition. The end's first
            // appearance is this boundary -- the eater has had no further
            // slot, so it still sits where the meal ended -- but the
            // environment phase already ran, so the bowl set is rebuilt as
            // the resolution saw it: the previous boundary's bowls, the
            // survivors at their current servings (nothing restocks a
            // bowl), the vanished ones empty. A chow ttl could expire a
            // STOCKED bowl and let an unlawful end pass here (never flag a
            // lawful one); the default config has no chow ttl.
            if matches!(ev.activity, Activity::Eating) {
                let bounds = ev
                    .activity
                    .bounds(&config.actions.durations)
                    .expect("an ended activity has bounds");
                if ev.span() < bounds.min {
                    let pos = world
                        .kitties
                        .iter()
                        .find(|k| k.id == ev.kitty_id)
                        .expect("kitties never leave the vec (Article II)")
                        .pos;
                    let resolution_bowls: Vec<Element> = prev_chow
                        .iter()
                        .map(|(&id, &bowl_pos)| Element {
                            id,
                            kind: ElementKind::Chow {
                                servings: world
                                    .elements
                                    .iter()
                                    .find(|e| e.id == id)
                                    .map_or(0, |e| match e.kind {
                                        ElementKind::Chow { servings } => servings,
                                        _ => 0,
                                    }),
                            },
                            pos: bowl_pos,
                            ttl: None,
                        })
                        .collect();
                    assert!(
                        adjacent_stocked_chow_in(&resolution_bowls, pos).is_none(),
                        "SC-001/spec 060: an eat ended after {} ticks, below its \
                         minimum {}, with its feeding condition still holding",
                        ev.span(),
                        bounds.min
                    );
                }
            }
            starting_pressure.remove(&(ev.kitty_id, ev.started));
            completed += 1;
        }

        prev_needs = world
            .kitties
            .iter()
            .map(|k| {
                (
                    k.id,
                    (k.needs.get(NeedKind::Eat), k.needs.get(NeedKind::Drink)),
                )
            })
            .collect();
        prev_chow = world
            .elements
            .iter()
            .filter(|e| matches!(e.kind, ElementKind::Chow { .. }))
            .map(|e| (e.id, e.pos))
            .collect();
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
