//! A cat who would rather be playing.
//!
//! `Playful` exists to prove the point of pluggable behavior: given the same world,
//! a kitty running this strategy lives a visibly different life from one running
//! [`NeedsDriven`](super::NeedsDriven). It chases bugs and greebles it has no
//! particular reason to chase, pesters its friends for a game, and only attends to
//! its needs when one becomes genuinely pressing.
//!
//! It is still a good cat: it takes easy wins when they are underfoot, keeps its
//! needs below the configured comfort line, and purrs about the result — it just
//! spends every spare moment playing. Being playful means a different life, not a
//! worse one.

use async_trait::async_trait;

use super::needs_driven::{finish_what_you_started, pursue, take_what_is_here_consenting};
use super::{selection, Behavior, DecisionContext};
use crate::action::Action;
use crate::seam::Decision;

pub struct Playful;

#[async_trait]
impl Behavior for Playful {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        // Two channels (spec 028): same shape as NeedsDriven -- the yield
        // word outranks announce, everything else announces by the shared
        // rule. The old chase-announce lottery collapsed into it: WantPlay
        // is spoken when Play is genuinely armed, because grounding is law
        // for everyone.
        let mut decision = Decision::from_legacy(self.decide_action(ctx));
        if decision.message.is_none() {
            decision.message = super::announce(ctx);
        }
        decision
    }

    fn is_builtin(&self) -> bool {
        true
    }
}

impl Playful {
    fn decide_action(&self, ctx: &DecisionContext) -> Action {
        // Even a playful cat finishes the nap it is in the middle of.
        if let Some(action) = finish_what_you_started(ctx) {
            return action;
        }

        // Opportunism is good sense, not a personality trait: a playful cat still
        // eats the food it is standing next to before running off after a bug.
        // Spec 047 site 3: but even a game within paw's reach honors the
        // consent line — adjacency is not a bypass.
        if let Some(action) = take_what_is_here_consenting(ctx) {
            return action;
        }

        // Some things cannot wait, even for a good game. The comfort line is
        // configurable ([behavior] playful_comfort, default 55): well below the
        // safeguard threshold, so a playful cat keeps itself in reasonable shape
        // instead of skirting the edge of distress between games. Since spec 042
        // each need's pressure is weighed first ([behavior.comfort_weight],
        // all 1.0 = exactly the classic unweighted check) -- so a demo config
        // can make a cat food-attentive without tripping seriousness on a
        // routine bath peak. The weights move only THIS trigger: getting
        // serious means the same scored selection the sensible cat uses, read
        // from unweighted needs -- a playful personality is a different life,
        // never a different immune system.
        let weights = &ctx.config.behavior.comfort_weight;
        let weighted_pressure = crate::needs::NeedKind::ALL
            .iter()
            .map(|kind| weights.get(*kind) * ctx.me.needs.get(*kind))
            .fold(0.0f32, f32::max);
        if weighted_pressure >= ctx.config.behavior.playful_comfort {
            // Spec 047 site 2: getting serious still honors the consent
            // line — the same scored selection the sensible cat uses, but
            // a blocked friend never enters its playmate scan.
            return pursue(ctx, selection::choose_consenting(ctx));
        }

        // (Purring left the proposal surface in spec 011: the engine rumbles
        // a contented cat in the background, no turn required.)

        // The game is wherever the nearest playmate worth having is -- critter
        // or friend, minus anything already written off as uncatchable. Shared
        // rules (viability, give-up, the solo backstop) live in `selection`.
        // (The chase-announce lottery died in spec 028: the shared announce
        // rule speaks WantPlay whenever it is genuinely armed and legal.)
        selection::scored_play_action(ctx)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::action::TargetRef;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::needs::NeedKind;
    use crate::test_support::decision_context;

    #[tokio::test]
    async fn a_playful_cat_chases_a_bug_it_has_no_need_to_chase() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            // Mildly hungry, below the comfort line (55) -- a sensible cat would
            // already be walking to the food; a playful one has better things to do.
            world.kitties[idx].needs.add(NeedKind::Eat, 40.0);
            world.push_element(Element {
                id: 600,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(12, 2), // present, but not underfoot
                ttl: None,
            });
            world.push_element(Element {
                id: 601,
                kind: ElementKind::Bug,
                pos: Position::new(9, 9),
                ttl: Some(100),
            });
        });

        assert_eq!(
            Playful.decide_action(&ctx),
            Action::Chase(TargetRef::Element { id: 601 }),
            "the bug wins over distant food"
        );
    }

    // ---- Spec 047: the consent gate on playful's own paths ------------

    /// Pins friend 2's needs exactly: blocked at line 30 (eat 40 tops
    /// play 10) unless a test overrides.
    fn stage_burdened_friend(world: &mut crate::world::World, pos: Position) {
        let f = world.kitty_index(2).unwrap();
        world.kitties[f].pos = pos;
        world.kitties[f].needs = crate::needs::Needs::default();
        world.kitties[f].needs.eat = crate::needs::Need::new(40.0);
        world.kitties[f].needs.play = crate::needs::Need::new(10.0);
    }

    fn set_consent_line(ctx: &mut crate::behavior::DecisionContext, line: f32) {
        std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .behavior
            .consent_line = line;
    }

    /// Spec 047 site 2 (get-serious, T009): above the comfort line with
    /// play the winning need, the gate still holds — the cat does not
    /// walk after the burdened friend, it pounces at nothing where it
    /// stands (the Article III degradation: play stays satisfiable,
    /// solo — assert the positive, analysis C1).
    #[tokio::test]
    async fn a_serious_playful_cat_honors_the_consent_line() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            // Over comfort (55): serious. Play is the only pressure, so it
            // wins the scored selection.
            world.kitties[idx].needs.add(NeedKind::Play, 80.0);
            // In reach (solo_play_reach 8) but NOT adjacent: the
            // opportunism rung cannot fire, isolating the get-serious path.
            stage_burdened_friend(world, Position::new(5, 8));
        });
        set_consent_line(&mut ctx, 30.0);
        assert_eq!(
            Playful.decide_action(&ctx),
            Action::play_solo(),
            "play is the errand, the friend is off the table: solo, never a chase"
        );
    }

    /// Spec 047 site 3 (opportunism, T011): a burdened idle friend within
    /// paw's reach is NOT batted into a game. With real play urge (over
    /// `worth_a_detour` 30, under comfort 55), no critter anywhere and the
    /// only friend blocked, the whole decision degrades to solo play —
    /// adjacency is not a bypass, and play stays satisfiable (analysis C1).
    #[tokio::test]
    async fn an_adjacent_burdened_friend_is_not_batted_into_a_game() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 45.0);
            stage_burdened_friend(world, Position::new(5, 6)); // adjacent
        });
        set_consent_line(&mut ctx, 30.0);
        assert_eq!(
            Playful.decide_action(&ctx),
            Action::play_solo(),
            "the opportunism rung must skip the burdened friend; solo, not conscription"
        );
    }

    /// Spec 047, medium-review finding 1 — ACCEPTED BY THE OWNER
    /// 2026-09-01 and pinned here as INTENDED: blocking the only playmate
    /// re-prices play as solo (distance 0, the pre-047 absent-friend
    /// rule), which near the play/eat crossover can flip one tick from
    /// "walk to the bowl" to "pounce at nothing first". Rationale on
    /// record: the scripted cat is a training teacher; marginal scoring
    /// detours wash out in training — what matters is that considering
    /// the OTHER cat's needs is modeled at all, so it can be learned.
    /// Bounded: solo play relieves play, eat keeps rising, safeguard
    /// urgency buries play past 75. Experiments' R2 (hungry-play share)
    /// watches the aggregate.
    #[tokio::test]
    async fn blocking_the_only_playmate_may_buy_solo_play_a_tick_over_eating() {
        let stage = |line: f32| {
            let mut ctx = decision_context(|world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = Position::new(5, 5);
                world.kitties[idx].needs = crate::needs::Needs::default();
                world.kitties[idx].needs.eat = crate::needs::Need::new(60.0); // serious (comfort 55)
                world.kitties[idx].needs.play = crate::needs::Need::new(58.0);
                world.push_element(Element {
                    id: 610,
                    kind: ElementKind::Chow { servings: 5 },
                    pos: Position::new(11, 5), // 6 tiles: eat pays the walk
                    ttl: None,
                });
                stage_burdened_friend(world, Position::new(5, 10)); // 5 tiles, in reach
            });
            set_consent_line(&mut ctx, line);
            Playful.decide_action(&ctx)
        };
        assert!(
            matches!(stage(0.0), Action::Move { .. }),
            "line off: play pays the 5-tile walk to the friend, eat wins"
        );
        assert_eq!(
            stage(30.0),
            Action::play_solo(),
            "line 30: the friend is blocked, play prices as solo (0 tiles) and outscores eat for a tick"
        );
    }

    #[tokio::test]
    async fn a_playful_cat_still_eats_the_food_it_is_standing_beside() {
        // Opportunism: adjacent food + real hunger beats the game, even below the
        // comfort line. This is the fix for the happiness tax.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Eat, 40.0);
            world.push_element(Element {
                id: 600,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(2, 3), // right there
                ttl: None,
            });
            world.push_element(Element {
                id: 601,
                kind: ElementKind::Bug,
                pos: Position::new(9, 9),
                ttl: Some(100),
            });
        });

        assert_eq!(Playful.decide_action(&ctx), Action::Eat);
    }

    #[tokio::test]
    async fn a_need_past_the_comfort_line_beats_the_game() {
        // Above playful_comfort (default 55) but far below the safeguard: the old
        // behavior would have kept playing; the rebalanced one gets serious early.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Drink, 60.0);
            world.push_element(Element {
                id: 602,
                kind: ElementKind::Water,
                pos: Position::new(12, 2),
                ttl: None,
            });
            world.push_element(Element {
                id: 603,
                kind: ElementKind::Bug,
                pos: Position::new(3, 3),
                ttl: Some(100),
            });
        });

        let action = Playful.decide_action(&ctx);
        assert!(
            matches!(action, Action::Move { .. } | Action::Meow { .. }),
            "expected a step toward water (or a meow about it), got {action:?}"
        );
    }

    #[tokio::test]
    async fn an_adjacent_critter_gets_played_with() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.push_element(Element {
                id: 602,
                kind: ElementKind::Greeble {
                    heading: crate::grid::Direction::North,
                },
                pos: Position::new(5, 6),
                ttl: Some(50),
            });
        });

        assert_eq!(
            Playful.decide_action(&ctx),
            Action::play_with(TargetRef::Element { id: 602 })
        );
    }

    #[tokio::test]
    async fn a_playful_cat_alone_pounces_at_nothing() {
        // Urgent play, every playmate far beyond reach: a playful cat
        // entertains itself sooner than pacing after the horizon.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Play, 80.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(15, 15);
        });
        ctx.me
            .set_meow_cooldown(crate::meow::MessageKind::WantPlay, u64::MAX);

        assert_eq!(Playful.decide_action(&ctx), Action::play_solo());
    }

    #[tokio::test]
    async fn a_desperate_need_overrides_playing() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 99.0);
            world.push_element(Element {
                id: 603,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(5, 5),
                ttl: None,
            });
            world.push_element(Element {
                id: 604,
                kind: ElementKind::Bug,
                pos: Position::new(5, 4),
                ttl: Some(100),
            });
        });

        let action = Playful.decide_action(&ctx);
        assert!(
            matches!(action, Action::Eat | Action::Meow { .. }),
            "a starving cat eats (or asks for food) rather than plays; got {action:?}"
        );
    }
}

/// Spec 042 US2: the weighted get-serious trigger's guard battery.
/// Both red-first directions, the all-1.0 identity pin, and the
/// trigger-only pin (US2/AC4).
#[cfg(test)]
mod comfort_weight_tests {
    use super::*;
    use crate::behavior::selection;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::needs::NeedKind;
    use crate::test_support::decision_context;
    use crate::TargetRef;

    /// A playful cat with one pressing need and food far off -- the
    /// serious/playful boundary stage. Comfort stays at the default 55.
    fn stage(kind: NeedKind, pressure: f32) -> crate::behavior::DecisionContext {
        decision_context(move |world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(kind, pressure);
            world.push_element(Element {
                id: 810,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(12, 2),
                ttl: None,
            });
            world.push_element(Element {
                id: 811,
                kind: ElementKind::Bug,
                pos: Position::new(6, 2),
                ttl: Some(100),
            });
        })
    }

    fn weighted(
        mut ctx: crate::behavior::DecisionContext,
        f: impl FnOnce(&mut crate::config::ComfortWeights),
    ) -> crate::behavior::DecisionContext {
        f(&mut std::sync::Arc::get_mut(&mut ctx.config)
            .unwrap()
            .behavior
            .comfort_weight);
        ctx
    }

    fn is_serious(ctx: &crate::behavior::DecisionContext) -> bool {
        // The observable boundary: a serious cat walks to the chow, a
        // playful one goes for the bug.
        match Playful.decide_action(ctx) {
            Action::Chase(TargetRef::Element { id }) => id == 810,
            Action::Move { .. } => true, // walking to relief
            Action::Eat | Action::Drink | Action::Sleep { .. } => true,
            // A serious bath cat grooms right where it stands.
            Action::Groom { .. } => true,
            _ => false,
        }
    }

    /// (a) An up-weighted need trips the line the unweighted check ignores.
    #[test]
    fn an_upweighted_eat_gets_serious_below_the_raw_comfort_line() {
        // eat 45: below comfort 55 raw, above it at weight 1.5 (67.5).
        let plain = stage(NeedKind::Eat, 45.0);
        assert!(!is_serious(&plain), "unweighted: still playing at 45");
        let ctx = weighted(stage(NeedKind::Eat, 45.0), |w| w.eat = 1.5);
        assert!(is_serious(&ctx), "weighted 1.5: 45 x 1.5 = 67.5 >= 55");
    }

    /// (b) A down-weighted need stays playful where the raw check trips.
    #[test]
    fn a_downweighted_bath_stays_playful_above_the_raw_comfort_line() {
        // bath 60: above comfort 55 raw, below it at weight 0.5 (30).
        let plain = stage(NeedKind::Bath, 60.0);
        assert!(is_serious(&plain), "unweighted: 60 trips the line");
        let ctx = weighted(stage(NeedKind::Bath, 60.0), |w| w.bath = 0.5);
        assert!(!is_serious(&ctx), "weighted 0.5: 60 x 0.5 = 30 < 55");
    }

    /// (c) The identity pin: all-1.0 weights are exactly the classic check.
    #[test]
    fn identity_weights_reproduce_the_unweighted_decision() {
        for (kind, pressure) in [
            (NeedKind::Eat, 40.0),
            (NeedKind::Eat, 54.9),
            (NeedKind::Eat, 55.0),
            (NeedKind::Bath, 70.0),
            (NeedKind::Drink, 30.0),
        ] {
            let plain = stage(kind, pressure);
            let idented = weighted(stage(kind, pressure), |_| {});
            assert_eq!(
                is_serious(&plain),
                is_serious(&idented),
                "{kind:?}@{pressure} must decide identically at identity weights"
            );
        }
    }

    /// (d) Trigger-only (US2/AC4): when the weighted check trips, what the
    /// serious cat does is exactly the unweighted scored selection.
    #[test]
    fn the_weights_move_the_trigger_never_the_serious_choice() {
        let ctx = weighted(stage(NeedKind::Eat, 45.0), |w| w.eat = 1.5);
        assert!(is_serious(&ctx), "the weighted trigger trips");
        assert_eq!(
            Playful.decide_action(&ctx),
            pursue(&ctx, selection::choose(&ctx)),
            "the serious action is the shared unweighted selection"
        );
    }
}
