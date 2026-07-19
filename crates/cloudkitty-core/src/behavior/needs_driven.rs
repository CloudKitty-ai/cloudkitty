//! The default behavior, and the engine's fallback.
//!
//! A sensible cat: attend to whatever is bothering you most, wander contentedly
//! when nothing is, mention it when something gets urgent, and purr when life is
//! good.
//!
//! This behavior is *total* -- there is no world state for which it fails to
//! return a reasonable action. That is precisely why the engine can fall back to
//! it when another behavior times out, panics, or misbehaves.

use async_trait::async_trait;

use super::{Behavior, DecisionContext};
use crate::action::{Action, TargetRef};
use crate::element::ElementType;
use crate::grid::Direction;
use crate::meow::MessageKind;
use crate::needs::NeedKind;

/// Worth topping up a need that is already within reach, rather than walking off
/// and having to come back for it.
const WORTH_A_DETOUR: f32 = 30.0;

/// Below the safeguard threshold a cat weighs convenience against pressure; each
/// tile of travel is worth this much need.
const TILE_COST: f32 = 1.0;

pub struct NeedsDriven;

#[async_trait]
impl Behavior for NeedsDriven {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // Never walk away from something you were going to want anyway.
        if let Some(action) = take_what_is_here(ctx) {
            return action;
        }

        let (most_pressing, pressure) = ctx.me.needs.highest_pressure();

        // Speak up when something is getting urgent -- but not every single tick.
        if let Some(message) = MessageKind::for_need(most_pressing) {
            if pressure >= ctx.config.meow.urgent_need_threshold
                && ctx.me.can_meow(message, ctx.world.tick)
                && ctx.rng.gen_bool(0.3)
            {
                return Action::Meow { message };
            }
        }

        // A contented cat purrs now and then.
        if ctx.me.happiness > ctx.config.thresholds.purr
            && ctx.me.can_meow(MessageKind::Purr, ctx.world.tick)
            && ctx.rng.gen_bool(0.06)
        {
            return Action::Purr;
        }

        // Nothing pressing: potter about.
        if pressure < 20.0 && ctx.rng.gen_bool(0.4) {
            return wander(ctx);
        }

        // Once a need is urgent enough that the world owes relief, deal with that
        // one and nothing else. Below that, prefer whatever is convenient, so a cat
        // does not trek across the world for a need it could meet on the way.
        let need = if pressure >= ctx.config.thresholds.safeguard {
            most_pressing
        } else {
            most_convenient(ctx, pressure)
        };

        pursue(ctx, need)
    }

    fn is_builtin(&self) -> bool {
        true
    }
}

/// Eat, drink or nap when the means are already underfoot and the need is real.
/// Shared with `Playful`: opportunism is good sense, not a personality trait.
pub(crate) fn take_what_is_here(ctx: &DecisionContext) -> Option<Action> {
    let me = &ctx.me;

    if me.needs.get(NeedKind::Eat) >= WORTH_A_DETOUR
        && ctx
            .world
            .elements_of(ElementType::Chow)
            .any(|e| me.pos.is_adjacent(&e.pos))
    {
        return Some(Action::Eat);
    }

    if me.needs.get(NeedKind::Drink) >= WORTH_A_DETOUR
        && ctx
            .world
            .elements_of(ElementType::Water)
            .any(|e| me.pos.is_adjacent(&e.pos))
    {
        return Some(Action::Drink);
    }

    // A sunbeam you are already sitting in is too good to waste.
    if me.needs.get(NeedKind::Sleep) >= WORTH_A_DETOUR
        && ctx.world.element_at(me.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam)
    {
        return Some(Action::Sleep { with: None });
    }

    None
}

/// Among the needs that are nearly as pressing as the worst one, pick whichever is
/// cheapest to actually do something about.
fn most_convenient(ctx: &DecisionContext, top_pressure: f32) -> NeedKind {
    let mut best = NeedKind::ALL[0];
    let mut best_score = f32::NEG_INFINITY;

    for kind in NeedKind::ALL {
        let pressure = ctx.me.needs.get(kind);
        // Only consider needs in the same league as the most pressing one.
        if pressure + 20.0 < top_pressure {
            continue;
        }
        let score = pressure - TILE_COST * travel_distance(ctx, kind) as f32;
        if score > best_score {
            best_score = score;
            best = kind;
        }
    }

    best
}

/// How far this cat would have to walk to do something about `need`.
fn travel_distance(ctx: &DecisionContext, need: NeedKind) -> u32 {
    let me = &ctx.me;
    let nearest = |kind: ElementType| {
        ctx.world
            .nearest_element(me.pos, kind)
            .map(|e| me.pos.chebyshev_distance(&e.pos))
    };

    match need {
        // Grooming and sleeping can happen anywhere at all.
        NeedKind::Bath | NeedKind::Sleep => 0,
        NeedKind::Eat => nearest(ElementType::Chow).unwrap_or(u32::MAX / 2),
        NeedKind::Drink => nearest(ElementType::Water).unwrap_or(u32::MAX / 2),
        NeedKind::Play => ctx
            .world
            .nearest_critter(me.pos)
            .map(|e| me.pos.chebyshev_distance(&e.pos))
            .or_else(|| {
                ctx.world
                    .nearest_friend(me.id, me.pos)
                    .map(|k| me.pos.chebyshev_distance(&k.pos))
            })
            .unwrap_or(u32::MAX / 2),
        NeedKind::Cuddle => ctx
            .world
            .nearest_friend(me.id, me.pos)
            .map(|k| me.pos.chebyshev_distance(&k.pos))
            .unwrap_or(u32::MAX / 2),
    }
}

/// Take one step toward relieving `need`.
pub(crate) fn pursue(ctx: &DecisionContext, need: NeedKind) -> Action {
    let me = &ctx.me;
    let world = &ctx.world;

    match need {
        NeedKind::Eat => seek_element(ctx, ElementType::Chow, Action::Eat),
        NeedKind::Drink => seek_element(ctx, ElementType::Water, Action::Drink),

        NeedKind::Bath => Action::Groom { target: None },

        NeedKind::Sleep => {
            // Already in a sunbeam? Perfect.
            if world.element_at(me.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam) {
                return Action::Sleep { with: None };
            }
            match world.nearest_element(me.pos, ElementType::Sunbeam) {
                // Worth walking to, if it is not an expedition.
                Some(sunbeam) if me.pos.chebyshev_distance(&sunbeam.pos) <= 8 => {
                    step_toward(ctx, sunbeam.pos)
                }
                // Otherwise a nap right here will do; a friend nearby makes it cosier.
                _ => Action::Sleep {
                    with: adjacent_friend(ctx),
                },
            }
        }

        NeedKind::Play => {
            if let Some(critter) = world.nearest_critter(me.pos) {
                return if me.pos.is_adjacent(&critter.pos) {
                    Action::Play(TargetRef::Element { id: critter.id })
                } else {
                    Action::Chase(TargetRef::Element { id: critter.id })
                };
            }
            // No bugs about? Friends are just as fun.
            match world.nearest_friend(me.id, me.pos) {
                Some(friend) if me.pos.is_adjacent(&friend.pos) => {
                    Action::Play(TargetRef::Kitty { id: friend.id })
                }
                Some(friend) => Action::Chase(TargetRef::Kitty { id: friend.id }),
                None => Action::Idle,
            }
        }

        NeedKind::Cuddle => match world.nearest_friend(me.id, me.pos) {
            Some(friend) if me.pos.is_adjacent(&friend.pos) => Action::Rest {
                with: Some(friend.id),
            },
            // Walking over for a cuddle is not a chase; this cat is not playing.
            Some(friend) => step_toward(ctx, friend.pos),
            None => Action::Rest { with: None },
        },
    }
}

/// Use the resource if it is within reach, otherwise walk toward the nearest one.
fn seek_element(ctx: &DecisionContext, kind: ElementType, use_it: Action) -> Action {
    let me = &ctx.me;
    let usable = ctx
        .world
        .elements_of(kind)
        .filter(|e| me.pos.is_adjacent(&e.pos))
        .min_by_key(|e| (me.pos.chebyshev_distance(&e.pos), e.id));

    if usable.is_some() {
        return use_it;
    }

    match ctx.world.nearest_element(me.pos, kind) {
        Some(target) => step_toward(ctx, target.pos),
        // The safeguard will have provided something by the next environment
        // phase; until then, there is nothing useful to do about it.
        None => Action::Idle,
    }
}

/// One step in the general direction of somewhere.
fn step_toward(ctx: &DecisionContext, target: crate::grid::Position) -> Action {
    match Direction::toward(ctx.me.pos, target) {
        Some(direction) => Action::move_to(direction),
        None => Action::Idle,
    }
}

fn adjacent_friend(ctx: &DecisionContext) -> Option<crate::kitty::KittyId> {
    ctx.world
        .others(ctx.me.id)
        .find(|k| ctx.me.pos.is_adjacent(&k.pos))
        .map(|k| k.id)
}

fn wander(ctx: &DecisionContext) -> Action {
    let direction = ctx
        .rng
        .choose(&Direction::ALL)
        .copied()
        .unwrap_or(Direction::North);
    Action::move_to(direction)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::behavior::Behavior;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::test_support::decision_context;

    #[tokio::test]
    async fn a_hungry_cat_beside_chow_eats() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 500,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 5),
                ttl: None,
            });
        });
        // Remove the randomness of meowing about it first.
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);

        assert_eq!(NeedsDriven.decide(&ctx).await, Action::Eat);
    }

    #[tokio::test]
    async fn a_hungry_cat_far_from_chow_walks_toward_it_without_chasing_it() {
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(1, 1);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 501,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(10, 10),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);

        // A bowl of food does not run away, so this is a walk, not a chase.
        assert_eq!(
            NeedsDriven.decide(&ctx).await,
            Action::move_to(crate::grid::Direction::East)
        );
    }

    #[tokio::test]
    async fn a_dirty_cat_grooms_itself() {
        let ctx = decision_context(|world| {
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Bath, 99.0);
        });
        assert_eq!(
            NeedsDriven.decide(&ctx).await,
            Action::Groom { target: None }
        );
    }

    #[tokio::test]
    async fn a_sleepy_cat_in_a_sunbeam_sleeps_right_there() {
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(4, 4);
            world.kitties[idx].needs.add(NeedKind::Sleep, 99.0);
            world.push_element(Element {
                id: 502,
                kind: ElementKind::Sunbeam,
                pos: Position::new(4, 4),
                ttl: Some(100),
            });
        });
        assert_eq!(NeedsDriven.decide(&ctx).await, Action::Sleep { with: None });
    }

    #[tokio::test]
    async fn the_fallback_always_returns_something_even_in_an_empty_world() {
        // No elements at all: NeedsDriven must still be total.
        for need in NeedKind::ALL {
            let ctx = decision_context(|world| {
                world.elements.clear();
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].needs.add(need, 99.0);
            });
            let action = NeedsDriven.decide(&ctx).await;
            // Any action is fine; not returning one is not an option.
            let _ = action;
        }
    }

    #[tokio::test]
    async fn decisions_are_deterministic_for_a_given_context() {
        let make = || {
            decision_context(|world| {
                let idx = world.kitty_index(1).unwrap();
                world.kitties[idx].needs.add(NeedKind::Play, 60.0);
            })
        };
        let a = NeedsDriven.decide(&make()).await;
        let b = NeedsDriven.decide(&make()).await;
        assert_eq!(a, b);
    }
}
