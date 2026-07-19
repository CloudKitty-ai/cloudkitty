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

use super::needs_driven::{pursue, take_what_is_here};
use super::{selection, Behavior, DecisionContext};
use crate::action::{Action, TargetRef};
use crate::meow::MessageKind;

pub struct Playful;

#[async_trait]
impl Behavior for Playful {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // Opportunism is good sense, not a personality trait: a playful cat still
        // eats the food it is standing next to before running off after a bug.
        if let Some(action) = take_what_is_here(ctx) {
            return action;
        }

        let (_, pressure) = ctx.me.needs.highest_pressure();

        // Some things cannot wait, even for a good game. The comfort line is
        // configurable ([behavior] playful_comfort, default 55): well below the
        // safeguard threshold, so a playful cat keeps itself in reasonable shape
        // instead of skirting the edge of distress between games. Getting serious
        // means the same scored selection the sensible cat uses -- a playful
        // personality is a different life, never a different immune system.
        if pressure >= ctx.config.behavior.playful_comfort {
            return pursue(ctx, selection::choose_need(ctx));
        }

        // A cat this happy should say so now and then.
        if ctx.me.happiness > ctx.config.thresholds.purr
            && ctx.me.can_meow(MessageKind::Purr, ctx.world.tick)
            && ctx.rng.gen_bool(0.06)
        {
            return Action::Purr;
        }

        // The game is wherever the nearest playmate worth having is -- critter
        // or friend, minus anything already written off as uncatchable. Shared
        // rules (viability, give-up, the solo backstop) live in `selection`.
        let play = selection::play_action(ctx);

        // Announce the plan occasionally before setting off after a friend.
        if let Action::Chase(TargetRef::Kitty { .. }) = play {
            if ctx.me.can_meow(MessageKind::WantPlay, ctx.world.tick) && ctx.rng.gen_bool(0.15) {
                return Action::Meow {
                    message: MessageKind::WantPlay,
                };
            }
        }

        play
    }

    fn is_builtin(&self) -> bool {
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
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
            Playful.decide(&ctx).await,
            Action::Chase(TargetRef::Element { id: 601 }),
            "the bug wins over distant food"
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

        assert_eq!(Playful.decide(&ctx).await, Action::Eat);
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

        let action = Playful.decide(&ctx).await;
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
            Playful.decide(&ctx).await,
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

        assert_eq!(Playful.decide(&ctx).await, Action::play_solo());
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

        let action = Playful.decide(&ctx).await;
        assert!(
            matches!(action, Action::Eat | Action::Meow { .. }),
            "a starving cat eats (or asks for food) rather than plays; got {action:?}"
        );
    }
}
