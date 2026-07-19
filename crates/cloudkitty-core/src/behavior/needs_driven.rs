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

use super::{selection, Behavior, DecisionContext};
use crate::action::Action;
use crate::element::ElementType;
use crate::grid::Direction;
use crate::meow::MessageKind;
use crate::needs::NeedKind;

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

        // One scored pass over every need: urgency weighs in, travel counts
        // against, and nothing gets locked out (see `selection`).
        pursue(ctx, selection::choose_need(ctx))
    }

    fn is_builtin(&self) -> bool {
        true
    }
}

/// Eat, drink, nap or play when the means are already underfoot and the need is
/// real. Shared with `Playful`: opportunism is good sense, not a personality
/// trait. The order is the emergency ladder: food and water first, the sunbeam
/// you are standing in, and only then a passing playmate.
pub(crate) fn take_what_is_here(ctx: &DecisionContext) -> Option<Action> {
    let me = &ctx.me;
    let detour = ctx.config.behavior.worth_a_detour;

    if me.needs.get(NeedKind::Eat) >= detour
        && ctx
            .world
            .elements_of(ElementType::Chow)
            .any(|e| me.pos.is_adjacent(&e.pos))
    {
        return Some(Action::Eat);
    }

    if me.needs.get(NeedKind::Drink) >= detour
        && ctx
            .world
            .elements_of(ElementType::Water)
            .any(|e| me.pos.is_adjacent(&e.pos))
    {
        return Some(Action::Drink);
    }

    // A sunbeam you are already sitting in is too good to waste.
    if me.needs.get(NeedKind::Sleep) >= detour
        && ctx.world.element_at(me.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam)
    {
        return Some(Action::Sleep { with: None });
    }

    // A bug within paw's reach gets batted at, whatever the errand was.
    if me.needs.get(NeedKind::Play) >= detour {
        if let Some(target) = selection::adjacent_playmate(ctx) {
            return Some(Action::play_with(target));
        }
    }

    None
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

        // Play targeting, give-up and the solo backstop live in `selection` so
        // both built-in profiles pursue fun by exactly the same rules.
        NeedKind::Play => selection::play_action(ctx),

        NeedKind::Cuddle => {
            // Only an idle friend can be drawn into a cuddle (spec 006
            // conscription) -- proposing at a busy one would just bounce to
            // Idle. Seek the nearest *free* friend instead.
            let free = world
                .others(me.id)
                .filter(|k| !k.activity.is_in_progress())
                .min_by_key(|k| (me.pos.chebyshev_distance(&k.pos), k.id));
            match free {
                Some(friend) if me.pos.is_adjacent(&friend.pos) => Action::Rest {
                    with: Some(friend.id),
                },
                // Walking over for a cuddle is not a chase; this cat is not playing.
                Some(friend) => step_toward(ctx, friend.pos),
                // Everyone is mid-scene; scenes are short (bounded by their
                // maximums), so wait rather than lock into a relief-less
                // solo rest.
                None => Action::Idle,
            }
        }
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

/// One step in the general direction of somewhere -- routing around other
/// kitties rather than freezing against them.
///
/// The naive version proposed the single straight-line direction; when a friend
/// happened to be standing on that tile, the Move validated to Idle and the cat
/// simply froze -- three cats in a row could deadlock for hundreds of ticks
/// with food two tiles away (found by the 004 welfare long-run). Instead: take
/// the best legal step that closes distance, and when fully walled in, sidestep
/// rather than stand still -- a shuffling cat finds the way around.
fn step_toward(ctx: &DecisionContext, target: crate::grid::Position) -> Action {
    let me = ctx.me.pos;
    let occupied = |dest: &crate::grid::Position| {
        ctx.world
            .kitties
            .iter()
            .any(|k| k.id != ctx.me.id && k.pos == *dest)
    };
    // Chebyshev alone cannot see progress on a diagonal (a cardinal step keeps
    // it equal when |dx| == |dy|), so manhattan breaks the tie: a step is
    // progress when it improves the pair lexicographically.
    let progress_score = |pos: &crate::grid::Position| {
        let dx = (target.x as i64 - pos.x as i64).unsigned_abs() as u32;
        let dy = (target.y as i64 - pos.y as i64).unsigned_abs() as u32;
        (dx.max(dy), dx + dy)
    };

    let current = progress_score(&me);
    let mut best: Option<((u32, u32), Direction)> = None;
    let mut fallback: Option<Direction> = None;
    for direction in Direction::ALL {
        let Some(dest) = me.step(direction, ctx.world.width, ctx.world.height) else {
            continue;
        };
        if occupied(&dest) {
            continue;
        }
        if fallback.is_none() {
            fallback = Some(direction);
        }
        let score = progress_score(&dest);
        if score < current && best.map(|(b, _)| score < b).unwrap_or(true) {
            best = Some((score, direction));
        }
    }

    match (best, fallback) {
        (Some((_, direction)), _) => Action::move_to(direction),
        // Nothing brings the cat closer: sidestep rather than freeze, unless
        // it is already beside the target or has nowhere legal to stand.
        (None, Some(direction)) if current.0 > 1 => Action::move_to(direction),
        _ => Action::Idle,
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
    async fn a_cat_with_pinned_bath_and_unreachable_play_grooms_within_the_tick() {
        // US1 acceptance 1: the old lock chased play forever; the scored pass
        // takes the zero-distance relief first.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Bath, 100.0);
            world.kitties[idx].needs.add(NeedKind::Play, 100.0);
            // Exclude the only playmate so play cannot resolve socially...
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(15, 15);
        });
        ctx.me.set_meow_cooldown(MessageKind::WantPlay, u64::MAX);
        ctx.me.set_meow_cooldown(MessageKind::WantCuddle, u64::MAX);

        // Bath (100, d0, never relieved) vs play (100, d0 via solo): the tie
        // goes to whichever waited longer -- both never, so eat..ALL order says
        // bath sits behind play. Stamp play as recently relieved to pin it.
        ctx.me.last_relief.insert(NeedKind::Play, 5);
        assert_eq!(
            NeedsDriven.decide(&ctx).await,
            Action::Groom { target: None }
        );
    }

    #[tokio::test]
    async fn a_bug_underfoot_gets_batted_at_even_mid_errand() {
        // US2 acceptance 1: walking to water, passing a bug -- pounce first.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Drink, 60.0);
            world.kitties[idx].needs.add(NeedKind::Play, 40.0);
            world.push_element(Element {
                id: 510,
                kind: ElementKind::Water,
                pos: Position::new(12, 5),
                ttl: None,
            });
            world.push_element(Element {
                id: 511,
                kind: ElementKind::Bug,
                pos: Position::new(5, 6), // right there
                ttl: Some(50),
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantDrink, u64::MAX);

        assert_eq!(
            NeedsDriven.decide(&ctx).await,
            Action::play_with(crate::action::TargetRef::Element { id: 511 })
        );
    }

    #[tokio::test]
    async fn opportunistic_play_yields_to_adjacent_food() {
        // US2 edge case: the emergency ladder holds -- a hungry cat beside its
        // chow eats before it bats at the bug beside it.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            world.push_element(Element {
                id: 512,
                kind: ElementKind::Chow { servings: 2 },
                pos: Position::new(5, 4),
                ttl: None,
            });
            world.push_element(Element {
                id: 513,
                kind: ElementKind::Bug,
                pos: Position::new(5, 6),
                ttl: Some(50),
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        ctx.me.set_meow_cooldown(MessageKind::WantPlay, u64::MAX);

        assert_eq!(NeedsDriven.decide(&ctx).await, Action::Eat);
    }

    #[tokio::test]
    async fn a_sleeping_friend_is_company_you_let_sleep() {
        // Superseded 004 edge case: back then a kitty could bat a sleeping
        // friend awake into play, so solo play had to defer to them. Spec
        // 006's conscription rule ends that (a sleeping cat is never yanked
        // awake), so the urgent player pounces at nothing instead of
        // proposing a play the engine would refuse.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 10;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 90.0);
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].pos = Position::new(5, 6);
            world.kitties[friend].activity = crate::kitty::Activity::Sleeping {
                in_sunbeam: false,
                with_friend: None,
            };
            world.kitties[friend].activity_clock = Some(crate::kitty::ActivityClock::start(9));
        });
        ctx.me.set_meow_cooldown(MessageKind::WantPlay, u64::MAX);

        assert_eq!(
            NeedsDriven.decide(&ctx).await,
            Action::play_solo(),
            "the nap is respected; play happens solo beside it"
        );
    }

    #[tokio::test]
    async fn a_blocked_cat_routes_around_a_friend_instead_of_freezing() {
        // The gridlock found by the welfare long-run: a friend standing on the
        // straight-line tile used to freeze the walk entirely (blocked Move ->
        // Idle, forever). The cat must take the free diagonal instead.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(14, 14);
            world.kitties[idx].needs.add(NeedKind::Drink, 95.0);
            let blocker = world.kitty_index(2).unwrap();
            world.kitties[blocker].pos = Position::new(13, 14); // on the direct path
            world.push_element(Element {
                id: 520,
                kind: ElementKind::Water,
                pos: Position::new(12, 15),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantDrink, u64::MAX);

        let action = NeedsDriven.decide(&ctx).await;
        assert_eq!(
            action,
            Action::move_to(Direction::South),
            "the free southern tile makes progress; freezing against the friend does not"
        );
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
