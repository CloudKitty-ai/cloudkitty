//! The constitution, checked every tick.
//!
//! These are the assertions the property suite hammers on: whatever behaviors
//! propose and however the world evolves, all of these must hold at the end of
//! every single tick.
//!
//! Enforcement policy: in debug and test builds a violation panics loudly, because
//! a violated invariant means the engine has a bug and we want the failing seed. In
//! release builds it is logged at error level instead -- crashing a running world
//! would punish the kitties for our mistake, which Article I will not have. The CI
//! gate is what actually keeps release builds honest.

use crate::config::Config;
use crate::element::ElementType;
use crate::needs::{NeedKind, NEED_MAX, NEED_MIN};
use crate::world::World;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Violation {
    pub article: &'static str,
    pub detail: String,
}

impl std::fmt::Display for Violation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} violated: {}", self.article, self.detail)
    }
}

/// Checks every constitutional guarantee. Returns the first violation found.
pub fn check(world: &World, config: &Config) -> Result<(), Violation> {
    // Article III: kitties cannot be alone.
    if world.kitties.len() < 2 {
        return Err(Violation {
            article: "Article III (kitties cannot be alone)",
            detail: format!("world holds {} kitties", world.kitties.len()),
        });
    }

    for kitty in &world.kitties {
        // Article I: needs are bounded pressures.
        for kind in NeedKind::ALL {
            let value = kitty.needs.get(kind);
            if !(NEED_MIN..=NEED_MAX).contains(&value) || value.is_nan() {
                return Err(Violation {
                    article: "Article I (kitties cannot suffer)",
                    detail: format!(
                        "{}'s {} need is {value}, outside [{NEED_MIN}, {NEED_MAX}]",
                        kitty.name,
                        kind.as_str()
                    ),
                });
            }
        }

        // Article I: happiness has a floor and can never reach zero.
        if kitty.happiness < config.happiness.floor || kitty.happiness.is_nan() {
            return Err(Violation {
                article: "Article I (kitties cannot suffer)",
                detail: format!(
                    "{}'s happiness is {}, below the floor of {}",
                    kitty.name, kitty.happiness, config.happiness.floor
                ),
            });
        }

        if !kitty.pos.in_bounds(world.width, world.height) {
            return Err(Violation {
                article: "World integrity",
                detail: format!(
                    "{} is at ({}, {}), outside the {}x{} world",
                    kitty.name, kitty.pos.x, kitty.pos.y, world.width, world.height
                ),
            });
        }
    }

    // One kitty per tile.
    let mut occupied = std::collections::BTreeSet::new();
    for kitty in &world.kitties {
        if !occupied.insert(kitty.pos) {
            return Err(Violation {
                article: "World integrity",
                detail: format!("two kitties share tile ({}, {})", kitty.pos.x, kitty.pos.y),
            });
        }
    }

    // One element per tile.
    let mut element_tiles = std::collections::BTreeSet::new();
    for el in &world.elements {
        if !element_tiles.insert(el.pos) {
            return Err(Violation {
                article: "World integrity",
                detail: format!("two elements share tile ({}, {})", el.pos.x, el.pos.y),
            });
        }
    }

    // Article I: the relief guarantee. A kitty past the safeguard threshold must
    // have something that can help it -- unless the world is physically full, in
    // which case the spec allows the spawn to be deferred.
    let world_is_full = world.elements.len() as u32 >= world.width * world.height;
    if !world_is_full {
        for need in [NeedKind::Eat, NeedKind::Drink] {
            let Some(kind) = ElementType::for_need(need) else {
                continue;
            };
            let in_want = world
                .kitties
                .iter()
                .find(|k| k.needs.get(need) > config.thresholds.safeguard);
            if let Some(kitty) = in_want {
                if world.count_of(kind) == 0 {
                    return Err(Violation {
                        article: "Article I (kitties cannot suffer)",
                        detail: format!(
                            "{}'s {} need is {:.1} (past the safeguard threshold of {}) but no {} exists",
                            kitty.name,
                            need.as_str(),
                            kitty.needs.get(need),
                            config.thresholds.safeguard,
                            kind.as_str()
                        ),
                    });
                }
            }
        }
    }

    Ok(())
}

/// Debug/test: panic. Release: log and carry on (see the module note).
pub fn assert_or_report(world: &World, config: &Config) {
    if let Err(violation) = check(world, config) {
        if cfg!(debug_assertions) {
            panic!("constitution violated at tick {}: {violation}", world.tick);
        } else {
            tracing::error!(tick = world.tick, %violation, "constitution violated");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grid::Position;
    use crate::test_support::test_world;

    #[test]
    fn a_healthy_world_passes() {
        let (world, config) = test_world();
        check(&world, &config).expect("a fresh world is lawful");
    }

    #[test]
    fn a_lonely_world_is_a_violation() {
        let (mut world, config) = test_world();
        // Only a test can do this; the engine has no such operation.
        world.kitties.truncate(1);
        let err = check(&world, &config).unwrap_err();
        assert!(err.article.contains("Article III"), "{err}");
    }

    #[test]
    fn happiness_below_the_floor_is_a_violation() {
        let (mut world, config) = test_world();
        world.kitties[0].happiness = 0.0;
        let err = check(&world, &config).unwrap_err();
        assert!(err.article.contains("Article I"), "{err}");
    }

    #[test]
    fn stacked_kitties_are_a_violation() {
        let (mut world, config) = test_world();
        let pos = world.kitties[0].pos;
        world.kitties[1].pos = pos;
        assert!(check(&world, &config).is_err());
    }

    #[test]
    fn a_hungry_kitty_with_no_food_is_a_violation() {
        let (mut world, config) = test_world();
        world
            .elements
            .retain(|e| e.element_type() != ElementType::Chow);
        world.kitties[0].needs.add(NeedKind::Eat, 99.0);

        let err = check(&world, &config).unwrap_err();
        assert!(err.article.contains("Article I"), "{err}");
        assert!(err.detail.contains("chow"), "{err}");
    }

    #[test]
    fn out_of_bounds_kitties_are_caught() {
        let (mut world, config) = test_world();
        world.kitties[0].pos = Position::new(world.width + 5, 0);
        assert!(check(&world, &config).is_err());
    }
}
