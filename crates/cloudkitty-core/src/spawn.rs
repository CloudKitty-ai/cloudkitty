//! Restocking the world.
//!
//! Two obligations live here. [`ensure_minimums`] keeps each element type at its
//! configured population. [`safeguard`] is Article I's promise: if a kitty's need
//! passes the safeguard threshold and nothing exists that could relieve it, the
//! world provides -- ignoring configured maximums, because a kitty's comfort
//! outranks an operator's tuning.

use crate::config::Config;
use crate::element::{Element, ElementKind, ElementType};
use crate::grid::Direction;
use crate::needs::NeedKind;
use crate::world::World;

/// Tops every element type back up to its configured minimum.
pub fn ensure_minimums(world: &mut World, config: &Config) {
    for kind in ElementType::ALL {
        let rule = config.elements.rule(kind);
        while world.count_of(kind) < rule.min {
            if !spawn_one(world, kind, config) {
                // No free tile: the obligation carries over to the next
                // environment phase rather than stacking elements.
                break;
            }
        }
    }
}

/// Article I's relief guarantee.
///
/// Only eating and drinking depend on a scarce resource; play is satisfied by any
/// critter or friend, cuddling by any friend (there are always at least two
/// kitties), bathing by self-grooming, and sleeping needs no element at all. So
/// those are the two needs this can ever have to act on.
pub fn safeguard(world: &mut World, config: &Config) {
    let threshold = config.thresholds.safeguard;

    for need in [NeedKind::Eat, NeedKind::Drink] {
        let Some(kind) = ElementType::for_need(need) else {
            continue;
        };
        let anyone_needs_it = world.kitties.iter().any(|k| k.needs.get(need) > threshold);
        if anyone_needs_it && world.count_of(kind) == 0 {
            // Deliberately past the configured maximum if it comes to that.
            spawn_one(world, kind, config);
        }
    }
}

/// Places one element of `kind` on a random free tile. Returns false when the world
/// has no room, in which case the caller should try again next phase.
fn spawn_one(world: &mut World, kind: ElementType, config: &Config) -> bool {
    let free = world.free_element_tiles();
    if free.is_empty() {
        return false;
    }
    let idx = world.rng.gen_range_u32(0, free.len() as u32) as usize;
    let pos = free[idx];
    let rule = config.elements.rule(kind);

    let element_kind = match kind {
        ElementType::Water => ElementKind::Water,
        ElementType::Chow => ElementKind::Chow {
            servings: rule.servings.unwrap_or(5).max(1),
        },
        ElementType::Bug => ElementKind::Bug,
        ElementType::Greeble => {
            let heading = *world
                .rng
                .choose(&Direction::ALL)
                .expect("Direction::ALL is never empty");
            ElementKind::Greeble { heading }
        }
        ElementType::Sunbeam => ElementKind::Sunbeam,
    };

    let id = world.allocate_element_id();
    world.elements.push(Element {
        id,
        kind: element_kind,
        pos,
        ttl: rule.ttl,
    });
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::{test_config, test_world};
    use crate::world::World;

    #[test]
    fn minimums_are_restored_after_a_wipe() {
        let config = test_config();
        let mut world = World::generate(&config);
        world.elements.clear();

        ensure_minimums(&mut world, &config);

        for kind in ElementType::ALL {
            assert!(
                world.count_of(kind) >= config.elements.rule(kind).min,
                "{kind:?} was not restocked"
            );
        }
    }

    #[test]
    fn spawning_never_exceeds_the_minimum_it_was_asked_for() {
        let config = test_config();
        let mut world = World::generate(&config);
        let before = world.count_of(ElementType::Water);
        ensure_minimums(&mut world, &config);
        assert_eq!(
            world.count_of(ElementType::Water),
            before,
            "already at minimum, nothing added"
        );
    }

    #[test]
    fn safeguard_provides_food_for_a_hungry_kitty() {
        let (mut world, config) = test_world();
        // Take away all the food, then make a kitty hungry enough to need it.
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Chow);
        assert_eq!(world.count_of(ElementType::Chow), 0);

        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx]
            .needs
            .add(NeedKind::Eat, config.thresholds.safeguard + 5.0);

        safeguard(&mut world, &config);

        assert!(
            world.count_of(ElementType::Chow) > 0,
            "Article I: relief must be provided"
        );
    }

    #[test]
    fn safeguard_provides_water_for_a_thirsty_kitty() {
        let (mut world, config) = test_world();
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Water);
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx]
            .needs
            .add(NeedKind::Drink, config.thresholds.safeguard + 5.0);

        safeguard(&mut world, &config);

        assert!(world.count_of(ElementType::Water) > 0);
    }

    #[test]
    fn safeguard_ignores_the_configured_maximum() {
        let (mut world, mut config) = test_world();
        // A world configured to hold no chow at all still has to feed a hungry cat.
        config.elements.chow.max = 1;
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Chow);

        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 99.0);
        safeguard(&mut world, &config);

        assert!(world.count_of(ElementType::Chow) >= 1);
    }

    #[test]
    fn safeguard_stays_quiet_when_nobody_is_in_need() {
        let (mut world, config) = test_world();
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Chow);
        // All needs are near zero in a fresh world.
        safeguard(&mut world, &config);
        assert_eq!(
            world.count_of(ElementType::Chow),
            0,
            "no need, no intervention"
        );
    }

    #[test]
    fn a_full_world_defers_spawning_rather_than_stacking() {
        let config = test_config();
        let mut world = World::generate(&config);

        // Fill every tile with water.
        world.elements.clear();
        for y in 0..world.height {
            for x in 0..world.width {
                let id = world.allocate_element_id();
                world.elements.push(Element {
                    id,
                    kind: ElementKind::Water,
                    pos: crate::grid::Position::new(x, y),
                    ttl: None,
                });
            }
        }

        let count_before = world.elements.len();
        ensure_minimums(&mut world, &config);
        assert_eq!(
            world.elements.len(),
            count_before,
            "no room means no spawn, not an overlapping one"
        );
    }
}
