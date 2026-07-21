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

/// The outcome of one scored pass: the need most worth acting on, plus the
/// playmate scan that pass already paid for, so pursuing play never scans the
/// world a second time in the same decision.
pub struct Choice {
    pub need: NeedKind,
    /// The nearest viable playmate at decision time. Meaningful to pursuit
    /// only when `need` is play; carried whole so the caller need not guess.
    pub playmate: Option<(TargetRef, Position)>,
}

/// Picks the need most worth acting on: highest score, ties to the need
/// longest without relief, then `NeedKind::ALL` order as the final
/// deterministic word. Needs with no relief path at all are skipped outright
/// (see [`travel_distance`]).
pub fn choose(ctx: &DecisionContext) -> Choice {
    let playmate = nearest_viable_playmate(ctx);
    let mut best: Option<(NeedKind, f32)> = None;

    for kind in NeedKind::ALL {
        let Some(s) = scored(ctx, kind, playmate) else {
            continue;
        };
        let wins = match best {
            None => true,
            Some((held, held_score)) => {
                s > held_score
                    || (s == held_score
                        && ctx.me.last_relief_tick(kind) < ctx.me.last_relief_tick(held))
            }
        };
        if wins {
            best = Some((kind, s));
        }
    }

    // Bath and play are relievable wherever the cat stands, so a best always
    // exists; the fallback is belt and braces, not a reachable path.
    let need = best.map(|(kind, _)| kind).unwrap_or(NeedKind::ALL[0]);
    Choice { need, playmate }
}

/// [`choose`], for callers (and tests) that only want the winning need.
pub fn choose_need(ctx: &DecisionContext) -> NeedKind {
    choose(ctx).need
}

/// The selection score for one need, or `None` when the need has no relief
/// path (see [`travel_distance`]). Public so tests (and curious plugin
/// authors) can check the arithmetic directly.
pub fn score(ctx: &DecisionContext, kind: NeedKind) -> Option<f32> {
    scored(ctx, kind, nearest_viable_playmate(ctx))
}

fn scored(
    ctx: &DecisionContext,
    kind: NeedKind,
    playmate: Option<(TargetRef, Position)>,
) -> Option<f32> {
    let behavior = &ctx.config.behavior;
    let distance = distance_given(ctx, kind, playmate)?;
    let pressure = ctx.me.needs.get(kind);
    let urgency = (pressure - ctx.config.thresholds.safeguard).max(0.0);
    Some(pressure + behavior.urgency_weight * urgency - behavior.tile_cost * distance as f32)
}

/// How far this cat would have to walk to do something about `need`, or
/// `None` when the world currently offers no way to relieve it at all.
///
/// "No way" is deliberately not encoded as a huge distance: a sentinel is
/// only as strong as the weight multiplying it, so a legal `tile_cost = 0`
/// would cancel it and let an unrelievable need win selection -- the exact
/// shape of the lock-in spec 004 removed. A skipped need is skipped under
/// every configuration.
pub fn travel_distance(ctx: &DecisionContext, need: NeedKind) -> Option<u32> {
    distance_given(ctx, need, nearest_viable_playmate(ctx))
}

fn distance_given(
    ctx: &DecisionContext,
    need: NeedKind,
    playmate: Option<(TargetRef, Position)>,
) -> Option<u32> {
    let me = &ctx.me;
    let nearest = |kind: ElementType| {
        ctx.world
            .nearest_element(me.pos, kind)
            .map(|e| me.pos.manhattan_distance(&e.pos))
    };

    match need {
        // Grooming happens wherever the cat is standing.
        NeedKind::Bath => Some(0),
        NeedKind::Sleep => Some(sleep_travel_distance(ctx)),
        NeedKind::Eat => nearest(ElementType::Chow),
        NeedKind::Drink => nearest(ElementType::Water),
        NeedKind::Play => Some(play_travel_distance(ctx, playmate)),
        NeedKind::Cuddle => ctx
            .world
            .nearest_friend(me.id, me.pos)
            .map(|k| me.pos.manhattan_distance(&k.pos)),
    }
}

/// The distance sleep pursuit would actually cover: a sunbeam within
/// `sunbeam_reach` is worth walking to, anything farther (or no sunbeam at
/// all) means a nap on the spot. Mirrors `pursue`'s sleep arm exactly -- the
/// score must never call sleep free and then commit the cat to a trek.
fn sleep_travel_distance(ctx: &DecisionContext) -> u32 {
    match ctx.world.nearest_element(ctx.me.pos, ElementType::Sunbeam) {
        Some(sunbeam) => {
            let d = ctx.me.pos.manhattan_distance(&sunbeam.pos);
            if d <= ctx.config.behavior.sunbeam_reach {
                d
            } else {
                0
            }
        }
        None => 0,
    }
}

/// The distance the play [`play_action`] would actually cover -- a viable
/// playmate's distance when one is worth walking to, zero when solo play is
/// what would happen.
fn play_travel_distance(ctx: &DecisionContext, playmate: Option<(TargetRef, Position)>) -> u32 {
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = ctx.me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;
    match playmate {
        Some((_, pos)) => {
            let d = ctx.me.pos.manhattan_distance(&pos);
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
/// it is the current pursuit target that has gained no ground in
/// `chase_patience_ticks` (a chase that is not working -- as opposed to one
/// that is merely long).
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
        .filter(|(target, _, _, _)| is_viable(ctx, *target))
        .min_by_key(|(_, pos, tag, id)| (me.pos.manhattan_distance(pos), *tag, *id))
        .map(|(target, pos, _, _)| (target, pos))
}

fn is_viable(ctx: &DecisionContext, target: TargetRef) -> bool {
    let tick = ctx.world.tick;
    if ctx.me.is_chase_excluded(target, tick) {
        return false;
    }
    // A kitty mid-activity cannot be conscripted into play (spec 006):
    // proposing it would only validate to Idle, and counting it viable at
    // distance 0 would suppress the solo-play backstop for as long as its
    // scene runs. Busy friends become playmates again when their scene ends.
    if let TargetRef::Kitty { id } = target {
        let busy = ctx
            .world
            .kitty(id)
            .map(|k| k.activity.is_in_progress())
            .unwrap_or(true);
        if busy {
            return false;
        }
    }
    if let Some(pursuit) = &ctx.me.pursuit {
        let patience = ctx.config.behavior.chase_patience_ticks;
        let stalled = tick.saturating_sub(pursuit.last_progress()) >= patience;
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
    play_action_with(ctx, nearest_viable_playmate(ctx))
}

/// [`play_action`] against a playmate scan the caller already ran -- how
/// [`choose`]'s result is pursued without scanning the world twice.
pub fn play_action_with(ctx: &DecisionContext, playmate: Option<(TargetRef, Position)>) -> Action {
    let me = &ctx.me;
    let reach = ctx.config.behavior.solo_play_reach;
    let urgent = me.needs.get(NeedKind::Play) >= ctx.config.thresholds.safeguard;

    match playmate {
        Some((target, pos)) => {
            if me.pos.is_adjacent(&pos) {
                Action::play_with(target)
            } else if me.pos.manhattan_distance(&pos) > reach && urgent {
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
        .min_by_key(|e| (me.pos.manhattan_distance(&e.pos), e.id))
        .map(|e| TargetRef::Element { id: e.id });
    critter.or_else(|| {
        ctx.world
            .others(me.id)
            // A friend mid-meal or asleep cannot be batted into a game
            // (spec 006 conscription); only an idle neighbour counts.
            .filter(|k| me.pos.is_adjacent(&k.pos) && !k.activity.is_in_progress())
            .min_by_key(|k| (me.pos.manhattan_distance(&k.pos), k.id))
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
        // The 004 R1 worked example, re-derived for spec 009's Manhattan
        // distances: the bug at (22,27) is now honestly 4 walking steps (was
        // Chebyshev 3), so play = 100 + 50 - 4 = 146 and the runner-up order
        // flips (sleep 146.7 above play 146) -- but bath, relief on the spot,
        // still wins at 150, which is the property this test guards.
        assert_eq!(score(&ctx, NeedKind::Bath), Some(150.0));
        assert_eq!(score(&ctx, NeedKind::Play), Some(146.0));
        assert!((score(&ctx, NeedKind::Sleep).unwrap() - 146.7).abs() < 0.1);
        assert_eq!(choose_need(&ctx), NeedKind::Bath);
    }

    #[test]
    fn an_unrelievable_need_is_skipped_not_priced() {
        // The 004-review P1 hole: with a legal `tile_cost = 0`, a sentinel
        // distance is multiplied away and a need with no relief path anywhere
        // wins on pressure alone -- the cat idles at high pressure while bath
        // and sleep sit free. Unreachability must survive every config.
        let mut ctx = decision_context(|world| {
            world.elements.clear(); // no chow anywhere
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Eat, 100.0);
            world.kitties[idx].needs.add(NeedKind::Bath, 50.0);
        });
        std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .behavior
            .tile_cost = 0.0;

        assert_eq!(
            score(&ctx, NeedKind::Eat),
            None,
            "no chow in the world means no eat score at all"
        );
        assert_eq!(
            choose_need(&ctx),
            NeedKind::Bath,
            "a need nothing can relieve must not outrank relief underfoot"
        );
    }

    #[test]
    fn sleep_is_priced_at_the_walk_its_pursuit_would_take() {
        // The 004-review scoring hole: sleep scored as distance 0 while its
        // pursuit walks up to `sunbeam_reach` tiles to a sunbeam, letting
        // "free" sleep beat food one step away and then trek right past it.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Sleep, 60.0);
            world.kitties[idx].needs.add(NeedKind::Eat, 58.0);
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 6), // one step away
                ttl: None,
            });
            world.push_element(Element {
                id: 701,
                kind: ElementKind::Sunbeam,
                pos: Position::new(13, 5), // 8 tiles: within reach, and priced
                ttl: Some(100),
            });
        });

        assert_eq!(
            travel_distance(&ctx, NeedKind::Sleep),
            Some(8),
            "the sunbeam walk is a real cost"
        );
        assert_eq!(
            choose_need(&ctx),
            NeedKind::Eat,
            "eat 58 - 1 beats sleep 60 - 8; the score and the walk agree"
        );
    }

    #[test]
    fn a_sunbeam_past_reach_means_a_nap_on_the_spot_priced_at_zero() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.push_element(Element {
                id: 702,
                kind: ElementKind::Sunbeam,
                pos: Position::new(13, 13), // 11 tiles, past reach 8
                ttl: Some(100),
            });
        });
        assert_eq!(
            travel_distance(&ctx, NeedKind::Sleep),
            Some(0),
            "pursuit would nap right here, so the score says so too"
        );
    }

    #[test]
    fn a_busy_friend_is_not_a_viable_playmate_and_solo_play_steps_in() {
        use crate::kitty::{Activity, ActivityClock};

        // An urgent player beside a friend who is mid-meal: proposing at the
        // friend would only bounce off validation (spec 006 conscription), so
        // the friend must not count as viable -- the solo backstop fires.
        let ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 10;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 6);
            world.kitties[friend].activity = Activity::Eating;
            world.kitties[friend].activity_clock = Some(ActivityClock::start(9));
        });

        assert_eq!(
            nearest_viable_playmate(&ctx),
            None,
            "a cat mid-meal is not on the menu"
        );
        assert_eq!(adjacent_playmate(&ctx), None);
        assert_eq!(
            play_action(&ctx),
            Action::play_solo(),
            "the solo backstop fires instead of a doomed proposal"
        );
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

    /// A pursuit of bug 802 that began at tick 80 and last gained ground at
    /// `improved_at`, seen at tick 100 with the bug `distance` tiles away.
    fn pursuing_ctx(improved_at: u64, distance: u32) -> crate::behavior::DecisionContext {
        decision_context(move |world| {
            world.elements.clear();
            world.tick = 100;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 80.0);
            world.kitties[idx].pursuit = Some(Pursuit {
                target: TargetRef::Element { id: 802 },
                started: 80,
                closest: distance,
                improved_at,
            });
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(20, 20);
            world.push_element(Element {
                id: 802,
                kind: ElementKind::Bug,
                pos: Position::new(5, 5 + distance),
                ttl: Some(50),
            });
        })
    }

    #[test]
    fn a_pursuit_that_has_gained_no_ground_for_a_whole_patience_window_is_dropped() {
        // Last improvement 20 ticks ago, patience 12: this chase is not working.
        let stalled = pursuing_ctx(80, 4);
        assert_ne!(
            nearest_viable_playmate(&stalled).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
    }

    #[test]
    fn a_chase_that_is_still_closing_survives_however_long_it_has_run() {
        // Started 20 ticks ago but gained ground 2 ticks ago: keep going.
        let improving = pursuing_ctx(98, 4);
        assert_eq!(
            nearest_viable_playmate(&improving).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 })
        );
    }

    #[test]
    fn a_long_chase_is_not_abandoned_at_the_moment_it_arrives() {
        // Regression: viability used to compare current distance against the
        // best-ever distance, which are equal exactly when the cat is doing as
        // well as it ever has -- so a 20-tick chase was condemned at the very
        // tick it caught up. Arriving adjacent (distance 1, just improved) must
        // leave the target viable and get pounced on.
        let arrived = pursuing_ctx(100, 1);
        assert_eq!(
            nearest_viable_playmate(&arrived).map(|(t, _)| t),
            Some(TargetRef::Element { id: 802 }),
            "the bug it just spent 20 ticks reaching is still worth playing with"
        );
        assert_eq!(
            play_action(&arrived),
            Action::play_with(TargetRef::Element { id: 802 }),
            "and the cat pounces rather than wandering off"
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
            Some(0),
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
