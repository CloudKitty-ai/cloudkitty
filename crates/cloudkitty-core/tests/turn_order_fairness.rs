//! The Article V (as amended, spec 013) guarding property: kitties have a
//! fair and equal chance at turn order, reproducibly. This is the test half
//! of the v1.1.0 constitutional amendment ceremony (Article VI: an amended
//! article, its spec, and its guarding tests land together).

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::{BehaviorRegistry, World};

#[test]
fn every_kitty_gets_an_equal_shot_at_acting_first() {
    // 12,000 draws of the same permutation the tick applies. With k kitties,
    // fair means each leads ~12000/k times; the bounds sit > 6 standard
    // deviations out, so noise cannot trip this while any systematic
    // favoritism (id order scores 12000-or-0) fails instantly.
    let config = Arc::new(Config::default());
    let mut world = World::generate(&config);
    let kitty_count = world.kitties.len();

    const DRAWS: u64 = 12_000;
    let mut first_slot: BTreeMap<u32, u64> = BTreeMap::new();
    let mut every_position: BTreeMap<(u32, usize), u64> = BTreeMap::new();
    for _ in 0..DRAWS {
        let order = world.draw_turn_order();
        *first_slot.entry(order[0]).or_insert(0) += 1;
        for (position, id) in order.iter().enumerate() {
            *every_position.entry((*id, position)).or_insert(0) += 1;
        }
    }

    let expected = DRAWS / kitty_count as u64;
    let p = 1.0 / kitty_count as f64;
    let sigma = (DRAWS as f64 * p * (1.0 - p)).sqrt();
    let tolerance = (6.0 * sigma).ceil() as u64;
    for kitty in &world.kitties {
        let led = first_slot.get(&kitty.id).copied().unwrap_or(0);
        assert!(
            led.abs_diff(expected) <= tolerance,
            "{} led {led} of {DRAWS} draws (expected {expected} ± {tolerance}): \
             the turn order is playing favorites",
            kitty.name
        );
        // And no kitty is ever locked out of any position.
        for position in 0..kitty_count {
            assert!(
                every_position
                    .get(&(kitty.id, position))
                    .copied()
                    .unwrap_or(0)
                    > 0,
                "{} never appeared in turn-order position {position}",
                kitty.name
            );
        }
    }
}

#[test]
fn the_fair_order_is_reproducible() {
    // "Equal, reproducible chance": two worlds from the same seed draw the
    // same orders forever -- fairness never costs determinism.
    let config = Arc::new(Config::default());
    let mut a = World::generate(&config);
    let mut b = World::generate(&config);
    for _ in 0..500 {
        assert_eq!(a.draw_turn_order(), b.draw_turn_order());
    }
}

#[tokio::test]
async fn the_tick_runs_whole_under_fair_order() {
    // The draw is exercised in place: real ticks, invariants asserting every
    // tick, no panic across a healthy stretch of world time.
    let config = Arc::new(Config::default());
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    for _ in 0..500 {
        world.tick(&registry, &config).await;
    }
    assert_eq!(world.tick, 500);
}
