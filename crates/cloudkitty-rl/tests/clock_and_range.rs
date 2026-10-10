//! Spec 058 SC-005 (no clock), FR-001a (no radius clamp), FR-012
//! (waypoint bearing). The clock red was observed under v5 in the
//! pre-bump probe (the last cell moved with episode_clock); the
//! overshoot and waypoint cells did not exist to test.

use std::sync::Arc;

use cloudkitty_core::explore::Lattice;
use cloudkitty_core::grid::Position;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::{encode_observation, offsets};

#[test]
fn a_stationary_world_encodes_identically_across_ticks() {
    // SC-005: no cell varies with time in a world where nothing happens
    // — scene age and staleness have nothing to age (idle cats, no
    // memory), so tick-shifting the SAME frozen state must encode
    // byte-identically. (encode_observation also takes no clock
    // argument any more; this pins the removal at the value level.)
    let c = Arc::new(test_config());
    let mut w = World::generate(&c);
    w.elements.clear();
    cloudkitty_core::test_support::forget_everything(&mut w);
    let view_now = w.snapshot().fog_for(1, c.vision.radius);
    w.tick += 500;
    let view_later = w.snapshot().fog_for(1, c.vision.radius);
    let a = encode_observation(&view_now, 1, &c, &ObservationConfig::default());
    let b = encode_observation(&view_later, 1, &c, &ObservationConfig::default());
    assert_eq!(a.values, b.values, "no cell varies with the tick alone (SC-005)");
}

#[test]
fn a_visible_friends_manhattan_distance_exceeds_the_euclidean_radius_unclamped() {
    // FR-001a: dx=2, dy=3 sits INSIDE a Euclidean r=4 disc (4+9=13 <=
    // 16) at Manhattan 5 > 4. The cells must carry 5, never a clamp at
    // r — this pin is what keeps a later "fix" from re-coupling the
    // distance cells to the vision geometry.
    let mut c = test_config();
    c.vision.radius = 4;
    c.kitties[0].x = 10;
    c.kitties[0].y = 10;
    c.kitties[1].x = 12;
    c.kitties[1].y = 13;
    c.validate().unwrap();
    let c = Arc::new(c);
    let mut w = World::generate(&c);
    w.elements.clear();
    cloudkitty_core::test_support::forget_everything(&mut w);
    let view = w.snapshot().fog_for(1, c.vision.radius);
    assert!(view.kitty(2).is_some(), "inside the Euclidean disc");
    let obs = encode_observation(&view, 1, &c, &ObservationConfig::default());
    let base = offsets::SELF_BLOCK;
    assert_eq!(obs.values[base], 1.0, "seen");
    assert_eq!(obs.values[base + 3], 5.0 / 40.0, "Manhattan 5 > r=4, unclamped");
    assert_eq!(
        obs.values[base + 4],
        5.0f32.ln_1p() / 400f32.ln_1p(),
        "log cell likewise"
    );
}

#[test]
fn waypoint_cells_carry_the_lattice_bearing_and_zero_on_arrival() {
    // FR-012: the cells equal the L1 unit bearing toward the exploration
    // tour's current waypoint, derived exactly as the exploration rule
    // derives its target; (0, 0) standing on it.
    let c = Arc::new(test_config());
    let mut w = World::generate(&c);
    w.elements.clear();
    cloudkitty_core::test_support::forget_everything(&mut w);
    let lattice = Lattice::for_world(c.world.width, c.world.height, c.vision.radius);
    let i = w.kitty_index(1).unwrap();
    let index = w.kitties[i].explore_waypoint;
    let wp = lattice.waypoint(index);

    // Off the waypoint: the L1 unit bearing toward it.
    let off = Position::new(wp.x + 3, wp.y.saturating_sub(1));
    let off = if off.in_bounds(c.world.width, c.world.height) {
        off
    } else {
        Position::new(wp.x.saturating_sub(3), wp.y + 1)
    };
    w.kitties[i].pos = off;
    let view = w.snapshot().fog_for(1, c.vision.radius);
    let obs = encode_observation(&view, 1, &c, &ObservationConfig::default());
    let dx = wp.x as f32 - off.x as f32;
    let dy = wp.y as f32 - off.y as f32;
    let d = dx.abs() + dy.abs();
    assert!(d > 0.0, "the probe stands off the waypoint");
    assert_eq!(obs.values[offsets::SELF_WAYPOINT], dx / d, "waypoint bearing-x");
    assert_eq!(obs.values[offsets::SELF_WAYPOINT + 1], dy / d, "waypoint bearing-y");

    // On the waypoint: (0, 0) — "stop" is a position fact, not a cell.
    w.kitties[i].pos = wp;
    let view = w.snapshot().fog_for(1, c.vision.radius);
    let obs = encode_observation(&view, 1, &c, &ObservationConfig::default());
    assert_eq!(obs.values[offsets::SELF_WAYPOINT], 0.0);
    assert_eq!(obs.values[offsets::SELF_WAYPOINT + 1], 0.0);
}
