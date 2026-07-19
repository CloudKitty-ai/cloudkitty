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

        // Distress bookkeeping: no start tick may outlive its distress. (The
        // other direction -- distress without a start tick -- is legal
        // transiently: a pre-004 snapshot arrives that way and the next needs
        // phase self-heals it, so equality would wrongly refuse old saves.)
        for kind in kitty.distress_since.keys() {
            if !kitty.in_distress.contains(kind) {
                return Err(Violation {
                    article: "Bookkeeping integrity",
                    detail: format!(
                        "{} has a distress_since entry for {} but is not in distress about it",
                        kitty.name,
                        kind.as_str()
                    ),
                });
            }
        }

        // Pursuit bookkeeping: a recorded chase started in the past and its
        // best distance fits on the grid.
        if let Some(p) = &kitty.pursuit {
            let max_distance = world.width.max(world.height);
            if p.started > world.tick || p.closest > max_distance {
                return Err(Violation {
                    article: "Bookkeeping integrity",
                    detail: format!(
                        "{}'s pursuit is implausible: started {} (tick {}), closest {}",
                        kitty.name, p.started, world.tick, p.closest
                    ),
                });
            }
        }

        // Exclusions are pruned as they expire; none may linger.
        if let Some(stale) = kitty
            .abandoned_chases
            .iter()
            .find(|a| a.until <= world.tick.saturating_sub(1))
        {
            return Err(Violation {
                article: "Bookkeeping integrity",
                detail: format!(
                    "{} still lists an exclusion that expired at {} (tick {})",
                    kitty.name, stale.until, world.tick
                ),
            });
        }

        // Activity bookkeeping (spec 006): the clock exists exactly when an
        // activity is in progress. Strict in both directions -- pre-006
        // snapshots carrying an unclocked activity are refused, not healed.
        match (kitty.activity.is_in_progress(), &kitty.activity_clock) {
            (true, None) => {
                return Err(Violation {
                    article: "Bookkeeping integrity",
                    detail: format!(
                        "{} has an activity in progress but no activity clock \
                         (pre-006 snapshots are not supported)",
                        kitty.name
                    ),
                });
            }
            (false, Some(_)) => {
                return Err(Violation {
                    article: "Bookkeeping integrity",
                    detail: format!("{} is idle but still carries an activity clock", kitty.name),
                });
            }
            (true, Some(clock)) => {
                // The clock runs forward and never claims an unfinished tick.
                if clock.started > clock.applied || clock.applied >= world.tick {
                    return Err(Violation {
                        article: "Bookkeeping integrity",
                        detail: format!(
                            "{}'s activity clock is implausible: started {}, applied {} (tick {})",
                            kitty.name, clock.started, clock.applied, world.tick
                        ),
                    });
                }
                // No activity outlives its configured maximum.
                if let Some(bounds) = kitty.activity.bounds(&config.actions.durations) {
                    let elapsed = clock.elapsed(world.tick.saturating_sub(1));
                    if elapsed > bounds.max {
                        return Err(Violation {
                            article: "Bookkeeping integrity",
                            detail: format!(
                                "{}'s activity has run {elapsed} ticks, past its maximum of {}",
                                kitty.name, bounds.max
                            ),
                        });
                    }
                }
            }
            (false, None) => {}
        }

        // Duets are never one-sided: a cuddle or social play binds both
        // partners with identical clocks (spec 006 FR-009).
        if let Some(partner_id) = kitty.activity.duet_partner() {
            let reciprocal = world.kitty(partner_id).and_then(|p| {
                (p.activity.duet_partner() == Some(kitty.id)).then_some(p.activity_clock)
            });
            match reciprocal {
                Some(partner_clock) if partner_clock == kitty.activity_clock => {}
                _ => {
                    return Err(Violation {
                        article: "Bookkeeping integrity",
                        detail: format!(
                            "{}'s duet with kitty {partner_id} is one-sided or out of step",
                            kitty.name
                        ),
                    });
                }
            }
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

    // ---- action durations (spec 006) ----------------------------------

    use crate::action::TargetRef;
    use crate::kitty::{Activity, ActivityClock};

    #[test]
    fn an_unclocked_activity_is_refused_not_healed() {
        let (mut world, config) = test_world();
        world.tick = 10;
        world.kitties[0].activity = Activity::Sleeping {
            in_sunbeam: false,
            with_friend: None,
        };
        let err = check(&world, &config).unwrap_err();
        assert!(err.detail.contains("pre-006"), "{err}");
    }

    #[test]
    fn an_orphaned_clock_is_a_violation() {
        let (mut world, config) = test_world();
        world.tick = 10;
        world.kitties[0].activity_clock = Some(ActivityClock::start(5));
        let err = check(&world, &config).unwrap_err();
        assert!(err.detail.contains("idle"), "{err}");
    }

    #[test]
    fn a_clock_may_not_claim_an_unfinished_tick() {
        let (mut world, config) = test_world();
        world.tick = 10;
        world.kitties[0].activity = Activity::Eating;
        world.kitties[0].activity_clock = Some(ActivityClock::start(10));
        let err = check(&world, &config).unwrap_err();
        assert!(err.detail.contains("implausible"), "{err}");

        // The lawful shape: serviced last on the tick that just finished.
        world.kitties[0].activity_clock = Some(ActivityClock::start(9));
        check(&world, &config).expect("a fresh meal is lawful");
    }

    #[test]
    fn an_activity_past_its_maximum_is_a_violation() {
        let (mut world, config) = test_world();
        world.tick = 100;
        world.kitties[0].activity = Activity::Eating;
        // Eat max is 5; this meal claims 7 ticks by the time tick 99 closed.
        world.kitties[0].activity_clock = Some(ActivityClock {
            started: 93,
            applied: 99,
        });
        let err = check(&world, &config).unwrap_err();
        assert!(err.detail.contains("maximum"), "{err}");
    }

    #[test]
    fn a_one_sided_duet_is_a_violation() {
        let (mut world, config) = test_world();
        world.tick = 10;
        world.kitties[0].activity = Activity::Playing {
            target: Some(TargetRef::Kitty {
                id: world.kitties[1].id,
            }),
        };
        world.kitties[0].activity_clock = Some(ActivityClock::start(9));
        let err = check(&world, &config).unwrap_err();
        assert!(err.detail.contains("one-sided"), "{err}");

        // Reciprocity with an identical clock is lawful.
        let me = world.kitties[0].id;
        world.kitties[1].activity = Activity::Playing {
            target: Some(TargetRef::Kitty { id: me }),
        };
        world.kitties[1].activity_clock = Some(ActivityClock::start(9));
        check(&world, &config).expect("a proper duet is lawful");
    }
}
