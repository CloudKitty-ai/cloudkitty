//! The needy presets (spec 067, `contracts/needy-law.md` §6): `needy` and
//! `needy_hold`, two research-only scripted seats. Both decide exactly as
//! the Gen 2 `teacher` preset until an episode's MASK is up; under a mask
//! they run the same ladder on a view where the masked needs read 0, then
//! drop any choice that would still relieve a masked need. Calling stays
//! on (owner ruling "A"): the message channel is the teacher's, read off
//! the UNMASKED kitty, so a needy cat wants, calls, and refuses relief.
//!
//! This half is advice quality, not law: the engine's needy verdict and
//! onset sweep (`World::needy_verdict`, research D5) enforce the mask on
//! every proposer; the preset only spends its masked turns on other needs
//! instead of being refused (research D14). The two presets decide
//! identically — the only difference, the release rule, lives in the
//! engine's schedule (`crate::needy::NeedyState::hold`).
//!
//! Neither preset teaches (`teaches() == false`, FR-010): its schedule is
//! private state no student can see (design doctrine rule 5).

use async_trait::async_trait;

use super::teacher::Teacher;
use super::{Behavior, DecisionContext};
use crate::action::Action;
use crate::needs::NeedKind;
use crate::needy::{proposer_relief, NeedSet};
use crate::seam::Decision;

/// Both needy registrations (`crate::needy::NAME`, `crate::needy::HOLD_NAME`).
#[derive(Debug, Clone, Copy, Default)]
pub struct Needy;

#[async_trait]
impl Behavior for Needy {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        let mask = ctx.me.needy.as_ref().map(|s| s.mask()).unwrap_or_default();
        if mask.is_empty() {
            // Outside an episode the seat IS the teacher, turn for turn.
            return Teacher::GEN2.decide(ctx).await;
        }
        let action = filter(Teacher::GEN2.decide_action(&masked_view(ctx, mask)), mask);
        let mut decision = Decision::from_legacy(action);
        if decision.message.is_none() {
            // Calling stays on: the want is read off the real kitty.
            decision.message = super::announce(ctx);
        }
        decision
    }

    fn is_builtin(&self) -> bool {
        true
    }

    fn teaches(&self) -> bool {
        false
    }
}

/// The ladder's view under a mask: the kitty with every masked need read
/// as 0, the same world and config, and a fork of the turn's stream (the
/// preset consumes nothing after the ladder, so the outcome is the
/// ladder's on this turn's stream).
fn masked_view(ctx: &DecisionContext, mask: NeedSet) -> DecisionContext {
    let mut me = ctx.me.clone();
    for kind in mask.iter() {
        let level = me.needs.get(kind);
        me.needs.add(kind, -level);
    }
    DecisionContext {
        me,
        world: ctx.world.clone(),
        rng: ctx.rng.fork(),
        config: ctx.config.clone(),
    }
}

/// The post-filter (needy-law §6): a choice whose relief meets the mask —
/// a groom response paying the groomer's masked cuddle, a co-sleep or
/// co-rest under a cuddle mask, luxury play (or the chase that pursues it)
/// under a play mask — becomes `Idle`, except a co-sleep while sleep is
/// unmasked, which becomes sleep alone (the kitty still sleeps). A co-rest
/// never becomes a solo rest: that relieves nothing and only holds the
/// kitty to the rest minimum.
fn filter(action: Action, mask: NeedSet) -> Action {
    let pursues_masked_play = matches!(action, Action::Chase(_)) && mask.contains(NeedKind::Play);
    if !proposer_relief(&action).meets(mask) && !pursues_masked_play {
        return action;
    }
    match action {
        Action::Sleep { with: Some(_) } if !mask.contains(NeedKind::Sleep) => {
            Action::Sleep { with: None }
        }
        _ => Action::Idle,
    }
}

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use super::*;
    use crate::action::TargetRef;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::meow::MessageKind;
    use crate::needy::{NeedyState, Phase};
    use crate::rng::DecisionRng;
    use crate::test_support::{decision_context_for, test_config};
    use crate::world::World;

    fn state(phase: Phase, next: &[NeedKind]) -> NeedyState {
        let mut s = NeedyState::new(1, 1, false, &Default::default());
        s.phase = phase;
        s.next = NeedSet::from_kinds(next);
        s
    }

    fn held(masked: &[NeedKind]) -> Option<NeedyState> {
        Some(state(
            Phase::Held {
                onset: 0,
                masked: NeedSet::from_kinds(masked),
            },
            masked,
        ))
    }

    fn decide(ctx: &DecisionContext) -> Decision {
        futures::executor::block_on(Needy.decide(ctx))
    }

    /// FR-006: outside an episode the needy seat decides exactly as the
    /// teacher — on 200 contexts from a live world, with the pending set
    /// covering every need (so a preset that read the PENDING set as a
    /// mask would diverge everywhere).
    #[test]
    fn with_no_mask_up_needy_decides_exactly_as_teacher() {
        let config = Arc::new(test_config());
        let registry = super::super::BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let mut compared = 0;
        for tick in 0..100u64 {
            let snapshot = world.snapshot();
            for id in [1, 2] {
                let mut me = snapshot.kitty(id).unwrap().clone();
                me.needy = Some(state(
                    Phase::Resting {
                        next_onset: u64::MAX,
                    },
                    &NeedKind::ALL,
                ));
                let ctx = |me: crate::kitty::Kitty| DecisionContext {
                    me,
                    world: Arc::new(snapshot.fog_for(id, config.vision.radius)),
                    rng: DecisionRng::from_seed(tick * 7 + u64::from(id)),
                    config: config.clone(),
                };
                let needy = decide(&ctx(me.clone()));
                let teacher = futures::executor::block_on(Teacher::GEN2.decide(&ctx(me)));
                assert_eq!(
                    needy, teacher,
                    "with no mask up the needy seat decides as the teacher (tick {tick}, kitty {id})"
                );
                compared += 1;
            }
            futures::executor::block_on(world.tick(&registry, &config));
        }
        assert_eq!(compared, 200);
    }

    #[test]
    fn under_a_play_mask_a_comfortable_kitty_never_plays() {
        for seed in 0..50u64 {
            let mut ctx = decision_context_for(1, |world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].pos = Position::new(5, 5);
                world.kitties[idx].needs.add(NeedKind::Play, 70.0);
                world.push_element(Element {
                    id: 950,
                    kind: ElementKind::Bug,
                    pos: Position::new(5, 6),
                    ttl: None,
                });
            });
            ctx.rng = DecisionRng::from_seed(seed);
            ctx.me.needy = held(&[NeedKind::Play]);
            let decision = decide(&ctx);
            assert!(
                !matches!(decision.activity, Action::Play { .. } | Action::Chase(_)),
                "never Play under a Play mask (seed {seed}): {:?}",
                decision.activity
            );
        }
    }

    #[test]
    fn under_an_eat_mask_a_hungry_kitty_turns_to_its_next_need() {
        let mut ctx = decision_context_for(1, |world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.kitties[idx].needs.add(NeedKind::Drink, 70.0);
            world.push_element(Element {
                id: 951,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(4, 5),
                ttl: None,
            });
            world.push_element(Element {
                id: 952,
                kind: ElementKind::Water,
                pos: Position::new(6, 5),
                ttl: None,
            });
        });
        ctx.me.needy = held(&[NeedKind::Eat]);
        assert_eq!(
            decide(&ctx).activity,
            Action::Drink,
            "the serious choice falls to the next need"
        );
    }

    #[test]
    fn under_a_cuddle_mask_a_sleepy_kitty_sleeps_alone() {
        let build = || {
            decision_context_for(1, |world| {
                world.elements.clear();
                let a = world.kitty_index(1).unwrap();
                world.kitties[a].pos = Position::new(5, 5);
                world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
                world.kitties[a].needs.add(NeedKind::Cuddle, 60.0);
                let b = world.kitty_index(2).unwrap();
                world.kitties[b].pos = Position::new(5, 6);
            })
        };
        let unmasked = futures::executor::block_on(Teacher::GEN2.decide(&build()));
        assert_eq!(
            unmasked.activity,
            Action::Sleep { with: Some(2) },
            "staged: the teacher would co-sleep here"
        );
        let mut ctx = build();
        ctx.me.needy = held(&[NeedKind::Cuddle]);
        assert_eq!(
            decide(&ctx).activity,
            Action::Sleep { with: None },
            "under a cuddle mask the kitty sleeps alone"
        );
    }

    /// FR-005 / FR-007 (owner "A"): calling stays on. The want is read off
    /// the REAL kitty — eat armed, eat its top need, no food in sight or in
    /// memory, so WantEat is legal under the fog want law — while the
    /// masked view (eat read 0, drink on top) would make it illegal.
    #[test]
    fn under_an_eat_mask_calling_stays_on_with_law_named_words() {
        let mut ctx = decision_context_for(1, |world| {
            world.elements.clear();
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].needs.add(NeedKind::Eat, 80.0);
            world.kitties[a].needs.add(NeedKind::Drink, 10.0);
            world.kitties[a].announce_armed.insert(NeedKind::Eat);
        });
        let unmasked = futures::executor::block_on(Teacher::GEN2.decide(&ctx));
        assert_eq!(
            unmasked.message,
            Some(MessageKind::WantEat),
            "staged: the teacher calls for food here"
        );
        ctx.me.needy = held(&[NeedKind::Eat]);
        let message = decide(&ctx).message;
        assert_eq!(
            message,
            Some(MessageKind::WantEat),
            "calling stays on under the mask"
        );
        let kind = message.unwrap();
        assert!(
            kind.related_need().is_some()
                || MessageKind::HERE_KINDS.contains(&kind)
                || matches!(kind, MessageKind::Purr | MessageKind::WaitForMe),
            "law-named words only (FR-007): {kind:?}"
        );
    }

    #[test]
    fn a_groom_response_under_a_cuddle_mask_is_dropped() {
        // The groom response pays the groomer's own cuddle: the zeroed view
        // cannot stop that rung (it answers a FRIEND's want), the filter does.
        assert_eq!(
            filter(
                Action::Groom { target: Some(2) },
                NeedSet::from_kinds(&[NeedKind::Cuddle])
            ),
            Action::Idle
        );
        assert_eq!(
            filter(
                Action::Groom { target: Some(2) },
                NeedSet::from_kinds(&[NeedKind::Bath])
            ),
            Action::Groom { target: Some(2) },
            "grooming a friend relieves the FRIEND's bath, not the groomer's"
        );
        assert_eq!(
            filter(
                Action::Chase(TargetRef::Element { id: 9 }),
                NeedSet::from_kinds(&[NeedKind::Play])
            ),
            Action::Idle,
            "a chase pursues play"
        );
    }

    #[test]
    fn under_a_cuddle_mask_a_co_rest_becomes_idle_never_a_solo_rest() {
        // needy-law §6: only a co-sleep keeps a solo form (sleep still
        // relieves); a solo rest relieves nothing and would only hold the
        // kitty to the rest minimum (the answered-cuddle-call rung).
        let cuddle = NeedSet::from_kinds(&[NeedKind::Cuddle]);
        assert_eq!(
            filter(Action::Rest { with: Some(2) }, cuddle),
            Action::Idle,
            "a co-rest under a cuddle mask is dropped, not kept alone"
        );
        assert_eq!(
            filter(Action::Sleep { with: Some(2) }, cuddle),
            Action::Sleep { with: None },
            "a co-sleep under a cuddle mask sleeps alone"
        );
        assert_eq!(
            filter(
                Action::Sleep { with: Some(2) },
                NeedSet::from_kinds(&[NeedKind::Cuddle, NeedKind::Sleep])
            ),
            Action::Idle,
            "with sleep masked too, nothing is left to keep"
        );
    }
}
