//! Spec 024 US2 integration: the mirrored two-chaser fixture.
//!
//! Two cats chase past each other down one lane, each squarely blocking
//! the other's straight step — the head-on geometry that produced the
//! 2026-07-20 dance family. This suite pins the outcome that matters
//! operationally — the pass engages the sidestep and resolves promptly —
//! and the determinism of the whole affair. (An earlier mirrored-window
//! metric was dropped by the 2026-08-01 review: under sequential apply
//! the first mover always clears the second's lane, so a both-blocked
//! round can never occur and the metric could not fail.)

use std::sync::Arc;

use cloudkitty_core::action::{self, Action, TargetRef};
use cloudkitty_core::element::{Element, ElementKind};
use cloudkitty_core::grid::Position;
use cloudkitty_core::{Config, World};

/// Head-on lane: kitty 1 at (7,5) chasing a bug east at (12,5); kitty 2
/// at (8,5) chasing a bug west at (3,5). Each cat's straight step is the
/// other cat. Kitty 3 parks far away. Bugs are pushed directly and no
/// world tick runs, so the environment never moves them — the fixture is
/// pure apply-arm mechanics.
fn head_on_world() -> (World, Arc<Config>) {
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    world.elements.clear();
    let a = world.kitty_index(1).unwrap();
    world.kitties[a].pos = Position::new(7, 5);
    let b = world.kitty_index(2).unwrap();
    world.kitties[b].pos = Position::new(8, 5);
    let c = world.kitty_index(3).unwrap();
    world.kitties[c].pos = Position::new(28, 28);
    world.elements.push(Element {
        id: 801,
        kind: ElementKind::Bug,
        pos: Position::new(12, 5),
        ttl: None,
    });
    world.elements.push(Element {
        id: 802,
        kind: ElementKind::Bug,
        pos: Position::new(3, 5),
        ttl: None,
    });
    (world, config)
}

/// Drives both chases for `steps` applies each and returns the two
/// trajectories (positions after each round).
fn run(steps: usize) -> (Vec<Position>, Vec<Position>) {
    let (mut world, config) = head_on_world();
    let mut a_track = Vec::new();
    let mut b_track = Vec::new();
    for _ in 0..steps {
        action::apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 801 }),
            &config,
        );
        action::apply(
            &mut world,
            2,
            Action::Chase(TargetRef::Element { id: 802 }),
            &config,
        );
        a_track.push(world.kitty(1).unwrap().pos);
        b_track.push(world.kitty(2).unwrap().pos);
    }
    (a_track, b_track)
}

fn manhattan(p: Position, q: Position) -> u32 {
    p.manhattan_distance(&q)
}

#[test]
fn head_on_chasers_pass_each_other_promptly() {
    let (a_track, b_track) = run(1_000);
    let a_goal = Position::new(12, 5);
    let b_goal = Position::new(3, 5);

    // The fixture's premise must engage: cat 1's very first step east is
    // squarely blocked by cat 2, so round 0 has to be a perpendicular
    // arc off the lane — same column, different row.
    assert_eq!(
        a_track[0].x, 7,
        "cat 1's straight step was blocked; an arc keeps the column"
    );
    assert_ne!(
        a_track[0].y, 5,
        "cat 1's first move must be an arc off the lane, not a stall"
    );

    // The chases must actually resolve: both cats reach their bugs. (A
    // chase apply steps onto the target tile when it gets there; reaching
    // Manhattan <= 1 means the pounce landed for this fixture's purpose.)
    assert!(
        a_track.iter().any(|p| manhattan(*p, a_goal) <= 1),
        "cat 1 never got past its friend: the lane is still janked"
    );
    assert!(
        b_track.iter().any(|p| manhattan(*p, b_goal) <= 1),
        "cat 2 never got past its friend"
    );

    // ...and PROMPTLY (spec 024 tasks T012's intent, sharpened by the
    // 2026-08-01 review): the straight walk is 4 rounds (start distance
    // 5, done at Manhattan <= 1) and the passing maneuver adds an arc or
    // two, so a generous multiple still binds — a rule that livelocked
    // (the dance family) or retreated (the distance-1 orbit) would blow
    // it by an order of magnitude.
    let done = (0..a_track.len())
        .find(|&i| manhattan(a_track[i], a_goal) <= 1 && manhattan(b_track[i], b_goal) <= 1)
        .unwrap_or(a_track.len());
    assert!(
        done <= 24,
        "the pass took {done} rounds; head-on chasers must resolve promptly"
    );
}

#[test]
fn the_whole_encounter_replays_bit_identically() {
    // Article V: same seed, same arcs, same passing maneuver — every time.
    assert_eq!(run(300), run(300), "the encounter is seeded, not random");
}
