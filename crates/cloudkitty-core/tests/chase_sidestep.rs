//! Spec 024 US2 integration: the mirrored two-chaser fixture.
//!
//! Two cats chase past each other down one lane, each squarely blocking
//! the other's straight step — the head-on geometry that produced the
//! 2026-07-20 dance family. The sidestep's master-RNG draws are
//! successive stream values, so the two cats can never compute the same
//! arc from shared state; this suite pins the operational definition of
//! "never a sustained lockstep" and the determinism of the whole affair.

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
fn head_on_chasers_pass_each_other_without_a_sustained_lockstep() {
    let (a_track, b_track) = run(1_000);
    let a_goal = Position::new(12, 5);
    let b_goal = Position::new(3, 5);

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

    // The operational lockstep bound (spec 024 tasks T012): no window of
    // 8+ consecutive rounds in which both displacement vectors are mirror
    // images across the lane (dx_a == -dx_b, dy_a == dy_b) while neither
    // cat closes distance on its own target. Only rounds where both
    // chases are still live count — two cats parked on their caught bugs
    // are finished hunters, not dancers.
    let done = (1..a_track.len())
        .find(|&i| manhattan(a_track[i], a_goal) <= 1 && manhattan(b_track[i], b_goal) <= 1)
        .unwrap_or(a_track.len());
    let mut worst = 0usize;
    let mut streak = 0usize;
    for i in 1..done {
        let da = (
            a_track[i].x as i64 - a_track[i - 1].x as i64,
            a_track[i].y as i64 - a_track[i - 1].y as i64,
        );
        let db = (
            b_track[i].x as i64 - b_track[i - 1].x as i64,
            b_track[i].y as i64 - b_track[i - 1].y as i64,
        );
        let mirrored = da.0 == -db.0 && da.1 == db.1;
        let a_closed = manhattan(a_track[i], a_goal) < manhattan(a_track[i - 1], a_goal);
        let b_closed = manhattan(b_track[i], b_goal) < manhattan(b_track[i - 1], b_goal);
        if mirrored && !a_closed && !b_closed {
            streak += 1;
            worst = worst.max(streak);
        } else {
            streak = 0;
        }
    }
    assert!(
        worst < 8,
        "a {worst}-round mirrored stall is a dance; the draws must decorrelate"
    );
}

#[test]
fn the_whole_encounter_replays_bit_identically() {
    // Article V: same seed, same arcs, same passing maneuver — every time.
    assert_eq!(run(300), run(300), "the encounter is seeded, not random");
}
