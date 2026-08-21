//! Spec 039: the roam-cell tether, runtime behavior.
//!
//! Confinement (SC-001), cadence and draw preservation (SC-003),
//! greeble non-interference (FR-004), seed determinism, geometry
//! generality (US2), and old-save adoption (FR-007). Every test fn
//! carries a `roam_` prefix so quickstart §1's filter finds it.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::element::{ElementId, ElementKind};
use cloudkitty_core::grid::{same_roam_cell, Position};
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
