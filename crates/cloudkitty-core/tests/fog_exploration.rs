//! Spec 049 SC-012 as ruled 2026-09-03 (T088): a blind exploring cat first
//! sights a bowl ANYWHERE on the served 20×20 world within one tour. The
//! lattice serpentine tour is coverage-complete by construction
//! (`explore::tests::coverage_is_complete_by_construction`); this is the
//! behavioural proof over real ticks at r = 5 -- a bowl on every tile
//! outside the starting disc, the tour index spread over the cycle, every
//! trial sighted within one tour plus the approach, the worst printed. The
//! engine's advance rule (reach, or beside a held waypoint) is pinned
//! beside it. The per-step scenarios live with the behaviour
//! (`needs_driven.rs`), the lattice geometry with `explore.rs`.

use std::sync::Arc;

use cloudkitty_core::config::{Config, KittyConfig};
use cloudkitty_core::element::{Element, ElementKind, ElementType};
use cloudkitty_core::explore::Lattice;
use cloudkitty_core::kitty::memory_index;
use cloudkitty_core::test_support::{forget_everything, test_config};
use cloudkitty_core::{Action, BehaviorRegistry, JointProposal, NeedKind, Position, World};

const R: u32 = 5;
const W: u32 = 20;
const START: Position = Position { x: 10, y: 10 };
/// One tour of the 3×3 lattice at 20×20, r = 5, is 16 legs of 6–7 steps;
/// a bowl anywhere is in view from some waypoint, so the bound is the walk
/// from the start to the farthest waypoint on the cycle, well inside 120.
/// The bound SC-012 states (T088): the tour's cycle in steps (the Manhattan
/// legs between consecutive waypoints -- 104 for the 3×3 lattice at 20×20,
/// r = 5) plus the approach from anywhere to the first waypoint (< W + H).
/// A bowl anywhere is in view from some waypoint, so one cycle after the
/// approach sees it. The measured worst is printed beside the bound.
fn budget(lattice: &Lattice) -> u64 {
    let steps: u64 = (0..lattice.cycle_len())
        .map(|i| {
            lattice
                .waypoint(i)
                .manhattan_distance(&lattice.waypoint(i + 1)) as u64
        })
        .sum();
    steps + (W + W) as u64
}

/// Two cats far apart (no idle friend in view), kitty 1 the blind hungry
/// explorer at the centre of a 20×20 world at r = 5.
fn blind_world(seed: u64) -> (World, Arc<Config>) {
    let mut config = test_config();
    config.world.width = W;
    config.world.height = W;
    config.world.seed = 1000 + seed;
    config.vision.radius = R;
    config.kitties = vec![
        KittyConfig {
            id: 1,
            name: "Miso".into(),
            x: START.x,
            y: START.y,
            behavior: "needs_driven".into(),
            needs: None,
        },
        KittyConfig {
            id: 2,
            name: "Biscuit".into(),
            x: 0,
            y: 0,
            behavior: "needs_driven".into(),
            needs: None,
        },
    ];
    config.validate().unwrap();
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    // No bowl but the one each test places; hungry, but below the pressure
    // at which the safeguard (75) would drop a bowl beside the cat inside
    // the window -- the sighting must be exploration's own.
    world
        .elements
        .retain(|e| e.element_type() != ElementType::Chow);
    forget_everything(&mut world);
    let idx = world.kitty_index(1).unwrap();
    world.kitties[idx].needs.add(NeedKind::Eat, 55.0);
    (world, config)
}

fn bowl(pos: Position) -> Element {
    Element {
        id: 9000,
        kind: ElementKind::Chow { servings: 5 },
        pos,
        ttl: None,
    }
}

fn set_waypoint(world: &mut World, id: u32, index: u32) {
    let idx = world.kitty_index(id).unwrap();
    world.kitties[idx].explore_waypoint = index;
}

async fn first_sight(world: &mut World, config: &Arc<Config>, budget: u64) -> Option<u64> {
    let registry = BehaviorRegistry::with_builtins();
    for t in 1..=budget {
        world.tick(&registry, config).await;
        if world.kitty(1).unwrap().memory[memory_index(ElementType::Chow)].is_some() {
            return Some(t);
        }
    }
    None
}

#[tokio::test(flavor = "current_thread")]
async fn every_tile_is_sighted_within_one_tour() {
    let lattice = Lattice::for_world(W, W, R);
    let cycle = lattice.cycle_len();
    let candidates: Vec<Position> = (0..W)
        .flat_map(|x| (0..W).map(move |y| Position::new(x, y)))
        .filter(|t| !START.visible_from(t, R))
        .collect();
    let budget = budget(&lattice);
    assert_eq!(budget, 104 + 40, "16 legs of 6-7 steps, plus the approach");
    let mut worst = (0u64, Position::new(0, 0), 0u32);
    let mut sightings: Vec<u64> = Vec::new();
    // Every tile once, the start index spread over the cycle by tile; the
    // four corners and the centre-adjacent tile from EVERY start index.
    let mut runs: Vec<(Position, u32)> = candidates
        .iter()
        .map(|&t| (t, (t.x * 7 + t.y * 13) % cycle))
        .collect();
    for t in [
        Position::new(0, 0),
        Position::new(W - 1, 0),
        Position::new(0, W - 1),
        Position::new(W - 1, W - 1),
        Position::new(16, 10),
    ] {
        runs.extend((0..cycle).map(|i| (t, i)));
    }
    for (target, start) in runs {
        let (mut world, config) = blind_world(start as u64);
        set_waypoint(&mut world, 1, start);
        // The bowl takes the tile whatever stood there (one element per tile).
        world.elements.retain(|e| e.pos != target);
        world.push_element(bowl(target));
        let t = first_sight(&mut world, &config, budget)
            .await
            .unwrap_or_else(|| {
                panic!(
                    "bowl at {target:?} from tour index {start}: not sighted within {budget} ticks"
                )
            });
        sightings.push(t);
        if t > worst.0 {
            worst = (t, target, start);
        }
    }
    sightings.sort_unstable();
    let n = sightings.len();
    eprintln!(
        "SC-012: over {n} blind trials first sight worst {} ticks (bowl at {:?}, from index {}), median {}, mean {:.1}; bound {budget}",
        worst.0,
        worst.1,
        worst.2,
        sightings[n / 2],
        sightings.iter().sum::<u64>() as f64 / n as f64
    );
    assert!(worst.0 <= budget);
}

/// FR-023 (T088): the engine advances the tour index when the cat stands
/// on its waypoint, or beside it while another cat holds the tile; never
/// otherwise. Generation spreads the start by id and skips a waypoint the
/// cat is spawned on.
#[test]
fn the_engine_advances_the_tour_on_reach_and_beside_a_held_waypoint() {
    let lattice = Lattice::for_world(W, W, R);
    assert_eq!(lattice.waypoint(3), Position::new(16, 10));
    assert_eq!(lattice.waypoint(4), Position::new(10, 10));
    let (world, _) = blind_world(0);
    assert_eq!(
        world.kitty(1).unwrap().explore_waypoint,
        1,
        "id 1 starts at index 1"
    );
    assert_eq!(
        world.kitty(2).unwrap().explore_waypoint,
        2,
        "id 2 starts at index 2"
    );

    let idle_tick = |world: &mut World, config: &Arc<Config>| {
        let mut proposals = JointProposal::new();
        for k in &world.kitties {
            proposals.propose(k.id, Action::Idle);
        }
        world.tick_with_proposals(&proposals, config);
    };
    // Standing on (16, 10) with index 3: advances to 4.
    let (mut world, config) = blind_world(0);
    let i1 = world.kitty_index(1).unwrap();
    world.kitties[i1].pos = Position::new(16, 10);
    set_waypoint(&mut world, 1, 3);
    idle_tick(&mut world, &config);
    assert_eq!(
        world.kitty(1).unwrap().explore_waypoint,
        4,
        "reached: advanced"
    );
    // Beside (10, 10) while kitty 2 stands on it, index 4: advances to 5.
    let (mut world, config) = blind_world(0);
    let i1 = world.kitty_index(1).unwrap();
    world.kitties[i1].pos = Position::new(11, 10);
    let i2 = world.kitty_index(2).unwrap();
    world.kitties[i2].pos = Position::new(10, 10);
    set_waypoint(&mut world, 1, 4);
    idle_tick(&mut world, &config);
    assert_eq!(
        world.kitty(1).unwrap().explore_waypoint,
        5,
        "held waypoint, beside it: advanced"
    );
    // Beside (10, 10) with nobody on it: unchanged (the cat can still land).
    let (mut world, config) = blind_world(0);
    let i1 = world.kitty_index(1).unwrap();
    world.kitties[i1].pos = Position::new(11, 10);
    set_waypoint(&mut world, 1, 4);
    idle_tick(&mut world, &config);
    assert_eq!(
        world.kitty(1).unwrap().explore_waypoint,
        4,
        "not reached: unchanged"
    );
    // The cycle wraps.
    let (mut world, config) = blind_world(0);
    let i1 = world.kitty_index(1).unwrap();
    world.kitties[i1].pos = lattice.waypoint(15);
    set_waypoint(&mut world, 1, 15);
    idle_tick(&mut world, &config);
    assert_eq!(
        world.kitty(1).unwrap().explore_waypoint,
        0,
        "the cycle wraps"
    );
}

/// A cat spawned on its start waypoint is already past it (generation
/// advances once), so the first exploring step is never an idle.
#[test]
fn a_cat_spawned_on_its_waypoint_starts_past_it() {
    let mut config = test_config();
    config.world.width = W;
    config.world.height = W;
    config.vision.radius = R;
    config.kitties[0].id = 1;
    config.kitties[0].x = 10; // index 1 = (10, 3)
    config.kitties[0].y = 3;
    config.kitties[1].x = 0;
    config.kitties[1].y = 0;
    config.validate().unwrap();
    let world = World::generate(&Arc::new(config));
    assert_eq!(world.kitty(1).unwrap().explore_waypoint, 2);
}
