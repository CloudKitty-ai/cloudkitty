//! Shared need selection for the built-in behaviors.
//!
//! One scored pass over all six needs, every tick, replacing the old two-mode
//! rule (a hard lock above the safeguard threshold, a convenience band below
//! it). The lock is what let one unattainable need starve five satisfiable
//! ones -- the 2026-07-18 root-cause analysis found kitties pinned at the
//! happiness floor because play could not land while bath and sleep, free for
//! the taking, were never chosen. Here urgency is a weight, not a veto:
//!
//! ```text
//! score = pressure + urgency_weight * max(0, pressure - safeguard)
//!         - tile_cost * travel_distance
//! ```
//!
//! Urgent needs still dominate anything similarly far away; they just cannot
//! outrank relief that is already underfoot. Ties go to the need that has
//! waited longest for relief, so nothing can be permanently shadowed at the
//! 100-cap by a fixed ordering.
//!
//! Both built-in profiles select through this module (and external behaviors
//! are welcome to copy it) -- one tested rule, no drift between personalities.

use super::DecisionContext;
use crate::action::{Action, TargetRef};
use crate::element::ElementType;
use crate::grid::Position;
use crate::needs::NeedKind;

/// A distance standing in for "no way to relieve this at all". Large enough to
/// lose every comparison, small enough to never overflow the score arithmetic.
const UNREACHABLE: u32 = u32::MAX / 2;

/// Picks the need most worth acting on: highest score, ties to the need
/// longest without relief, then `NeedKind::ALL` order as the final
/// deterministic word.
pub fn choose_need(ctx: &DecisionContext) -> NeedKind {
    let mut best = NeedKind::ALL[0];
    let mut best_score = score(ctx, best);

    for kind in NeedKind::ALL.into_iter().skip(1) {
        let s = score(ctx, kind);
        let wins = s > best_score
            || (s == best_score && ctx.me.last_relief_tick(kind) < ctx.me.last_relief_tick(best));
        if wins {
            best = kind;
            best_score = s;
        }
    }

    best
}

/// The selection score for one need. Public so tests (and curious plugin
/// authors) can check the arithmetic directly.
pub fn score(ctx: &DecisionContext, kind: NeedKind) -> f32 {
    let behavior = &ctx.config.behavior;
    let pressure = ctx.me.needs.get(kind);
    let urgency = (pressure - ctx.config.thresholds.safeguard).max(0.0);
    pressure + behavior.urgency_weight * urgency
        - behavior.tile_cost * travel_distance(ctx, kind) as f32
}

/// How far this cat would have to walk to do something about `need`.
pub fn travel_distance(ctx: &DecisionContext, need: NeedKind) -> u32 {
    let me = &ctx.me;
    let nearest = |kind: ElementType| {
        ctx.world
            .nearest_element(me.pos, kind)
            .map(|e| me.pos.chebyshev_distance(&e.pos))
    };

    match need {
        // Grooming and sleeping can happen anywhere at all.
        NeedKind::Bath | NeedKind::Sleep => 0,
        NeedKind::Eat => nearest(ElementType::Chow).unwrap_or(UNREACHABLE),
        NeedKind::Drink => nearest(ElementType::Water).unwrap_or(UNREACHABLE),
        NeedKind::Play => play_travel_distance(ctx),
        NeedKind::Cuddle => ctx
            .world
            .nearest_friend(me.id, me.pos)
            .map(|k| me.pos.chebyshev_distance(&k.pos))
            .unwrap_or(UNREACHABLE),
    }
}

/// The distance the play [`play_action`] would actually cover -- a viable
/// playmate's distance when one is worth walking to, zero when solo play is
/// what would happen.
fn play_travel_distance(ctx: &DecisionContext) -> u32 {
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = ctx.me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;
    match nearest_viable_playmate(ctx) {
        Some((_, pos)) => {
            let d = ctx.me.pos.chebyshev_distance(&pos);
            if d > reach && urgent {
                0 // solo play right here beats the trek
            } else {
                d
            }
        }
        // Nobody viable at all: the kitty entertains itself on the spot.
        None => 0,
    }
}

/// The nearest playmate still worth pursuing -- critter or fellow kitty --
/// ordered by (distance, critters-before-kitties, id) so the choice is stable.
///
/// A candidate stops being viable while it sits in `abandoned_chases`, or while
/// it is the current pursuit target with the patience window elapsed and no
/// improvement on the closest distance achieved (a chase that is not working).
pub fn nearest_viable_playmate(ctx: &DecisionContext) -> Option<(TargetRef, Position)> {
    let me = &ctx.me;

    let critters = ctx.world.critters().map(|e| {
        (
            TargetRef::Element { id: e.id },
            e.pos,
            0u8, // critters win distance ties: bugs are more fun than bothering a friend
            e.id,
        )
    });
    let friends = ctx
        .world
        .others(me.id)
        .map(|k| (TargetRef::Kitty { id: k.id }, k.pos, 1u8, k.id));

    critters
        .chain(friends)
        .filter(|(target, pos, _, _)| is_viable(ctx, *target, *pos))
        .min_by_key(|(_, pos, tag, id)| (me.pos.chebyshev_distance(pos), *tag, *id))
        .map(|(target, pos, _, _)| (target, pos))
}

fn is_viable(ctx: &DecisionContext, target: TargetRef, pos: Position) -> bool {
    let tick = ctx.world.tick;
    if ctx.me.is_chase_excluded(target, tick) {
        return false;
    }
    if let Some(pursuit) = &ctx.me.pursuit {
        let patience = ctx.config.behavior.chase_patience_ticks;
        let stalled = tick.saturating_sub(pursuit.started) >= patience
            && ctx.me.pos.chebyshev_distance(&pos) >= pursuit.closest;
        if pursuit.target == target && stalled {
            return false;
        }
    }
    true
}

/// One step toward relieving play: pounce on an adjacent playmate, walk after a
/// viable one worth reaching, and otherwise pounce at nothing -- solo play, the
/// backstop that makes play (like bath and sleep) satisfiable anywhere.
pub fn play_action(ctx: &DecisionContext) -> Action {
    let me = &ctx.me;
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;

    match nearest_viable_playmate(ctx) {
        Some((target, pos)) => {
            if me.pos.is_adjacent(&pos) {
                Action::play_with(target)
            } else if me.pos.chebyshev_distance(&pos) > reach && urgent {
                // Everyone worth playing with is far away and the need is real:
                // a kitty does not sulk, it pounces at nothing.
                Action::play_solo()
            } else {
                Action::Chase(target)
            }
        }
        None => Action::play_solo(),
    }
}

/// An adjacent playmate for the opportunism pass: any critter or fellow kitty
/// within paw's reach. Exclusion does not apply here -- a target that wandered
/// into range costs nothing to bat at, however hopeless it was to chase.
pub fn adjacent_playmate(ctx: &DecisionContext) -> Option<TargetRef> {
    let me = &ctx.me;
    let critter = ctx
        .world
        .critters()
        .filter(|e| me.pos.is_adjacent(&e.pos))
        .min_by_key(|e| (me.pos.chebyshev_distance(&e.pos), e.id))
        .map(|e| TargetRef::Element { id: e.id });
    critter.or_else(|| {
        ctx.world
            .others(me.id)
            .filter(|k| me.pos.is_adjacent(&k.pos))
            .min_by_key(|k| (me.pos.chebyshev_distance(&k.pos), k.id))
            .map(|k| TargetRef::Kitty { id: k.id })
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::element::{Element, ElementKind};
    use crate::kitty::{AbandonedChase, Pursuit};
    use crate::test_support::decision_context;

    /// The stuck world of tick 1465, reconstructed: Miso at (21,30), bath and
    /// play both pinned at 100, sleep 98.9, a bug 3 tiles away, water 6 and
    /// chow 8 tiles off, friends ~16 away. The old selection locked onto play
    /// forever; the score must pick bath -- relief on the spot.
    fn miso_ctx() -> crate::behavior::DecisionContext {
        decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(21, 30);
            let needs = &mut world.kitties[idx].needs;
            needs.add(NeedKind::Eat, 34.5);
            needs.add(NeedKind::Drink, 30.5);
            needs.add(NeedKind::Sleep, 98.9);
            needs.add(NeedKind::Play, 100.0);
            needs.add(NeedKind::Cuddle, 45.75);
            needs.add(NeedKind::Bath, 100.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 20);
            world.push_element(Element {
                id: 102,
                kind: ElementKind::Bug,
                pos: Position::new(22, 27),
                ttl: Some(95),
            });
            world.push_element(Element {
                id: 5,
                kind: ElementKind::Water,
                pos: Position::new(27, 29),
                ttl: None,
            });
            world.push_element(Element {
                id: 10,
                kind: ElementKind::Chow { servings: 1 },
                pos: Position::new(29, 31),
                ttl: None,
            });
        })
    }

    #[test]
    fn the_stuck_kitty_grooms_instead_of_fixating_on_play() {
        let ctx = miso_ctx();
        // The R1 worked example, verbatim: bath 150 > play 147 > sleep 146.7.
        assert_eq!(score(&ctx, NeedKind::Bath), 150.0);
        assert_eq!(score(&ctx, NeedKind::Play), 147.0);
        assert!((score(&ctx, NeedKind::Sleep) - 146.7).abs() < 0.1);
        assert_eq!(choose_need(&ctx), NeedKind::Bath);
    }

    #[test]
    fn urgent_play_with_no_playmate_near_resolves_on_the_spot_not_by_trekking() {
        let mut ctx = miso_ctx();
        // Bath freshly relieved, the bug gone: the nearest playmate is a friend
        // 16 tiles off. Urgent play is still satisfiable right here (solo), so
        // play may win selection -- but it must resolve as a pounce at nothing,
        // never a cross-map trek. One solo helping later, sleep takes over.
        let world = std::sync::Arc::get_mut(&mut ctx.world).unwrap();
        world.elements.retain(|e| e.id != 102);
        ctx.me.needs.add(NeedKind::Bath, -80.0);

        assert_eq!(choose_need(&ctx), NeedKind::Play);
        assert_eq!(play_action(&ctx), Action::play_solo());

        // After the solo relief lands, the scored pass moves on to sleep.
        ctx.me
            .needs
            .add(NeedKind::Play, -ctx.config.actions.solo_play_relief);
        assert_eq!(choose_need(&ctx), NeedKind::Sleep);
    }

    #[test]
    fn genuine_urgency_still_beats_a_mild_zero_distance_need() {
        // Eat at 80 with chow five tiles away must outrank bath at 50 underfoot:
        // eat = 80 + 2*5 - 5 = 85 vs bath = 50.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
            world.kitties[idx].needs.add(NeedKind::Bath, 50.0);
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(10, 5),
                ttl: None,
            });
        });
        assert_eq!(choose_need(&ctx), NeedKind::Eat);
    }

    #[test]
    fn ties_go_to_the_need_longest_without_relief() {
        // Bath and sleep both pinned at 100, both zero distance, identical
        // scores -- the old enum order would say sleep, forever. Relief
        // recency must decide instead.
        let make = |bath_relieved: u64, sleep_relieved: u64| {
            decision_context(move |world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].needs.add(NeedKind::Bath, 100.0);
                world.kitties[idx].needs.add(NeedKind::Sleep, 100.0);
                world.kitties[idx]
                    .last_relief
                    .insert(NeedKind::Bath, bath_relieved);
                world.kitties[idx]
                    .last_relief
                    .insert(NeedKind::Sleep, sleep_relieved);
            })
        };

        let ctx = make(10, 500);
        assert_eq!(choose_need(&ctx), NeedKind::Bath, "bath waited longer");
        let ctx = make(500, 10);
        assert_eq!(choose_need(&ctx), NeedKind::Sleep, "now sleep has");
        // Never-relieved beats any stamp at all.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Bath, 100.0);
            world.kitties[idx].needs.add(NeedKind::Sleep, 100.0);
            world.kitties[idx].last_relief.insert(NeedKind::Sleep, 1);
        });
        assert_eq!(choose_need(&ctx), NeedKind::Bath);
    }

    #[test]
    fn identical_contexts_choose_identically() {
        let a = choose_need(&miso_ctx());
        let b = choose_need(&miso_ctx());
        assert_eq!(a, b);
    }

    #[test]
    fn a_nearer_friend_beats_a_farther_critter() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 8); // 3 away
            world.push_element(Element {
                id: 800,
                kind: ElementKind::Bug,
                pos: Position::new(12, 5), // 7 away
                ttl: Some(50),
            });
        });
        assert_eq!(
            nearest_viable_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 })
        );
    }

    #[test]
    fn an_excluded_target_is_skipped_for_its_whole_window() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].abandoned_chases.push(AbandonedChase {
                target: TargetRef::Element { id: 801 },
                until: world.tick + 60,
            });
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 15); // 10 away
            world.push_element(Element {
                id: 801,
                kind: ElementKind::Greeble {
                    heading: crate::grid::Direction::North,
                },
                pos: Position::new(5, 7), // 2 away, but written off
                ttl: Some(50),
            });
        });
        assert_eq!(
            nearest_viable_playmate(&ctx).map(|(t, _)| t),
            Some(TargetRef::Kitty { id: 2 }),
            "the excluded greeble does not count, however close"
        );
    }

    #[test]
    fn a_stalled_pursuit_target_is_not_viable_but_an_improving_one_is() {
        let make = |closest: u32| {
            decision_context(move |world| {
                world.elements.clear();
                world.tick = 100;
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = Position::new(5, 5);
                world.kitties[idx].pursuit = Some(Pursuit {
                    target: TargetRef::Element { id: 802 },
                    started: 80, // 20 ticks ago > patience 12
                    closest,
                });
                let friend = world.kitty_index(2).unwrap();
                world.kitties[friend].pos = Position::new(20, 20);
                world.push_element(Element {
                    id: 802,
                    kind: ElementKind::Bug,
                    pos: Position::new(5, 9), // currently 4 away
                    ttl: Some(50),
                });
            })
        };

        // Best-ever was 4 and it is still 4: stalled, skip it.
        let stalled = make(4);
        assert_ne!(
            nearest_viable_playmate(&stalled).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
        // Best-ever was 6 and it is 4 now: closing in, keep going.
        let improving = make(6);
        assert_eq!(
            nearest_viable_playmate(&improving).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
    }

    #[test]
    fn urgent_play_with_everyone_out_of_reach_goes_solo() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(31, 31); // far past reach 8
        });
        assert_eq!(play_action(&ctx), Action::play_solo());
        assert_eq!(
            travel_distance(&ctx, NeedKind::Play),
            0,
            "the score must agree that relief is on the spot"
        );
    }

    #[test]
    fn an_adjacent_partner_is_preferred_over_solo_play() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(2, 3);
        });
        assert_eq!(
            play_action(&ctx),
            Action::play_with(TargetRef::Kitty { id: 2 })
        );
    }

    #[test]
    fn moderate_play_with_a_reachable_playmate_chases() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 50.0);
            world.push_element(Element {
                id: 803,
                kind: ElementKind::Bug,
                pos: Position::new(6, 2), // 4 away, within reach
                ttl: Some(50),
            });
        });
        assert_eq!(
            play_action(&ctx),
            Action::Chase(TargetRef::Element { id: 803 })
        );
    }
}
