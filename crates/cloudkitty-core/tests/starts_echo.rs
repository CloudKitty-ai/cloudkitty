//! Spec 062 SC-006 (engine half): the provenance echo equals the world.
//!
//! bc-collect's meta echo comes from the same pure `starts::draw` the world
//! build uses; this pins the two against each other — every echoed (x, y)
//! equals the tick-0 world-state readback exactly, and every echoed
//! category equals an independent geometric classification of the position.
//! The meta.json field shapes themselves are contracts/provenance.md's and
//! are exercised live by quickstart.md §5.

use cloudkitty_core::config::{Config, KittyConfig, StartsConfig};
use cloudkitty_core::starts::{self, StartCategory};
use cloudkitty_core::world::World;

#[test]
fn the_draw_echo_equals_the_tick_zero_world_exactly() {
    for seed in [1u64, 20261016, 555] {
        let mut config = Config::default();
        config.world.width = 20;
        config.world.height = 16;
        config.world.seed = seed;
        config.starts = Some(StartsConfig {
            edge_ring_share: 0.25,
            corner_share: 0.05,
        });
        config.kitties = (1..=4u32)
            .map(|id| {
                let mut k = KittyConfig::new(id, format!("K{id}"), 0, 0, "needs_driven");
                k.x = None;
                k.y = None;
                k
            })
            .collect();
        // One pinned kitty so the echo's drawn=false arm is covered too.
        config.kitties[2].x = Some(10);
        config.kitties[2].y = Some(8);
        config.validate().unwrap();

        let echo = starts::draw(&config).unwrap();
        let world = World::generate(&config);
        assert_eq!(echo.len(), world.kitties.len());
        for s in &echo {
            let kitty = world
                .kitties
                .iter()
                .find(|k| k.id == s.kitty)
                .expect("echoed kitty exists at tick 0");
            assert_eq!(
                kitty.pos, s.position,
                "seed {seed}: echo for kitty {} disagrees with tick-0 state",
                s.kitty
            );
            // Independent classification, restated — not the draw's record.
            let on_x = s.position.x == 0 || s.position.x == config.world.width - 1;
            let on_y = s.position.y == 0 || s.position.y == config.world.height - 1;
            let independent = match (on_x, on_y) {
                (true, true) => StartCategory::Corner,
                (false, false) => StartCategory::Interior,
                _ => StartCategory::EdgeRing,
            };
            assert_eq!(s.category, independent, "seed {seed}, kitty {}", s.kitty);
        }
        let pinned = echo.iter().find(|s| s.kitty == 3).unwrap();
        assert!(!pinned.drawn, "the explicit kitty echoes drawn=false");
    }
}
