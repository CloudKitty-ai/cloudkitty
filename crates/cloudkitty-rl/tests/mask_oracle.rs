//! The mask pure-oracle property test (spec 014 amended FR-018, T020).
//!
//! For every menu entry, the mask's verdict must equal the engine's own
//! judgment — counterpart pruning, validation, and duration enforcement run
//! for real on a probe world — with **no carve-outs**. Plus the structural
//! never-all-zero property across randomized rosters and activities,
//! including the four named crowded-continuation constructions that
//! exercise target-priority slot ordering: a crowded duet, a crowded
//! co-sleep, a crowded groom, and a default-population critter cluster
//! around an ongoing element play.

use cloudkitty_core::action::TargetRef;
use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::{Direction, Position};
use cloudkitty_core::kitty::{Activity, ActivityClock, Kitty, KittyId};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use cloudkitty_rl::codec::ActionCodec;
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::mask::legal_action_mask;
use cloudkitty_rl::observe::TargetTable;
use proptest::prelude::*;

/// The oracle: mask verdict == the engine's apply-slot gauntlet, run for
/// real (mutations included) on a fresh probe per entry. Also asserts the
/// structural never-all-zero property for every kitty.
fn assert_mask_matches_engine(world: &World, config: &Config) {
    let snapshot = world.snapshot();
    let obs_cfg = ObservationConfig::default();
    let codec = ActionCodec::v1(&obs_cfg);

    for kitty in &snapshot.kitties {
        let table = TargetTable::build(&snapshot, kitty.id, &obs_cfg);
        let mask = legal_action_mask(&snapshot, kitty.id, &table, &codec, config);

        for (index, &bit) in mask.iter().enumerate() {
            let proposal = codec.decode(index, &table).unwrap();
            let mut probe = World::from_snapshot(&snapshot);
            let applied = probe.apply_slot_verdict(kitty.id, proposal, config);
            let engine_says = applied == proposal;
            assert_eq!(
                bit, engine_says,
                "kitty {} entry {index} ({proposal:?}): mask {bit}, engine {engine_says} \
                 (applied {applied:?})",
                kitty.id
            );
        }

        assert!(
            mask.iter().any(|&b| b),
            "all-zero mask for kitty {} in activity {:?}",
            kitty.id,
            kitty.activity
        );
    }
}

// ---- randomized rosters and activities --------------------------------

#[derive(Debug, Clone)]
enum ActivitySpec {
    Idle,
    Eating,
    Drinking,
    RestSolo,
    RestWith(usize),
    SleepSolo,
    SleepWith(usize),
    GroomSelf,
    GroomFriend(usize),
    PlaySolo,
    PlayKitty(usize),
    PlayCritter(usize),
}

fn arb_activity() -> impl Strategy<Value = ActivitySpec> {
    prop_oneof![
        Just(ActivitySpec::Idle),
        Just(ActivitySpec::Eating),
        Just(ActivitySpec::Drinking),
        Just(ActivitySpec::RestSolo),
        (1usize..6).prop_map(ActivitySpec::RestWith),
        Just(ActivitySpec::SleepSolo),
        (1usize..6).prop_map(ActivitySpec::SleepWith),
        Just(ActivitySpec::GroomSelf),
        (1usize..6).prop_map(ActivitySpec::GroomFriend),
        Just(ActivitySpec::PlaySolo),
        (1usize..6).prop_map(ActivitySpec::PlayKitty),
        (0usize..8).prop_map(ActivitySpec::PlayCritter),
    ]
}

#[derive(Debug, Clone)]
struct WorldSpec {
    roster: usize,
    positions: Vec<(u32, u32)>,
    activities: Vec<ActivitySpec>,
    serviced: Vec<u64>,
}

fn arb_world_spec() -> impl Strategy<Value = WorldSpec> {
    (2usize..=6)
        .prop_flat_map(|roster| {
            (
                Just(roster),
                prop::collection::vec((0u32..32, 0u32..32), roster),
                prop::collection::vec(arb_activity(), roster),
                prop::collection::vec(0u64..6, roster),
            )
        })
        .prop_map(|(roster, positions, activities, serviced)| WorldSpec {
            roster,
            positions,
            activities,
            serviced,
        })
}

/// Builds a world from a spec. States need not be *reachable* — the mask
/// must agree with the engine on whatever state it is shown — but duets are
/// kept reciprocal and clocks paired, matching the engine's invariants.
fn build_world(spec: &WorldSpec, config: &Config) -> World {
    let mut world = World::generate(config);
    world.tick = 10;

    // Grow the roster to the requested size and place everyone.
    let mut next_id = world.kitties.iter().map(|k| k.id).max().unwrap_or(0) + 1;
    while world.kitties.len() < spec.roster {
        world.kitties.push(Kitty::new(
            next_id,
            format!("K{next_id}"),
            Position::new(0, 0),
            "needs_driven",
        ));
        next_id += 1;
    }
    world.kitties.truncate(spec.roster.max(2));
    world.kitties.sort_by_key(|k| k.id);
    let ids: Vec<KittyId> = world.kitties.iter().map(|k| k.id).collect();
    for (i, &(x, y)) in spec.positions.iter().enumerate().take(ids.len()) {
        let idx = world.kitty_index(ids[i]).unwrap();
        world.kitties[idx].pos = Position::new(x, y);
    }

    let critters: Vec<u32> = world.snapshot().critters().map(|e| e.id).collect();

    for i in 0..ids.len() {
        let idx = world.kitty_index(ids[i]).unwrap();
        if world.kitties[idx].activity_clock.is_some() {
            continue; // already bound into a duet from an earlier partner
        }
        let serviced = spec.serviced.get(i).copied().unwrap_or(0);
        let started = world.tick - serviced.min(world.tick);
        let clock = ActivityClock {
            started,
            applied: world.tick.saturating_sub(1).max(started),
        };
        let partner_of = |offset: usize| ids[(i + offset) % ids.len()];
        let activity = match spec
            .activities
            .get(i)
            .cloned()
            .unwrap_or(ActivitySpec::Idle)
        {
            ActivitySpec::Idle => None,
            ActivitySpec::Eating => Some(Activity::Eating),
            ActivitySpec::Drinking => Some(Activity::Drinking),
            ActivitySpec::RestSolo => Some(Activity::Resting { with_friend: None }),
            ActivitySpec::SleepSolo => Some(Activity::Sleeping {
                in_sunbeam: false,
                with_friend: None,
            }),
            ActivitySpec::GroomSelf => Some(Activity::Grooming { target: None }),
            ActivitySpec::PlaySolo => Some(Activity::Playing { target: None }),
            ActivitySpec::SleepWith(o) => {
                let p = partner_of(o);
                (p != ids[i]).then_some(Activity::Sleeping {
                    in_sunbeam: false,
                    with_friend: Some(p),
                })
            }
            ActivitySpec::GroomFriend(o) => {
                let p = partner_of(o);
                (p != ids[i]).then_some(Activity::Grooming { target: Some(p) })
            }
            ActivitySpec::RestWith(o) | ActivitySpec::PlayKitty(o) => {
                let p = partner_of(o);
                let free = p != ids[i]
                    && world
                        .kitty(p)
                        .map(|k| k.activity_clock.is_none())
                        .unwrap_or(false);
                if free {
                    let social_play = matches!(spec.activities[i], ActivitySpec::PlayKitty(_));
                    // Bind the duet reciprocally with the shared clock.
                    let (mine, theirs) = if social_play {
                        (
                            Activity::Playing {
                                target: Some(TargetRef::Kitty { id: p }),
                            },
                            Activity::Playing {
                                target: Some(TargetRef::Kitty { id: ids[i] }),
                            },
                        )
                    } else {
                        (
                            Activity::Resting {
                                with_friend: Some(p),
                            },
                            Activity::Resting {
                                with_friend: Some(ids[i]),
                            },
                        )
                    };
                    let pidx = world.kitty_index(p).unwrap();
                    world.kitties[pidx].activity = theirs;
                    world.kitties[pidx].activity_clock = Some(clock);
                    Some(mine)
                } else {
                    None
                }
            }
            ActivitySpec::PlayCritter(c) => {
                critters
                    .get(c % critters.len().max(1))
                    .map(|&id| Activity::Playing {
                        target: Some(TargetRef::Element { id }),
                    })
            }
        };
        if let Some(activity) = activity {
            let idx = world.kitty_index(ids[i]).unwrap();
            world.kitties[idx].activity = activity;
            world.kitties[idx].activity_clock = Some(clock);
        }
    }
    world
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(48))]

    #[test]
    fn the_mask_is_a_pure_oracle_and_never_all_zero(spec in arb_world_spec()) {
        let config = Config::default();
        let world = build_world(&spec, &config);
        assert_mask_matches_engine(&world, &config);
    }
}

// ---- the four named crowded-continuation constructions ------------------
//
// Each puts the activity's referenced entity at the losing end of the
// nearest-K tie-break (three crowders with smaller ids at equal or smaller
// distance), starts the clock fresh (inside the minimum), and asserts the
// exact continuation is masked in — the corner target-priority exists for.

/// Five kitties: me (id 1) at the center, three crowders (ids 3, 4, 5) on
/// three neighboring tiles, the referenced friend LAST in every tie-break
/// (id 9) on the fourth. Nearest-3 by (distance, id) would pick the
/// crowders and crowd the friend out.
fn crowded_base(config: &Config) -> World {
    let mut world = World::generate(config);
    world.tick = 10;
    world.kitties.retain(|k| k.id == 1);
    for (id, x, y) in [(3u32, 15u32, 16u32), (4, 17, 16), (5, 16, 15), (9, 16, 17)] {
        world.kitties.push(Kitty::new(
            id,
            format!("K{id}"),
            Position::new(x, y),
            "needs_driven",
        ));
    }
    world.kitties.sort_by_key(|k| k.id);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].pos = Position::new(16, 16);
    world
}

fn assert_continuation_masked_in(world: &World, config: &Config, expected: &str) {
    let snapshot = world.snapshot();
    let obs_cfg = ObservationConfig::default();
    let codec = ActionCodec::v1(&obs_cfg);
    let table = TargetTable::build(&snapshot, 1, &obs_cfg);
    let mask = legal_action_mask(&snapshot, 1, &table, &codec, config);

    assert!(
        mask.iter().any(|&b| b),
        "{expected}: all-zero mask — the crowded-continuation corner is open"
    );
    // And the engine agrees bit for bit (the oracle on the construction).
    assert_mask_matches_engine(world, config);

    // The mid-minimum mask is exactly the continuation.
    let me = snapshot.kitty(1).unwrap();
    let continuation = me.activity.continuation().expect("an activity is ongoing");
    let set: Vec<_> = (0..mask.len()).filter(|&i| mask[i]).collect();
    assert_eq!(
        set.len(),
        1,
        "{expected}: mid-minimum mask is one entry, got {set:?}"
    );
    assert_eq!(
        codec.decode(set[0], &table).unwrap(),
        continuation,
        "{expected}: the one masked-in entry is the exact continuation"
    );
}

#[test]
fn a_crowded_duet_keeps_its_continuation_expressible() {
    let config = Config::default();
    let mut world = crowded_base(&config);
    let clock = ActivityClock::start(world.tick);
    let me = world.kitty_index(1).unwrap();
    world.kitties[me].activity = Activity::Resting {
        with_friend: Some(9),
    };
    world.kitties[me].activity_clock = Some(clock);
    let partner = world.kitty_index(9).unwrap();
    world.kitties[partner].activity = Activity::Resting {
        with_friend: Some(1),
    };
    world.kitties[partner].activity_clock = Some(clock);

    assert_continuation_masked_in(&world, &config, "crowded duet");
}

#[test]
fn a_crowded_co_sleep_keeps_its_continuation_expressible() {
    // Co-sleep references without binding — exactly what duet_partner()
    // misses; keying target-priority on Activity::partner() covers it.
    let config = Config::default();
    let mut world = crowded_base(&config);
    let me = world.kitty_index(1).unwrap();
    world.kitties[me].activity = Activity::Sleeping {
        in_sunbeam: false,
        with_friend: Some(9),
    };
    world.kitties[me].activity_clock = Some(ActivityClock::start(world.tick));

    assert_continuation_masked_in(&world, &config, "crowded co-sleep");
}

#[test]
fn a_crowded_groom_keeps_its_continuation_expressible() {
    let config = Config::default();
    let mut world = crowded_base(&config);
    let me = world.kitty_index(1).unwrap();
    world.kitties[me].activity = Activity::Grooming { target: Some(9) };
    world.kitties[me].activity_clock = Some(ActivityClock::start(world.tick));

    assert_continuation_masked_in(&world, &config, "crowded groom");
}

#[test]
fn a_default_population_critter_cluster_keeps_an_ongoing_play_expressible() {
    // The corner reachable at the DEFAULT config (research.md R1): five
    // critters, four critter slots. Four bugs with small ids crowd close;
    // the played-with greeble (large id) sits adjacent but loses every
    // tie-break. Without target-priority the continuation Play{Element}
    // would be inexpressible mid-minimum.
    let config = Config::default();
    let mut world = crowded_base(&config);
    world.elements.retain(|e| !e.element_type().is_critter());
    for (id, x, y) in [
        (50u32, 15u32, 16u32),
        (51, 17, 16),
        (52, 16, 15),
        (53, 15, 15),
    ] {
        world.push_element(Element {
            id,
            kind: ElementKind::Bug,
            pos: Position::new(x, y),
            ttl: Some(500),
        });
    }
    world.push_element(Element {
        id: 900,
        kind: ElementKind::Greeble {
            heading: Direction::North,
        },
        pos: Position::new(16, 17),
        ttl: Some(500),
    });
    // The greeble's tile collides with kitty 9's home; move that kitty off.
    let k9 = world.kitty_index(9).unwrap();
    world.kitties[k9].pos = Position::new(20, 20);

    let me = world.kitty_index(1).unwrap();
    world.kitties[me].activity = Activity::Playing {
        target: Some(TargetRef::Element { id: 900 }),
    };
    world.kitties[me].activity_clock = Some(ActivityClock::start(world.tick));

    let snapshot = world.snapshot();
    let table = TargetTable::build(&snapshot, 1, &ObservationConfig::default());
    assert!(
        table.critters.contains(&Some(900)),
        "the played-with critter holds a slot: {:?}",
        table.critters
    );
    assert_continuation_masked_in(&world, &config, "critter cluster");
}
