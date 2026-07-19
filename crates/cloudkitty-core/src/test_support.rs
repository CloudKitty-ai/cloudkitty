//! Fixtures shared by unit tests, the property suite, and integration tests.
//!
//! Public so the `tests/` directory (and anyone writing their own behavior) can
//! build a small, deterministic world without reinventing a config.

use std::sync::Arc;

use crate::behavior::DecisionContext;
use crate::config::{Config, ElementRule, ElementsConfig, KittyConfig, WorldConfig};
use crate::kitty::KittyId;
use crate::rng::DecisionRng;
use crate::world::World;

/// A compact 16x16 world with two contrasting cats. Small enough to reason about,
/// large enough to be legal (>= 32 tiles).
pub fn test_config() -> Config {
    Config {
        world: WorldConfig {
            width: 16,
            height: 16,
            tick_ms: 800,
            seed: 1234,
            bind: "127.0.0.1:0".to_string(),
        },
        kitties: vec![
            KittyConfig {
                id: 1,
                name: "Miso".into(),
                x: 3,
                y: 3,
                behavior: "needs_driven".into(),
                needs: None,
            },
            KittyConfig {
                id: 2,
                name: "Biscuit".into(),
                x: 12,
                y: 12,
                behavior: "playful".into(),
                needs: None,
            },
        ],
        elements: ElementsConfig {
            water: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: None,
            },
            chow: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: Some(5),
            },
            bug: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(120),
                servings: None,
            },
            greeble: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(90),
                servings: None,
            },
            sunbeam: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(150),
                servings: None,
            },
        },
        ..Config::default()
    }
}

/// A freshly generated world plus the config that made it.
pub fn test_world() -> (World, Config) {
    let config = test_config();
    debug_assert!(config.validate().is_ok(), "the test config must be valid");
    let world = World::generate(&config);
    (world, config)
}

/// Builds a decision context for kitty 1 after applying `setup` to the world.
pub fn decision_context(setup: impl FnOnce(&mut World)) -> DecisionContext {
    decision_context_for(1, setup)
}

pub fn decision_context_for(id: KittyId, setup: impl FnOnce(&mut World)) -> DecisionContext {
    let config = Arc::new(test_config());
    let mut world = World::generate(&config);
    setup(&mut world);
    let me = world
        .kitty(id)
        .expect("the requested kitty exists in the test world")
        .clone();
    DecisionContext {
        me,
        world: Arc::new(world.snapshot()),
        rng: DecisionRng::from_seed(9876),
        config,
    }
}
