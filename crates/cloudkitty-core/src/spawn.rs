//! Restocking the world.
//!
//! Two obligations live here. [`ensure_minimums`] keeps each element type at its
//! configured population. [`safeguard`] is Article I's promise: if a kitty's need
//! passes the safeguard threshold and nothing exists that could relieve it, the
//! world provides -- ignoring configured maximums, because a kitty's comfort
//! outranks an operator's tuning.

use crate::config::Config;
use crate::element::{Element, ElementKind, ElementType};
use crate::grid::{Direction, Position};
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
    let pos = pick_spread_tile(world, kind, &free);
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

/// How many random candidate tiles a spawn considers before choosing.
const SPREAD_CANDIDATES: usize = 8;

/// Picks a spawn tile with a preference for open space, so the RNG cannot pile
/// every water tile into one corner of the map.
///
/// Best-of-N sampling: draw a handful of candidate tiles from the free list (all
/// randomness through the master RNG — Article V), then keep the one farthest
/// from the nearest element of the same type. This is a *preference*, never a
/// constraint: some candidate always wins, so a spawn — in particular an
/// Article I safeguard spawn — can never fail for want of a well-spread tile.
fn pick_spread_tile(world: &mut World, kind: ElementType, free: &[Position]) -> Position {
    debug_assert!(!free.is_empty());

    // Draw the candidates first, unconditionally, so the number of RNG draws per
    // spawn does not depend on world contents more than it must.
    let mut candidates = [free[0]; SPREAD_CANDIDATES];
    for slot in candidates.iter_mut() {
        let idx = world.rng.gen_range_u32(0, free.len() as u32) as usize;
        *slot = free[idx];
    }

    let same_type: Vec<Position> = world
        .elements
        .iter()
        .filter(|e| e.element_type() == kind)
        .map(|e| e.pos)
        .collect();

    // Nothing to spread away from: the first draw is a plain uniform pick.
    if same_type.is_empty() {
        return candidates[0];
    }

    best_spread(&candidates, &same_type)
}

/// The candidate whose nearest same-type neighbour is farthest away. Ties keep
/// the earliest-drawn candidate, so the outcome is fully determined by the draw
/// order and never by float or iteration quirks.
fn best_spread(candidates: &[Position], existing: &[Position]) -> Position {
    debug_assert!(!candidates.is_empty() && !existing.is_empty());
    let mut best = candidates[0];
    let mut best_gap = 0u32;
    for (i, candidate) in candidates.iter().enumerate() {
        let gap = existing
            .iter()
            .map(|p| candidate.chebyshev_distance(p))
            .min()
            .unwrap_or(u32::MAX);
        if i == 0 || gap > best_gap {
            best = *candidate;
            best_gap = gap;
        }
    }
    best
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
    fn best_spread_picks_the_candidate_farthest_from_its_kind() {
        use crate::grid::Position;
        let existing = vec![Position::new(0, 0), Position::new(1, 1)];
        let candidates = vec![
            Position::new(2, 2),   // gap 1 from (1,1)
            Position::new(10, 10), // gap 9 -- the winner
            Position::new(5, 5),   // gap 4
        ];
        assert_eq!(best_spread(&candidates, &existing), Position::new(10, 10));
    }

    #[test]
    fn best_spread_ties_keep_the_earliest_candidate() {
        use crate::grid::Position;
        let existing = vec![Position::new(0, 0)];
        let candidates = vec![
            Position::new(3, 3),
            Position::new(0, 3),
            Position::new(3, 0),
        ];
        // All three have gap 3; the first drawn wins, deterministically.
        assert_eq!(best_spread(&candidates, &existing), Position::new(3, 3));
    }

    #[test]
    fn spawned_elements_spread_out_rather_than_clustering() {
        // Pin every water tile the world starts with into one corner, then ask for
        // more. With spread sampling the newcomers should land well away from the
        // corner pile; a uniform pick would happily land beside it.
        let (mut world, mut config) = test_world();
        config.elements.water.min = 5;
        config.elements.water.max = 8;
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Water);
        for (i, pos) in [(0u32, 0u32), (1, 0), (0, 1)].iter().enumerate() {
            let id = world.allocate_element_id();
            world.elements.push(Element {
                id: id + i as u32,
                kind: ElementKind::Water,
                pos: crate::grid::Position::new(pos.0, pos.1),
                ttl: None,
            });
        }

        ensure_minimums(&mut world, &config); // tops up from 3 to 5

        let waters: Vec<_> = world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Water)
            .map(|e| e.pos)
            .collect();
        assert_eq!(waters.len(), 5);

        // The two new tiles must not have joined the corner cluster. (Seeded and
        // deterministic: this asserts the algorithm, not luck.)
        let corner = crate::grid::Position::new(0, 0);
        let newcomers: Vec<_> = waters
            .iter()
            .filter(|p| p.chebyshev_distance(&corner) > 1)
            .collect();
        assert_eq!(newcomers.len(), 2, "waters: {waters:?}");
        for p in newcomers {
            assert!(
                p.chebyshev_distance(&corner) >= 5,
                "new water at {p:?} landed too close to the existing cluster"
            );
        }
    }

    #[test]
    fn the_first_element_of_a_kind_is_a_plain_uniform_pick() {
        // No same-type elements to spread from: spawning must still work and must
        // not consult other kinds' positions.
        let (mut world, config) = test_world();
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Sunbeam);
        ensure_minimums(&mut world, &config);
        assert!(world.count_of(ElementType::Sunbeam) >= 1);
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
