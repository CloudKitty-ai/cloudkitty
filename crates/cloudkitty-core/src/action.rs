//! Actions: what a kitty does with its tick.
//!
//! Article IV: behaviors *propose*, the engine disposes. Every proposal passes
//! through [`validate`], which returns the action to actually apply --
//! [`Action::Idle`] whenever the proposal is illegal for the current world state.
//! Nothing here can return an error, because an advisor's mistake must never
//! become a kitty's problem.

use serde::{Deserialize, Deserializer, Serialize};

use crate::config::Config;
use crate::element::{ElementId, ElementKind, ElementType};
use crate::grid::Direction;
use crate::kitty::{Activity, ActivityClock, KittyId};
use crate::meow::{cooldown_for, Meow, MessageKind};
use crate::needs::NeedKind;
use crate::world::World;

/// What a `chase` or `play` action is aimed at.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "target", rename_all = "snake_case")]
pub enum TargetRef {
    Element { id: ElementId },
    Kitty { id: KittyId },
}

/// The raw fields a flattened play target may carry, before we decide whether
/// they form a well-shaped target at all.
#[derive(Deserialize)]
struct RawPlayTarget {
    #[serde(default)]
    target: Option<String>,
    #[serde(default)]
    id: Option<u32>,
}

/// Deserializes `Play`'s optional target *strictly*.
///
/// `#[serde(flatten)]` over an `Option` silently yields `None` for anything it
/// cannot parse, which would turn a malformed proposal -- `{"action":"play",
/// "target":"element"}` with no id -- into solo play. Solo play is always legal
/// and carries relief, so a garbled proposal would become a *reward* instead of
/// the safe no-op Article IV promises. An absent target is solo play; a partial
/// or unrecognized one is an error, so it reaches the engine as a failed
/// proposal and falls back like any other misbehaving advisor.
fn strict_play_target<'de, D>(deserializer: D) -> Result<Option<TargetRef>, D::Error>
where
    D: Deserializer<'de>,
{
    let raw = RawPlayTarget::deserialize(deserializer)?;
    match (raw.target.as_deref(), raw.id) {
        (None, None) => Ok(None),
        (Some("element"), Some(id)) => Ok(Some(TargetRef::Element { id })),
        (Some("kitty"), Some(id)) => Ok(Some(TargetRef::Kitty { id })),
        (target, id) => Err(serde::de::Error::custom(format!(
            "a play target must be a complete {{\"target\": \"element\"|\"kitty\", \"id\": N}} \
             or omitted entirely for solo play; got target={target:?}, id={id:?}"
        ))),
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
pub enum Action {
    Move {
        direction: Direction,
    },
    Rest {
        #[serde(default)]
        with: Option<KittyId>,
    },
    Sleep {
        #[serde(default)]
        with: Option<KittyId>,
    },
    Groom {
        #[serde(default)]
        target: Option<KittyId>,
    },
    Eat,
    Drink,
    Chase(TargetRef),
    /// Play with a partner, or -- with no target -- pounce at nothing (solo
    /// play, for a kitty with nobody in reach). The wire shape is unchanged for
    /// social play; solo play simply omits the target.
    Play {
        #[serde(
            flatten,
            default,
            deserialize_with = "strict_play_target",
            skip_serializing_if = "Option::is_none"
        )]
        target: Option<TargetRef>,
    },
    Purr,
    Meow {
        message: MessageKind,
    },
    Idle,
}

impl Action {
    pub fn move_to(direction: Direction) -> Self {
        Action::Move { direction }
    }

    pub fn play_with(target: TargetRef) -> Self {
        Action::Play {
            target: Some(target),
        }
    }

    pub fn play_solo() -> Self {
        Action::Play { target: None }
    }

    /// Play and chase -- the actions a cat takes purely for fun. Used to tell
    /// personalities apart.
    pub fn is_playful(&self) -> bool {
        matches!(self, Action::Play { .. } | Action::Chase(_))
    }
}

/// Returns the action the engine will actually apply: the proposal if it is legal,
/// otherwise `Idle`. This is the whole of Article IV's enforcement surface.
// `_config`: no current rule consults configuration (the retired Purr arm
// was the last), but the parameter stays -- validation is Article IV's whole
// enforcement surface and its shape should not churn with individual rules.
pub fn validate(world: &World, kitty_id: KittyId, proposal: Action, _config: &Config) -> Action {
    let Some(kitty) = world.kitty(kitty_id) else {
        return Action::Idle;
    };

    let legal = match proposal {
        Action::Idle | Action::Meow { .. } => true,

        // A meow that is on cooldown is still a legal action -- it just produces
        // silence. Purring retired as an action in spec 011: it is engine-owned
        // background state now (see `World::purr_phase`), so a purr proposal --
        // stale snapshot replay, future external behavior -- resolves to Idle
        // like any other illegal proposal. The variant survives only because
        // pre-011 snapshots may carry `"last_action": "purr"`.
        Action::Purr => false,

        Action::Move { direction } => match kitty.pos.step(direction, world.width, world.height) {
            Some(dest) => world.kitty_at(dest).is_none(),
            None => false,
        },

        // Cuddling conscripts the partner into a shared activity, so the
        // partner must be free (spec 006). Sleeping *beside* a friend binds
        // nobody and keeps the plain availability rule.
        Action::Rest { with } => match with {
            None => true,
            Some(friend_id) => world.is_conscriptable_friend(kitty_id, friend_id),
        },
        Action::Sleep { with } => match with {
            None => true,
            Some(friend_id) => world.is_available_friend(kitty_id, friend_id),
        },

        Action::Groom { target } => match target {
            None => true,
            Some(friend_id) => world.is_available_friend(kitty_id, friend_id),
        },

        Action::Eat => world.adjacent_stocked_chow(kitty.pos).is_some(),

        Action::Drink => world
            .adjacent_element(kitty.pos, ElementType::Water)
            .is_some(),

        // Chasing is for things that run away: bugs, greebles and friends. Walking
        // to a food bowl is a `Move`, not a chase.
        Action::Chase(target) => match target {
            TargetRef::Element { id } => world
                .element(id)
                .map(|e| e.element_type().is_critter())
                .unwrap_or(false),
            TargetRef::Kitty { id } => id != kitty_id && world.kitty(id).is_some(),
        },

        Action::Play { target } => match target {
            // Pouncing at nothing is always legal, like grooming oneself.
            None => true,
            Some(TargetRef::Element { id }) => world
                .element(id)
                .map(|e| e.element_type().is_critter() && kitty.pos.is_adjacent(&e.pos))
                .unwrap_or(false),
            // Social play is a duet: the partner is conscripted, so the
            // partner must be free (spec 006).
            Some(TargetRef::Kitty { id }) => world.is_conscriptable_friend(kitty_id, id),
        },
    };

    if legal {
        proposal
    } else {
        Action::Idle
    }
}

/// Applies an already-validated action. Every need change goes through the clamped
/// `Need` type, so Article I holds no matter what magnitudes the config carries.
pub fn apply(world: &mut World, kitty_id: KittyId, action: Action, config: &Config) {
    let tick = world.tick;

    // A continuation of the ongoing activity services it rather than starting
    // over: the duration clock never resets mid-scene (spec 006), however the
    // continuation was phrased (same action re-proposed, or Idle).
    if world
        .kitty(kitty_id)
        .map(|k| k.activity_clock.is_some() && k.activity.is_continued_by(&action))
        .unwrap_or(false)
    {
        continue_current_activity(world, kitty_id, config);
        return;
    }

    match action {
        // A genuine do-nothing: an Idle proposal from a kitty with an
        // activity in progress never reaches this arm (the continuation
        // check above intercepts every clocked kitty).
        Action::Idle => {}

        Action::Move { direction } => {
            let Some(kitty) = world.kitty(kitty_id) else {
                return;
            };
            if let Some(dest) = kitty.pos.step(direction, world.width, world.height) {
                if let Some(idx) = world.kitty_index(kitty_id) {
                    world.kitties[idx].pos = dest;
                }
                set_idle(world, kitty_id);
            }
        }

        Action::Rest { with } => {
            let partner = with.filter(|f| world.is_conscriptable_friend(kitty_id, *f));
            begin_activity(
                world,
                kitty_id,
                Activity::Resting {
                    with_friend: partner,
                },
            );
            if let Some(friend) = partner {
                // A cuddle is a duet: the partner is bound in with the same
                // clock, and both get the closeness.
                begin_activity(
                    world,
                    friend,
                    Activity::Resting {
                        with_friend: Some(kitty_id),
                    },
                );
            }
            apply_activity_effects(world, kitty_id, config);
        }

        Action::Sleep { with } => {
            let partner = with.filter(|f| world.is_available_friend(kitty_id, *f));
            let in_sunbeam = world
                .kitty(kitty_id)
                .map(|k| {
                    world.element_at(k.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam)
                })
                .unwrap_or(false);
            begin_activity(
                world,
                kitty_id,
                Activity::Sleeping {
                    in_sunbeam,
                    with_friend: partner,
                },
            );
            apply_activity_effects(world, kitty_id, config);
        }

        Action::Groom { target } => {
            begin_activity(world, kitty_id, Activity::Grooming { target });
            apply_activity_effects(world, kitty_id, config);
        }

        Action::Eat => {
            begin_activity(world, kitty_id, Activity::Eating);
            apply_activity_effects(world, kitty_id, config);
        }

        Action::Drink => {
            begin_activity(world, kitty_id, Activity::Drinking);
            apply_activity_effects(world, kitty_id, config);
        }

        Action::Chase(target) => {
            let Some(kitty_pos) = world.kitty(kitty_id).map(|k| k.pos) else {
                return;
            };
            let target_pos = match target {
                TargetRef::Element { id } => world.element(id).map(|e| e.pos),
                TargetRef::Kitty { id } => world.kitty(id).map(|k| k.pos),
            };
            if let Some(target_pos) = target_pos {
                if let Some(dir) = Direction::toward(kitty_pos, target_pos) {
                    if let Some(dest) = kitty_pos.step(dir, world.width, world.height) {
                        // A chase that runs into another kitty simply stalls; the
                        // spec turns blocked movement into idling, never an error.
                        if world.kitty_at(dest).is_none() {
                            if let Some(idx) = world.kitty_index(kitty_id) {
                                world.kitties[idx].pos = dest;
                            }
                        }
                    }
                }
            }
            set_idle(world, kitty_id);
        }

        Action::Play { target } => {
            // Defensive mirror of validate, like the Rest arm's partner
            // filter: a kitty partner who cannot be conscripted (already
            // mid-activity) downgrades the proposal to solo play rather than
            // minting a one-sided duet that the invariants would refuse.
            let target = target.filter(|t| match t {
                TargetRef::Kitty { id } => world.is_conscriptable_friend(kitty_id, *id),
                TargetRef::Element { .. } => true,
            });
            begin_activity(world, kitty_id, Activity::Playing { target });
            if let Some(TargetRef::Kitty { id }) = target {
                // Social play is a duet: the partner is bound in with the
                // same clock, and both cats get the fun.
                begin_activity(
                    world,
                    id,
                    Activity::Playing {
                        target: Some(TargetRef::Kitty { id: kitty_id }),
                    },
                );
            }
            apply_activity_effects(world, kitty_id, config);
        }

        // Unreachable through validation since spec 011 (a purr proposal is
        // always Idle); kept as a harmless no-op because `apply` stays total
        // over the wire-compatible Action surface.
        Action::Purr => {}

        Action::Meow { message } => {
            emit_meow(world, kitty_id, message, config, tick);
        }
    }
}

/// Services the ongoing activity for one more tick (spec 006). Every activity
/// persists across ticks this way: the clock is stamped *unconditionally* --
/// even a tick that delivers no effects (a paused meal at an empty bowl, a
/// duet partner whose effects already landed this tick) must stay visible to
/// the end rules -- and per-tick effects land only when they have not already
/// been applied this tick.
fn continue_current_activity(world: &mut World, kitty_id: KittyId, config: &Config) {
    let tick = world.tick;
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    let Some(clock) = kitty.activity_clock else {
        // Nothing to continue. (A clockless in-progress activity cannot
        // exist in a lawful world -- strict invariant, no legacy heals.)
        return;
    };
    let effects_due = clock.applied < tick;
    stamp_serviced(world, kitty_id, tick);
    if effects_due {
        apply_activity_effects(world, kitty_id, config);
    }
}

/// One tick's worth of the ongoing activity's effects. The *only* effect
/// body: the starting tick and every continuation both land here, so what a
/// scene does per tick can never quietly differ between tick 1 and ticks
/// 2..n (the drift the 006 review caught brewing between the twin eat paths).
fn apply_activity_effects(world: &mut World, kitty_id: KittyId, config: &Config) {
    let effects = config.actions;
    let tick = world.tick;
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    let activity = kitty.activity;
    let pos = kitty.pos;

    match activity {
        // Unreachable for a lawful kitty (effects run only on activities in
        // progress); a harmless no-op rather than a panic, matching the
        // invariants' release policy.
        Activity::Idle => {}

        Activity::Eating => {
            if let Some(id) = world.adjacent_stocked_chow(pos).map(|e| e.id) {
                if let Some(el) = world.element_mut(id) {
                    if let ElementKind::Chow { servings } = &mut el.kind {
                        *servings = servings.saturating_sub(1);
                    }
                }
                lower_need(world, kitty_id, NeedKind::Eat, effects.eat_relief);
            }
            // An empty bowl is a paused meal: the cat licks the bowl clean --
            // no relief, no consumption; the caller's serviced stamp keeps
            // the end rules in reach so the meal ends once its minimum is met.
        }

        Activity::Drinking => {
            lower_need(world, kitty_id, NeedKind::Drink, effects.drink_relief);
        }

        Activity::Grooming { target } => match target {
            None => lower_need(world, kitty_id, NeedKind::Bath, effects.groom_relief),
            Some(friend) => {
                // Grooming a friend cleans them and satisfies the groomer's
                // own need for closeness. Only the groomer is in an activity;
                // the friend stays free and may wander off, ending it.
                lower_need(world, friend, NeedKind::Bath, effects.groom_relief);
                lower_need(world, kitty_id, NeedKind::Cuddle, effects.cuddle_relief);
            }
        },

        Activity::Playing { target } => match target {
            // Solo play is real play, just a smaller helping of it.
            None => lower_need(world, kitty_id, NeedKind::Play, effects.solo_play_relief),
            Some(TargetRef::Element { .. }) => {
                lower_need(world, kitty_id, NeedKind::Play, effects.play_relief);
            }
            Some(TargetRef::Kitty { id }) => {
                // The duet's effects land once per tick, from whichever
                // partner's slot runs first; the partner's stamp closes the
                // door on a second helping.
                lower_need(world, kitty_id, NeedKind::Play, effects.play_relief);
                lower_need(world, id, NeedKind::Play, effects.play_relief);
                stamp_serviced(world, id, tick);
            }
        },

        Activity::Resting { with_friend } => {
            if let Some(friend) = with_friend {
                lower_need(world, kitty_id, NeedKind::Cuddle, effects.cuddle_relief);
                lower_need(world, friend, NeedKind::Cuddle, effects.cuddle_relief);
                stamp_serviced(world, friend, tick);
            }
            // Solo rest is posture, not relief -- it ends by interrupt or cap.
        }

        Activity::Sleeping { with_friend, .. } => {
            // Re-check the nap's companions every serviced tick: the sunbeam
            // may have drifted away, and a co-sleeping friend (a companion,
            // never a conscript) may have wandered off.
            let partner = with_friend.filter(|f| world.is_available_friend(kitty_id, *f));
            let in_sunbeam =
                world.element_at(pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam);
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Sleeping {
                    in_sunbeam,
                    with_friend: partner,
                };
            }
            apply_sleep_relief(world, kitty_id, in_sunbeam, partner, config);
        }
    }
}

fn apply_sleep_relief(
    world: &mut World,
    kitty_id: KittyId,
    in_sunbeam: bool,
    partner: Option<KittyId>,
    config: &Config,
) {
    let relief = if in_sunbeam {
        config.actions.sleep_relief_sunbeam
    } else {
        config.actions.sleep_relief
    };
    lower_need(world, kitty_id, NeedKind::Sleep, relief);
    if let Some(friend) = partner {
        lower_need(
            world,
            kitty_id,
            NeedKind::Cuddle,
            config.actions.cuddle_relief,
        );
        lower_need(
            world,
            friend,
            NeedKind::Cuddle,
            config.actions.cuddle_relief,
        );
    }
}

fn emit_meow(
    world: &mut World,
    kitty_id: KittyId,
    message: MessageKind,
    config: &Config,
    tick: u64,
) {
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    // A meow on cooldown is swallowed, but the kitty still spent its turn saying
    // nothing -- exactly as the spec requires.
    if !kitty.can_meow(message, tick) {
        return;
    }
    let need_value = message.related_need().map(|n| kitty.needs.get(n));
    let cooldown = cooldown_for(
        message,
        need_value,
        config.meow.cooldown_ticks,
        config.meow.urgent_cooldown_ticks,
        config.meow.urgent_need_threshold,
    );
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].set_meow_cooldown(message, tick + cooldown);
    }
    world.recent_meows.push(Meow {
        kitty_id,
        kind: message,
        tick,
    });
}

/// Every relief in the engine flows through here, which is what makes the
/// `last_relief` stamp complete: actions, passive sleep ticks, and partner
/// effects all land in one place.
fn lower_need(world: &mut World, kitty_id: KittyId, need: NeedKind, amount: f32) {
    let tick = world.tick;
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].needs.add(need, -amount.abs());
        world.kitties[idx].last_relief.insert(need, tick);
    }
}

fn set_idle(world: &mut World, kitty_id: KittyId) {
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].clear_activity();
    }
}

/// Starts an activity with a fresh clock (spec 006). Every activity write and
/// its clock move together, keeping the strict pairing the invariants demand.
fn begin_activity(world: &mut World, kitty_id: KittyId, activity: Activity) {
    let tick = world.tick;
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].activity = activity;
        world.kitties[idx].activity_clock = Some(ActivityClock::start(tick));
    }
}

/// Marks the ongoing activity as serviced this tick without touching `started`.
fn stamp_serviced(world: &mut World, kitty_id: KittyId, tick: u64) {
    if let Some(idx) = world.kitty_index(kitty_id) {
        if let Some(clock) = &mut world.kitties[idx].activity_clock {
            clock.applied = tick;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::element::Element;
    use crate::grid::Position;
    use crate::test_support::test_world;

    #[test]
    fn blocked_moves_become_idle() {
        let (mut world, config) = test_world();
        // Put kitty 1 in the top-left corner and try to walk off the edge.
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(0, 0);

        let validated = validate(&world, 1, Action::move_to(Direction::North), &config);
        assert_eq!(validated, Action::Idle, "walking off the grid is illegal");
    }

    #[test]
    fn moving_onto_another_kitty_is_illegal() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        let b = world.kitty_index(2).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[b].pos = Position::new(5, 4); // directly north

        let validated = validate(&world, 1, Action::move_to(Direction::North), &config);
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn eating_requires_nearby_chow() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);

        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Idle);

        world.push_element(Element {
            id: 900,
            kind: ElementKind::Chow { servings: 2 },
            pos: Position::new(5, 6),
            ttl: None,
        });
        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Eat);
    }

    #[test]
    fn diagonal_interactions_are_out_of_range() {
        // Spec 009 FR-002: a target on a diagonal tile is out of range for
        // every interaction — the proposal resolves to Idle, never fires.
        // The same layouts shifted one tile to orthogonal validate through.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Chow { servings: 2 },
            pos: Position::new(6, 6), // corner-to-corner
            ttl: None,
        });
        world.push_element(Element {
            id: 904,
            kind: ElementKind::Water,
            pos: Position::new(4, 6),
            ttl: None,
        });
        world.push_element(Element {
            id: 905,
            kind: ElementKind::Bug,
            pos: Position::new(4, 4),
            ttl: Some(50),
        });

        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Idle);
        assert_eq!(validate(&world, 1, Action::Drink, &config), Action::Idle);
        assert_eq!(
            validate(
                &world,
                1,
                Action::play_with(TargetRef::Element { id: 905 }),
                &config
            ),
            Action::Idle,
            "batting across a corner is no longer a thing"
        );

        // Step each element to an orthogonal neighbour: all three legal again.
        world.element_mut(903).unwrap().pos = Position::new(6, 5);
        world.element_mut(904).unwrap().pos = Position::new(4, 5);
        world.element_mut(905).unwrap().pos = Position::new(5, 4);
        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Eat);
        assert_eq!(validate(&world, 1, Action::Drink, &config), Action::Drink);
        assert_eq!(
            validate(
                &world,
                1,
                Action::play_with(TargetRef::Element { id: 905 }),
                &config
            ),
            Action::play_with(TargetRef::Element { id: 905 })
        );
    }

    #[test]
    fn a_diagonal_friend_is_out_of_reach_for_duets_and_grooming() {
        // Spec 009: cuddling, social play, co-sleeping and grooming all take
        // the orthogonal range through the friend-availability helpers.
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        let b = world.kitty_index(2).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[b].pos = Position::new(6, 6); // corner-to-corner

        for proposal in [
            Action::Rest { with: Some(2) },
            Action::Sleep { with: Some(2) },
            Action::Groom { target: Some(2) },
            Action::play_with(TargetRef::Kitty { id: 2 }),
        ] {
            assert_eq!(
                validate(&world, 1, proposal, &config),
                Action::Idle,
                "diagonal partner must be out of range for {proposal:?}"
            );
        }

        world.kitties[b].pos = Position::new(6, 5); // beside
        assert_eq!(
            validate(&world, 1, Action::Rest { with: Some(2) }, &config),
            Action::Rest { with: Some(2) }
        );
        assert_eq!(
            validate(&world, 1, Action::Groom { target: Some(2) }, &config),
            Action::Groom { target: Some(2) }
        );
    }

    #[test]
    fn empty_chow_cannot_be_eaten() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Chow { servings: 0 },
            pos: Position::new(5, 5),
            ttl: None,
        });
        assert_eq!(validate(&world, 1, Action::Eat, &config), Action::Idle);
    }

    #[test]
    fn eating_consumes_one_serving_and_relieves_hunger() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.kitties[idx].needs.add(NeedKind::Eat, 80.0);
        world.push_element(Element {
            id: 902,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(5, 5),
            ttl: None,
        });

        apply(&mut world, 1, Action::Eat, &config);

        let kitty = world.kitty(1).unwrap();
        assert!(
            (kitty.needs.get(NeedKind::Eat) - 40.0).abs() < 0.01,
            "80 - 40 relief"
        );
        let chow = world.element(902).unwrap();
        assert!(matches!(chow.kind, ElementKind::Chow { servings: 2 }));
    }

    #[test]
    fn playing_with_a_friend_delights_them_both() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[a].needs.add(NeedKind::Play, 60.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(5, 6);
        world.kitties[b].needs.add(NeedKind::Play, 60.0);

        apply(
            &mut world,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
            &config,
        );

        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Play) - 35.0).abs() < 0.01);
        assert!(
            (world.kitty(2).unwrap().needs.get(NeedKind::Play) - 35.0).abs() < 0.01,
            "the friend has fun too"
        );
    }

    #[test]
    fn playing_with_a_distant_friend_is_illegal() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(1, 1);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);

        let validated = validate(
            &world,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
            &config,
        );
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn purring_is_no_longer_an_action() {
        // Spec 011: purring is engine-owned background state; the proposal
        // shape survives for pre-011 snapshots' last_action, but validation
        // refuses it regardless of how earned the purr would have been.
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = false;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);

        // Even a delighted kitty spends no turn on it...
        world.kitties[idx].happiness = 80.0;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);

        // ...and neither does a brightening one.
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = true;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);
    }

    #[test]
    fn grooming_a_friend_cleans_them_and_comforts_the_groomer() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Bath, 60.0);

        apply(&mut world, 1, Action::Groom { target: Some(2) }, &config);

        assert!((world.kitty(2).unwrap().needs.get(NeedKind::Bath) - 30.0).abs() < 0.01);
        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Cuddle) - 30.0).abs() < 0.01);
    }

    #[test]
    fn sleeping_in_a_sunbeam_is_more_restful() {
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(6, 6);
        world.kitties[idx].needs.add(NeedKind::Sleep, 90.0);

        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        let plain = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);

        let idx2 = world.kitty_index(2).unwrap();
        world.kitties[idx2].pos = Position::new(2, 2);
        world.kitties[idx2].needs.add(NeedKind::Sleep, 90.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(2, 2),
            ttl: Some(50),
        });
        apply(&mut world, 2, Action::Sleep { with: None }, &config);
        let sunny = 90.0 - world.kitty(2).unwrap().needs.get(NeedKind::Sleep);

        assert!(sunny > plain, "sunbeam {sunny} should beat plain {plain}");
    }

    #[test]
    fn meows_on_cooldown_are_silently_dropped() {
        let (mut world, config) = test_world();
        apply(
            &mut world,
            1,
            Action::Meow {
                message: MessageKind::FollowMe,
            },
            &config,
        );
        assert_eq!(world.recent_meows.len(), 1);

        // Immediately again: cooldown swallows it, but it was still a legal action.
        apply(
            &mut world,
            1,
            Action::Meow {
                message: MessageKind::FollowMe,
            },
            &config,
        );
        assert_eq!(world.recent_meows.len(), 1, "second meow was dropped");
    }

    #[test]
    fn idling_keeps_a_sleeping_kitty_asleep() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Sleep, 80.0);
        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        assert!(world.kitty(1).unwrap().activity.is_sleeping());

        // Effects land once per tick (spec 006), so the continuation is
        // serviced on the next tick, as it would be in the real loop.
        world.tick += 1;
        let before = world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        apply(&mut world, 1, Action::Idle, &config);
        let after = world.kitty(1).unwrap().needs.get(NeedKind::Sleep);

        assert!(world.kitty(1).unwrap().activity.is_sleeping());
        assert!(after < before, "sleep continues to restore");
        let clock = world.kitty(1).unwrap().activity_clock.expect("clocked");
        assert_eq!(
            clock.applied, world.tick,
            "the continuation stamped the clock"
        );
    }

    #[test]
    fn a_departed_cosleeping_partner_stops_granting_cuddles() {
        // A cuddle partner is conscripted and cannot wander (spec 006); a
        // co-sleeping partner is a companion, not a conscript, and can.
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(3, 3);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(3, 4);

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        assert_eq!(world.kitty(1).unwrap().activity.partner(), Some(2));
        assert!(
            world.kitty(2).unwrap().activity_clock.is_none(),
            "a co-sleeping reference binds nobody"
        );

        // The friend wanders off.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);
        world.tick += 1;
        apply(&mut world, 1, Action::Idle, &config);

        assert_eq!(
            world.kitty(1).unwrap().activity.partner(),
            None,
            "sleeping continues, but alone"
        );
        assert!(world.kitty(1).unwrap().activity.is_sleeping());
    }

    #[test]
    fn a_play_proposal_at_a_busy_partner_downgrades_to_solo_play() {
        // Direct apply() callers bypass validate; the arm's defensive filter
        // must not mint a one-sided duet or yank the partner out of its meal.
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(3, 3);
        world.kitties[a].needs.add(NeedKind::Play, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(3, 4);
        world.kitties[b].activity = Activity::Eating;
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        let partner_clock = world.kitty(2).unwrap().activity_clock;

        apply(
            &mut world,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
            &config,
        );

        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Playing { target: None },
            "the proposal downgrades to solo play"
        );
        assert_eq!(
            world.kitty(2).unwrap().activity,
            Activity::Eating,
            "the busy partner keeps its meal"
        );
        assert_eq!(
            world.kitty(2).unwrap().activity_clock,
            partner_clock,
            "and its clock is untouched"
        );
        assert_eq!(
            world.kitty(2).unwrap().needs.get(NeedKind::Play),
            0.0,
            "no play relief is invented for the absent partner"
        );
    }

    #[test]
    fn a_cuddle_is_a_duet_with_one_shared_clock() {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(3, 3);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(3, 4);

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);

        assert_eq!(world.kitty(1).unwrap().activity.partner(), Some(2));
        assert_eq!(
            world.kitty(2).unwrap().activity.partner(),
            Some(1),
            "the partner is bound into the duet"
        );
        assert_eq!(
            world.kitty(1).unwrap().activity_clock,
            world.kitty(2).unwrap().activity_clock,
            "one shared clock"
        );
    }

    #[test]
    fn chasing_a_vanished_target_is_illegal() {
        let (world, config) = test_world();
        let validated = validate(
            &world,
            1,
            Action::Chase(TargetRef::Element { id: 99_999 }),
            &config,
        );
        assert_eq!(validated, Action::Idle);
    }

    #[test]
    fn only_critters_can_be_chased() {
        let (mut world, config) = test_world();
        world.elements.clear();
        world.push_element(Element {
            id: 910,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(7, 7),
            ttl: None,
        });
        world.push_element(Element {
            id: 911,
            kind: ElementKind::Bug,
            pos: Position::new(8, 8),
            ttl: Some(50),
        });

        // Food does not flee.
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Element { id: 910 }),
                &config
            ),
            Action::Idle
        );
        // Bugs do.
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Element { id: 911 }),
                &config
            ),
            Action::Chase(TargetRef::Element { id: 911 })
        );
    }

    #[test]
    fn social_play_keeps_its_pre_004_wire_shape() {
        let action = Action::play_with(TargetRef::Element { id: 103 });
        let json = serde_json::to_value(action).unwrap();
        assert_eq!(
            json,
            serde_json::json!({"action": "play", "target": "element", "id": 103}),
            "old consumers must see the exact old shape"
        );
        // And the old shape parses back.
        let parsed: Action =
            serde_json::from_value(serde_json::json!({"action":"play","target":"kitty","id":2}))
                .unwrap();
        assert_eq!(parsed, Action::play_with(TargetRef::Kitty { id: 2 }));
    }

    #[test]
    fn solo_play_serializes_without_a_target_and_round_trips() {
        let json = serde_json::to_value(Action::play_solo()).unwrap();
        assert_eq!(json, serde_json::json!({"action": "play"}));
        let parsed: Action = serde_json::from_value(json).unwrap();
        assert_eq!(parsed, Action::play_solo());
    }

    #[test]
    fn a_malformed_play_target_is_an_error_not_a_free_helping_of_solo_play() {
        // Regression: `#[serde(flatten)]` over an Option swallows anything it
        // cannot parse, which turned a garbled proposal into solo play --
        // always legal, and rewarded. A broken advisor must get the safe no-op
        // path, never relief it did not earn (Article IV).
        for malformed in [
            r#"{"action":"play","target":"element"}"#,      // no id
            r#"{"action":"play","target":"kitty"}"#,        // no id
            r#"{"action":"play","id":7}"#,                  // no target kind
            r#"{"action":"play","target":"bogus","id":1}"#, // unknown kind
            r#"{"action":"play","target":"element","id":"three"}"#, // wrong id type
        ] {
            let parsed: Result<Action, _> = serde_json::from_str(malformed);
            assert!(
                parsed.is_err(),
                "{malformed} parsed as {:?} instead of failing",
                parsed.unwrap()
            );
        }

        // ...while both legitimate shapes still parse exactly as before.
        assert_eq!(
            serde_json::from_str::<Action>(r#"{"action":"play","target":"element","id":103}"#)
                .unwrap(),
            Action::play_with(TargetRef::Element { id: 103 })
        );
        assert_eq!(
            serde_json::from_str::<Action>(r#"{"action":"play","target":"kitty","id":2}"#).unwrap(),
            Action::play_with(TargetRef::Kitty { id: 2 })
        );
        assert_eq!(
            serde_json::from_str::<Action>(r#"{"action":"play"}"#).unwrap(),
            Action::play_solo()
        );
    }

    #[test]
    fn every_target_kind_survives_the_strict_play_parser() {
        // The strict parser spells out the target kinds, so a new TargetRef
        // variant must be added there too. This test is what catches it.
        for target in [TargetRef::Element { id: 11 }, TargetRef::Kitty { id: 2 }] {
            let json = serde_json::to_string(&Action::play_with(target)).unwrap();
            assert_eq!(
                serde_json::from_str::<Action>(&json).unwrap(),
                Action::play_with(target),
                "{json} did not survive a round trip -- is strict_play_target missing a kind?"
            );
        }
    }

    #[test]
    fn solo_play_is_always_legal() {
        let (world, config) = test_world();
        assert_eq!(
            validate(&world, 1, Action::play_solo(), &config),
            Action::play_solo(),
            "pouncing at nothing needs no permission, like self-grooming"
        );
    }

    #[test]
    fn solo_play_relieves_less_than_the_real_thing() {
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Play, 80.0);

        apply(&mut world, 1, Action::play_solo(), &config);

        let after = world.kitty(1).unwrap().needs.get(NeedKind::Play);
        let expected = 80.0 - config.actions.solo_play_relief;
        assert!(
            (after - expected).abs() < 0.01,
            "solo relief is solo_play_relief ({}), got {after}",
            config.actions.solo_play_relief
        );
        assert!(
            config.actions.solo_play_relief < config.actions.play_relief,
            "config validation keeps social play the better deal"
        );
    }

    #[test]
    fn a_kitty_cannot_target_itself() {
        let (world, config) = test_world();
        assert_eq!(
            validate(
                &world,
                1,
                Action::Chase(TargetRef::Kitty { id: 1 }),
                &config
            ),
            Action::Idle
        );
        assert_eq!(
            validate(
                &world,
                1,
                Action::play_with(TargetRef::Kitty { id: 1 }),
                &config
            ),
            Action::Idle
        );
    }
}
