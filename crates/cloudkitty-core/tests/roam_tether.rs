//! Spec 039: the roam-cell tether, runtime behavior.
//!
//! Confinement (SC-001), cadence and draw preservation (SC-003),
//! greeble non-interference (FR-004), seed determinism, geometry
//! generality (US2), and old-save adoption (FR-007). Every test fn
//! carries a `roam_` prefix so quickstart §1's filter finds it.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::action::{Action, TargetRef};
use cloudkitty_core::element::{Element, ElementId, ElementKind};
use cloudkitty_core::grid::{same_roam_cell, Position};
use cloudkitty_core::seam::JointProposal;
use cloudkitty_core::{BehaviorRegistry, Config, World};

const CELL: u32 = 4;

fn tethered_config(width: u32, height: u32, seed: u64) -> Arc<Config> {
    let mut config = Config::default();
    config.world.width = width;
    config.world.height = height;
    config.world.seed = seed;
    config.elements.bug.roam_cell = Some(CELL);
    // The default roster is placed for the default world; re-seat it inside
    // whatever geometry this test asked for.
    let spots = [(2, 2), (width - 3, 2), (2, height - 3), (width - 3, height - 3), (width / 2, height / 2)];
    for (kitty, &(x, y)) in config.kitties.iter_mut().zip(spots.iter()) {
        kitty.x = x;
        kitty.y = y;
    }
    config.validate().expect("tethered config is valid");
    Arc::new(config)
}

fn run(
    config: &Arc<Config>,
    ticks: u64,
    mut observe: impl FnMut(&World),
) -> World {
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    for _ in 0..ticks {
        runtime.block_on(world.tick(&registry, config));
        observe(&world);
    }
    world
}

/// SC-001: over full lifetimes across many seeds, no bug ever stands
/// outside the cell it was first seen in. Birth position is recorded the
/// first tick an element id appears; ids are never reused within a run.
#[test]
fn roam_tether_confines_bugs_for_life() {
    for seed in 0..10u64 {
        let config = tethered_config(20, 20, 900_000 + seed);
        let mut births: BTreeMap<ElementId, Position> = BTreeMap::new();
        run(&config, 2_000, |world| {
            for el in world.elements.iter() {
                if !matches!(el.kind, ElementKind::Bug) {
                    continue;
                }
                let birth = *births.entry(el.id).or_insert(el.pos);
                assert!(
                    same_roam_cell(birth, el.pos, CELL),
                    "seed {seed}: bug {} born {birth:?} escaped to {:?} at tick {}",
                    el.id,
                    el.pos,
                    world.tick
                );
            }
        });
        // The run must actually have watched bugs (ttl 300 default: several
        // generations in 2000 ticks).
        assert!(births.len() >= 3, "seed {seed}: too few bugs observed");
    }
}

/// SC-003, the observable form: a bug's position never changes on a tick
/// its schedule says it rests (`bug_moves_this_tick` untouched by the
/// tether), a moving tick advances it at most one tile (no redraw can
/// manufacture a second step), and the tether does not freeze the
/// population (bugs still actually move).
#[test]
fn roam_cadence_attempts_match_schedule() {
    let config = tethered_config(20, 20, 424_242);
    let mut last: BTreeMap<ElementId, (Position, u64)> = BTreeMap::new();
    let mut moves = 0u64;
    run(&config, 2_000, |world| {
        for el in world.elements.iter() {
            if !matches!(el.kind, ElementKind::Bug) {
                continue;
            }
            if let Some((prev, prev_tick)) = last.get(&el.id) {
                if *prev_tick + 1 == world.tick && *prev != el.pos {
                    // `self.tick += 1` lands AFTER the environment phase
                    // (world.rs:374), so movement observed at world.tick was
                    // computed against the schedule at world.tick - 1.
                    assert!(
                        el.bug_moves_this_tick(world.tick - 1),
                        "bug {} moved into tick {} which its schedule rests",
                        el.id,
                        world.tick
                    );
                    assert_eq!(
                        prev.manhattan_distance(&el.pos),
                        1,
                        "bug {} jumped more than one tile in one tick",
                        el.id
                    );
                    moves += 1;
                }
            }
            last.insert(el.id, (el.pos, world.tick));
        }
    });
    assert!(moves > 100, "the tether froze the bugs: {moves} moves in 2000 ticks");
}

/// FR-004: the tether binds bugs only. Greebles under a bug tether still
/// range across cell boundaries exactly as before.
#[test]
fn roam_greebles_stay_free_range() {
    let config = tethered_config(20, 20, 77_777);
    let mut births: BTreeMap<ElementId, Position> = BTreeMap::new();
    let mut escaped = false;
    run(&config, 1_000, |world| {
        for el in world.elements.iter() {
            if !matches!(el.kind, ElementKind::Greeble { .. }) {
                continue;
            }
            let birth = *births.entry(el.id).or_insert(el.pos);
            if !same_roam_cell(birth, el.pos, CELL) {
                escaped = true;
            }
        }
    });
    assert!(
        escaped,
        "no greeble ever left its birth cell in 1000 ticks — the tether is leaking onto greebles"
    );
}

/// US2: ragged geometry at runtime. On 26×26 with 4-cells the far edges
/// are 2-wide remainder strips; bugs born there confine to those smaller
/// cells by the same rule, no special case. The test also proves the
/// remainder region actually got exercised — silent non-coverage would
/// otherwise read as a pass.
#[test]
fn roam_ragged_world_confines_remainder_cells_too() {
    let mut remainder_births = 0u32;
    for seed in 0..10u64 {
        let config = tethered_config(26, 26, 660_000 + seed);
        let mut births: BTreeMap<ElementId, Position> = BTreeMap::new();
        run(&config, 2_000, |world| {
            for el in world.elements.iter() {
                if !matches!(el.kind, ElementKind::Bug) {
                    continue;
                }
                let birth = *births.entry(el.id).or_insert(el.pos);
                assert!(
                    same_roam_cell(birth, el.pos, CELL),
                    "seed {seed}: bug {} born {birth:?} escaped to {:?}",
                    el.id,
                    el.pos
                );
            }
        });
        remainder_births += births
            .values()
            .filter(|p| p.x >= 24 || p.y >= 24)
            .count() as u32;
    }
    assert!(
        remainder_births >= 1,
        "no bug was ever born in a remainder strip across 10 seeds — the geometry case went untested"
    );
}

/// US2 scenario 3: a cell larger than the world means the whole world is
/// one cell — behavior indistinguishable from unbounded. The freedom
/// signal: some bug leaves the 4-cell of its birth, which a 4-tether
/// would forbid.
#[test]
fn roam_cell_larger_than_world_is_no_tether_at_all() {
    let mut config = Config::default();
    config.world.width = 20;
    config.world.height = 20;
    config.world.seed = 31_337;
    config.elements.bug.roam_cell = Some(64);
    let spots = [(2, 2), (17, 2), (2, 17), (17, 17), (10, 10)];
    for (kitty, &(x, y)) in config.kitties.iter_mut().zip(spots.iter()) {
        kitty.x = x;
        kitty.y = y;
    }
    config.validate().expect("world-sized cell is legal");
    let config = Arc::new(config);
    let mut births: BTreeMap<ElementId, Position> = BTreeMap::new();
    let mut roamed_freely = false;
    run(&config, 2_000, |world| {
        for el in world.elements.iter() {
            if !matches!(el.kind, ElementKind::Bug) {
                continue;
            }
            let birth = *births.entry(el.id).or_insert(el.pos);
            assert!(
                same_roam_cell(birth, el.pos, 64),
                "impossible: left a cell larger than the world"
            );
            if !same_roam_cell(birth, el.pos, CELL) {
                roamed_freely = true;
            }
        }
    });
    assert!(
        roamed_freely,
        "no bug ever left a 4-cell under a 64-cell config — the tether is tighter than configured"
    );
}

/// FR-007: a pre-039 save loads without migration and its bugs adopt the
/// tether from the cell they stand in at load. The "pre-039 world" is a
/// flag-absent run of this engine — which the golden digest proves is the
/// pre-039 engine bit-for-bit — serialized mid-life, then resumed under
/// the tether config.
#[test]
fn roam_old_save_adopts_the_tether_at_load_position() {
    // A flag-absent world, run long enough that bugs are scattered.
    let mut untethered = Config::default();
    untethered.world.seed = 55_555;
    untethered.validate().expect("default-shaped config is valid");
    let untethered = Arc::new(untethered);
    let saved = run(&untethered, 500, |_| {});
    let snapshot = serde_json::to_string(&saved).expect("world serializes");

    // The tether config differs only in elements — the resume gate's
    // fingerprint must not move (w/h/seed/kitty-ids only).
    let mut tethered = (*untethered).clone();
    tethered.elements.bug.roam_cell = Some(CELL);
    tethered.elements.bug.ttl = Some(600);
    tethered.elements.greeble.ttl = Some(600);
    tethered.validate().expect("the served package is valid");
    assert_eq!(
        untethered.fingerprint(),
        tethered.fingerprint(),
        "the tether package moved the save-compatibility fingerprint"
    );

    // Resume the old world under the new config: no migration, and every
    // pre-existing bug confines from its LOAD position, mid-life.
    let mut world: World = serde_json::from_str(&snapshot).expect("old save loads unchanged");
    let load_positions: BTreeMap<ElementId, (Position, Option<u64>)> = world
        .elements
        .iter()
        .filter(|el| matches!(el.kind, ElementKind::Bug))
        .map(|el| (el.id, (el.pos, el.ttl)))
        .collect();
    assert!(!load_positions.is_empty(), "the saved world has bugs to adopt");

    let tethered = Arc::new(tethered);
    let registry = BehaviorRegistry::with_builtins();
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    for step in 1..=100u64 {
        runtime.block_on(world.tick(&registry, &tethered));
        for el in world.elements.iter() {
            let Some((load_pos, load_ttl)) = load_positions.get(&el.id) else {
                continue; // born after the load: US1's ordinary case
            };
            assert!(
                same_roam_cell(*load_pos, el.pos, CELL),
                "loaded bug {} left its load-position cell",
                el.id
            );
            // Its countdown continues uninterrupted: the old ttl keeps
            // draining; the new 600 applies to respawns only.
            if let (Some(t0), Some(t)) = (load_ttl, el.ttl) {
                assert_eq!(*t0 - step, t, "loaded bug {} ttl jumped", el.id);
            }
        }
    }
}

/// Article V under the tether: same seed, same config, same world —
/// bit-for-bit after 5000 ticks.
#[test]
fn roam_same_seed_same_world() {
    let config = tethered_config(20, 20, 13_131);
    let a = run(&config, 5_000, |_| {});
    let b = run(&config, 5_000, |_| {});
    assert_eq!(
        serde_json::to_string(&a).unwrap(),
        serde_json::to_string(&b).unwrap(),
        "tethered evolution is not deterministic"
    );
}

// ---- Spec 039 fallback amendment: the final pounce (FR-011/FR-012) ----

/// A surgical chase scenario: the hunter at `cat`, one bug at `bug`,
/// everyone else parked in the far corner, and the hunter's proposal is
/// exactly Chase(that bug). Returns the hunter's position after one tick.
fn pounce_chase_tick(pounce: bool, cat: (u32, u32), bug: (u32, u32), blocker: Option<(u32, u32)>) -> Position {
    let mut config = Config::default();
    config.world.seed = 5_150;
    config.behavior.pounce = pounce;
    let mut spots = [cat, (18, 18), (16, 18), (18, 16), (16, 16)];
    if let Some(b) = blocker {
        spots[1] = b;
    }
    for (kitty, &(x, y)) in config.kitties.iter_mut().zip(spots.iter()) {
        kitty.x = x;
        kitty.y = y;
    }
    config.validate().expect("pounce scenario config is valid");
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    world.elements.clear();
    world.elements.push(Element {
        id: 9_999,
        kind: ElementKind::Bug,
        pos: Position::new(bug.0, bug.1),
        ttl: None,
    });
    let hunter = world.kitties[0].id;
    let proposals = JointProposal::from_actions([(
        hunter,
        Action::Chase(TargetRef::Element { id: 9_999 }),
    )]);
    world.tick_with_proposals(&proposals, &config);
    world.kitties[0].pos
}

#[test]
fn roam_pounce_closes_from_distance_three() {
    // (a) FR-011: step (5,5)->(6,5), post-step distance 2, pounce ->(7,5).
    assert_eq!(
        pounce_chase_tick(true, (5, 5), (8, 5), None),
        Position::new(7, 5)
    );
}

#[test]
fn roam_pounce_never_steps_past_adjacency() {
    // (b) distance 2 start: step to adjacency, and the pounce must NOT
    // fire at post-step distance 1.
    assert_eq!(
        pounce_chase_tick(true, (6, 5), (8, 5), None),
        Position::new(7, 5)
    );
}

#[test]
fn roam_pounce_does_not_fire_from_distance_four() {
    // (c) post-step distance 3: a single ordinary step, no lunge.
    assert_eq!(
        pounce_chase_tick(true, (4, 5), (8, 5), None),
        Position::new(5, 5)
    );
}

#[test]
fn roam_pounce_never_fires_on_kitty_targets() {
    // (d) the owner's elements-only ruling. Hunter at (5,5) chases the
    // kitty parked at (8,5): one step only, whatever the distance.
    let mut config = Config::default();
    config.world.seed = 5_151;
    config.behavior.pounce = true;
    let spots = [(5, 5), (8, 5), (16, 18), (18, 16), (16, 16)];
    for (kitty, &(x, y)) in config.kitties.iter_mut().zip(spots.iter()) {
        kitty.x = x;
        kitty.y = y;
    }
    config.validate().expect("kitty-chase config is valid");
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let hunter = world.kitties[0].id;
    let quarry = world.kitties[1].id;
    let proposals = JointProposal::from_actions([(
        hunter,
        Action::Chase(TargetRef::Kitty { id: quarry }),
    )]);
    world.tick_with_proposals(&proposals, &config);
    assert_eq!(world.kitties[0].pos, Position::new(6, 5));
}

#[test]
fn roam_pounce_blocked_lunge_is_lost() {
    // (e) a kitty stands on the lunge tile (7,5): the first step lands
    // (6,5), the pounce leg is blocked and simply lost — no routing, no
    // retreat, the cat holds at distance 2.
    assert_eq!(
        pounce_chase_tick(true, (5, 5), (8, 5), Some((7, 5))),
        Position::new(6, 5)
    );
}

#[test]
fn roam_pounce_off_is_todays_chase() {
    // (f) FR-012: flag off = the pre-pounce engine, single step.
    assert_eq!(
        pounce_chase_tick(false, (5, 5), (8, 5), None),
        Position::new(6, 5)
    );
}
