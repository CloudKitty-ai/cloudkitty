//! Spec 058 SC-001: the size invariance the F-053 collapse motivated.
//! The same relative scene encoded at 20x20 and at 100x100 yields
//! identical spatial cells — bearing exact, both magnitudes equal —
//! because every spatial feature is Manhattan-decomposed under frozen
//! literals, never normalized by world dimensions. Observed RED under
//! the v5 encoder (dx/width differed across sizes) in the spec-058
//! pre-bump probe.

use std::sync::Arc;

use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;
use cloudkitty_rl::config::ObservationConfig;
use cloudkitty_rl::observe::{block_widths, encode_observation, offsets};

/// Encode observer 1 with friend 2 at the same relative offset in a
/// world of the given size; return the friend row's spatial cells and
/// the whole kitty-row block for the stronger full compare.
fn row_cells(size: u32, mx: u32) -> (Vec<f32>, Vec<f32>) {
    let mut c = test_config();
    c.world.width = size;
    c.world.height = size;
    c.kitties[0].x = mx;
    c.kitties[0].y = mx;
    c.kitties[1].x = mx + 2;
    c.kitties[1].y = mx + 1;
    c.validate().unwrap();
    let c = Arc::new(c);
    let mut w = World::generate(&c);
    w.elements.clear();
    cloudkitty_core::test_support::forget_everything(&mut w);
    let view = w.snapshot().fog_for(1, c.vision.radius);
    let obs = encode_observation(&view, 1, &c, &ObservationConfig::default());
    let base = offsets::SELF_BLOCK;
    (
        obs.values[base + 1..base + 5].to_vec(),
        obs.values[base..base + offsets::KITTY_SLOT].to_vec(),
    )
}

#[test]
fn the_same_relative_scene_encodes_identically_at_20_and_100() {
    let (spatial_20, row_20) = row_cells(20, 5);
    let (spatial_100, row_100) = row_cells(100, 50);
    assert_eq!(
        spatial_20, spatial_100,
        "bearing + both magnitudes are world-size-free (SC-001)"
    );
    assert_eq!(row_20, row_100, "the whole friend row is size-invariant");
    // And the cells are the ruled decomposition for dx=2, dy=1, d=3.
    assert_eq!(spatial_20[0], 2.0 / 3.0, "bearing-x = dx/d");
    assert_eq!(spatial_20[1], 1.0 / 3.0, "bearing-y = dy/d");
    assert_eq!(spatial_20[2], 3.0 / 40.0, "linear = d/40");
    assert_eq!(
        spatial_20[3],
        3.0f32.ln_1p() / 400f32.ln_1p(),
        "log = log1p(d)/log1p(400)"
    );
}

#[test]
fn wall_cells_are_absolute_tiles_not_fractions() {
    // A cat 5 tiles from the N and W walls reads the same wall cells at
    // both sizes (fractional position read 0.25 vs 0.05 — the
    // entanglement FR-003 removes). Order N/E/S/W; linear /40 only.
    let walls = |size: u32| {
        let mut c = test_config();
        c.world.width = size;
        c.world.height = size;
        c.kitties[0].x = 5;
        c.kitties[0].y = 5;
        c.validate().unwrap();
        let c = Arc::new(c);
        let mut w = World::generate(&c);
        w.elements.clear();
        let view = w.snapshot().fog_for(1, c.vision.radius);
        let obs = encode_observation(&view, 1, &c, &ObservationConfig::default());
        obs.values[offsets::SELF_WALLS..offsets::SELF_WALLS + 4].to_vec()
    };
    let w20 = walls(20);
    let w100 = walls(100);
    assert_eq!(w20[0], w100[0], "N: 5 tiles either way");
    assert_eq!(w20[3], w100[3], "W: 5 tiles either way");
    assert_eq!(w20[0], 5.0 / 40.0, "absolute tiles under /40");
    // E/S DO differ — they are real distances to different walls, which
    // is exactly the point: the edge is an entity at a distance, not a
    // fraction of an arbitrary map.
    assert_eq!(w20[1], 14.0 / 40.0, "E at 20x20");
    assert_eq!(w100[1], 1.0, "E at 100x100: 94 tiles clamps the linear cell");
    let _ = block_widths();
}
