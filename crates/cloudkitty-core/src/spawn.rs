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

/// Tops every element type back up to its configured minimum. Water
/// carries one extra obligation first: the guaranteed lake (spec 027).
pub fn ensure_minimums(world: &mut World, config: &Config) {
    ensure_lake(world, config);
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

/// The guaranteed lake (spec 027): a world whose water minimum can afford
/// it (>= 4) always holds at least one 2x2 all-water square. Runs before
/// the ordinary top-up so the square's tiles count toward the minimum;
/// below the threshold it is silently inactive, so sparse worlds — the
/// frozen scarcity exam runs a minimum of 1 — never gain a new way to
/// fail. Like every placement rule here, it is an obligation the world
/// meets when room allows and carries over when it does not: nothing is
/// ever evicted or stacked, and the Article I safeguard path is
/// untouched.
fn ensure_lake(world: &mut World, config: &Config) {
    if config.elements.water.min < 4 {
        return;
    }
    let water: Vec<Position> = world
        .elements
        .iter()
        .filter(|e| e.element_type() == ElementType::Water)
        .map(|e| e.pos)
        .collect();
    let is_water = |p: &Position| water.contains(p);
    let square = |x: u32, y: u32| {
        [
            Position::new(x, y),
            Position::new(x + 1, y),
            Position::new(x, y + 1),
            Position::new(x + 1, y + 1),
        ]
    };
    // Already holding a lake: the default world's steady state (permanent
    // water), checked once per environment phase.
    let complete = |x: u32, y: u32| square(x, y).iter().all(is_water);
    if water
        .iter()
        .any(|p| p.x + 1 < world.width && p.y + 1 < world.height && complete(p.x, p.y))
    {
        return;
    }

    // Valid anchors: 2x2 squares made only of water-or-free tiles. The
    // free list is the same source ordinary spawns draw from, so the
    // one-element-per-tile rule is inherited, not re-implemented.
    let free = world.free_element_tiles();
    let usable = |p: &Position| is_water(p) || free.contains(p);
    let mut anchors: Vec<Position> = Vec::new();
    // Every anchor overlapping existing water joins deterministically
    // (no RNG spent): a damaged lake is thereby always in the running,
    // so re-forming completes the survivor in place instead of building
    // a rival square elsewhere.
    for p in &water {
        for (ax, ay) in [
            (p.x.checked_sub(1), p.y.checked_sub(1)),
            (Some(p.x), p.y.checked_sub(1)),
            (p.x.checked_sub(1), Some(p.y)),
            (Some(p.x), Some(p.y)),
        ] {
            let (Some(ax), Some(ay)) = (ax, ay) else {
                continue;
            };
            if ax + 1 < world.width
                && ay + 1 < world.height
                && square(ax, ay).iter().all(usable)
                && !anchors.contains(&Position::new(ax, ay))
            {
                anchors.push(Position::new(ax, ay));
            }
        }
    }
    // Plus a sampled handful of fresh anchors, all randomness through
    // the master RNG (Article V). Draw count depends on config alone.
    let fresh: Vec<Position> = free
        .iter()
        .filter(|p| p.x + 1 < world.width && p.y + 1 < world.height)
        .filter(|p| square(p.x, p.y).iter().all(usable))
        .copied()
        .collect();
    if !fresh.is_empty() {
        for _ in 0..config.elements.spread_candidates {
            let idx = world.rng.gen_range_u32(0, fresh.len() as u32) as usize;
            if !anchors.contains(&fresh[idx]) {
                anchors.push(fresh[idx]);
            }
        }
    }
    if anchors.is_empty() {
        // No room anywhere: carry over, exactly like an unmet minimum.
        return;
    }

    // Fewest missing tiles first (completion beats construction), then
    // the interior preference — gated on the knob, so a zero penalty
    // leaves ties to draw order here as everywhere else.
    let on_edge =
        |p: &Position| p.x == 0 || p.y == 0 || p.x + 1 >= world.width || p.y + 1 >= world.height;
    let mut best = anchors[0];
    let mut best_key = (usize::MAX, usize::MAX);
    for (i, a) in anchors.iter().enumerate() {
        let missing = square(a.x, a.y).iter().filter(|p| !is_water(p)).count();
        let edge_tiles = if config.elements.edge_penalty > 0.0 {
            square(a.x, a.y).iter().filter(|p| on_edge(p)).count()
        } else {
            0
        };
        let key = (missing, edge_tiles);
        if i == 0 || key < best_key {
            best = *a;
            best_key = key;
        }
    }

    let rule = config.elements.rule(ElementType::Water);
    for pos in square(best.x, best.y) {
        if is_water(&pos) {
            continue;
        }
        let id = world.allocate_element_id();
        let ttl = rule.ttl.map(|base| jittered_ttl(world, base, config));
        world.elements.push(Element {
            id,
            kind: ElementKind::Water,
            pos,
            ttl,
        });
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
    let pos = pick_spread_tile(world, kind, &free, config);
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
    let ttl = rule.ttl.map(|base| jittered_ttl(world, base, config));
    world.elements.push(Element {
        id,
        kind: element_kind,
        pos,
        ttl,
    });
    true
}

/// Draws `base` ± the configured `[elements] ttl_jitter` uniformly through
/// the master RNG (Article V), floored at 1 so a base smaller than the
/// jitter can never spawn an already-expired element. The jitter exists so
/// a cohort born together never expires together -- restocking is
/// immediate, and without the stagger the whole population relocates in
/// one synchronized jump every cycle (owner observation 2026-07-23,
/// glaring at turbo speed on sunbeams, which nothing ever perturbs).
fn jittered_ttl(world: &mut World, base: u64, config: &Config) -> u64 {
    let jitter = config.elements.ttl_jitter;
    let offset = world.rng.gen_range_u32(0, 2 * jitter as u32 + 1) as u64;
    (base + offset).saturating_sub(jitter).max(1)
}

/// Picks a spawn tile with a preference for open space, so the RNG cannot pile
/// every water tile into one corner of the map.
///
/// Best-of-N sampling (N = `[elements] spread_candidates`): draw candidate
/// tiles from the free list (all randomness through the master RNG —
/// Article V), then keep the one farthest from the nearest element of the
/// same type, discounted by the interior preference (spec 027): a
/// perimeter candidate's score is docked `[elements] edge_penalty` tiles.
/// This is a *preference*, never a constraint: some candidate always wins,
/// so a spawn — in particular an Article I safeguard spawn — can never
/// fail for want of a well-spread or well-centered tile.
fn pick_spread_tile(
    world: &mut World,
    kind: ElementType,
    free: &[Position],
    config: &Config,
) -> Position {
    debug_assert!(!free.is_empty());

    // Draw the candidates first, unconditionally, so the number of RNG draws per
    // spawn does not depend on world contents more than it must.
    let mut candidates = vec![free[0]; config.elements.spread_candidates];
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

    best_spread(
        &candidates,
        &same_type,
        config.elements.edge_penalty,
        world.width,
        world.height,
    )
}

/// The candidate with the best score: nearest-same-type gap (equal for all
/// when there is nothing to spread from — absorbing what used to be an
/// early return), minus the edge penalty for perimeter tiles. Ties keep
/// the earliest-drawn candidate, so the outcome is fully determined by the
/// draw order and never by float or iteration quirks — and a zero penalty
/// reproduces the pre-027 selection exactly, draw for draw.
fn best_spread(
    candidates: &[Position],
    existing: &[Position],
    edge_penalty: f32,
    width: u32,
    height: u32,
) -> Position {
    debug_assert!(!candidates.is_empty());
    let mut best = candidates[0];
    let mut best_score = f32::NEG_INFINITY;
    for (i, candidate) in candidates.iter().enumerate() {
        let gap = if existing.is_empty() {
            0.0
        } else {
            existing
                .iter()
                .map(|p| candidate.chebyshev_distance(p))
                .min()
                .unwrap_or(u32::MAX) as f32
        };
        let on_edge = candidate.x == 0
            || candidate.y == 0
            || candidate.x + 1 >= width
            || candidate.y + 1 >= height;
        let score = gap - if on_edge { edge_penalty } else { 0.0 };
        if i == 0 || score > best_score {
            best = *candidate;
            best_score = score;
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
        // Penalty 0: the pre-027 selection, exactly.
        assert_eq!(
            best_spread(&candidates, &existing, 0.0, 32, 32),
            Position::new(10, 10)
        );
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
        assert_eq!(
            best_spread(&candidates, &existing, 0.0, 32, 32),
            Position::new(3, 3)
        );
    }

    #[test]
    fn the_edge_penalty_is_a_preference_that_zero_disables_exactly() {
        use crate::grid::Position;
        let existing = vec![Position::new(5, 5)];
        // The perimeter candidate has the better gap (5 vs 3).
        let candidates = vec![Position::new(0, 0), Position::new(8, 5)];
        // Penalty 0: gap wins, edge and all -- today's behavior.
        assert_eq!(
            best_spread(&candidates, &existing, 0.0, 10, 10),
            Position::new(0, 0)
        );
        // A penalty larger than the gap margin (5 - 3 = 2) flips it inward.
        assert_eq!(
            best_spread(&candidates, &existing, 3.0, 10, 10),
            Position::new(8, 5)
        );
        // ...but never into prohibition: an all-perimeter field still picks.
        let rim = vec![Position::new(0, 4), Position::new(9, 2)];
        assert_eq!(
            best_spread(&rim, &existing, 3.0, 10, 10),
            Position::new(0, 4),
            "equal penalties cancel; ties keep the earliest draw"
        );
    }

    #[test]
    fn without_kin_the_penalty_prefers_the_first_interior_draw() {
        use crate::grid::Position;
        // No same-type elements: gap is equal-for-all. At penalty 0 the
        // earliest draw wins (the pre-027 early return); with a penalty
        // the first interior candidate does.
        let candidates = vec![Position::new(0, 0), Position::new(4, 4)];
        assert_eq!(
            best_spread(&candidates, &[], 0.0, 10, 10),
            Position::new(0, 0)
        );
        assert_eq!(
            best_spread(&candidates, &[], 2.0, 10, 10),
            Position::new(4, 4)
        );
    }

    #[test]
    fn spawned_elements_spread_out_rather_than_clustering() {
        // Pin every chow bowl the world starts with into one corner, then ask
        // for more. With spread sampling the newcomers should land well away
        // from the corner pile; a uniform pick would happily land beside it.
        // (Chow, not water, since spec 027: water at min >= 4 owes a lake
        // first, which would legitimately *complete* the corner cluster --
        // the lake has its own tests. This one is about spread alone.)
        let (mut world, mut config) = test_world();
        config.elements.chow.min = 5;
        config.elements.chow.max = 8;
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Chow);
        for (i, pos) in [(0u32, 0u32), (1, 0), (0, 1)].iter().enumerate() {
            let id = world.allocate_element_id();
            world.elements.push(Element {
                id: id + i as u32,
                kind: ElementKind::Chow { servings: 5 },
                pos: crate::grid::Position::new(pos.0, pos.1),
                ttl: None,
            });
        }

        ensure_minimums(&mut world, &config); // tops up from 3 to 5

        let bowls: Vec<_> = world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Chow)
            .map(|e| e.pos)
            .collect();
        assert_eq!(bowls.len(), 5);

        // The two new tiles must not have joined the corner cluster. (Seeded and
        // deterministic: this asserts the algorithm, not luck.)
        let corner = crate::grid::Position::new(0, 0);
        let newcomers: Vec<_> = bowls
            .iter()
            .filter(|p| p.chebyshev_distance(&corner) > 1)
            .collect();
        assert_eq!(newcomers.len(), 2, "bowls: {bowls:?}");
        for p in newcomers {
            assert!(
                p.chebyshev_distance(&corner) >= 5,
                "new chow at {p:?} landed too close to the existing cluster"
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

    fn has_lake(world: &World) -> bool {
        let waters: Vec<_> = world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Water)
            .map(|e| e.pos)
            .collect();
        waters.iter().any(|p| {
            [(1, 0), (0, 1), (1, 1)]
                .iter()
                .all(|(dx, dy)| waters.iter().any(|q| q.x == p.x + dx && q.y == p.y + dy))
        })
    }

    #[test]
    fn every_well_watered_world_holds_a_lake() {
        // Spec 027 SC-001: at the engine defaults (water min 5 >= 4) every
        // seeded world contains a 2x2 all-water square.
        for seed in 0..50u64 {
            let mut config = Config::default();
            config.world.seed = seed;
            let world = World::generate(&config);
            assert!(has_lake(&world), "seed {seed} generated no lake");
        }
    }

    #[test]
    fn sparse_water_means_no_lake_and_no_error() {
        // The frozen scarcity exam's shape: water min 1. The guarantee is
        // silently inactive -- validation passes, generation succeeds.
        let (_, mut config) = test_world();
        config.elements.water.min = 1;
        config.elements.water.max = 3;
        config.validate().expect("sparse water validates");
        let world = World::generate(&config);
        assert!(
            world.count_of(ElementType::Water) >= 1,
            "the minimum is still honored"
        );
    }

    #[test]
    fn at_minimum_four_the_water_population_is_exactly_the_lake() {
        // The boundary: min == 4 means the lake IS the standing water.
        let (_, mut config) = test_world();
        config.elements.water.min = 4;
        config.elements.water.max = 6;
        let world = World::generate(&config);
        assert_eq!(world.count_of(ElementType::Water), 4);
        assert!(has_lake(&world));
    }

    #[test]
    fn a_damaged_lake_is_completed_in_place_not_rebuilt_elsewhere() {
        // Break one tile of a standing lake; the restock must complete the
        // survivor (water-adjacent anchors join the candidate set
        // deterministically), not raise a rival square elsewhere.
        let (mut world, mut config) = test_world();
        config.elements.water.min = 4;
        config.elements.water.max = 6;
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Water);
        for (i, (x, y)) in [(6u32, 6u32), (7, 6), (6, 7)].iter().enumerate() {
            world.elements.push(Element {
                id: 9800 + i as u32,
                kind: ElementKind::Water,
                pos: Position::new(*x, *y),
                ttl: None,
            });
        }
        ensure_minimums(&mut world, &config);
        let waters: Vec<_> = world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Water)
            .map(|e| e.pos)
            .collect();
        assert!(
            waters.contains(&Position::new(7, 7)),
            "the missing corner was filled in place: {waters:?}"
        );
        assert!(has_lake(&world));
    }

    #[test]
    fn a_full_board_defers_the_lake_without_evicting() {
        // No valid anchor anywhere: the obligation carries over, exactly
        // like an unmet minimum. Fill the board with chow, then ask.
        let (mut world, mut config) = test_world();
        config.elements.water.min = 4;
        config.elements.water.max = 6;
        world.elements.clear();
        for y in 0..world.height {
            for x in 0..world.width {
                let id = world.allocate_element_id();
                world.elements.push(Element {
                    id,
                    kind: ElementKind::Chow { servings: 5 },
                    pos: Position::new(x, y),
                    ttl: None,
                });
            }
        }
        let before = world.elements.len();
        ensure_minimums(&mut world, &config);
        assert_eq!(
            world.elements.len(),
            before,
            "no room: no lake, no eviction, no stacking"
        );
    }

    #[test]
    fn lakes_are_deterministic_per_seed() {
        let mut config = Config::default();
        config.world.seed = 42;
        let a = World::generate(&config);
        let b = World::generate(&config);
        let waters = |w: &World| {
            let mut v: Vec<_> = w
                .elements
                .iter()
                .filter(|e| e.element_type() == ElementType::Water)
                .map(|e| (e.pos.x, e.pos.y))
                .collect();
            v.sort_unstable();
            v
        };
        assert_eq!(waters(&a), waters(&b), "same seed, same lake, same water");
    }

    #[test]
    fn the_interior_preference_moves_the_aggregate_off_the_rim() {
        // Spec 027 SC-002: across a seeded sample at defaults, elements
        // sit on the perimeter well below its area share; with the
        // penalty at 0 the rim share rises back toward the area share.
        let share = |penalty: f32| {
            let mut on_rim = 0usize;
            let mut total = 0usize;
            for seed in 0..40u64 {
                let mut config = Config::default();
                config.world.seed = seed;
                config.elements.edge_penalty = penalty;
                let world = World::generate(&config);
                for e in &world.elements {
                    total += 1;
                    if e.pos.x == 0
                        || e.pos.y == 0
                        || e.pos.x + 1 >= world.width
                        || e.pos.y + 1 >= world.height
                    {
                        on_rim += 1;
                    }
                }
            }
            on_rim as f64 / total as f64
        };
        let with_penalty = share(2.0);
        let without = share(0.0);
        // 24x24 rim is ~16% of tiles. The penalty must push the share
        // clearly under the area share AND under the no-penalty regime.
        assert!(
            with_penalty < 0.16,
            "rim share {with_penalty:.3} not below the area share"
        );
        assert!(
            with_penalty < without,
            "penalty {with_penalty:.3} vs none {without:.3}: no movement"
        );
    }

    #[test]
    fn timed_spawns_stagger_their_ttls_instead_of_marching_in_lockstep() {
        // Owner call 2026-07-23: a cohort born together must not expire
        // together. Every timed spawn draws base ± TTL_JITTER, so even the
        // freshly generated world starts staggered.
        let mut config = test_config();
        config.elements.sunbeam.min = 10;
        config.elements.sunbeam.max = 12;
        config.elements.sunbeam.ttl = Some(300);
        let world = World::generate(&config);

        let ttls: Vec<u64> = world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Sunbeam)
            .map(|e| e.ttl.expect("sunbeams are timed"))
            .collect();
        assert_eq!(ttls.len(), 10);
        for ttl in &ttls {
            assert!((200..=400).contains(ttl), "ttl {ttl} outside base ± jitter");
        }
        assert!(
            ttls.iter().any(|t| t != &ttls[0]),
            "ten draws all identical: the jitter is not being applied"
        );
    }

    #[test]
    fn a_ttl_base_smaller_than_the_jitter_still_spawns_alive() {
        // The floor: an operator's short-lived critter (base < jitter) must
        // never roll an already-expired element.
        let mut config = test_config();
        config.elements.bug.min = 10;
        config.elements.bug.max = 12;
        config.elements.bug.ttl = Some(5);
        let world = World::generate(&config);

        for el in world
            .elements
            .iter()
            .filter(|e| e.element_type() == ElementType::Bug)
        {
            let ttl = el.ttl.expect("bugs are timed");
            assert!(ttl >= 1, "a spawn must never be born expired");
            assert!(ttl <= 5 + 100, "jitter cannot exceed base + TTL_JITTER");
            assert!(!el.is_expired());
        }
    }
}
