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

use super::relief::ReliefSource;
use super::{selection, Behavior, DecisionContext};
use crate::seam::Decision;
use crate::action::Action;
use crate::element::ElementType;
use crate::grid::Direction;
use crate::needs::NeedKind;

pub struct NeedsDriven;

#[async_trait]
impl Behavior for NeedsDriven {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        // Two channels (spec 028): the ladder picks the activity; the
        // announce rule rides along, never displacing it. The one word the
        // ladder itself can produce is the yield ("Wait for me!"), which
        // from_legacy lifts onto the channel and which outranks announce --
        // etiquette speaks first.
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

impl NeedsDriven {
    fn decide_action(&self, ctx: &DecisionContext) -> Action {
        // A scene in progress that is still doing its job gets finished first.
        if let Some(action) = finish_what_you_started(ctx) {
            return action;
        }

        // Never walk away from something you were going to want anyway.
        if let Some(action) = take_what_is_here(ctx) {
            return action;
        }

        let (_, pressure) = ctx.me.needs.highest_pressure();

        // (Announcing left the ladder in spec 028: the message channel
        // rides along every decision -- see `decide` -- so speaking up no
        // longer costs a rung or a turn. Purring left in spec 011.)

        // Nothing pressing: potter about.
        if pressure < 20.0 && ctx.rng.gen_bool(0.4) {
            return wander(ctx);
        }

        // One scored pass over every need: urgency weighs in, travel counts
        // against, and nothing gets locked out (see `selection`).
        pursue(ctx, selection::choose(ctx))
    }
}

/// Keep at what you are doing until it has done its job. The engine holds a
/// scene through its configured minimum; this is the behavior-side commitment
/// past it: an activity whose governing need is still above zero is continued
/// rather than re-litigated every tick, so a nap runs until the kitty is
/// rested (or the engine's maximum calls time). Grooming reads the need off
/// the friend being groomed, matching the engine's own end rule. Solo rest is
/// posture, not relief -- it carries no governing need and is re-decided
/// freely. Shared with `Playful`: finishing what you started is good sense,
/// not a personality trait.
pub(crate) fn finish_what_you_started(ctx: &DecisionContext) -> Option<Action> {
    let activity = ctx.me.activity;
    let need = activity.governing_need()?;
    let remaining = match activity {
        crate::kitty::Activity::Grooming {
            target: Some(friend),
        } => ctx.world.kitty(friend)?.needs.get(need),
        _ => ctx.me.needs.get(need),
    };
    if remaining <= 0.0 {
        return None;
    }
    activity.continuation()
}

/// The emergency ladder: the needs opportunism considers, in load-bearing
/// order — food and water first, the sunbeam you are standing in, and only
/// then a passing playmate. Cuddle and Bath are deliberately absent: they
/// are never grabbed opportunistically.
///
/// Membership contract (spec 019 review): every Element/Sunbeam/Playmate-
/// shaped need in `relief()` belongs on this ladder, and no Friend/InPlace
/// need may join it (the match below would no-op it silently). The
/// `ladder_membership_matches_relief_shapes` test enforces both directions;
/// a deliberate omission gets an allow-list entry there, with its reason.
const OPPORTUNISM_LADDER: [NeedKind; 4] = [
    NeedKind::Eat,
    NeedKind::Drink,
    NeedKind::Sleep,
    NeedKind::Play,
];

/// Eat, drink, nap or play when the means are already underfoot and the need is
/// real. Shared with `Playful`: opportunism is good sense, not a personality
/// trait. The need→relief pairing comes from the one authoritative definition
/// (`relief.rs`, spec 019); this function owns only the underfoot checks.
pub(crate) fn take_what_is_here(ctx: &DecisionContext) -> Option<Action> {
    let me = &ctx.me;
    let detour = ctx.config.behavior.worth_a_detour;

    for need in OPPORTUNISM_LADDER {
        if me.needs.get(need) < detour {
            continue;
        }
        match need.relief() {
            ReliefSource::Element { kind, use_it } => {
                if ctx
                    .world
                    .elements_of(kind)
                    .any(|e| me.pos.is_adjacent(&e.pos))
                {
                    return Some(use_it);
                }
            }
            // A sunbeam you are already sitting in is too good to waste.
            ReliefSource::Sunbeam => {
                if ctx.world.element_at(me.pos).map(|e| e.element_type())
                    == Some(ElementType::Sunbeam)
                {
                    return Some(Action::Sleep { with: None });
                }
            }
            // A bug within paw's reach gets batted at, whatever the errand was.
            ReliefSource::Playmate => {
                if let Some(target) = selection::adjacent_playmate(ctx) {
                    return Some(Action::play_with(target));
                }
            }
            // Not opportunistic (and absent from the ladder).
            ReliefSource::Friend | ReliefSource::InPlace { .. } => {}
        }
    }

    None
}

/// Take one step toward relieving the chosen need. Takes the whole
/// [`selection::Choice`] so the playmate the scored pass already found is
/// pursued directly instead of being scanned for a second time.
pub(crate) fn pursue(ctx: &DecisionContext, choice: selection::Choice) -> Action {
    let me = &ctx.me;
    let world = &ctx.world;

    // The need→relief pairing comes from the one authoritative definition
    // (`relief.rs`, spec 019); this function owns only how each relief
    // shape is pursued.
    match choice.need.relief() {
        ReliefSource::Element { kind, use_it } => seek_element(ctx, kind, use_it),

        ReliefSource::InPlace { use_it } => use_it,

        ReliefSource::Sunbeam => {
            // Already in a sunbeam? Perfect.
            if world.element_at(me.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam) {
                return Action::Sleep { with: None };
            }
            match selection::sunbeam_worth_walking(ctx) {
                // Worth walking to, if it is not an expedition. The same
                // priced helper feeds the sleep score in `selection` (the
                // within-shape agreement the `relief` module documents).
                Some((pos, _)) => step_toward(ctx, pos),
                // Otherwise a nap right here will do; a friend nearby makes it cosier.
                None => Action::Sleep {
                    with: adjacent_friend(ctx),
                },
            }
        }

        // Play targeting, give-up and the solo backstop live in `selection` so
        // both built-in profiles pursue fun by exactly the same rules -- against
        // the playmate the scored pass already found.
        ReliefSource::Playmate => selection::play_action_with(ctx, choice.playmate),

        ReliefSource::Friend => {
            // Only an idle friend can be drawn into a cuddle (spec 006
            // conscription) -- proposing at a busy one would just bounce to
            // Idle. Seek the nearest *free* friend instead.
            let free = world
                .others(me.id)
                .filter(|k| !k.activity.is_in_progress())
                .min_by_key(|k| (me.pos.manhattan_distance(&k.pos), k.id));
            match free {
                Some(friend) if me.pos.is_adjacent(&friend.pos) => Action::Rest {
                    with: Some(friend.id),
                },
                // Approach etiquette (spec 012): at the corner, the higher-id
                // kitty asks and holds; the lower one closes the last step.
                Some(friend) if selection::should_wait_for(ctx, friend.id, friend.pos) => {
                    selection::wait_for_them(ctx)
                }
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
        .min_by_key(|e| (me.pos.manhattan_distance(&e.pos), e.id));

    if usable.is_some() {
        return use_it;
    }

    // Walk toward the element the priced score chose -- the same
    // `(priced_travel, id)` choice `selection` makes, so a bowl across a
    // pond is pursued only when it truly is the cheapest walk (spec 010).
    match selection::priced_nearest_element(ctx, kind) {
        Some((pos, _)) => step_toward(ctx, pos),
        // The safeguard will have provided something by the next environment
        // phase; until then, there is nothing useful to do about it.
        None => Action::Idle,
    }
}

/// One step in the general direction of somewhere -- routing around other
/// kitties rather than freezing against them, and preferring dry paws while
/// it is at it.
///
/// The naive version proposed the single straight-line direction; when a friend
/// happened to be standing on that tile, the Move validated to Idle and the cat
/// simply froze -- three cats in a row could deadlock for hundreds of ticks
/// with food two tiles away (found by the 004 welfare long-run). Instead: take
/// the best legal step that closes distance, and when fully walled in, sidestep
/// rather than stand still -- a shuffling cat finds the way around.
///
/// Water aversion (spec 010) changes only the *ordering*, never the options:
/// among distance-closing steps, a wet destination carries a
/// `water_step_cost` surcharge, so dry progress beats wet progress -- but
/// when the only step that closes distance is wet, the kitty wades. The set
/// of steps it is willing to take is exactly the pre-010 set, which is the
/// whole anti-stuck argument: no layout can trap a cat that will always
/// paddle when paddling is the only way forward. The sidestep fallback
/// prefers dry tiles for the same reason a cat standing in a puddle gets out
/// of it.
fn step_toward(ctx: &DecisionContext, target: crate::grid::Position) -> Action {
    let me = ctx.me.pos;
    let occupied = |dest: &crate::grid::Position| {
        ctx.world
            .kitties
            .iter()
            .any(|k| k.id != ctx.me.id && k.pos == *dest)
    };
    let is_water = |pos: &crate::grid::Position| {
        ctx.world
            .elements_of(ElementType::Water)
            .any(|e| e.pos == *pos)
    };
    // Manhattan is the walk (4-way steps), so progress is simply a lower
    // step count. This also keeps a kitty maneuvering when it stands
    // diagonal to its target: Manhattan 2 is *not* arrived under the 009
    // orthogonal-interaction rule, where Chebyshev used to call it done.
    let progress_score = |pos: &crate::grid::Position| target.manhattan_distance(pos);

    // Directions are tried dominant-axis first (the `Direction::toward`
    // rule), so equal-cost ties prefer closing the larger gap. Found by the
    // welfare long-run during 010: with a fixed N/E/S/W order, two kitties
    // meeting head-on in a corridor could lock into a mirrored period-2
    // shuffle for dozens of ticks -- the fixed tie kept steering the cat
    // back into the contested lane when an equally-good open lane existed.
    // Closing the dominant axis also keeps both axes improvable longer,
    // which is what gives the water surcharge dry alternatives to pick.
    let order = {
        let dx = target.x as i64 - me.x as i64;
        let dy = target.y as i64 - me.y as i64;
        let horiz = if dx > 0 {
            Direction::East
        } else {
            Direction::West
        };
        let vert = if dy > 0 {
            Direction::South
        } else {
            Direction::North
        };
        let (first, second) = if dx.abs() >= dy.abs() {
            (horiz, vert)
        } else {
            (vert, horiz)
        };
        let mut order = [first, second, first, second];
        let mut n = 2;
        for d in Direction::ALL {
            if d != first && d != second {
                order[n] = d;
                n += 1;
            }
        }
        order
    };

    let current = progress_score(&me);
    // Spec 024: one shared water-aversion ratio -- see
    // `selection::bath_ratio` for why score and walk must price alike.
    let bath_ratio = selection::bath_ratio(ctx);
    let mut best: Option<(f32, Direction)> = None;
    let mut dry_sidesteps: Vec<Direction> = Vec::new();
    let mut wet_sidesteps: Vec<Direction> = Vec::new();
    for direction in order {
        let Some(dest) = me.step(direction, ctx.world.width, ctx.world.height) else {
            continue;
        };
        if occupied(&dest) {
            continue;
        }
        if is_water(&dest) {
            wet_sidesteps.push(direction);
        } else {
            dry_sidesteps.push(direction);
        }
        let score = progress_score(&dest);
        if score < current {
            let cost = score as f32
                + if is_water(&dest) {
                    ctx.config.behavior.water_step_cost * bath_ratio
                } else {
                    0.0
                };
            if best.map(|(b, _)| cost < b).unwrap_or(true) {
                best = Some((cost, direction));
            }
        }
    }

    match best {
        Some((_, direction)) => Action::move_to(direction),
        // Nothing brings the cat closer: sidestep rather than freeze, unless
        // it is already beside the target or has nowhere legal to stand.
        // The sidestep is a genuine shuffle -- drawn from this kitty's own
        // seeded decision randomness among free tiles (dry preferred, spec
        // 010) -- because a *fixed* pick lets two blocked kitties sidestep
        // in lockstep indefinitely: the head-on transit dance the welfare
        // gate caught during 012 (ticks 1329-1365, three cats bouncing in
        // formation). Seeded means deterministic (Article V); per-kitty
        // means never synchronized for long (spec 012 FR-008).
        None if current > 1 => {
            let pool = if dry_sidesteps.is_empty() {
                &wet_sidesteps
            } else {
                &dry_sidesteps
            };
            match ctx.rng.choose(pool) {
                Some(direction) => Action::move_to(*direction),
                None => Action::Idle,
            }
        }
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
    use crate::meow::MessageKind;
    use crate::behavior::Behavior;
    use crate::element::{Element, ElementKind};
    use crate::grid::Position;
    use crate::test_support::decision_context;

    #[tokio::test]
    async fn a_napping_cat_stays_asleep_until_rested() {
        // The commitment rule: mid-nap with sleep need remaining, the cat
        // keeps sleeping -- even beside a bowl its hunger would otherwise
        // send it to (the opportunism ladder yields to the scene in
        // progress).
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 20;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Sleep, 40.0);
            world.kitties[idx].needs.add(NeedKind::Eat, 90.0);
            world.kitties[idx].activity = crate::kitty::Activity::Sleeping {
                in_sunbeam: false,
                with_friend: None,
            };
            world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(15));
            world.push_element(Element {
                id: 570,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 6),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::Sleep { with: None },
            "a nap still doing its job is finished, not re-litigated"
        );
    }

    #[tokio::test]
    async fn a_rested_cat_moves_on_from_its_nap() {
        // The boundary: governing need at zero releases the commitment, and
        // the ordinary scored pass takes over (here: the adjacent chow).
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            world.tick = 20;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            // sleep need stays at its spawn value of zero: the nap is done
            world.kitties[idx].needs.add(NeedKind::Eat, 90.0);
            world.kitties[idx].activity = crate::kitty::Activity::Sleeping {
                in_sunbeam: false,
                with_friend: None,
            };
            world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(15));
            world.push_element(Element {
                id: 571,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 6),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(NeedsDriven.decide_action(&ctx), Action::Eat);
    }

    #[tokio::test]
    async fn a_groomer_finishes_the_friend_not_itself() {
        // Grooming commitment reads the groomed friend's bath need -- the
        // engine's own end rule -- so a clean groomer keeps washing a still-
        // dirty friend, and a still-dirty groomer releases a clean one.
        let dirty_friend = decision_context(|world| {
            world.tick = 20;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].activity = crate::kitty::Activity::Grooming { target: Some(2) };
            world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(15));
            let friend = world.kitty_index(2).unwrap();
            world.kitties[friend].needs.add(NeedKind::Bath, 60.0);
        });
        assert_eq!(
            NeedsDriven.decide_action(&dirty_friend),
            Action::Groom { target: Some(2) },
        );

        let clean_friend = decision_context(|world| {
            world.tick = 20;
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Bath, 60.0); // its own dirt is not the question
            world.kitties[idx].activity = crate::kitty::Activity::Grooming { target: Some(2) };
            world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(15));
            // the friend's bath need stays at its spawn value of zero: clean
        });
        assert_ne!(
            NeedsDriven.decide_action(&clean_friend),
            Action::Groom { target: Some(2) },
            "a clean friend releases the groomer whatever its own coat looks like"
        );
    }

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

        assert_eq!(NeedsDriven.decide_action(&ctx), Action::Eat);
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
            NeedsDriven.decide_action(&ctx),
            Action::move_to(crate::grid::Direction::East)
        );
    }

    #[tokio::test]
    async fn a_cat_diagonal_to_chow_steps_beside_it_then_eats() {
        // Spec 009 FR-004: diagonal is not arrived. The kitty must convert the
        // corner into a compass neighbourhood -- one step east or south -- and
        // only then eat. Under the old Chebyshev rules this was an instant Eat.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 530,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(6, 6), // corner-to-corner
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            // East and south both close the corner; direction order breaks
            // the tie deterministically in favour of east.
            Action::move_to(Direction::East),
            "a diagonal bowl is walked to, not eaten across"
        );

        // One step later, beside the bowl: now it is dinner time.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(6, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 531,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(6, 6),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(NeedsDriven.decide_action(&ctx), Action::Eat);
    }

    /// A bowl with every compass seat taken, for the crowded-target edge case
    /// (spec 009 "Crowded targets", analyze M1). Kitty 1 is the waiter, two
    /// steps north of the bowl; kitties 2-5 occupy all four seats.
    fn crowded_bowl_ctx() -> crate::behavior::DecisionContext {
        use crate::config::KittyConfig;
        use crate::rng::DecisionRng;
        use std::sync::Arc;

        let mut config = crate::test_support::test_config();
        config.kitties = vec![
            ("Waiter", 8, 6),
            ("North", 8, 7),
            ("South", 8, 9),
            ("West", 7, 8),
            ("East", 9, 8),
        ]
        .into_iter()
        .enumerate()
        .map(|(i, (name, x, y))| KittyConfig {
            id: (i + 1) as u32,
            name: name.into(),
            x,
            y,
            behavior: "needs_driven".into(),
            needs: None,
        })
        .collect();
        let config = Arc::new(config);
        let mut world = crate::world::World::generate(&config);
        world.elements.clear();
        world.push_element(Element {
            id: 540,
            kind: ElementKind::Chow { servings: 5 },
            pos: Position::new(8, 8),
            ttl: None,
        });
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 95.0);

        let mut me = world.kitty(1).unwrap().clone();
        me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        crate::behavior::DecisionContext {
            me,
            world: Arc::new(world.snapshot()),
            rng: DecisionRng::from_seed(9876),
            config,
        }
    }

    #[tokio::test]
    async fn a_cat_crowded_away_from_its_bowl_shuffles_legally_instead_of_reaching_across() {
        // The waiter cannot improve its distance (the only closer tile is a
        // taken seat), must not eat from out of range, and must not freeze:
        // the sidestep fallback keeps it milling about until the world moves
        // on. The bowl itself will usually be licked clean by the seated four
        // before a seat frees -- retarget-and-respawn is the designed relief
        // path (owner decision 2026-07-20), driven end-to-end in the welfare
        // suite's crowded-bowl run.
        let ctx = crowded_bowl_ctx();
        let action = NeedsDriven.decide_action(&ctx);
        assert_eq!(
            action,
            Action::move_to(Direction::West),
            "the first free direction in preference order (dominant axis first) is a \
             lawful shuffle, not Idle and never a diagonal Eat"
        );
    }

    #[tokio::test]
    async fn a_dry_step_beats_a_wet_step_when_both_close_distance() {
        // Spec 010 US1: south and east both close on the bowl; east is a
        // puddle. Direction order would say east -- the surcharge says south.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 550,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(7, 7),
                ttl: None,
            });
            world.push_element(Element {
                id: 551,
                kind: ElementKind::Water,
                pos: Position::new(6, 5), // the wet eastern step
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::move_to(Direction::South),
            "dry progress beats wet progress"
        );
    }

    #[tokio::test]
    async fn a_kitty_wades_when_water_is_the_only_way_forward() {
        // Spec 010 FR-002: the bowl is dead ahead across a puddle and no dry
        // step closes distance -- preference yields, the kitty paddles.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 552,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 8),
                ttl: None,
            });
            world.push_element(Element {
                id: 553,
                kind: ElementKind::Water,
                pos: Position::new(5, 6), // squarely on the only closing step
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::move_to(Direction::South),
            "crossing is never refused -- a wet improving step beats no step"
        );
    }

    #[tokio::test]
    async fn the_sidestep_fallback_prefers_a_dry_tile() {
        // Nothing closes distance (the only improving tile holds a friend).
        // Fallback preference order from (5,5) toward (5,8) is S, W, N, E;
        // west is a puddle, so the dry-preferring shuffle picks north --
        // without the dry rule, plain order would say the wet west tile.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            let blocker = world.kitty_index(2).unwrap();
            world.kitties[blocker].pos = Position::new(5, 6); // on the sole improving step
            world.push_element(Element {
                id: 554,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 8),
                ttl: None,
            });
            world.push_element(Element {
                id: 555,
                kind: ElementKind::Water,
                pos: Position::new(4, 5), // the wet western sidestep, first in fallback order
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        // The sidestep is a seeded shuffle (spec 012 FR-008), so the exact
        // direction is the rng's business -- the *property* is that it moves,
        // and only onto a dry free tile (north or east here; west is wet,
        // south is a friend).
        let action = NeedsDriven.decide_action(&ctx);
        assert!(
            action == Action::move_to(Direction::North)
                || action == Action::move_to(Direction::East),
            "a shuffling cat shuffles dry when it can (got {action:?})"
        );
    }

    #[tokio::test]
    async fn a_kitty_standing_in_a_puddle_steps_out_dry_side_first() {
        // Spec 010 FR-005: the kitty starts *on* water with two equal-progress
        // exits, one dry (east) and one wet (south). It leaves dry-side.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 556,
                kind: ElementKind::Water,
                pos: Position::new(5, 5), // under its paws
                ttl: None,
            });
            world.push_element(Element {
                id: 557,
                kind: ElementKind::Water,
                pos: Position::new(5, 6), // the wet southern exit
                ttl: None,
            });
            world.push_element(Element {
                id: 558,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(7, 7),
                ttl: None,
            });
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        // Standing on water means water is "adjacent" -- keep drink below the
        // opportunism line so the errand stays the errand.
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::move_to(Direction::East),
            "out of the puddle, dry paws first"
        );
    }

    #[tokio::test]
    async fn the_bowl_walked_toward_is_the_bowl_the_priced_score_chose() {
        // Spec 010 US2 / the 004 agreement rule: the nearer bowl sits across
        // two water tiles (priced 4 + 2x4 = 12); the farther bowl is 6 dry
        // steps east. Selection prices the detour, and the walk goes east --
        // pre-010 the kitty marched south at the raw-nearest bowl.
        let mut ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 560,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 9), // 4 steps, but wet ones
                ttl: None,
            });
            world.push_element(Element {
                id: 561,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(11, 5), // 6 dry steps
                ttl: None,
            });
            for (id, y) in [(562u32, 7u32), (563, 8)] {
                world.push_element(Element {
                    id,
                    kind: ElementKind::Water,
                    pos: Position::new(5, y),
                    ttl: None,
                });
            }
        });
        ctx.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::move_to(Direction::East),
            "the priced choice and the walk agree on the dry bowl"
        );
    }

    #[tokio::test]
    async fn a_low_bath_cat_is_the_swimmer_to_both_deciders() {
        // Spec 024 FR-005: the surcharge scales by the cat's own bath
        // trait. Geometry: the wet bowl is 4 steps south across two water
        // tiles; the dry bowl is 9 steps east. At the shipped surcharge a
        // plain cat prices the wet path 4 + 2x4 = 12 and detours east; a
        // half-bath cat prices it 4 + 2x2 = 8 and swims south. One world,
        // one rule, two personalities.
        let build = |world: &mut crate::world::World| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Eat, 95.0);
            world.push_element(Element {
                id: 570,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(5, 9),
                ttl: None,
            });
            world.push_element(Element {
                id: 571,
                kind: ElementKind::Chow { servings: 3 },
                pos: Position::new(14, 5),
                ttl: None,
            });
            for (id, y) in [(572u32, 7u32), (573, 8)] {
                world.push_element(Element {
                    id,
                    kind: ElementKind::Water,
                    pos: Position::new(5, y),
                    ttl: None,
                });
            }
        };

        let mut plain = decision_context(build);
        plain.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&plain),
            Action::move_to(Direction::East),
            "the plain cat detours dry"
        );

        let mut swimmer = decision_context(build);
        swimmer.me.set_meow_cooldown(MessageKind::WantEat, u64::MAX);
        let mut config = crate::test_support::test_config();
        config.kitties[0].needs = Some(crate::config::NeedRateOverrides {
            bath: Some(config.needs.bath * 0.5), // ratio 0.5: barely minds wet fur
            ..Default::default()
        });
        config.validate().expect("valid");
        swimmer.config = std::sync::Arc::new(config);
        assert_eq!(
            NeedsDriven.decide_action(&swimmer),
            Action::move_to(Direction::South),
            "the swimmer takes the pond shortcut"
        );
    }

    #[tokio::test]
    async fn a_cuddle_seeker_asks_and_waits_at_the_corner() {
        // Spec 012: the higher-id kitty one corner from its cuddle target
        // spends the even tick on "Wait for me!" instead of dancing.
        let mut ctx = crate::test_support::decision_context_for(2, |world| {
            world.elements.clear();
            world.tick = 100; // even
            let friend = world.kitty_index(1).unwrap();
            world.kitties[friend].pos = Position::new(5, 5);
            let me = world.kitty_index(2).unwrap();
            world.kitties[me].pos = Position::new(6, 6); // Manhattan 2
            world.kitties[me].needs.add(NeedKind::Cuddle, 90.0);
        });
        ctx.me.set_meow_cooldown(MessageKind::WantCuddle, u64::MAX);
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
            Action::Meow {
                message: MessageKind::WaitForMe
            }
        );
    }

    #[tokio::test]
    async fn a_dirty_cat_grooms_itself() {
        let ctx = decision_context(|world| {
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Bath, 99.0);
        });
        assert_eq!(
            NeedsDriven.decide_action(&ctx),
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
        assert_eq!(NeedsDriven.decide_action(&ctx), Action::Sleep { with: None });
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
            let action = NeedsDriven.decide_action(&ctx);
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
            NeedsDriven.decide_action(&ctx),
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
            NeedsDriven.decide_action(&ctx),
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

        assert_eq!(NeedsDriven.decide_action(&ctx), Action::Eat);
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
            NeedsDriven.decide_action(&ctx),
            Action::play_solo(),
            "the nap is respected; play happens solo beside it"
        );
    }

    #[tokio::test]
    async fn a_blocked_cat_routes_around_a_friend_instead_of_freezing() {
        // The gridlock found by the welfare long-run: a friend standing on the
        // straight-line tile used to freeze the walk entirely (blocked Move ->
        // Idle, forever). The cat must route around via the free southern
        // tile instead -- still a step that closes walking distance.
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

        let action = NeedsDriven.decide_action(&ctx);
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

    /// Spec 019 review guard: ladder membership must track relief shapes.
    /// Both directions matter — an opportunistic-shaped need missing from
    /// the ladder is silently never grabbed underfoot; a Friend/InPlace
    /// need added to the ladder is a silent dead rung (the no-op arm).
    /// A future deliberate omission joins an allow-list here, with its
    /// reason.
    #[test]
    fn ladder_membership_matches_relief_shapes() {
        use super::super::relief::ReliefSource;
        for need in NeedKind::ALL {
            let opportunistic = matches!(
                need.relief(),
                ReliefSource::Element { .. } | ReliefSource::Sunbeam | ReliefSource::Playmate
            );
            assert_eq!(
                opportunistic,
                OPPORTUNISM_LADDER.contains(&need),
                "{need:?}: opportunistic-shaped needs and OPPORTUNISM_LADDER membership \
                 must agree (deliberate omissions get an allow-list in this test)"
            );
        }
    }

    #[tokio::test]
    async fn announcing_never_alters_the_chosen_activity() {
        // Spec 028 FR-017 (the engine-side half of FR-021): the message is
        // computed after and independent of the activity, so deciding with
        // the channel in play picks the same activity as the ladder alone.
        // A hungry cat mid-walk announces WantEat and keeps walking.
        let ctx = decision_context(|world| {
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(2, 2);
            world.kitties[idx].needs.add(NeedKind::Eat, 60.0);
            world.kitties[idx].announce_armed.insert(NeedKind::Eat);
            world.push_element(Element {
                id: 700,
                kind: ElementKind::Chow { servings: 5 },
                pos: Position::new(12, 2),
                ttl: None,
            });
        });
        let decision = NeedsDriven.decide(&ctx).await;
        assert_eq!(
            decision.activity,
            NeedsDriven.decide_action(&ctx),
            "the channel rides along; it never displaces the turn"
        );
        assert_eq!(
            decision.message,
            Some(MessageKind::WantEat),
            "and the errand is announced mid-walk"
        );
    }

    #[tokio::test]
    async fn a_grounded_cat_announces_its_highest_pressure_legal_want() {
        // Two armed needs: the higher pressure wins; ties would fall to
        // NeedKind::ALL order (the selection precedent).
        let ctx = decision_context(|world| {
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Eat, 40.0);
            world.kitties[idx].needs.add(NeedKind::Cuddle, 55.0);
            world.kitties[idx].announce_armed.insert(NeedKind::Eat);
            world.kitties[idx].announce_armed.insert(NeedKind::Cuddle);
        });
        let decision = NeedsDriven.decide(&ctx).await;
        assert_eq!(decision.message, Some(MessageKind::WantCuddle));
    }

    #[tokio::test]
    async fn an_ungrounded_cat_is_silent() {
        // Nothing armed: the deterministic rule has nothing legal to say,
        // whatever the raw pressures are.
        let ctx = decision_context(|world| {
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].needs.add(NeedKind::Eat, 60.0);
            world.kitties[idx].announce_armed.clear();
        });
        let decision = NeedsDriven.decide(&ctx).await;
        assert_eq!(decision.message, None, "unarmed means Silent, by law");
    }
}
