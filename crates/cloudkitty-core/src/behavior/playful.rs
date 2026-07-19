//! A cat who would rather be playing.
//!
//! `Playful` exists to prove the point of pluggable behavior: given the same world,
//! a kitty running this strategy lives a visibly different life from one running
//! [`NeedsDriven`](super::NeedsDriven). It chases bugs and greebles it has no
//! particular reason to chase, pesters its friends for a game, and only attends to
//! its needs when one becomes genuinely pressing.
//!
//! It is still a good cat: past the urgency threshold it defers to the sensible
//! behavior, so being playful never means being neglected.

use async_trait::async_trait;

use super::needs_driven::pursue;
use super::{Behavior, DecisionContext};
use crate::action::{Action, TargetRef};
use crate::meow::MessageKind;

pub struct Playful;

#[async_trait]
impl Behavior for Playful {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        let (need, pressure) = ctx.me.needs.highest_pressure();

        // Some things cannot wait, even for a good game. The line is the world's
        // own safeguard threshold rather than a number invented here: past it the
        // world is already obliged to provide relief, so a cat that keeps playing
        // is a cat heading for distress.
        if pressure >= ctx.config.thresholds.safeguard {
            return pursue(ctx, need);
        }

        let me = &ctx.me;
        let world = &ctx.world;

        // Bugs and greebles first -- and greebles count, even though no human
        // watching will ever see what this cat is so excited about.
        if let Some(critter) = world.nearest_critter(me.pos) {
            return if me.pos.is_adjacent(&critter.pos) {
                Action::Play(TargetRef::Element { id: critter.id })
            } else {
                Action::Chase(TargetRef::Element { id: critter.id })
            };
        }

        // No critters? Rope a friend into it.
        if let Some(friend) = world.nearest_friend(me.id, me.pos) {
            if me.pos.is_adjacent(&friend.pos) {
                return Action::Play(TargetRef::Kitty { id: friend.id });
            }
            // Announce the plan occasionally, then go and find them.
            if ctx.me.can_meow(MessageKind::WantPlay, world.tick) && ctx.rng.gen_bool(0.15) {
                return Action::Meow {
                    message: MessageKind::WantPlay,
                };
            }
            return Action::Chase(TargetRef::Kitty { id: friend.id });
        }

        // An empty world: fall back to being sensible.
        pursue(ctx, need)
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
            // Mildly hungry -- a sensible cat would go and eat.
            world.kitties[idx].needs.add(NeedKind::Eat, 60.0);
            world.push_element(Element {
                id: 600,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(2, 3),
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
            "the bug wins over the food"
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
            Action::Play(TargetRef::Element { id: 602 })
        );
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
