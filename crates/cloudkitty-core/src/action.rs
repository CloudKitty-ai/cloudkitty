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
/// Bump on any breaking change to the accepted proposal shapes. Version 2
/// (spec 033): `follow_me` stopped parsing as a message kind (renamed
/// `mew` -- no alias, a lying name is what the rename removed) and seven
/// kinds joined the accepted set (here_food, here_water, here_critter,
/// here_sunbeam, chirp, trill, ekekek). Version 3 (spec 049 FR-048, owner
/// ruled 2026-09-03): `world` is the deciding cat's FOG VIEW -- the same
/// shape, fogged contents (kitties and elements inside its disc, every
/// recent meow) -- and the wire grew fields: `memory` and `explore_heading`
/// on kitties (blanked on friends), `pos` and `reply` on meows. A v2
/// plugin assuming full sight could not tell it sees a partial world, so
/// the version says so; refusing it falls back per Article IV.
pub const PROPOSAL_WIRE_VERSION: u32 = 3;

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
        #[serde(deserialize_with = "wire_message_kind")]
        pub message: MessageKind,
    }

    /// The wire's own vocabulary: exactly the `wire_name()` spellings,
    /// never serde's — the snapshot-facing `follow_me` alias on `Mew`
    /// (033 review Finding 3) is a persistence affordance, and wire v2
    /// dropped `follow_me` deliberately (spec 033 D4, no alias). Routing
    /// the wire through `wire_name()` keeps that ruling standing no matter
    /// what aliases persistence grows.
    fn wire_message_kind<'de, D>(deserializer: D) -> Result<MessageKind, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let spelling = String::deserialize(deserializer)?;
        MessageKind::ALL
            .into_iter()
            .find(|kind| kind.wire_name() == spelling)
            .ok_or_else(|| serde::de::Error::custom(format!("unknown message kind `{spelling}`")))
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
    // The signature keeps its config parameter (the stable validate shape
    // every probe and caller shares) though no current arm reads it: the
    // purr threshold moved to message_legal with the deliberate purr.
    let _ = config;
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

        // Resting and sleeping beside a friend bind nobody (spec 041 made
        // rest co-sleep's sibling), so both keep the plain availability
        // rule: any adjacent friend, whatever it is doing. This deletes
        // rest's share of the partnered-refusal tax structurally.
        Action::Rest { with } => match with {
            None => true,
            Some(friend_id) => world.is_available_friend(kitty_id, friend_id),
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
            // A companion, never a conscript (spec 041): mirror the sleep
            // arm exactly. The partner keeps its own activity and clock.
            let partner = with.filter(|f| world.is_available_friend(kitty_id, *f));
            begin_activity(
                world,
                kitty_id,
                Activity::Resting {
                    with_friend: partner,
                },
            );
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
                // The final pounce (spec 039 FR-011, the owner's
                // pre-authorized fallback): whatever the chase movement above
                // resolved to, if it left an ELEMENT target at Manhattan
                // distance exactly 2, the cat lunges one more plain step
                // toward it. A lunge, not a route: blocked or off-grid is a
                // lost step, no sidestep tiers, no RNG draw — so the
                // flag-off stream is untouched and the flag-on stream adds
                // no draws (FR-012). Kitty targets never pounce (the
                // elements-only ruling).
                if config.behavior.pounce && matches!(target, TargetRef::Element { .. }) {
                    if let Some(idx) = world.kitty_index(kitty_id) {
                        let pos = world.kitties[idx].pos;
                        if pos.manhattan_distance(&target_pos) == 2 {
                            if let Some(dir) = Direction::toward(pos, target_pos) {
                                if let Some(dest) = pos.step(dir, world.width, world.height) {
                                    if world.kitty_at(dest).is_none() {
                                        world.kitties[idx].pos = dest;
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
                lower_need(
                    world,
                    kitty_id,
                    NeedKind::Cuddle,
                    effects.groom_cuddle_relief,
                );
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
            // Re-check the companion every serviced tick, exactly as the
            // sleeping arm below does: a wandered-off partner drops the
            // scene to solo posture, clock untouched (spec 041 FR-001).
            let partner = with_friend.filter(|f| world.is_available_friend(kitty_id, *f));
            if let Some(idx) = world.kitty_index(kitty_id) {
                world.kitties[idx].activity = Activity::Resting {
                    with_friend: partner,
                };
            }
            if let Some(friend) = partner {
                // The tier is resolved fresh from the partner's live state
                // by the shared mutual predicate (FR-002): mutual when the
                // partner is itself settled, the drip otherwise. Both
                // parties receive the tier rate, each scene from its own
                // slot -- no binding, no partner-side stamp.
                let mutual = world.is_settled(friend);
                let rate = if mutual {
                    effects.rest_mutual_relief
                } else {
                    effects.rest_drip_relief
                };
                lower_need(world, kitty_id, NeedKind::Cuddle, rate);
                lower_need(world, friend, NeedKind::Cuddle, rate);
                count_tier_tick(world, kitty_id, mutual);
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
    // The FR-014/15 mutual predicate -- `World::is_settled`, the one shared
    // definition (spec 041 FR-002). Evaluated ONCE, above both uses: it
    // prices the cuddle tier below and gates warmth conduction in the sleep
    // rate (spec 031), so the two can never disagree about whether the pile
    // is mutual.
    let mutual = partner.is_some_and(|friend| world.is_settled(friend));
    // Warmth conducts through the pile (spec 031): a mutual partner on a
    // sunbeam tile gives the sleeper sunbeam-grade sleep. Direct partner
    // only, and the rate is selected, never stacked -- any combination of
    // beams pays exactly sleep_relief_sunbeam. A failed lookup is simply
    // no warmth (the plain rate), never an error.
    let partner_warm = mutual
        && partner
            .and_then(|friend| world.kitty(friend))
            .is_some_and(|k| {
                world.element_at(k.pos).map(|e| e.element_type()) == Some(ElementType::Sunbeam)
            });
    let relief = if in_sunbeam || partner_warm {
        config.actions.sleep_relief_sunbeam
    } else {
        config.actions.sleep_relief
    };
    lower_need(world, kitty_id, NeedKind::Sleep, relief);
    if let Some(friend) = partner {
        // Cosleep priced by presence (spec 028 FR-014/FR-015): the mutual
        // tier when the partner is itself sleeping or resting, the passive
        // drip otherwise. Both parties receive the tier rate; the sleeper's
        // Sleep relief above is untouched. The rest duet and the groomer
        // have their own dials since spec 041 (rest_mutual_relief,
        // groom_cuddle_relief) -- moving the cosleep pair never touches them.
        let rate = if mutual {
            config.actions.cosleep_mutual_relief
        } else {
            config.actions.cosleep_drip_relief
        };
        lower_need(world, kitty_id, NeedKind::Cuddle, rate);
        lower_need(world, friend, NeedKind::Cuddle, rate);
        count_tier_tick(world, kitty_id, mutual);
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
    // Spec 049 FR-040: the speaker's position at emission, stamped once.
    let pos = kitty.pos;
    // The stamped intensity (spec 028): the grounding need's value at
    // emission, on [0, 1] -- a listener hears how hungry, not just that.
    // Every non-want kind carries 0.0 (spec 033 clarify verdict: intensity
    // means need pressure, exclusively -- a Here* richness stamp would rot
    // anti-conservatively, overstating as servings fall).
    let intensity = message
        .related_need()
        .map(|need| (kitty.needs.get(need) / 100.0).clamp(0.0, 1.0))
        .unwrap_or(0.0);
    // One uniform stamp: the audibility window doubles as the per-kind
    // cooldown -- one live digest entry per kind per emitter, never sooner.
    if let Some(idx) = world.kitty_index(kitty_id) {
        world.kitties[idx].set_meow_cooldown(message, tick + config.meow.recent_window_ticks);
    }
    // The reply bit lands with the here tier (spec 049 FR-040): false
    // until the law over the fog view exists.
    world.recent_meows.push(Meow {
        kitty_id,
        kind: message,
        tick,
        intensity,
        pos,
        reply: false,
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

/// One serviced partnered tick of a tiered scene (rest or co-sleep):
/// bumps the scene owner's mutual or drip counter (spec 041 FR-011),
/// exactly one per tick, chosen by the shared predicate's verdict. Solo
/// ticks call nothing, so the counters' shortfall against the span counts
/// them honestly.
fn count_tier_tick(world: &mut World, kitty_id: KittyId, mutual: bool) {
    if let Some(idx) = world.kitty_index(kitty_id) {
        if let Some(clock) = &mut world.kitties[idx].activity_clock {
            if mutual {
                clock.mutual_ticks += 1;
            } else {
                clock.drip_ticks += 1;
            }
        }
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
            crate::meow::message_legal(
                world.kitty(1).unwrap(),
                MessageKind::Purr,
                50,
                &config,
                &world.elements
            ),
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
            &config,
            &world.elements
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
            crate::meow::message_legal(
                world.kitty(1).unwrap(),
                MessageKind::Purr,
                50,
                &config,
                &world.elements
            ),
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
    fn warmth_conducts_from_a_mutual_partner_on_a_beam() {
        // Spec 031 US1 scenarios 1-3: the sleeper is off-beam; its mutual
        // partner (sleeping, and separately resting -- the FR-014/15
        // definition) stands on a sunbeam tile; the sleeper sleeps at
        // sunbeam grade. The beam-resting partner itself receives NO sleep
        // relief -- only sleep provides sleep relief.
        for partner_activity in [
            Activity::Sleeping {
                in_sunbeam: true,
                with_friend: Some(1),
            },
            Activity::Resting {
                with_friend: Some(1),
            },
        ] {
            let (mut world, config) = test_world();
            world.elements.clear();
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].pos = Position::new(4, 4);
            world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
            let b = world.kitty_index(2).unwrap();
            world.kitties[b].pos = Position::new(4, 5);
            world.kitties[b].activity = partner_activity;
            world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
            world.kitties[b].needs.add(NeedKind::Sleep, 90.0);
            world.push_element(Element {
                id: 903,
                kind: ElementKind::Sunbeam,
                pos: Position::new(4, 5),
                ttl: Some(50),
            });

            apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

            let got = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
            assert!(
                (got - config.actions.sleep_relief_sunbeam).abs() < 0.01,
                "{partner_activity:?}: conducted warmth pays the sunbeam rate, got {got}"
            );
            // The awake (resting) partner gets no sleep relief from the
            // pile -- neither from A's serviced tick nor from its OWN:
            // service B's resting tick too and hold the assertion.
            if matches!(partner_activity, Activity::Resting { .. }) {
                apply_activity_effects(&mut world, 2, &config);
                let b_sleep = world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
                assert!(
                    (b_sleep - 90.0).abs() < 0.01,
                    "a resting cat receives no sleep relief, got {b_sleep}"
                );
            }
        }
    }

    #[test]
    fn either_on_beam_warms_both_sleeping_partners() {
        // Spec 031 US1 scenario 2: the beam is under ONE partner; both
        // sleeping partners sleep at the sunbeam rate -- the beam-holder by
        // the own-tile rule, the other by conduction.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Sleep, 90.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(4, 4),
            ttl: Some(50),
        });

        // A (on the beam) starts the cosleep; B is then put to sleep naming
        // A and serviced -- each side's relief is its own serviced tick.
        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        let a_got = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (a_got - config.actions.sleep_relief_sunbeam).abs() < 0.01,
            "the beam-holder keeps the own-tile rule, got {a_got}"
        );

        apply(&mut world, 2, Action::Sleep { with: Some(1) }, &config);
        let b_got = 90.0 - world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (b_got - config.actions.sleep_relief_sunbeam).abs() < 0.01,
            "the off-beam partner is warmed by conduction, got {b_got}"
        );
    }

    #[test]
    fn conducted_warmth_ends_when_the_beam_does() {
        // Spec 031 US1 scenario 4 / FR-006: conduction re-evaluates every
        // serviced tick; the beam expiring drops the rate back to plain on
        // the next service, exactly like the own-tile rule.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].activity = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(1),
        };
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        world.kitties[b].needs.add(NeedKind::Sleep, 90.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(4, 5),
            ttl: Some(50),
        });

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        let warm = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (warm - config.actions.sleep_relief_sunbeam).abs() < 0.01,
            "while the beam lives, conduction pays sunbeam grade, got {warm}"
        );

        // The beam expires; the next serviced tick is back to plain for
        // BOTH partners -- the conducted sleeper and the (stale-flagged)
        // former beam-holder alike.
        world.elements.clear();
        let a_before = world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        let b_before = world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
        apply_activity_effects(&mut world, 1, &config);
        apply_activity_effects(&mut world, 2, &config);
        let a_cooled = a_before - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        let b_cooled = b_before - world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (a_cooled - config.actions.sleep_relief).abs() < 0.01,
            "no beam, no warmth: the conducted sleeper is back to plain, got {a_cooled}"
        );
        assert!(
            (b_cooled - config.actions.sleep_relief).abs() < 0.01,
            "the former beam-holder cools too, stale flag and all, got {b_cooled}"
        );
    }

    #[test]
    fn warmth_never_chains_past_the_direct_partner() {
        // Spec 031 US2 scenario 1 / FR-002: A sleeps with B (off-beam,
        // mutual); C stands on a beam cosleeping with B. The beam is two
        // hops from A -- A gets the plain rate.
        let mut config = crate::test_support::test_config();
        config.kitties.push(crate::config::KittyConfig {
            id: 3,
            name: "Pumpkin".into(),
            x: 4,
            y: 6,
            behavior: "needs_driven".into(),
            needs: None,
        });
        let mut world = World::generate(&config);
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].activity = Activity::Sleeping {
            in_sunbeam: false,
            with_friend: Some(3),
        };
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        let c = world.kitty_index(3).unwrap();
        world.kitties[c].pos = Position::new(4, 6);
        world.kitties[c].activity = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(2),
        };
        world.kitties[c].activity_clock = Some(ActivityClock::start(world.tick));
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(4, 6),
            ttl: Some(50),
        });

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

        let got = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (got - config.actions.sleep_relief).abs() < 0.01,
            "a beam under the partner's partner conducts nothing, got {got}"
        );
    }

    #[test]
    fn two_beams_pay_exactly_one_sunbeam_rate() {
        // Spec 031 US2 scenario 2 / FR-003: both partners on beams -- the
        // rate is selected, not summed.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].activity = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(1),
        };
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        for (id, pos) in [(903, Position::new(4, 4)), (904, Position::new(4, 5))] {
            world.push_element(Element {
                id,
                kind: ElementKind::Sunbeam,
                pos,
                ttl: Some(50),
            });
        }

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

        let got = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (got - config.actions.sleep_relief_sunbeam).abs() < 0.01,
            "two beams still pay exactly the one sunbeam rate, got {got}"
        );
    }

    #[test]
    fn a_drip_tier_partner_on_a_beam_conducts_nothing() {
        // Spec 031 US2 scenario 3: the partner stands on a beam but is
        // neither sleeping nor resting (the drip tier) -- the conduction
        // source condition is exactly the FR-014/15 mutual definition, so
        // no warmth flows and the cuddle tier stays the drip.
        let (mut world, mut config) = test_world();
        config.actions.cosleep_drip_relief = 3.0;
        config.actions.cosleep_mutual_relief = 11.0;
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].activity = Activity::Idle;
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(4, 5),
            ttl: Some(50),
        });

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

        let got = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (got - config.actions.sleep_relief).abs() < 0.01,
            "an awake bystander on a beam is not a pile, got {got}"
        );
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 47.0).abs() < 0.01,
            "the cuddle tier stays the drip -- one mutual evaluation feeds both, got {a_cuddle}"
        );
    }

    #[test]
    fn solo_rates_and_the_conduction_piles_cuddle_are_untouched() {
        // Spec 031 US2 scenarios 4-5 / FR-007: solo sleep pays exactly
        // today's rates on and off beams, and a conduction pile's Cuddle
        // relief is exactly the mutual tier it was before this feature.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 90.0);
        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        let plain = 90.0 - world.kitty(1).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (plain - config.actions.sleep_relief).abs() < 0.01,
            "solo off-beam is exactly sleep_relief, got {plain}"
        );

        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(2, 2);
        world.kitties[b].needs.add(NeedKind::Sleep, 90.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(2, 2),
            ttl: Some(50),
        });
        apply(&mut world, 2, Action::Sleep { with: None }, &config);
        let sunny = 90.0 - world.kitty(2).unwrap().needs.get(NeedKind::Sleep);
        assert!(
            (sunny - config.actions.sleep_relief_sunbeam).abs() < 0.01,
            "solo on-beam is exactly sleep_relief_sunbeam, got {sunny}"
        );

        // A conduction pile pays the same mutual cuddle tier as before.
        let (mut world, config) = test_world();
        world.elements.clear();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].activity = Activity::Sleeping {
            in_sunbeam: true,
            with_friend: Some(1),
        };
        world.kitties[b].activity_clock = Some(ActivityClock::start(world.tick));
        world.kitties[b].needs.add(NeedKind::Cuddle, 50.0);
        world.push_element(Element {
            id: 903,
            kind: ElementKind::Sunbeam,
            pos: Position::new(4, 5),
            ttl: Some(50),
        });
        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        let b_cuddle = world.kitty(2).unwrap().needs.get(NeedKind::Cuddle);
        let expected = 50.0 - config.actions.cosleep_mutual_relief;
        assert!(
            (a_cuddle - expected).abs() < 0.01 && (b_cuddle - expected).abs() < 0.01,
            "conduction never touches the cuddle tier: {a_cuddle} / {b_cuddle}"
        );
    }

    #[test]
    fn every_emission_stamps_and_is_heard() {
        // Spec 028 emission shape: apply_message emits (recent_meows push,
        // audible to everyone) and stamps the per-kind cooldown in the same
        // breath. Legality is the caller's ruling (message_legal) -- this
        // path itself never swallows.
        let (mut world, config) = test_world();
        let tick = world.tick;
        apply_message(&mut world, 1, MessageKind::Mew, &config, tick);
        assert_eq!(world.recent_meows.len(), 1);
        let first_stamp = world.kitty(1).unwrap().meow_cooldowns[&MessageKind::Mew];
        assert_eq!(first_stamp, tick + config.meow.recent_window_ticks);

        world.tick += 1;
        let tick = world.tick;
        apply_message(&mut world, 1, MessageKind::Mew, &config, tick);
        assert_eq!(world.recent_meows.len(), 2, "the emit path never swallows");
        let second_stamp = world.kitty(1).unwrap().meow_cooldowns[&MessageKind::Mew];
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

        apply_message(&mut world, 1, MessageKind::Mew, &config, tick);
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
    fn a_cuddle_names_a_companion_and_owns_its_clock() {
        // Repointed at spec 041 (the old guard asserted the bound duet:
        // partner conscripted, one shared clock). Rest is co-sleep's
        // sibling now: the rester names its companion and owns the only
        // clock in the scene.
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(3, 3);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(3, 4);

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);

        assert_eq!(world.kitty(1).unwrap().activity.partner(), Some(2));
        assert_eq!(
            world.kitty(2).unwrap().activity.partner(),
            None,
            "the companion is never bound into the scene"
        );
        assert!(
            world.kitty(1).unwrap().activity_clock.is_some(),
            "the rester owns a clock"
        );
        assert!(
            world.kitty(2).unwrap().activity_clock.is_none(),
            "the companion has none"
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
    use crate::element::{Element, ElementKind};
    use crate::grid::{Direction, Position};
    use crate::kitty::Activity;
    use crate::meow::MessageKind;
    use crate::needs::NeedKind;
    use crate::test_support::test_world;

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

    #[test]
    fn cosleep_pays_the_tier_the_partners_presence_earns() {
        // Spec 028 US5: a mutually-sleeping partner earns the mutual rate,
        // a merely-present one the drip -- both parties, both tiers, the
        // sleeper's own Sleep relief untouched either way.
        for (partner_activity, expected_dial) in [
            (
                Activity::Sleeping {
                    in_sunbeam: false,
                    with_friend: None,
                },
                "mutual",
            ),
            (Activity::Idle, "drip"),
        ] {
            let (mut world, mut config) = test_world();
            // Distinct rates so the tier choice is visible in the arithmetic.
            config.actions.cosleep_drip_relief = 3.0;
            config.actions.cosleep_mutual_relief = 11.0;
            let a = world.kitty_index(1).unwrap();
            world.kitties[a].pos = Position::new(4, 4);
            world.kitties[a].needs.add(NeedKind::Sleep, 80.0);
            world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
            let b = world.kitty_index(2).unwrap();
            world.kitties[b].pos = Position::new(4, 5);
            world.kitties[b].activity = partner_activity;
            if partner_activity.is_in_progress() {
                world.kitties[b].activity_clock =
                    Some(crate::kitty::ActivityClock::start(world.tick));
            }
            world.kitties[b].needs.add(NeedKind::Cuddle, 50.0);

            apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

            let expected = if expected_dial == "mutual" { 11.0 } else { 3.0 };
            let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
            let b_cuddle = world.kitty(2).unwrap().needs.get(NeedKind::Cuddle);
            assert!(
                (a_cuddle - (50.0 - expected)).abs() < 0.01,
                "{expected_dial}: sleeper got {a_cuddle}"
            );
            assert!(
                (b_cuddle - (50.0 - expected)).abs() < 0.01,
                "{expected_dial}: partner got {b_cuddle}"
            );
        }
    }

    #[test]
    fn cosleep_defaults_are_behavior_preserving() {
        // With all three dials equal at 15.0 (the shipped defaults), one
        // serviced cosleep tick moves cuddle exactly as the classic
        // cuddle_relief arithmetic did -- asserted numerically in this one
        // build, the honest form of "byte-identical to yesterday".
        let (mut world, config) = test_world();
        assert_eq!(config.actions.cosleep_drip_relief, 15.0);
        assert_eq!(config.actions.cosleep_mutual_relief, 15.0);
        assert_eq!(config.actions.rest_mutual_relief, 15.0);
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Sleep, 80.0);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);

        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);

        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 35.0).abs() < 0.01,
            "defaults reproduce yesterday's arithmetic exactly"
        );
    }

    #[test]
    fn cosleep_dials_never_touch_the_duet_or_the_groomer() {
        // Severing the three-flow coupling (FR-016): move both cosleep
        // dials to extremes and the rest duet and groom payments hold at
        // the classic cuddle_relief.
        let (mut world, mut config) = test_world();
        config.actions.cosleep_drip_relief = 0.0;
        config.actions.cosleep_mutual_relief = 99.0;
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Bath, 60.0);

        // The groomer's warmth: classic cuddle_relief (15), not a cosleep tier.
        apply(&mut world, 1, Action::Groom { target: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 35.0).abs() < 0.01,
            "the groomer is paid by cuddle_relief, got {a_cuddle}"
        );

        // The mutual rest scene: same isolation (a settled partner earns
        // the rest mutual tier, spec 041 -- not a cosleep tier).
        let (mut world, mut config) = test_world();
        config.actions.cosleep_drip_relief = 0.0;
        config.actions.cosleep_mutual_relief = 99.0;
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Cuddle, 50.0);
        world.kitties[b].activity = Activity::Resting { with_friend: None };
        world.kitties[b].activity_clock = Some(crate::kitty::ActivityClock::start(world.tick));
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 35.0).abs() < 0.01,
            "the scene is paid by rest_mutual_relief, got {a_cuddle}"
        );
    }

    /// Two kitties adjacent, one carrying 50 cuddle need each, nothing else
    /// nearby -- the spec-041 pricing stage.
    fn cuddle_pricing_stage() -> (crate::world::World, Config) {
        let (mut world, config) = test_world();
        let a = world.kitty_index(1).unwrap();
        world.kitties[a].pos = Position::new(4, 4);
        world.kitties[a].needs.add(NeedKind::Cuddle, 50.0);
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(4, 5);
        world.kitties[b].needs.add(NeedKind::Cuddle, 50.0);
        (world, config)
    }

    #[test]
    fn each_split_dial_moves_only_its_own_site() {
        // Spec 041 US3 AC-3: the two call sites are provably independent --
        // move one split dial alone and only its own site's payment moves.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_mutual_relief = 4.0;
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].needs.add(NeedKind::Bath, 60.0);
        settle(&mut world, 2);
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 46.0).abs() < 0.01,
            "the duet follows its own dial, got {a_cuddle}"
        );

        // The groomer is untouched by the rest dial's move...
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_mutual_relief = 4.0;
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].needs.add(NeedKind::Bath, 60.0);
        apply(&mut world, 1, Action::Groom { target: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 35.0).abs() < 0.01,
            "the groomer ignores rest_mutual_relief, got {a_cuddle}"
        );

        // ...and the duet is untouched by the groomer's.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.groom_cuddle_relief = 4.0;
        settle(&mut world, 2);
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 35.0).abs() < 0.01,
            "the duet ignores groom_cuddle_relief, got {a_cuddle}"
        );
    }

    /// Settles a kitty into solo rest: a mutual-tier partner in the
    /// spec-041 sense (the shared predicate reads Sleeping | Resting).
    fn settle(world: &mut crate::world::World, id: KittyId) {
        let idx = world.kitty_index(id).unwrap();
        world.kitties[idx].activity = Activity::Resting { with_friend: None };
        world.kitties[idx].activity_clock = Some(crate::kitty::ActivityClock::start(world.tick));
    }

    /// Puts kitty 2 mid-meal: a busy partner in the spec-041 sense.
    fn make_busy_eating(world: &mut crate::world::World) {
        world.push_element(Element {
            id: 901,
            kind: ElementKind::Chow { servings: 5 },
            pos: Position::new(3, 5),
            ttl: None,
        });
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].activity = Activity::Eating;
        world.kitties[b].activity_clock = Some(crate::kitty::ActivityClock::start(world.tick));
    }

    #[test]
    fn rest_beside_a_busy_friend_is_legal_and_conscripts_nobody() {
        // Spec 041 US1 AC-1: availability legality (FR-001). A cat mid-meal
        // is restable-beside; it is never bound, stamped, or clock-touched.
        let (mut world, config) = cuddle_pricing_stage();
        make_busy_eating(&mut world);
        let before_clock = world.kitty(2).unwrap().activity_clock;

        let validated = validate(&world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(
            validated,
            Action::Rest { with: Some(2) },
            "rest beside a busy adjacent friend is legal"
        );

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Resting {
                with_friend: Some(2)
            },
            "the rester keeps its named companion"
        );
        assert_eq!(
            world.kitty(2).unwrap().activity,
            Activity::Eating,
            "the partner keeps its own activity"
        );
        assert_eq!(
            world.kitty(2).unwrap().activity_clock,
            before_clock,
            "the partner's clock is untouched -- no binding, no stamp"
        );
    }

    #[test]
    fn rest_toward_a_non_adjacent_kitty_resolves_to_idle() {
        // The kept half of the legality rule: adjacency still gates.
        let (mut world, config) = cuddle_pricing_stage();
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);
        let validated = validate(&world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(validated, Action::Idle, "distance still makes it illegal");
    }

    #[test]
    fn resting_beside_an_idle_friend_binds_nobody() {
        // Spec 041 FR-001: even a free partner is a companion, never a
        // conscript -- exactly Sleep{with}'s shape.
        let (mut world, config) = cuddle_pricing_stage();
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Resting {
                with_friend: Some(2)
            }
        );
        assert_eq!(
            world.kitty(2).unwrap().activity,
            Activity::Idle,
            "the idle partner stays idle"
        );
        assert!(
            world.kitty(2).unwrap().activity_clock.is_none(),
            "the partner gets no clock"
        );
    }

    #[test]
    fn rest_pays_the_tier_the_partners_state_earns() {
        // Spec 041 FR-002 via the shared predicate: drip for a merely-
        // present partner, mutual for a settled one -- both parties either
        // way, resolved from the partner's live state.
        for (settled, expected) in [(false, 2.0f32), (true, 11.0f32)] {
            let (mut world, mut config) = cuddle_pricing_stage();
            config.actions.rest_drip_relief = 2.0;
            config.actions.rest_mutual_relief = 11.0;
            if settled {
                let b = world.kitty_index(2).unwrap();
                world.kitties[b].activity = Activity::Sleeping {
                    in_sunbeam: false,
                    with_friend: None,
                };
                world.kitties[b].activity_clock =
                    Some(crate::kitty::ActivityClock::start(world.tick));
            } else {
                make_busy_eating(&mut world);
            }

            apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);

            let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
            let b_cuddle = world.kitty(2).unwrap().needs.get(NeedKind::Cuddle);
            assert!(
                (a_cuddle - (50.0 - expected)).abs() < 0.01,
                "settled={settled}: the rester got {a_cuddle}"
            );
            assert!(
                (b_cuddle - (50.0 - expected)).abs() < 0.01,
                "settled={settled}: the partner got {b_cuddle}"
            );
        }
    }

    #[test]
    fn a_mid_scene_settle_flips_the_tier_that_tick() {
        // Spec 041 US1 AC-2 + the flap edge case: the tier is resolved
        // fresh every serviced tick, no hysteresis, no memory.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_drip_relief = 2.0;
        config.actions.rest_mutual_relief = 11.0;
        make_busy_eating(&mut world);

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let after_drip = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (after_drip - 48.0).abs() < 0.01,
            "tick 1 pays the drip, got {after_drip}"
        );

        // The partner settles; the very next serviced tick pays mutual.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].activity = Activity::Resting { with_friend: None };
        world.tick += 1;
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let after_mutual = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (after_mutual - (48.0 - 11.0)).abs() < 0.01,
            "the settle flips drip -> mutual on that tick, got {after_mutual}"
        );
    }

    #[test]
    fn a_rester_beside_a_sleeping_friend_collects_mutual_from_its_own_slot() {
        // Spec 041 US1 AC-3: self-service symmetry -- the sleeper never
        // named the rester, and the rester still collects the mutual rate
        // from its own slot.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_mutual_relief = 11.0;
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].activity = Activity::Sleeping {
            in_sunbeam: false,
            with_friend: None,
        };
        world.kitties[b].activity_clock = Some(crate::kitty::ActivityClock::start(world.tick));

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 39.0).abs() < 0.01,
            "mutual from the rester's own slot, got {a_cuddle}"
        );
    }

    #[test]
    fn a_wandered_rest_partner_drops_the_scene_to_solo_posture() {
        // Spec 041 US1 AC-4: the per-tick re-filter mirrors co-sleep's
        // companion re-check -- solo posture, no relief, clock not reset.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_drip_relief = 2.0;
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        let started = world.kitty(1).unwrap().activity_clock.unwrap().started;

        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);
        world.tick += 1;
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);

        let k1 = world.kitty(1).unwrap();
        assert_eq!(
            k1.activity,
            Activity::Resting { with_friend: None },
            "the scene survives as solo posture"
        );
        assert_eq!(
            k1.activity_clock.unwrap().started,
            started,
            "the duration clock is not reset"
        );
        let a_cuddle = k1.needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 48.0).abs() < 0.01,
            "the solo tick pays nothing, got {a_cuddle}"
        );
    }

    #[test]
    fn a_reciprocal_cosleep_pair_is_paid_from_both_slots() {
        // Spec 041 US2/AC3, the per-scene (not per-pair) shape: both
        // naming each other, both slots serviced in one tick, each cat
        // receives the mutual rate TWICE. This is the engine's existing
        // payment shape, priced into the model; a well-meaning "dedup"
        // that stamps or skips the second slot is the regression this
        // guard exists to catch. Instruments count scenes, not relief
        // events.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.cosleep_mutual_relief = 11.0;
        for (me, friend) in [(1, 2), (2, 1)] {
            let idx = world.kitty_index(me).unwrap();
            world.kitties[idx].activity = Activity::Sleeping {
                in_sunbeam: false,
                with_friend: Some(friend),
            };
            world.kitties[idx].activity_clock =
                Some(crate::kitty::ActivityClock::start(world.tick));
        }
        world.tick += 1;
        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        apply(&mut world, 2, Action::Sleep { with: Some(1) }, &config);
        for id in [1, 2] {
            let got = world.kitty(id).unwrap().needs.get(NeedKind::Cuddle);
            assert!(
                (got - (50.0 - 2.0 * 11.0)).abs() < 0.01,
                "kitty {id} collects the mutual rate from both slots, got {got}"
            );
        }
    }

    #[test]
    fn tier_counters_accumulate_per_tier_and_sum_below_the_span() {
        // Spec 041 FR-011: one counter bump per serviced partnered tick,
        // mutual xor drip by the shared predicate; a solo (wandered-
        // partner) tick bumps neither, so the sum's shortfall against the
        // span counts exactly the solo ticks.
        let (mut world, mut config) = cuddle_pricing_stage();
        config.actions.rest_drip_relief = 2.0;
        config.actions.rest_mutual_relief = 11.0;
        make_busy_eating(&mut world);

        // Tick 1: partner busy -> drip.
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        // Tick 2: partner settled -> mutual.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].activity = Activity::Resting { with_friend: None };
        world.tick += 1;
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        // Tick 3: partner wandered -> solo, neither counter.
        let b = world.kitty_index(2).unwrap();
        world.kitties[b].pos = Position::new(9, 9);
        world.tick += 1;
        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);

        let clock = world.kitty(1).unwrap().activity_clock.unwrap();
        assert_eq!(clock.drip_ticks, 1, "one drip tick");
        assert_eq!(clock.mutual_ticks, 1, "one mutual tick");
        let serviced = clock.applied - clock.started + 1;
        assert_eq!(serviced, 3, "three serviced ticks");
        assert_eq!(
            u64::from(clock.mutual_ticks + clock.drip_ticks),
            serviced - 1,
            "the shortfall is exactly the one solo tick"
        );
    }

    #[test]
    fn cosleep_scenes_count_their_tiers_too() {
        // FR-011 covers both tiered activities; a solo nap counts nothing.
        let (mut world, config) = cuddle_pricing_stage();
        make_busy_eating(&mut world);
        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        let clock = world.kitty(1).unwrap().activity_clock.unwrap();
        assert_eq!((clock.mutual_ticks, clock.drip_ticks), (0, 1), "drip tick");

        let (mut world, mut config) = cuddle_pricing_stage();
        settle(&mut world, 2);
        apply(&mut world, 1, Action::Sleep { with: Some(2) }, &config);
        let clock = world.kitty(1).unwrap().activity_clock.unwrap();
        assert_eq!(
            (clock.mutual_ticks, clock.drip_ticks),
            (1, 0),
            "mutual tick"
        );

        // A solo nap is not a tiered scene.
        config.actions.rest_drip_relief = 2.0;
        let (mut world, _) = cuddle_pricing_stage();
        apply(&mut world, 1, Action::Sleep { with: None }, &config);
        let clock = world.kitty(1).unwrap().activity_clock.unwrap();
        assert_eq!((clock.mutual_ticks, clock.drip_ticks), (0, 0));
    }

    #[test]
    fn at_the_launch_price_a_drip_scene_exists_but_pays_nothing() {
        // Spec 041 D5: with rest_drip_relief at its 0.0 default the
        // engine-sibling change is legality-only -- the busy-partner scene
        // is real, and nobody is paid.
        let (mut world, config) = cuddle_pricing_stage();
        assert_eq!(config.actions.rest_drip_relief, 0.0);
        make_busy_eating(&mut world);

        apply(&mut world, 1, Action::Rest { with: Some(2) }, &config);
        assert_eq!(
            world.kitty(1).unwrap().activity,
            Activity::Resting {
                with_friend: Some(2)
            },
            "the scene exists"
        );
        let a_cuddle = world.kitty(1).unwrap().needs.get(NeedKind::Cuddle);
        assert!(
            (a_cuddle - 50.0).abs() < 0.01,
            "and pays nothing at launch, got {a_cuddle}"
        );
    }

    /// Spec 033 US1/AC6 (FR-016 + FR-005): announce-then-consume is LAWFUL.
    /// The engine guarantees emission-time truth only -- a speaker may
    /// honestly say "food here" and then eat the last serving, and the
    /// announcement is never retracted when the referent dies. This test
    /// exists so a future "fairness" mechanism (a reservation, a lock, a
    /// penalty) fails loudly against the spec's stated boundary.
    #[test]
    fn announcing_food_and_eating_it_all_is_lawful() {
        use crate::element::{Element, ElementKind};
        use crate::meow::{message_legal, MessageKind};
        let (mut world, config) = test_world();
        world.tick = 50;
        world.elements.clear();
        let idx = world.kitty_index(1).unwrap();
        world.kitties[idx].pos = crate::grid::Position::new(8, 8);
        let base = world.kitties[idx].needs.get(NeedKind::Eat);
        world.kitties[idx].needs.add(NeedKind::Eat, 60.0 - base);
        world.push_element(Element {
            id: 950,
            kind: ElementKind::Chow { servings: 1 },
            pos: crate::grid::Position::new(8, 9),
            ttl: None,
        });

        // The announcement is true and accepted.
        assert!(message_legal(
            world.kitty(1).unwrap(),
            MessageKind::HereFood,
            50,
            &config,
            &world.elements
        ));
        apply_message(&mut world, 1, MessageKind::HereFood, &config, 50);
        assert!(
            world
                .recent_meows
                .iter()
                .any(|m| m.kind == MessageKind::HereFood && m.kitty_id == 1),
            "the announcement sounded"
        );
        let meow = world
            .recent_meows
            .iter()
            .find(|m| m.kind == MessageKind::HereFood)
            .unwrap();
        assert_eq!(meow.intensity, 0.0, "Here* stamps 0.0 (clarify verdict)");

        // The speaker eats the last serving: the ORDINARY eat path, no
        // downgrade, no penalty, relief granted in full.
        let eat_before = world.kitty(1).unwrap().needs.get(NeedKind::Eat);
        apply(&mut world, 1, Action::Eat, &config);
        let eat_after = world.kitty(1).unwrap().needs.get(NeedKind::Eat);
        assert!(
            (eat_before - eat_after - config.actions.eat_relief).abs() < 0.01,
            "relief granted in full: {eat_before} -> {eat_after}"
        );
        let bowl = world.element(950).unwrap();
        assert!(
            matches!(bowl.kind, ElementKind::Chow { servings: 0 }),
            "the last serving is gone"
        );
        assert!(bowl.is_expired(), "an empty bowl despawns at env resolve");

        // The announcement persists, un-retracted: the digest tracks the
        // SPEAKER, so it can never point at the dead bowl anyway -- that is
        // emitter-tracking and emission-time truth in one observable.
        assert!(
            world
                .recent_meows
                .iter()
                .any(|m| m.kind == MessageKind::HereFood && m.kitty_id == 1),
            "announcements are never retracted when the referent dies"
        );
        // And the WORD is now ungrounded for the next attempt: an empty
        // bowl is not food here.
        assert!(!message_legal(
            world.kitty(1).unwrap(),
            MessageKind::HereFood,
            51,
            &config,
            &world.elements
        ));
    }
}
