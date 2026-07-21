//! The welfare bounds of specs 004 and 006, as permanent regression guards.
//!
//! The 2026-07-18 RCA measured the broken world: low-happiness episodes of
//! 200-500 ticks, every kitty touching the happiness floor, 14-22% of time
//! below happiness 45, needs pinned at the cap for 90+ ticks beside free
//! relief. Spec 004 fixed selection; spec 006 (action durations, full relief
//! every tick of an activity) lifted welfare further, and the bounds below
//! were re-baselined against its measured envelope (2026-07-19: means
//! 88.9 / 73.4 / 85.9, zero ticks below 45, zero floor touches). The 004
//! guarantees remain as hard floors beside each bound: tightening is the only
//! direction these constants may move.
//!
//! This test runs the default-shaped world for 20,000 ticks and holds the
//! engine to those bounds, then runs it again from the same seed to prove
//! determinism survived (004 SC-006 / 006 SC-005 -- the comparison includes
//! the activity timelines, which ride in the serialized kitties).
//!
//! **When a low-happiness streak trips here, suspect a multi-agent livelock
//! first.** Every streak failure to date (2026-07-20, three in one day) was
//! kitties moving in synchronized loops, not a welfare-arithmetic bug: a
//! head-on corridor mirror (fixed in 010, dominant-axis tie-break), a
//! mutual-approach corner orbit (fixed in 012, "Wait for me!" etiquette),
//! and a lockstep convoy sidestep (fixed in 012 FR-008, seeded shuffle).
//! The diagnostic that works: a throwaway probe test printing the stuck
//! kitty's needs, `last_action`, and *every* kitty's position per tick over
//! the failing window -- period-2 position cycles are the signature. See
//! `behavior/mod.rs`'s livelock note for the symmetry-breaking patterns.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::element::{ElementKind, ElementType};
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::{BehaviorRegistry, World};

/// Spec 009 SC-001: interactions happen only in orthogonal range (own tile +
/// four compass neighbours). Asserted per tick on the scenes whose
/// counterparts cannot move mid-scene and so are soundly observable *after*
/// the environment phase: a Drinking kitty's water (permanent, stationary)
/// and a conscripted duet's partner (both clocked, both stationary).
///
/// Meals are deliberately *not* asserted here: a lawful meal can begin on a
/// bowl's last serving — the bowl is orthogonal at apply time, gets consumed,
/// expires in the same tick's environment phase, and `ensure_minimums` may
/// even drop a fresh bowl diagonal to the eater before this observation runs
/// (both cases found by this suite's own determinism, ticks 134 and 2343).
/// Post-tick element positions cannot identify a meal's bowl; the meal-range
/// rule is enforced at its true seam instead — `validate` and
/// `adjacent_stocked_chow` gate both entry and every serving through
/// orthogonal `is_adjacent`, unit-tested in `action.rs` and `world.rs`.
fn assert_orthogonal_scenes(world: &World) {
    for kitty in world.kitties.iter() {
        match kitty.activity {
            Activity::Drinking => {
                let water_in_range = world.elements.iter().any(|e| {
                    e.element_type() == ElementType::Water
                        && kitty.pos.manhattan_distance(&e.pos) <= 1
                });
                assert!(
                    water_in_range,
                    "009 SC-001: {} is drinking with no water in orthogonal range at tick {}",
                    kitty.name, world.tick
                );
            }
            Activity::Resting {
                with_friend: Some(friend),
            }
            | Activity::Playing {
                target: Some(cloudkitty_core::action::TargetRef::Kitty { id: friend }),
            } => {
                let partner_in_range = world
                    .kitties
                    .iter()
                    .any(|k| k.id == friend && kitty.pos.manhattan_distance(&k.pos) <= 1);
                assert!(
                    partner_in_range,
                    "009 SC-001: {}'s duet partner is out of orthogonal range at tick {}",
                    kitty.name, world.tick
                );
            }
            _ => {}
        }
    }
}

const TICKS: u64 = 20_000;
const LOW_HAPPINESS: f32 = 45.0;
/// No low-happiness stretch may exceed this many consecutive ticks.
const MAX_LOW_STREAK: u64 = 20;
/// At most this share of ticks below LOW_HAPPINESS, per kitty.
const MAX_LOW_SHARE: f64 = 0.01;
/// No need this close to its cap for more than 25 consecutive ticks
/// while zero-distance relief for it exists.
const NEAR_CAP: f32 = 99.0;
const MAX_PINNED_STREAK: u64 = 25;
/// No distress older than this, and mean happiness at least 70.
const MAX_DISTRESS_AGE: u64 = 150;
const MIN_MEAN_HAPPINESS: f32 = 70.0;

/// The 004 baselines, never to be loosened past (006 SC-003). A future change
/// that needs a bound above one of these floors is a welfare regression.
const SPEC_004_MAX_LOW_STREAK: u64 = 100;
const SPEC_004_MAX_LOW_SHARE: f64 = 0.05;
const SPEC_004_MAX_PINNED_STREAK: u64 = 25;
const SPEC_004_MAX_DISTRESS_AGE: u64 = 150;
const SPEC_004_MIN_MEAN_HAPPINESS: f32 = 65.0;

const _: () = assert!(MAX_LOW_STREAK <= SPEC_004_MAX_LOW_STREAK);
const _: () = assert!(MAX_LOW_SHARE <= SPEC_004_MAX_LOW_SHARE);
const _: () = assert!(MAX_PINNED_STREAK <= SPEC_004_MAX_PINNED_STREAK);
const _: () = assert!(MAX_DISTRESS_AGE <= SPEC_004_MAX_DISTRESS_AGE);
const _: () = assert!(MIN_MEAN_HAPPINESS >= SPEC_004_MIN_MEAN_HAPPINESS);

/// SC-003's definition of "relief at zero travel distance" for `kind`.
fn zero_distance_relief_exists(world: &World, kitty_idx: usize, kind: NeedKind) -> bool {
    let kitty = &world.kitties[kitty_idx];
    match kind {
        // Grooming and napping happen anywhere; solo play makes play the same.
        NeedKind::Bath | NeedKind::Sleep | NeedKind::Play => true,
        NeedKind::Cuddle => world
            .kitties
            .iter()
            .any(|other| other.id != kitty.id && kitty.pos.is_adjacent(&other.pos)),
        NeedKind::Eat => world
            .elements
            .iter()
            .any(|e| e.element_type() == ElementType::Chow && kitty.pos.is_adjacent(&e.pos)),
        NeedKind::Drink => world
            .elements
            .iter()
            .any(|e| e.element_type() == ElementType::Water && kitty.pos.is_adjacent(&e.pos)),
    }
}

#[tokio::test]
async fn twenty_thousand_ticks_stay_within_the_welfare_bounds() {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let floor = config.happiness.floor;
    let kitty_count = world.kitties.len();

    let mut low_streak = vec![0u64; kitty_count];
    let mut max_low_streak = vec![0u64; kitty_count];
    let mut low_ticks = vec![0u64; kitty_count];
    let mut happiness_sum = vec![0f64; kitty_count];
    let mut floor_touches = vec![0u64; kitty_count];
    let mut max_distress_age = 0u64;
    let mut pinned_streaks: BTreeMap<(usize, NeedKind), u64> = BTreeMap::new();
    let mut max_pinned: BTreeMap<(usize, NeedKind), u64> = BTreeMap::new();

    for _ in 0..TICKS {
        world.tick(&registry, &config).await;
        assert_orthogonal_scenes(&world);

        for idx in 0..kitty_count {
            let kitty = &world.kitties[idx];
            happiness_sum[idx] += kitty.happiness as f64;

            if kitty.happiness <= floor {
                floor_touches[idx] += 1;
            }
            if kitty.happiness < LOW_HAPPINESS {
                low_ticks[idx] += 1;
                low_streak[idx] += 1;
                max_low_streak[idx] = max_low_streak[idx].max(low_streak[idx]);
            } else {
                low_streak[idx] = 0;
            }

            for since in kitty.distress_since.values() {
                max_distress_age = max_distress_age.max(world.tick.saturating_sub(*since));
            }
        }

        // SC-003 needs positions, so it reads the world after the kitty pass.
        for idx in 0..kitty_count {
            for kind in NeedKind::ALL {
                let key = (idx, kind);
                let pinned = world.kitties[idx].needs.get(kind) >= NEAR_CAP
                    && zero_distance_relief_exists(&world, idx, kind);
                let streak = pinned_streaks.entry(key).or_insert(0);
                if pinned {
                    *streak += 1;
                    let best = max_pinned.entry(key).or_insert(0);
                    *best = (*best).max(*streak);
                } else {
                    *streak = 0;
                }
            }
        }
    }

    let names: Vec<_> = world.kitties.iter().map(|k| k.name.clone()).collect();
    for idx in 0..kitty_count {
        let mean = happiness_sum[idx] / TICKS as f64;
        let low_share = low_ticks[idx] as f64 / TICKS as f64;
        println!(
            "{}: mean {:.1}, below-45 {:.1}% (longest streak {}), floor touches {}",
            names[idx],
            mean,
            low_share * 100.0,
            max_low_streak[idx],
            floor_touches[idx],
        );

        assert!(
            max_low_streak[idx] <= MAX_LOW_STREAK,
            "SC-001: {} was below {LOW_HAPPINESS} happiness for {} consecutive ticks (limit {MAX_LOW_STREAK})",
            names[idx],
            max_low_streak[idx]
        );
        assert_eq!(
            floor_touches[idx], 0,
            "SC-002: {} touched the happiness floor",
            names[idx]
        );
        assert!(
            low_share <= MAX_LOW_SHARE,
            "SC-002: {} spent {:.1}% of ticks below {LOW_HAPPINESS} (limit {:.0}%; baseline was 14-22%)",
            names[idx],
            low_share * 100.0,
            MAX_LOW_SHARE * 100.0
        );
        assert!(
            mean >= MIN_MEAN_HAPPINESS as f64,
            "SC-004: {}'s mean happiness {:.1} fell short of {MIN_MEAN_HAPPINESS}",
            names[idx],
            mean
        );
    }

    assert!(
        max_distress_age <= MAX_DISTRESS_AGE,
        "SC-004: a distress went unresolved for {max_distress_age} ticks (limit {MAX_DISTRESS_AGE}; baseline was 216+)"
    );

    for ((idx, kind), streak) in max_pinned {
        assert!(
            streak <= MAX_PINNED_STREAK,
            "SC-003: {}'s {} need sat within 1.0 of the cap for {} consecutive ticks \
             while zero-distance relief existed (limit {MAX_PINNED_STREAK})",
            names[idx],
            kind.as_str(),
            streak
        );
    }
}

#[tokio::test]
async fn a_crowded_out_kitty_is_fed_by_retarget_and_respawn_not_by_reaching_across() {
    // Spec 009 "Crowded targets" (analyze M1): every compass seat at a bowl is
    // taken, and at one serving per seated eater per tick the bowl will be
    // licked clean long before the waiter's turn. The design answer (owner
    // decision 2026-07-20) is not a queue and not new contention mechanics:
    // the waiter shuffles lawfully, the drained bowl expires, chow respawns to
    // its minimum, and the waiter retargets. This drives that loop end to end
    // and holds the 009 orthogonality assertions throughout.
    use cloudkitty_core::config::KittyConfig;
    use cloudkitty_core::element::Element;
    use cloudkitty_core::grid::Position;
    use cloudkitty_core::test_support::test_config;

    let mut config = test_config();
    config.kitties = [
        ("Waiter", 8u32, 6u32),
        ("North", 8, 7),
        ("South", 8, 9),
        ("West", 7, 8),
        ("East", 9, 8),
    ]
    .iter()
    .enumerate()
    .map(|(i, (name, x, y))| KittyConfig {
        id: (i + 1) as u32,
        name: (*name).into(),
        x: *x,
        y: *y,
        behavior: "needs_driven".into(),
        needs: None,
    })
    .collect();
    config.validate().expect("the crowded-bowl config is valid");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();

    let mut world = World::generate(&config);
    world.elements.clear();
    world.push_element(Element {
        id: 9001,
        kind: ElementKind::Chow { servings: 5 },
        pos: Position::new(8, 8), // all four seats taken
        ttl: None,
    });
    world.push_element(Element {
        id: 9002,
        kind: ElementKind::Chow { servings: 5 },
        pos: Position::new(12, 8), // the retarget destination
        ttl: None,
    });
    for kitty in world.kitties.iter_mut() {
        kitty.needs.add(NeedKind::Eat, 95.0); // everyone is hungry; the seats eat first
    }

    const BOUND: u64 = 150;
    let mut waiter_fed_at = None;
    for _ in 0..BOUND {
        world.tick(&registry, &config).await;
        assert_orthogonal_scenes(&world);
        let waiter = world.kitties.iter().find(|k| k.id == 1).unwrap();
        if waiter_fed_at.is_none() && matches!(waiter.activity, Activity::Eating) {
            waiter_fed_at = Some(world.tick);
        }
    }

    let fed_at = waiter_fed_at
        .unwrap_or_else(|| panic!("the crowded-out kitty was never fed within {BOUND} ticks"));
    println!("the waiter ate at tick {fed_at}");
}

#[tokio::test]
async fn a_pre_009_scene_stranded_on_a_diagonal_ends_gracefully() {
    // Spec 009 FR-003 / SC-003: a snapshot saved under the old Chebyshev rules
    // may resume with a scene whose counterpart is now only diagonally
    // adjacent -- legal then, out of range now. Nothing crashes and nothing
    // sticks: a stranded drink ends on the first tick (the per-tick
    // counterpart rule), and a stranded meal past its minimum ends on the
    // first tick too, having consumed nothing -- relief only ever flows
    // through orthogonal `adjacent_stocked_chow`, so the diagonal bowl is
    // never touched.
    use cloudkitty_core::config::KittyConfig;
    use cloudkitty_core::element::Element;
    use cloudkitty_core::grid::Position;
    use cloudkitty_core::kitty::ActivityClock;
    use cloudkitty_core::test_support::test_config;

    let mut config = test_config();
    // A third kitty keeps the world legal while the two under test are posed.
    config.kitties.push(KittyConfig {
        id: 3,
        name: "Bystander".into(),
        x: 1,
        y: 1,
        behavior: "needs_driven".into(),
        needs: None,
    });
    config.validate().expect("valid");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();

    let mut world = World::generate(&config);
    world.elements.clear();
    world.tick = 100;

    // Kitty 1: mid-meal, past its minimum, bowl diagonal (the pre-009 pose).
    let eater = world.kitties.iter().position(|k| k.id == 1).unwrap();
    world.kitties[eater].pos = Position::new(5, 5);
    world.kitties[eater].needs.add(NeedKind::Eat, 60.0);
    world.kitties[eater].activity = Activity::Eating;
    world.kitties[eater].activity_clock = Some(ActivityClock::start(96));
    world.push_element(Element {
        id: 9101,
        kind: ElementKind::Chow { servings: 3 },
        pos: Position::new(6, 6),
        ttl: None,
    });

    // Kitty 2: mid-drink, water diagonal.
    let drinker = world.kitties.iter().position(|k| k.id == 2).unwrap();
    world.kitties[drinker].pos = Position::new(10, 10);
    world.kitties[drinker].needs.add(NeedKind::Drink, 60.0);
    world.kitties[drinker].activity = Activity::Drinking;
    world.kitties[drinker].activity_clock = Some(ActivityClock::start(99));
    world.push_element(Element {
        id: 9102,
        kind: ElementKind::Water,
        pos: Position::new(11, 11),
        ttl: None,
    });

    world.tick(&registry, &config).await;

    let eater = world.kitties.iter().find(|k| k.id == 1).unwrap();
    assert!(
        !matches!(eater.activity, Activity::Eating),
        "the stranded meal ended on the first tick after resuming"
    );
    let drinker = world.kitties.iter().find(|k| k.id == 2).unwrap();
    assert!(
        !matches!(drinker.activity, Activity::Drinking),
        "the stranded drink ended on the first tick after resuming"
    );
    let bowl = world.elements.iter().find(|e| e.id == 9101).unwrap();
    assert!(
        matches!(bowl.kind, ElementKind::Chow { servings: 3 }),
        "no serving ever crossed the diagonal"
    );
}

/// Shared scaffolding for the spec 010 crafted-geometry runs: a 16x16 world
/// with kitty 1 hungry at `start`, kitty 2 parked in a far corner, one bowl,
/// a hand-placed pond, and every element type at its minimum so the
/// environment spawns nothing mid-run (bug/greeble ttls exceed the bound).
/// Returns each tick's position of kitty 1 up to `bound`, stopping once it
/// eats; panics if it never does.
async fn drive_hungry_kitty_around(
    start: (u32, u32),
    bowl: (u32, u32),
    pond: &[(u32, u32)],
    bound: u64,
) -> Vec<(u32, u32)> {
    use cloudkitty_core::element::Element;
    use cloudkitty_core::grid::Position;
    use cloudkitty_core::test_support::test_config;

    let config = Arc::new(test_config());
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    world.elements.clear();

    let idx = world.kitties.iter().position(|k| k.id == 1).unwrap();
    world.kitties[idx].pos = Position::new(start.0, start.1);
    world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
    let other = world.kitties.iter().position(|k| k.id == 2).unwrap();
    world.kitties[other].pos = Position::new(15, 0);

    let mut next_id = 9200u32;
    let mut place = |world: &mut World, kind: ElementKind, pos: (u32, u32), ttl: Option<u64>| {
        world.push_element(Element {
            id: next_id,
            kind,
            pos: Position::new(pos.0, pos.1),
            ttl,
        });
        next_id += 1;
    };
    place(&mut world, ElementKind::Chow { servings: 5 }, bowl, None);
    for &tile in pond {
        place(&mut world, ElementKind::Water, tile, None);
    }
    // The rest of the census, far from the action, so minimums stay met and
    // nothing new spawns before the bound.
    place(&mut world, ElementKind::Bug, (15, 14), Some(bound + 100));
    place(
        &mut world,
        ElementKind::Greeble {
            heading: cloudkitty_core::grid::Direction::North,
        },
        (14, 15),
        Some(bound + 100),
    );
    place(&mut world, ElementKind::Sunbeam, (0, 15), Some(bound + 100));

    let mut trail = Vec::new();
    for _ in 0..bound {
        world.tick(&registry, &config).await;
        let kitty = world.kitties.iter().find(|k| k.id == 1).unwrap();
        trail.push((kitty.pos.x, kitty.pos.y));
        if matches!(kitty.activity, Activity::Eating) {
            return trail;
        }
    }
    panic!("the hungry kitty was not fed within {bound} ticks; trail: {trail:?}");
}

#[tokio::test]
async fn a_kitty_skirts_the_pond_when_dry_progress_exists() {
    // Spec 010 US1/SC-001: the pond sits squarely on the pre-010 walking
    // line from (4,4) to the bowl at (8,8) (east-first staircase through
    // (6,4)/(7,4)). With both axes open, every step has a dry alternative
    // that still closes distance -- the kitty must arrive with dry paws.
    let pond = [(6, 4), (7, 4), (6, 5)];
    let trail = drive_hungry_kitty_around((4, 4), (8, 8), &pond, 60).await;
    for pos in &trail {
        assert!(
            !pond.contains(pos),
            "the kitty stepped in the pond at {pos:?}; trail: {trail:?}"
        );
    }
}

#[tokio::test]
async fn a_kitty_wades_when_the_bowl_is_dead_across_the_water() {
    // Spec 010 US1 acceptance 2 / FR-002: a three-tile water band lies
    // straight across the only distance-closing direction. The preference
    // yields: the kitty paddles through and is fed -- never stuck.
    let pond = [(4, 6), (5, 6), (6, 6)];
    let trail = drive_hungry_kitty_around((5, 3), (5, 9), &pond, 60).await;
    assert!(
        trail.iter().any(|pos| pond.contains(pos)),
        "expected a wade through the band; trail: {trail:?}"
    );
}

#[tokio::test]
async fn purrs_come_in_waves_with_bounded_durations_and_one_meow_each() {
    // Spec 011 SC-002, as a property over the default world: every purr's
    // duration sits within [min_ticks, max_ticks]; consecutive purrs by one
    // kitty are separated by at least cooldown_ticks; every purr begins with
    // exactly one purr meow stamped at its start tick, and no purr meow is
    // ever stamped mid-purr; and the default world -- a happy one -- rumbles.
    use cloudkitty_core::meow::MessageKind;
    use std::collections::BTreeSet;

    let config = Arc::new(Config::default());
    config.validate().expect("valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let n = world.kitties.len();
    let mut prev_purr: Vec<Option<u64>> = vec![None; n];
    let mut last_end: Vec<Option<u64>> = vec![None; n];
    let mut starts_per_kitty = vec![0u64; n];
    let mut start_set: BTreeSet<(u32, u64)> = BTreeSet::new();
    let mut seen_meows: BTreeSet<(u32, u64)> = BTreeSet::new();

    for _ in 0..2_000 {
        world.tick(&registry, &config).await;
        let just = world.tick - 1; // the tick the purr phase ran in

        for (idx, kitty) in world.kitties.iter().enumerate() {
            match (prev_purr[idx], kitty.purring_until) {
                (None, Some(until)) => {
                    let duration = until - just;
                    assert!(
                        (config.purr.min_ticks..=config.purr.max_ticks).contains(&duration),
                        "{}: purr duration {duration} outside bounds at tick {just}",
                        kitty.name
                    );
                    if let Some(end) = last_end[idx] {
                        assert!(
                            just >= end + config.purr.cooldown_ticks,
                            "{}: purr at {just} inside the cooldown after {end}",
                            kitty.name
                        );
                    }
                    starts_per_kitty[idx] += 1;
                    start_set.insert((kitty.id, just));
                }
                (Some(until), None) => {
                    assert!(
                        just >= until,
                        "{}: purr ended early at {just} (scheduled {until})",
                        kitty.name
                    );
                    last_end[idx] = Some(until);
                }
                (Some(a), Some(b)) => {
                    assert_eq!(a, b, "{}: a purr may not be rescheduled", kitty.name);
                }
                (None, None) => {}
            }
            prev_purr[idx] = kitty.purring_until;
        }

        // Every purr meow in the window belongs to exactly one recorded start.
        for meow in world
            .recent_meows
            .iter()
            .filter(|m| m.kind == MessageKind::Purr)
        {
            let key = (meow.kitty_id, meow.tick);
            if seen_meows.insert(key) {
                assert!(
                    start_set.contains(&key),
                    "purr meow at tick {} from kitty {} matches no purr start",
                    meow.tick,
                    meow.kitty_id
                );
            }
        }
    }

    // One meow per start (the retention window is 10 ticks, far wider than
    // the 1-tick observation gap, so no start's meow can be missed).
    assert_eq!(
        seen_meows.len(),
        start_set.len(),
        "every purr announces itself exactly once"
    );
    for (idx, starts) in starts_per_kitty.iter().enumerate() {
        assert!(
            *starts > 0,
            "{} never purred in 2000 ticks of the default happy world",
            world.kitties[idx].name
        );
    }
}

#[tokio::test]
async fn the_same_seed_replays_the_same_five_thousand_ticks_exactly() {
    // SC-006. 5,000 ticks is plenty to catch a stray source of nondeterminism
    // without doubling the suite's runtime.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();

    let run = || async {
        let mut world = World::generate(&config);
        for _ in 0..5_000 {
            world.tick(&registry, &config).await;
        }
        serde_json::to_string(&world).expect("worlds serialize")
    };

    let first = run().await;
    let second = run().await;
    assert_eq!(
        first, second,
        "two runs from the same seed and config diverged (Article V)"
    );
}
