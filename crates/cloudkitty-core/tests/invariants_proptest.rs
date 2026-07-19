//! The constitution's CI gate (Article VI).
//!
//! Randomized worlds, randomized -- and actively hostile -- behaviors, thousands of
//! ticks, with every guarantee in Articles I-III checked after every single one.
//! If this suite is green, no sequence of events any behavior can produce will hurt
//! a kitty.
//!
//! When it fails, proptest prints the seed and shrinks the case, and because the
//! engine is deterministic that seed reproduces the failure exactly.

use std::sync::Arc;

use cloudkitty_core::behavior::test_behaviors::{AlwaysInvalid, Chaos, QuietExternal};
use cloudkitty_core::config::{ElementRule, ElementsConfig, KittyConfig, WorldConfig};
use cloudkitty_core::element::ElementType;
use cloudkitty_core::{invariants, BehaviorRegistry, Config, NeedKind, World};
use proptest::prelude::*;

/// Every behavior a generated world may hand its kitties, including the ones that
/// lie and flail.
fn behavior_names() -> Vec<&'static str> {
    vec![
        "needs_driven",
        "playful",
        "always_invalid",
        "chaos",
        "quiet_external",
    ]
}

fn registry() -> BehaviorRegistry {
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register("always_invalid", Arc::new(AlwaysInvalid));
    registry.register("chaos", Arc::new(Chaos));
    registry.register("quiet_external", Arc::new(QuietExternal));
    registry
}

/// Builds a valid config from generated parameters.
fn build_config(
    width: u32,
    height: u32,
    seed: u64,
    behavior_picks: Vec<usize>,
    element_spread: u32,
) -> Config {
    let names = behavior_names();
    let kitties: Vec<KittyConfig> = behavior_picks
        .iter()
        .enumerate()
        .map(|(i, pick)| KittyConfig {
            id: i as u32 + 1,
            name: format!("Kitty{}", i + 1),
            // Unique, in-bounds starting tiles.
            x: (i as u32) % width,
            y: (i as u32) / width,
            behavior: names[pick % names.len()].to_string(),
            needs: None,
        })
        .collect();

    let hard_max = ElementsConfig::hard_max(width * height).max(1);
    let rule = |min: u32, ttl: Option<u64>, servings: Option<u32>| ElementRule {
        min: min.min(hard_max),
        max: (min + element_spread).min(hard_max).max(min.min(hard_max)),
        ttl,
        servings,
    };

    Config {
        world: WorldConfig {
            width,
            height,
            tick_ms: 800,
            seed,
            bind: "127.0.0.1:0".to_string(),
        },
        kitties,
        elements: ElementsConfig {
            water: rule(1, None, None),
            chow: rule(1, None, Some(3)),
            bug: rule(1, Some(60), None),
            greeble: rule(1, Some(40), None),
            sunbeam: rule(1, Some(80), None),
        },
        ..Config::default()
    }
}

/// Drives a world and asserts the constitution after every tick.
fn run_and_check(config: Config, ticks: u64) -> Result<(), TestCaseError> {
    prop_assert!(
        config.validate().is_ok(),
        "generated config should be valid: {:?}",
        config.validate()
    );

    let registry = registry();
    let config = Arc::new(config);
    let mut world = World::generate(&config);

    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");

    let starting_ids: Vec<u32> = world.kitties.iter().map(|k| k.id).collect();

    for _ in 0..ticks {
        runtime.block_on(world.tick(&registry, &config));

        // Article I, II and III, all at once.
        if let Err(violation) = invariants::check(&world, &config) {
            return Err(TestCaseError::fail(format!(
                "tick {}: {violation}",
                world.tick
            )));
        }

        // Article II, stated the blunt way: the same cats, every tick, forever.
        let ids: Vec<u32> = world.kitties.iter().map(|k| k.id).collect();
        prop_assert_eq!(&ids, &starting_ids, "a kitty was removed or reordered");

        // Article I in detail, beyond what `check` asserts.
        for kitty in &world.kitties {
            for kind in NeedKind::ALL {
                let value = kitty.needs.get(kind);
                prop_assert!(
                    (0.0..=100.0).contains(&value),
                    "{}'s {} need escaped its bounds: {value}",
                    kitty.name,
                    kind.as_str()
                );
            }
            prop_assert!(
                kitty.happiness >= config.happiness.floor,
                "{} sank below the happiness floor: {}",
                kitty.name,
                kitty.happiness
            );
            prop_assert!(
                kitty.happiness > 0.0,
                "happiness reached zero, which Article I forbids"
            );
        }
    }

    Ok(())
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(12))]

    /// Many different worlds, a few hundred ticks each: breadth of configuration.
    #[test]
    fn randomized_worlds_never_violate_the_constitution(
        width in 8u32..20,
        height in 8u32..20,
        seed in any::<u64>(),
        picks in prop::collection::vec(0usize..5, 2..6),
        spread in 0u32..3,
    ) {
        let config = build_config(width, height, seed, picks, spread);
        run_and_check(config, 900)?;
    }
}

/// Depth to match the breadth above: one world, ten thousand ticks, with hostile
/// advisors throughout. This is the run the spec asks for by name (SC-002).
#[test]
fn ten_thousand_ticks_with_adversarial_behaviors() {
    let mut config = build_config(
        16,
        16,
        0xC10D_C0FF_EE00_5EED,
        // One of each: sensible, playful, liar, flailer, and a well-behaved
        // external behavior.
        vec![0, 1, 2, 3, 4],
        2,
    );
    config.world.seed = 987_654_321;

    run_and_check(config, 10_000).expect("10,000 ticks must not violate the constitution");
}

/// The safeguard has to hold even when the world starts with nothing to eat or
/// drink and everyone is desperate.
#[test]
fn a_barren_world_provides_for_desperate_kitties() {
    let config = Arc::new(build_config(12, 12, 42, vec![0, 1], 1));
    let registry = registry();
    let mut world = World::generate(&config);

    // Strip the pantry bare and make everyone very hungry and thirsty.
    world
        .elements
        .retain(|e| !matches!(e.element_type(), ElementType::Chow | ElementType::Water));
    for kitty in &mut world.kitties {
        kitty.needs.add(NeedKind::Eat, 99.0);
        kitty.needs.add(NeedKind::Drink, 99.0);
    }

    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap();

    // One tick is all the world gets to make good on its promise.
    runtime.block_on(world.tick(&registry, &config));

    assert!(
        world.count_of(ElementType::Chow) > 0,
        "Article I: food must appear for a starving kitty"
    );
    assert!(
        world.count_of(ElementType::Water) > 0,
        "Article I: water must appear for a thirsty kitty"
    );
    invariants::check(&world, &config).expect("and the world remains lawful");
}

/// A world where every single kitty has a behavior that proposes only illegal
/// actions. Nothing should happen to any of them.
#[test]
fn a_world_of_liars_still_keeps_its_kitties_safe() {
    let mut config = build_config(10, 10, 7, vec![2, 2, 2], 1);
    config.world.seed = 555;
    run_and_check(config, 2_000).expect("hostile advisors cannot harm a kitty");
}
