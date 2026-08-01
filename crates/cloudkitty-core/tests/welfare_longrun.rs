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
//! The 20,000-tick bounds run itself lives in
//! `crates/cloudkitty-rl/tests/welfare_longrun.rs` since spec 014 (T033):
//! its metric accounting moved into the shared `cloudkitty-rl::welfare`
//! module so the CI gate and the evaluation harness score with literally
//! the same code. The determinism replay (004 SC-006 / 006 SC-005) and the
//! scenario suites below stay here, beside the engine they exercise.
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

use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::element::ElementKind;
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::test_support::assert_orthogonal_scenes;
use cloudkitty_core::{BehaviorRegistry, World};

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
    //
    // Re-baselined by spec 022 (FR-015): the motor is silent by default, so
    // the announcement half of the property is asserted against an
    // always-announcing world (announce_probability = 1) -- exactly the
    // pre-022 behavior. The wave properties are announce-independent.
    use cloudkitty_core::meow::MessageKind;
    use std::collections::BTreeSet;

    let mut announcing = Config::default();
    announcing.purr.announce_probability = 1.0;
    let config = Arc::new(announcing);
    config.validate().expect("valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let n = world.kitties.len();
    let mut prev_purr: Vec<Option<u64>> = vec![None; n];
    let mut last_end: Vec<Option<u64>> = vec![None; n];
    let mut last_duration: Vec<Option<u64>> = vec![None; n];
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
                    // Spec 022 re-baseline: the rest is proportional --
                    // at least ⌈cooldown_factor_min × the previous purr's
                    // duration⌉ (the drawn factor can only lengthen it).
                    if let (Some(end), Some(prev_d)) = (last_end[idx], last_duration[idx]) {
                        let min_rest =
                            (config.purr.cooldown_factor_min * prev_d as f32).ceil() as u64;
                        assert!(
                            just >= end + min_rest,
                            "{}: purr at {just} inside the minimum rest after {end}",
                            kitty.name
                        );
                    }
                    last_duration[idx] = Some(duration);
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
