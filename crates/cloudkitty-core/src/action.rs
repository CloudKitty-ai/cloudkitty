//! Actions: what a kitty does with its tick.
//!
//! Article IV (v1.2.0): behaviors *propose*, the engine disposes -- in two
//! distinct layers. External bytes MUST enter through [`parse_proposal`], the
//! strict outer gate: anything malformed fails there and the kitty's fallback
//! behavior takes the turn (the derived `Deserialize` stays lenient about
//! unknown keys and is reserved for data the engine wrote itself, like
//! snapshots). What parses then passes through [`validate`], which returns
//! the action to actually apply -- [`Action::Idle`] whenever the proposal is
//! illegal for the current world state. Neither layer can become a kitty's
//! problem: an advisor's mistake resolves to a safe outcome, never an error.

use serde::{Deserialize, Deserializer, Serialize};

use crate::config::Config;
use crate::element::{ElementId, ElementKind, ElementType};
use crate::grid::{Direction, Position};
use crate::kitty::{Activity, ActivityClock, KittyId};
use crate::meow::{Meow, MessageKind};
use crate::needs::NeedKind;
use crate::world::{PurrOrigin, World};

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
/// and carries relief, so a garbled proposal would become a *free treat* instead of
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

/// The proposal wire's version, carried in every plugin decision request.
/// Bump on any breaking change to the accepted proposal shapes.
pub const PROPOSAL_WIRE_VERSION: u32 = 1;

/// Why a proposal failed to parse (spec 016). Every kind resolves the same
/// way downstream -- the fallback decides, per amended Article IV's default --
/// so these exist for the operator reading the rejection log, not for
/// divergent handling.
#[derive(Debug, thiserror::Error)]
pub enum ProposalError {
    #[error("not JSON: {0}")]
    NotJson(serde_json::Error),
    #[error("valid JSON, but a proposal must be an object")]
    NotAnObject,
    #[error("no \"action\" key names the action kind")]
    MissingKind,
    #[error("unknown action kind {0}")]
    UnknownKind(String),
    #[error("bad fields for {kind:?}: {error}")]
    InvalidFields {
        kind: &'static str,
        error: serde_json::Error,
    },
}

/// Per-variant strict mirrors of [`Action`]'s wire shapes (spec 016,
/// research R1). `deny_unknown_fields` cannot be used on `Action` itself
/// (it is internally tagged and `Play` flattens), so each variant's fields
/// are accepted by a mirror that *can* reject unknown keys, then converted
/// into the real variant -- field by field, so a drift between `Action` and
/// its mirror is a compile error or an immediate round-trip test failure,
/// never a silently widened wire.
mod proposal_wire {
    use serde::Deserialize;

    use super::TargetRef;
    use crate::grid::Direction;
    use crate::kitty::KittyId;
    use crate::meow::MessageKind;

    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct MoveWire {
        pub direction: Direction,
    }

    /// Rest and sleep share a shape: an optional kitty to duet with.
    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct WithWire {
        #[serde(default)]
        pub with: Option<KittyId>,
    }

    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct GroomWire {
        #[serde(default)]
        pub target: Option<KittyId>,
    }

    /// Eat, drink, purr, and idle carry nothing but their kind.
    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct EmptyWire {}

    #[derive(Deserialize, Clone, Copy)]
    #[serde(rename_all = "snake_case")]
    pub(super) enum TargetKindWire {
        Element,
        Kitty,
    }

    impl TargetKindWire {
        pub(super) fn with_id(self, id: u32) -> TargetRef {
            match self {
                TargetKindWire::Element => TargetRef::Element { id },
                TargetKindWire::Kitty => TargetRef::Kitty { id },
            }
        }
    }

    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct ChaseWire {
        pub target: TargetKindWire,
        pub id: u32,
    }

    /// Play's target is optional but must be all-or-nothing -- the same rule
    /// `strict_play_target` enforces on the internal derive.
    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct PlayWire {
        #[serde(default)]
        pub target: Option<TargetKindWire>,
        #[serde(default)]
        pub id: Option<u32>,
    }

    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct MeowWire {
        pub message: MessageKind,
    }
}

/// Parses one proposal from external bytes, strictly (spec 016 FR-002).
///
/// This -- not `Action`'s derived `Deserialize` -- is the mandatory entry
/// point wherever untrusted bytes arrive (plugin transports). The derive
/// stays lenient about unknown keys and is reserved for data we wrote
/// ourselves (snapshots, fixtures); everything the engine serializes parses
/// back through here unchanged (the round-trip suite pins that).
pub fn parse_proposal(input: &str) -> Result<Action, ProposalError> {
    // Duplicate keys collapsed to the last occurrence here, before any
    // strict check -- standard JSON semantics, documented in the contract.
    let value: serde_json::Value = serde_json::from_str(input).map_err(ProposalError::NotJson)?;
    parse_proposal_value(value)
}

/// [`parse_proposal`] for input that is already a parsed [`serde_json::Value`]
/// (the plugin reply envelope carries the proposal as one). Same strict gate,
/// same semantics -- duplicate keys collapsed last-wins when the `Value` was
/// parsed, exactly as `parse_proposal`'s own first step would have -- without
/// a render-to-string round trip.
pub fn parse_proposal_value(value: serde_json::Value) -> Result<Action, ProposalError> {
    use proposal_wire::*;

    let serde_json::Value::Object(mut map) = value else {
        return Err(ProposalError::NotAnObject);
    };
    let Some(kind_value) = map.remove("action") else {
        return Err(ProposalError::MissingKind);
    };
    let serde_json::Value::String(kind) = kind_value else {
        return Err(ProposalError::UnknownKind(kind_value.to_string()));
    };
    let rest = serde_json::Value::Object(map);

    fn fields<T: serde::de::DeserializeOwned>(
        kind: &'static str,
        rest: serde_json::Value,
    ) -> Result<T, ProposalError> {
        serde_json::from_value(rest).map_err(|error| ProposalError::InvalidFields { kind, error })
    }

    match kind.as_str() {
        "move" => Ok(Action::Move {
            direction: fields::<MoveWire>("move", rest)?.direction,
        }),
        "rest" => Ok(Action::Rest {
            with: fields::<WithWire>("rest", rest)?.with,
        }),
        "sleep" => Ok(Action::Sleep {
            with: fields::<WithWire>("sleep", rest)?.with,
        }),
        "groom" => Ok(Action::Groom {
            target: fields::<GroomWire>("groom", rest)?.target,
        }),
        "eat" => fields::<EmptyWire>("eat", rest).map(|_| Action::Eat),
        "drink" => fields::<EmptyWire>("drink", rest).map(|_| Action::Drink),
        "chase" => {
            let wire = fields::<ChaseWire>("chase", rest)?;
            Ok(Action::Chase(wire.target.with_id(wire.id)))
        }
        "play" => {
            let wire = fields::<PlayWire>("play", rest)?;
            match (wire.target, wire.id) {
                (None, None) => Ok(Action::play_solo()),
                (Some(target), Some(id)) => Ok(Action::play_with(target.with_id(id))),
                _ => Err(ProposalError::InvalidFields {
                    kind: "play",
                    error: <serde_json::Error as serde::de::Error>::custom(
                        "a play target must be a complete {\"target\": \"element\"|\"kitty\", \
                         \"id\": N} or omitted entirely for solo play",
                    ),
                }),
            }
        }
        "purr" => fields::<EmptyWire>("purr", rest).map(|_| Action::Purr),
        "meow" => Ok(Action::Meow {
            message: fields::<MeowWire>("meow", rest)?.message,
        }),
        "idle" => fields::<EmptyWire>("idle", rest).map(|_| Action::Idle),
        other => Err(ProposalError::UnknownKind(other.to_string())),
    }
}

/// Returns the action the engine will actually apply: the proposal if it is legal,
/// otherwise `Idle`. This is the whole of Article IV's enforcement surface.
pub fn validate(world: &World, kitty_id: KittyId, proposal: Action, config: &Config) -> Action {
    let Some(kitty) = world.kitty(kitty_id) else {
        return Action::Idle;
    };

    let legal = match proposal {
        // Spec 028: the meow left the activity menu -- the message channel
        // (`Decision.message`, ruled by `meow::message_legal`) is the only
        // way to speak, deliberate purr included. A stray Meow proposal
        // (plugin wire, stale replay) resolves to Idle: the Purr-retirement
        // precedent, lawful degradation over error.
        Action::Meow { .. } => false,
        Action::Idle => true,

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
                        if world.kitty_at(dest).is_none() {
                            if let Some(idx) = world.kitty_index(kitty_id) {
                                world.kitties[idx].pos = dest;
                            }
                        } else {
                            // Spec 024: a blocked chase step routes around the
                            // friend instead of freezing mid-pounce. Two tiers:
                            // a lawful step that still CLOSES distance wins
                            // (the other axis, when the target sits diagonal);
                            // otherwise a perpendicular arc (+1 Manhattan) --
                            // routing around a blocker standing squarely in an
                            // axis-aligned lane necessarily arcs before it
                            // passes. The reverse direction is never a
                            // candidate: arcing is routing, walking backwards
                            // is retreat. The pick is one uniform draw from
                            // the master RNG at apply time in the tick's fair
                            // apply order -- deterministic given the seed, and
                            // two blocked kitties draw successive stream
                            // values, so they can never compute the same pick
                            // from shared state (the livelock family's root
                            // cause; behavior/mod.rs's note, spec 012
                            // FR-008's guarantees delivered engine-side). The
                            // draw count depends only on world state, never
                            // on config (the fixed-shape rule governs config,
                            // not state). Preference-free: no dry-tile bias,
                            // the engine is mechanics -- a wet sidestep pays
                            // the wet-fur charge. Empty pool (boxed in) keeps
                            // the old stall, patience clock unchanged. Pounce
                            // range keeps it too: at distance 1 every lawful
                            // perpendicular step is +1 Manhattan -- a
                            // guaranteed retreat wearing an arc's name -- so
                            // a cat already beside its target never draws
                            // (the `current > 1` rule needs_driven's own
                            // sidestep has always had).
                            let current = kitty_pos.manhattan_distance(&target_pos);
                            if current > 1 {
                                let mut closing: Vec<Position> = Vec::new();
                                let mut arcing: Vec<Position> = Vec::new();
                                for d in Direction::ALL {
                                    if d == dir || d == dir.opposite() {
                                        continue;
                                    }
                                    let Some(p) = kitty_pos.step(d, world.width, world.height)
                                    else {
                                        continue;
                                    };
                                    if world.kitty_at(p).is_some() {
                                        continue;
                                    }
                                    if p.manhattan_distance(&target_pos) < current {
                                        closing.push(p);
                                    } else {
                                        arcing.push(p);
                                    }
                                }
                                let pool = if closing.is_empty() {
                                    &arcing
                                } else {
                                    &closing
                                };
                                if let Some(side) = world.rng.choose(pool).copied() {
                                    if let Some(idx) = world.kitty_index(kitty_id) {
                                        world.kitties[idx].pos = side;
                                    }
                                }
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

        // Unreachable through validation since spec 028 (the message
        // channel is the only way to meow); a harmless no-op like Purr,
        // because `apply` stays total over the wire-compatible surface.
        Action::Meow { .. } => {}
    }
}

/// Applies one kitty's **message** for the tick (spec 028): the second half
/// of a `Decision`, ruled legal by `meow::message_legal` before this is
/// called. `Purr` starts the deliberate purr (the same phenomenon the
/// retired purr-meow row started); every other kind emits.
pub(crate) fn apply_message(
    world: &mut World,
    kitty_id: KittyId,
    kind: MessageKind,
    config: &Config,
    tick: u64,
) {
    match kind {
        MessageKind::Purr => start_deliberate_purr(world, kitty_id, config, tick),
        _ => emit_message(world, kitty_id, kind, config, tick),
    }
}

/// The deliberate purr (spec 022): the purr-meow row starts a real purr
/// phase -- the same phenomenon the motor produces, initiated by choice.
/// Already purring (either origin) is a silent no-op: the turn is spent,
/// nothing is drawn, nothing is announced. Otherwise the shared start
/// transition (`World::start_purr`) runs here, at apply time in the tick's
/// fair apply order (the Article V pin), with the one start announcement
/// recorded directly -- a state announcement, never swallowed and stamping
/// no message cooldown. The motor's cooldown is deliberately not consulted:
/// choice beats reflex (spec 022 FR-005), which is what makes this action's
/// outcome fully predictable to a policy.
fn start_deliberate_purr(world: &mut World, kitty_id: KittyId, config: &Config, tick: u64) {
    let Some(idx) = world.kitty_index(kitty_id) else {
        return;
    };
    if world.kitties[idx].purring_until.is_some() {
        return;
    }
    world.start_purr(idx, config, tick, PurrOrigin::Deliberate);
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
            Some(TargetRef::Element { id }) => {
                // Spec 025: element play is worth what the element is, read
                // at effect time. In the canonical loop a vanished target
                // never reaches this arm -- prune_dead_activity ends the
                // scene at the kitty's next slot -- so the solo fallback is
                // defense-in-depth: apply stays total for direct callers,
                // and a missing (or non-critter) id pays the pouncing-at-
                // nothing price, never a critter's. The duet arm below is
                // deliberately untouched.
                let relief = match world.element(id).map(|e| e.element_type()) {
                    Some(ElementType::Bug) => effects.play_relief_bug,
                    Some(ElementType::Greeble) => effects.play_relief_greeble,
                    _ => effects.solo_play_relief,
                };
                lower_need(world, kitty_id, NeedKind::Play, relief);
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

fn emit_message(
    world: &mut World,
    kitty_id: KittyId,
    message: MessageKind,
    config: &Config,
    tick: u64,
) {
    let Some(kitty) = world.kitty(kitty_id) else {
        return;
    };
    // The stamped intensity (spec 028): the grounding need's value at
    // emission, on [0, 1] -- a listener hears how hungry, not just that.
    // The social words (FollowMe, WaitForMe) carry 0.0.
    let intensity = message
        .related_need()
        .map(|need| (kitty.needs.get(need) / 100.0).clamp(0.0, 1.0))
        .unwrap_or(0.0);
    // One uniform stamp: the audibility window doubles as the per-kind
    // cooldown -- one live digest entry per kind per emitter, never sooner.
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].set_meow_cooldown(message, tick + config.meow.recent_window_ticks);
    }
    world.recent_meows.push(Meow {
        kitty_id,
        kind: message,
        tick,
        intensity,
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

        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Play) - 40.0).abs() < 0.01);
        assert!(
            (world.kitty(2).unwrap().needs.get(NeedKind::Play) - 40.0).abs() < 0.01,
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
    fn the_legacy_purr_action_is_still_refused() {
        // Spec 011 retired `Action::Purr`; spec 022 deliberately did NOT
        // revive it (shape B rejected -- the deliberate purr is the
        // purr-meow row instead). The legacy wire shape survives only for
        // pre-011 snapshots' last_action, and validation refuses it
        // regardless of how earned the purr would have been.
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = false;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);

        world.kitties[idx].happiness = 80.0;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);

        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = true;
        assert_eq!(validate(&world, 1, Action::Purr, &config), Action::Idle);
    }

    #[test]
    fn a_deliberate_purr_starts_a_real_purr_with_one_announcement() {
        // Spec 022 US1, carried by the message channel since spec 028: the
        // purr message starts a purr phase with the normal duration draw and
        // exactly one start announcement -- even under an active motor
        // cooldown (choice beats reflex, FR-005).
        let (mut world, config) = test_world();
        world.tick = 50;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0; // earned
        world.kitties[idx].purr_cooldown_until = 1_000; // motor deep in rest

        assert!(
            crate::meow::message_legal(world.kitty(1).unwrap(), MessageKind::Purr, 50, &config),
            "an earned purr message is legal"
        );
        apply_message(&mut world, 1, MessageKind::Purr, &config, 50);

        let kitty = world.kitty(1).unwrap();
        let until = kitty.purring_until.expect("the chosen purr is real");
        let duration = kitty
            .purring_duration
            .expect("the duration is stored for the proportional cooldown");
        assert_eq!(until, 50 + duration);
        assert!(
            (config.purr.min_ticks..=config.purr.max_ticks).contains(&duration),
            "duration {duration} within [{}, {}]",
            config.purr.min_ticks,
            config.purr.max_ticks
        );
        let purrs = world
            .recent_meows
            .iter()
            .filter(|m| m.kind == MessageKind::Purr)
            .count();
        assert_eq!(purrs, 1, "exactly one announcement, never swallowed");
    }

    #[test]
    fn an_unearned_purr_message_is_illegal() {
        // Spec 022 FR-004's earned gate, spoken through the channel since
        // spec 028: message_legal says no, so enforcement downgrades the
        // message to Silent (the channel's Article IV).
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 50.0;
        world.kitties[idx].happiness_rose = false;
        assert!(!crate::meow::message_legal(
            world.kitty(1).unwrap(),
            MessageKind::Purr,
            world.tick,
            &config
        ));
    }

    #[test]
    fn a_retired_meow_proposal_lawfully_resolves() {
        // Spec 028 (the Purr-retirement precedent): the meow left the
        // activity menu. A stray Meow proposal -- plugin wire, stale
        // replay -- parses, validates to Idle, and applies as a no-op;
        // never an error, never an emission.
        let (mut world, config) = test_world();
        for message in MessageKind::ALL {
            let proposal = Action::Meow { message };
            assert_eq!(
                validate(&world, 1, proposal, &config),
                Action::Idle,
                "{message:?} as an activity resolves to Idle"
            );
        }
        let before = world.recent_meows.len();
        apply(
            &mut world,
            1,
            Action::Meow {
                message: MessageKind::WantEat,
            },
            &config,
        );
        assert_eq!(world.recent_meows.len(), before, "no emission from apply");
    }

    #[test]
    fn a_deliberate_purr_while_already_purring_is_a_silent_no_op() {
        // Spec 022 FR-006: turn consumed, no state change, no announcement,
        // and -- crucially -- no RNG draw. Comparing full serialized worlds
        // (RNG state included) proves the stream is untouched.
        let (mut world, config) = test_world();
        world.tick = 50;
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].happiness = 90.0;
        world.kitties[idx].purring_until = Some(55);
        world.kitties[idx].purring_duration = Some(9);
        let twin = world.clone();

        assert!(
            crate::meow::message_legal(world.kitty(1).unwrap(), MessageKind::Purr, 50, &config),
            "legal while purring -- the no-op is lawful, not masked"
        );
        apply_message(&mut world, 1, MessageKind::Purr, &config, 50);

        assert_eq!(
            serde_json::to_string(&world).unwrap(),
            serde_json::to_string(&twin).unwrap(),
            "silent no-op: identical world, identical RNG stream"
        );
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

        assert!((world.kitty(2).unwrap().needs.get(NeedKind::Bath) - 40.0).abs() < 0.01);
        assert!((world.kitty(1).unwrap().needs.get(NeedKind::Cuddle) - 35.0).abs() < 0.01);
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
    fn every_emission_stamps_and_is_heard() {
        // Spec 028 emission shape: apply_message emits (recent_meows push,
        // audible to everyone) and stamps the per-kind cooldown in the same
        // breath. Legality is the caller's ruling (message_legal) -- this
        // path itself never swallows.
        let (mut world, config) = test_world();
        let tick = world.tick;
        apply_message(&mut world, 1, MessageKind::FollowMe, &config, tick);
        assert_eq!(world.recent_meows.len(), 1);
        let first_stamp = world.kitty(1).unwrap().meow_cooldowns[&MessageKind::FollowMe];
        assert_eq!(first_stamp, tick + config.meow.recent_window_ticks);

        world.tick += 1;
        let tick = world.tick;
        apply_message(&mut world, 1, MessageKind::FollowMe, &config, tick);
        assert_eq!(world.recent_meows.len(), 2, "the emit path never swallows");
        let second_stamp = world.kitty(1).unwrap().meow_cooldowns[&MessageKind::FollowMe];
        assert!(second_stamp > first_stamp, "every emission re-stamps");
    }

    #[test]
    fn the_stamp_is_the_window_and_intensity_is_the_need() {
        // Spec 028: every emission stamps tick + recent_window_ticks (the
        // urgent carve-out is gone), and a want-kind stamps the grounding
        // need's value /100 as its intensity; social words stamp 0.0.
        let (mut world, config) = test_world();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].needs.add(NeedKind::Eat, 90.0);
        let tick = world.tick;
        apply_message(&mut world, 1, MessageKind::WantEat, &config, tick);
        assert_eq!(
            world.kitty(1).unwrap().meow_cooldowns[&MessageKind::WantEat],
            tick + config.meow.recent_window_ticks,
            "uniform stamp: the window is the cooldown"
        );
        let meow = world.recent_meows.last().unwrap();
        assert!(
            (meow.intensity - 0.9).abs() < 1e-6,
            "want-kind intensity is need/100, got {}",
            meow.intensity
        );

        apply_message(&mut world, 1, MessageKind::FollowMe, &config, tick);
        assert_eq!(
            world.recent_meows.last().unwrap().intensity,
            0.0,
            "social words carry no intensity"
        );
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

    /// Rig: chaser at (5,5), a bug down the lane, an optional blocker.
    /// Returns the world ready for one Chase apply (spec 024 sidestep).
    /// Without a blocker, kitty 2 parks in the far corner of the 16x16
    /// test world -- in bounds, out of the lane.
    fn chase_lane(bug: Position, blocker: Option<Position>) -> (crate::world::World, Config) {
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = blocker.unwrap_or(Position::new(15, 15));
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Bug,
            pos: bug,
            ttl: None,
        });
        (world, config)
    }

    #[test]
    fn a_blocked_lane_chase_arcs_instead_of_stalling() {
        // The headline jank (spec 024 US2): friend squarely in the lane.
        // Both perpendicular arcs are +1 Manhattan; the reverse and the
        // stall are the two forbidden outcomes.
        let (mut world, config) = chase_lane(Position::new(8, 5), Some(Position::new(6, 5)));
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 901 }),
            &config,
        );
        let pos = world.kitty(1).unwrap().pos;
        assert!(
            pos == Position::new(5, 4) || pos == Position::new(5, 6),
            "an arc, not a stall or a retreat: {pos:?}"
        );
    }

    #[test]
    fn a_diagonal_blocked_chase_takes_the_closing_axis() {
        // Target at (8,7): east is dominant and blocked; south still
        // CLOSES (4 < 5), north merely arcs -- the closing tier wins
        // deterministically, no coin involved in which tier.
        let (mut world, config) = chase_lane(Position::new(8, 7), Some(Position::new(6, 5)));
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 901 }),
            &config,
        );
        assert_eq!(
            world.kitty(1).unwrap().pos,
            Position::new(5, 6),
            "the other axis closes and is preferred over any arc"
        );
    }

    #[test]
    fn a_chase_already_beside_its_kitty_stays_put() {
        // Distance 1: the target's own tile is the "blocked" step and
        // every perpendicular tile is +1 Manhattan, so any sidestep would
        // be a guaranteed retreat -- the orbit the 024 review caught.
        // Pounce range holds still, exactly the pre-024 stall (and no
        // RNG draw: the stream must not remember the near-miss).
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(6, 5);
        let before = serde_json::to_string(&world.rng).unwrap();
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Kitty { id: 2 }),
            &config,
        );
        assert_eq!(
            world.kitty(1).unwrap().pos,
            Position::new(5, 5),
            "an adjacent chaser must hold its pounce, never orbit away"
        );
        assert_eq!(
            serde_json::to_string(&world.rng).unwrap(),
            before,
            "pounce range must not consume a draw"
        );
    }

    #[test]
    fn a_chase_beside_its_bug_under_a_sitting_friend_stays_put() {
        // The element flavor of the same edge: the bug one step away,
        // a friend sitting on it. Stall, not retreat, no draw.
        let (mut world, config) = chase_lane(Position::new(6, 5), Some(Position::new(6, 5)));
        let before = serde_json::to_string(&world.rng).unwrap();
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 901 }),
            &config,
        );
        assert_eq!(world.kitty(1).unwrap().pos, Position::new(5, 5));
        assert_eq!(
            serde_json::to_string(&world.rng).unwrap(),
            before,
            "pounce range must not consume a draw"
        );
    }

    #[test]
    fn a_boxed_in_chase_stalls_exactly_as_before() {
        // Corner cat: east blocked by a friend, south blocked by another,
        // north off-grid, west is the forbidden reverse. Empty pool ->
        // the pre-024 stall, patience clock's territory.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(0, 0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(1, 0);
        // The two-kitty test roster needs one more paw in the way: a
        // fixture-only clone (apply consults positions, nothing deeper).
        let mut third = world.kitties[b].clone();
        third.id = 99;
        third.pos = Position::new(0, 1);
        world.kitties.push(third);
        world.push_element(Element {
            id: 902,
            kind: ElementKind::Bug,
            pos: Position::new(3, 0),
            ttl: None,
        });
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 902 }),
            &config,
        );
        assert_eq!(
            world.kitty(1).unwrap().pos,
            Position::new(0, 0),
            "nowhere lawful to go: the stall survives"
        );
    }

    #[test]
    fn same_seed_same_sidestep() {
        let run = || {
            let (mut world, config) = chase_lane(Position::new(8, 5), Some(Position::new(6, 5)));
            apply(
                &mut world,
                1,
                Action::Chase(TargetRef::Element { id: 901 }),
                &config,
            );
            world.kitty(1).unwrap().pos
        };
        assert_eq!(run(), run(), "Article V: the arc is seeded, not random");
    }

    #[test]
    fn the_sidestep_draws_only_when_blocked() {
        // Stream-shape sanity: an unblocked chase consumes no randomness;
        // a blocked one consumes exactly its one draw. (Config never
        // changes draw shape -- world state may.)
        let (mut world, config) = chase_lane(Position::new(8, 5), None);
        let before = serde_json::to_string(&world.rng).unwrap();
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 901 }),
            &config,
        );
        assert_eq!(
            serde_json::to_string(&world.rng).unwrap(),
            before,
            "an open lane draws nothing"
        );

        let (mut world, config) = chase_lane(Position::new(8, 5), Some(Position::new(6, 5)));
        let before = serde_json::to_string(&world.rng).unwrap();
        apply(
            &mut world,
            1,
            Action::Chase(TargetRef::Element { id: 901 }),
            &config,
        );
        assert_ne!(
            serde_json::to_string(&world.rng).unwrap(),
            before,
            "a blocked lane consumes its one sidestep draw"
        );
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
        // always legal, and relieving. A broken advisor must get the safe no-op
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
    fn element_play_pays_by_what_the_element_is() {
        // Spec 025 US1: the gradient is real -- a bug tick and a greeble
        // tick differ, and both differ from the old uniform play_relief.
        for kind in [
            ElementKind::Bug,
            ElementKind::Greeble {
                heading: Direction::North,
            },
        ] {
            let (mut world, config) = test_world();
            world.elements.clear();
            let idx = world.kitty_index(1).unwrap();
            world.kitties[idx].pos = Position::new(5, 5);
            world.kitties[idx].needs.add(NeedKind::Play, 80.0);
            world.push_element(Element {
                id: 950,
                kind: kind.clone(),
                pos: Position::new(5, 6),
                ttl: Some(50),
            });

            apply(
                &mut world,
                1,
                Action::play_with(TargetRef::Element { id: 950 }),
                &config,
            );

            let relief = match kind.element_type() {
                ElementType::Bug => config.actions.play_relief_bug,
                _ => config.actions.play_relief_greeble,
            };
            let after = world.kitty(1).unwrap().needs.get(NeedKind::Play);
            let expected = 80.0 - relief;
            assert!(
                (after - expected).abs() < 0.01,
                "{kind:?} play must pay its own value, got {after}, wanted {expected}"
            );
        }
    }

    #[test]
    fn duet_play_still_pays_both_partners_the_kitty_value() {
        // Spec 025 FR-001: the duet arm is byte-for-byte pre-split -- each
        // partner gains play_relief (never a critter value), once, and the
        // partner is stamped serviced against a second helping.
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(5, 5);
        world.kitties[a].needs.add(NeedKind::Play, 80.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(5, 6);
        world.kitties[b].needs.add(NeedKind::Play, 80.0);

        apply(
            &mut world,
            1,
            Action::play_with(TargetRef::Kitty { id: 2 }),
            &config,
        );

        for id in [1, 2] {
            let after = world.kitty(id).unwrap().needs.get(NeedKind::Play);
            let expected = 80.0 - config.actions.play_relief;
            assert!(
                (after - expected).abs() < 0.01,
                "kitty {id} gains exactly the kitty value, got {after}"
            );
        }
        let partner_clock = world.kitty(2).unwrap().activity_clock.expect("bound in");
        assert_eq!(
            partner_clock.applied, world.tick,
            "the partner's stamp closes the door on a second helping"
        );
    }

    #[test]
    fn a_vanished_play_target_pays_the_solo_price() {
        // Spec 025 FR-003. The canonical loop ends a vanished-target scene
        // at the kitty's next slot (prune_dead_activity; see
        // world::tests::a_vanished_critter_ends_play_where_it_stands), so
        // this drives apply() directly: the one path that can still see a
        // missing id must stay total and pay the pouncing-at-nothing
        // price -- never a 35/tick tail from an empty tile.
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.kitties[idx].needs.add(NeedKind::Play, 80.0);
        world.push_element(Element {
            id: 951,
            kind: ElementKind::Greeble {
                heading: Direction::North,
            },
            pos: Position::new(5, 6),
            ttl: Some(50),
        });

        apply(
            &mut world,
            1,
            Action::play_with(TargetRef::Element { id: 951 }),
            &config,
        );
        let after_first = world.kitty(1).unwrap().needs.get(NeedKind::Play);
        let expected_first = 80.0 - config.actions.play_relief_greeble;
        assert!(
            (after_first - expected_first).abs() < 0.01,
            "tick one, greeble present: greeble price"
        );

        // The greeble is gone; the continuation is serviced next tick.
        world.elements.retain(|e| e.id != 951);
        world.tick += 1;
        apply(&mut world, 1, Action::Idle, &config);

        let after_second = world.kitty(1).unwrap().needs.get(NeedKind::Play);
        let expected_second = after_first - config.actions.solo_play_relief;
        assert!(
            (after_second - expected_second).abs() < 0.01,
            "tick two, greeble gone: solo price, got {after_second}, wanted {expected_second}"
        );
        assert!(
            matches!(
                world.kitty(1).unwrap().activity,
                Activity::Playing {
                    target: Some(TargetRef::Element { id: 951 })
                }
            ),
            "apply() alone reprices; ending the scene is the slot pipeline's job"
        );
        let clock = world.kitty(1).unwrap().activity_clock.expect("clocked");
        assert_eq!(
            clock.applied, world.tick,
            "the continuation stamped the clock"
        );
    }

    #[test]
    fn a_non_critter_target_defensively_pays_solo() {
        // Unreachable through validate (only adjacent critters pass), but
        // apply stays total: a chow id routed straight in pays solo, never
        // a critter value and never a panic (spec 025 FR-003).
        let (mut world, config) = test_world();
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = Position::new(5, 5);
        world.kitties[idx].needs.add(NeedKind::Play, 80.0);
        world.push_element(Element {
            id: 952,
            kind: ElementKind::Chow { servings: 3 },
            pos: Position::new(5, 6),
            ttl: None,
        });

        apply(
            &mut world,
            1,
            Action::play_with(TargetRef::Element { id: 952 }),
            &config,
        );

        let after = world.kitty(1).unwrap().needs.get(NeedKind::Play);
        let expected = 80.0 - config.actions.solo_play_relief;
        assert!(
            (after - expected).abs() < 0.01,
            "a non-critter target pays the solo price, got {after}"
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

/// The proposal wire's contract suite (spec 016 US1). The module name keeps
/// `cargo test -p cloudkitty-core proposal` as the one-filter gate the
/// quickstart promises.
#[cfg(test)]
mod proposal_contract_tests {
    use super::*;
    use crate::grid::Direction;
    use crate::meow::MessageKind;

    /// Every proposal shape the engine can construct -- the round-trip
    /// corpus. A new `Action` variant that is not added here still fails the
    /// suite: its serialization hits `parse_proposal` as an unknown kind.
    fn every_constructible_shape() -> Vec<Action> {
        let mut shapes = Vec::new();
        for direction in Direction::ALL {
            shapes.push(Action::move_to(direction));
        }
        shapes.push(Action::Rest { with: None });
        shapes.push(Action::Rest { with: Some(2) });
        shapes.push(Action::Sleep { with: None });
        shapes.push(Action::Sleep { with: Some(3) });
        shapes.push(Action::Groom { target: None });
        shapes.push(Action::Groom { target: Some(1) });
        shapes.push(Action::Eat);
        shapes.push(Action::Drink);
        shapes.push(Action::Chase(TargetRef::Element { id: 17 }));
        shapes.push(Action::Chase(TargetRef::Kitty { id: 3 }));
        shapes.push(Action::play_solo());
        shapes.push(Action::play_with(TargetRef::Element { id: 8 }));
        shapes.push(Action::play_with(TargetRef::Kitty { id: 2 }));
        shapes.push(Action::Purr);
        // Every message kind, from the enum's own roster -- an eighth meow
        // joins the corpus the moment it joins MessageKind::ALL (whose own
        // exhaustive-match tests force it in).
        for message in MessageKind::ALL {
            shapes.push(Action::Meow { message });
        }
        shapes.push(Action::Idle);
        shapes
    }

    #[test]
    fn every_shape_the_engine_serializes_round_trips_unchanged() {
        let shapes = every_constructible_shape();
        // 15 fixed shapes (rest/sleep/groom x2, eat, drink, chase x2,
        // play x3, purr, idle) plus one per direction and one per meow.
        let expected = 15 + Direction::ALL.len() + MessageKind::ALL.len();
        assert_eq!(shapes.len(), expected, "the corpus covers every wire shape");
        for action in shapes {
            let wire = serde_json::to_string(&action).expect("actions serialize");
            let parsed =
                parse_proposal(&wire).unwrap_or_else(|e| panic!("{wire} must parse strictly: {e}"));
            assert_eq!(parsed, action, "round-trip identity for {wire}");
        }
    }

    /// The rejection matrix (FR-002): every malformed-variant class, per
    /// shape where it applies. The `rejected` examples from
    /// contracts/wire-protocol.md appear verbatim.
    #[test]
    fn malformed_proposals_are_rejected_never_reshaped() {
        let rejected = [
            // -- the contract's own rejected examples, verbatim ------------
            r#"{"action": "levitate"}"#,
            r#"{"action": "move"}"#,
            r#"{"action": "move", "direction": "up"}"#,
            r#"{"action": "move", "direction": "north", "speed": 9}"#,
            r#"{"action": "chase", "target": "element"}"#,
            r#"{"action": "play", "id": 2}"#,
            r#"{"action": "groom", "target": "Miso"}"#,
            r#"{"action": "rest", "with": -1}"#,
            r#""idle""#,
            // -- unknown or missing kind -----------------------------------
            r#"{"direction": "north"}"#,
            r#"{"action": 7}"#,
            r#"{"action": null}"#,
            // -- missing required fields -----------------------------------
            r#"{"action": "meow"}"#,
            r#"{"action": "chase", "id": 4}"#,
            // -- wrong types ------------------------------------------------
            r#"{"action": "move", "direction": 5}"#,
            r#"{"action": "sleep", "with": "Biscuit"}"#,
            r#"{"action": "chase", "target": "kitty", "id": -3}"#,
            r#"{"action": "chase", "target": "kitty", "id": 1.5}"#,
            // -- unrecognized closed-set values ----------------------------
            r#"{"action": "meow", "message": "want_snacks"}"#,
            r#"{"action": "chase", "target": "bogus", "id": 1}"#,
            r#"{"action": "play", "target": "sunbeam", "id": 1}"#,
            // -- incomplete play target ------------------------------------
            r#"{"action": "play", "target": "kitty"}"#,
            // -- unknown extra fields, one per shape ------------------------
            r#"{"action": "rest", "with": 2, "snuggle": true}"#,
            r#"{"action": "sleep", "where": "sunbeam"}"#,
            r#"{"action": "groom", "target": 1, "vigor": 11}"#,
            r#"{"action": "eat", "snack": "chow"}"#,
            r#"{"action": "drink", "amount": 2}"#,
            r#"{"action": "chase", "target": "kitty", "id": 1, "speed": 9}"#,
            r#"{"action": "play", "target": "kitty", "id": 2, "style": "pounce"}"#,
            r#"{"action": "purr", "volume": 11}"#,
            r#"{"action": "meow", "message": "want_play", "volume": 11}"#,
            r#"{"action": "idle", "why": "sleepy"}"#,
            // -- not an object / not JSON ----------------------------------
            r#"[{"action": "idle"}]"#,
            r#"42"#,
            r#"meow meow"#,
            r#""#,
        ];
        for wire in rejected {
            assert!(
                parse_proposal(wire).is_err(),
                "{wire:?} must be rejected, not reshaped into a legal action"
            );
        }
    }

    #[test]
    fn rejection_kinds_name_the_problem_for_the_operator() {
        assert!(matches!(
            parse_proposal(r#"{"action": "levitate"}"#),
            Err(ProposalError::UnknownKind(k)) if k == "levitate"
        ));
        assert!(matches!(
            parse_proposal(r#"{"direction": "north"}"#),
            Err(ProposalError::MissingKind)
        ));
        assert!(matches!(
            parse_proposal(r#""idle""#),
            Err(ProposalError::NotAnObject)
        ));
        assert!(matches!(
            parse_proposal("meow meow"),
            Err(ProposalError::NotJson(_))
        ));
        // The mirror's serde error names the offending extra field.
        let err = parse_proposal(r#"{"action": "move", "direction": "north", "speed": 9}"#)
            .expect_err("extra fields reject");
        assert!(
            err.to_string().contains("unknown field `speed`"),
            "the operator sees which field was wrong: {err}"
        );
    }

    #[test]
    fn a_stale_purr_proposal_parses_and_is_left_to_validation() {
        // Purr retired as an action in spec 011: recognizing the shape and
        // idling it at validation keeps a confused advisor from being
        // punished as a parse error.
        assert_eq!(
            parse_proposal(r#"{"action": "purr"}"#).unwrap(),
            Action::Purr
        );
    }

    #[test]
    fn duplicate_keys_collapse_to_the_last_occurrence_before_strict_checks() {
        // Standard JSON semantics, documented in the wire contract: the
        // JSON parser resolves duplicates (last wins) before the strict
        // checks ever see the object.
        assert_eq!(
            parse_proposal(r#"{"action": "move", "direction": "north", "direction": "south"}"#)
                .unwrap(),
            Action::move_to(Direction::South)
        );
    }
}
