//! Spec 062 SC-003: the baseline stays attributable.
//!
//! A knob-on world and a knob-off world whose explicit starts equal the
//! drawn ones, same seed, run a full horizon: every readable surface is
//! byte-identical every tick — element history included. This is the
//! feature's load-bearing guarantee (FR-004): the start draw consumes a
//! domain-separated sub-stream, never the master world stream, so every
//! divergence in an A/B that touches the knob is attributable to the
//! starts themselves.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::config::{Config, KittyConfig, StartsConfig};
use cloudkitty_core::starts;
use cloudkitty_core::world::World;

const HORIZON: u64 = 300;

fn knob_on_config() -> Config {
    let mut config = Config::default();
    config.world.width = 20;
    config.world.height = 16;
    config.world.seed = 20261016;
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
    config.validate().expect("the knob-on config is valid");
    config
}

#[tokio::test(flavor = "current_thread")]
async fn knob_on_equals_knob_off_with_the_drawn_starts_explicit() {
    let on_config = knob_on_config();
    let drawn = starts::draw(&on_config).expect("the draw succeeds");

    // The knob-off twin: [starts] absent, every kitty pinned to its draw.
    let mut off_config = on_config.clone();
    off_config.starts = None;
    for kitty in &mut off_config.kitties {
        let s = drawn.iter().find(|s| s.kitty == kitty.id).unwrap();
        kitty.x = Some(s.position.x);
        kitty.y = Some(s.position.y);
    }
    off_config.validate().expect("the explicit twin is valid");

    let on_config = Arc::new(on_config);
    let off_config = Arc::new(off_config);
    let mut on = World::generate(&on_config);
    let mut off = World::generate(&off_config);

    let registry = BehaviorRegistry::with_builtins();
    for tick in 0..=HORIZON {
        let a = serde_json::to_string(&on.snapshot()).unwrap();
        let b = serde_json::to_string(&off.snapshot()).unwrap();
        assert_eq!(
            a, b,
            "tick {tick}: knob-on and explicit-equal worlds diverged -- the \
             start draw leaked into the master stream (FR-004)"
        );
        if tick < HORIZON {
            on.tick(&registry, &on_config).await;
            off.tick(&registry, &off_config).await;
        }
    }
    // The element history, not just the final frame: both logs drained the
    // same master stream, so the distress record must agree too.
    assert_eq!(
        serde_json::to_string(&on.distress.events().collect::<Vec<_>>()).unwrap(),
        serde_json::to_string(&off.distress.events().collect::<Vec<_>>()).unwrap(),
        "distress histories diverged across the horizon"
    );
}
