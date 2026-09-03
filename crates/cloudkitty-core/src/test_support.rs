//! Fixtures shared by unit tests, the property suite, and integration tests.
//!
//! Public so the `tests/` directory (and anyone writing their own behavior) can
//! build a small, deterministic world without reinventing a config.

use std::sync::Arc;

use crate::action::TargetRef;
use crate::behavior::DecisionContext;
use crate::config::{Config, ElementRule, ElementsConfig, KittyConfig, VisionConfig, WorldConfig};
use crate::element::ElementType;
use crate::kitty::{Activity, KittyId};
use crate::rng::DecisionRng;
use crate::world::World;

/// Spec 009 SC-001: interactions happen only in orthogonal range (own tile +
/// four compass neighbours). Asserted on the scenes whose counterparts
/// cannot move mid-scene and so are soundly observable *after* the
/// environment phase: a Drinking kitty's water (permanent, stationary) and
/// a conscripted duet's partner (both clocked, both stationary).
///
/// Meals are deliberately *not* asserted here: a lawful meal can begin on a
/// bowl's last serving — the bowl is orthogonal at apply time, gets
/// consumed, expires in the same tick's environment phase, and
/// `ensure_minimums` may even drop a fresh bowl diagonal to the eater
/// before this observation runs. The meal-range rule is enforced at its
/// true seam — `validate` and `adjacent_stocked_chow` — and unit-tested
/// there.
///
/// Shared here (spec 014 review) so both long-run suites — the engine's
/// scenario tests and the welfare gate in `cloudkitty-rl` — assert the
/// same spatial law every tick.
pub fn assert_orthogonal_scenes(world: &World) {
    for kitty in world.kitties.iter() {
        match kitty.activity {
            Activity::Drinking => {
                let water_in_range = world.elements.iter().any(|e| {
                    e.element_type() == ElementType::Water
                        && kitty.pos.manhattan_distance(&e.pos) <= 1
                });
                assert!(
                    water_in_range,
                    "009 SC-001: {} is drinking with no water in orthogonal range at tick {}",
                    kitty.name, world.tick
                );
            }
            // Since spec 041 a rest reference is co-sleep-like: the partner
            // can lawfully step away, and the reference persists until the
            // rester's next service re-filters it -- so Resting, like
            // Sleeping, carries no every-tick adjacency law here. Social
            // play remains the one bound duet.
            Activity::Playing {
                target: Some(TargetRef::Kitty { id: friend }),
            } => {
                let partner_in_range = world
                    .kitties
                    .iter()
                    .any(|k| k.id == friend && kitty.pos.manhattan_distance(&k.pos) <= 1);
                assert!(
                    partner_in_range,
                    "009 SC-001: {}'s duet partner is out of orthogonal range at tick {}",
                    kitty.name, world.tick
                );
            }
            _ => {}
        }
    }
}

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
                roam_cell: None,
                dart: false,
            },
            chow: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: Some(5),
                roam_cell: None,
                dart: false,
            },
            bug: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(120),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            greeble: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(90),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            sunbeam: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(150),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            ..ElementsConfig::default()
        },
        // Spec 049 T080: this 16x16 stage and every test staged on it were
        // written under global vision; the world-covering radius (64 >=
        // any pair of tiles here) keeps them meaning what they meant. Fog
        // tests set their own radius (`config.vision.radius = 5`).
        vision: VisionConfig {
            radius: 64,
            memory_timeout_ticks: 0,
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
        // Through the fog view, like every real decision (spec 049 R1); the
        // test config pins a world-covering radius (see `test_config`).
        world: Arc::new(world.snapshot().fog_for(id, config.vision.radius)),
        rng: DecisionRng::from_seed(9876),
        config,
    }
}

/// Spec 049 FR-030: a 3.0 config states every section -- a fragment that
/// names only what a test is about no longer loads on its own. This
/// completes such a fragment over the serialised `Config::default()`:
/// tables merge recursively with the fragment's keys winning, and a
/// non-table value (the `[[kitty]]` roster included) replaces the default
/// wholesale. Tests of the parser itself (`deny_unknown_fields`, a missing
/// section named) must NOT use it -- the raw text is their subject.
pub fn complete_toml(fragment: &str) -> String {
    fn merge(base: &mut toml::Table, over: toml::Table) {
        for (key, value) in over {
            match (base.get_mut(&key), value) {
                (Some(toml::Value::Table(b)), toml::Value::Table(o)) => merge(b, o),
                (_, v) => {
                    base.insert(key, v);
                }
            }
        }
    }
    let mut merged = toml::Table::try_from(Config::default()).expect("the defaults serialise");
    let over: toml::Table = toml::from_str(fragment).expect("the fragment is valid TOML");
    merge(&mut merged, over);
    toml::to_string(&merged).expect("the merged table serialises")
}
