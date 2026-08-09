//! The joint-action seam (spec 014): drive the world from outside, honestly.
//!
//! This module is the engine-side surface external drivers build on. It knows
//! nothing of the training vocabulary next door — it speaks proposals,
//! the same language behaviors do (Article IV). Two things live here:
//!
//! - the types the seam trades in ([`Provenance`], [`ResolvedDecision`], and —
//!   as the seam lands — the joint proposal and tick report), and
//! - the budgetless behavior-driven driver, which resolves every behavior
//!   without the wall-clock budget (FR-017) and returns the proposals it
//!   dispatched — the parity capture (research.md R4).

use std::collections::BTreeMap;
use std::sync::Arc;

use serde::{Deserialize, Serialize};

use crate::action::Action;
use crate::behavior::{resolve_decisions, BehaviorRegistry};
use crate::config::Config;
use crate::events::{ActivityEnd, DistressEvent};
use crate::kitty::KittyId;
use crate::meow::MessageKind;
use crate::world::World;

/// One kitty's full decision (spec 028): an activity to spend the turn on
/// and, riding along, an optional message. `None` is silence -- the message
/// channel never costs the turn, and the pair is the only carrier shape any
/// decider returns.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Decision {
    pub activity: Action,
    /// `None` = Silent. Engine-legality is enforced at apply: an illegal
    /// message downgrades to Silent; the paired activity is untouched.
    pub message: Option<MessageKind>,
}

impl Decision {
    /// An activity with nothing to say.
    pub fn silent(activity: Action) -> Self {
        Self {
            activity,
            message: None,
        }
    }

    /// Transitional (spec 028): maps the retiring turn-spending meow onto
    /// the two-channel shape -- `Action::Meow` becomes an idle turn carrying
    /// the message; everything else is silent. Dies with the last internal
    /// `Action::Meow` producer (T012's announce rule).
    pub fn from_legacy(action: Action) -> Self {
        match action {
            Action::Meow { message } => Self {
                activity: Action::Idle,
                message: Some(message),
            },
            other => Self::silent(other),
        }
    }

}

impl From<Action> for Decision {
    /// A bare activity is a silent decision -- the conversion typed drivers
    /// lean on so proposing an `Action` keeps meaning what it always meant.
    fn from(activity: Action) -> Self {
        Self::silent(activity)
    }
}

/// How a dispatched decision came to be (spec 014 FR-017). Every headlessly
/// dispatched decision carries one of these marks, so a broken advisor can
/// never ride the fallback through an evaluation unnoticed.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Provenance {
    /// The kitty's own advisor — a behavior, or an external proposer —
    /// produced this decision.
    PolicyMade,
    /// Dispatch fell back to the default behavior: the advisor panicked,
    /// was unknown, or (in the served world only) ran out its time budget.
    FallbackTaken,
    /// Joint-action seam only: no well-formed proposal was supplied for this
    /// kitty, and the engine substituted idle (Article IV's safe no-op).
    /// Deliberately distinct from `FallbackTaken`, whose meaning is reserved
    /// for dispatched decisions.
    SubstitutedIdle,
}

/// One tick's dealt per-kitty decision seeds (spec 014 FR-002/FR-003).
///
/// Deliberately opaque and consumed **by value**: only
/// [`World::deal_decision_seeds`] can mint one (stamping the tick it was
/// dealt for), and applying it to a tick moves it. A driver therefore
/// cannot skip the deal, reuse a stale deal, or apply one twice — the
/// master RNG's draw shape is checked by construction, not promised by a
/// doc comment. [`World::tick_with_proposals_seeded`] asserts the stamp
/// matches the tick it is applied to.
#[derive(Debug)]
#[must_use = "dropping a deal silently desyncs the master RNG; apply it to the tick \
              it was dealt for, or use World::advance_past_decision_draws to advance \
              deliberately"]
pub struct DealtSeeds {
    pub(crate) tick: u64,
    pub(crate) seeds: Vec<(KittyId, u64)>,
}

impl DealtSeeds {
    /// The seed dealt to `kitty_id`, if it was in the roster at deal time.
    pub fn seed_for(&self, kitty_id: KittyId) -> Option<u64> {
        self.seeds
            .iter()
            .find(|(id, _)| *id == kitty_id)
            .map(|&(_, seed)| seed)
    }

    /// Every (kitty, seed) pair, stable id order.
    pub fn iter(&self) -> impl Iterator<Item = (KittyId, u64)> + '_ {
        self.seeds.iter().copied()
    }
}

/// One kitty's decision as the budgetless resolver produced it: the proposal,
/// the decision seed it was dealt (drawn from the master RNG in stable id
/// order, as always), and how the decision came to be. Returned to the
/// caller, never stored in world state (research.md R4).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ResolvedDecision {
    pub kitty_id: KittyId,
    pub decision: Decision,
    /// The seed this kitty's `DecisionRng` was built from this tick.
    pub seed: u64,
    pub provenance: Provenance,
}

/// One per-kitty entry of a joint proposal. `Malformed` records an entry that
/// arrived over a wire and failed to parse — typed drivers never construct
/// it, but the seam must account for it (Article IV: malformation resolves
/// to idle, never to an error).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProposalEntry {
    Decision(Decision),
    Malformed,
}

/// One tick's worth of externally supplied proposals (spec 014 FR-001).
///
/// No validation at construction: absence, duplication (last write wins at
/// the map level), and malformation all resolve per kitty to idle inside the
/// tick. Entries for unknown kitty ids are ignored and reported unconsumed
/// in the [`TickReport`].
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct JointProposal {
    entries: BTreeMap<KittyId, ProposalEntry>,
}

impl JointProposal {
    pub fn new() -> Self {
        Self::default()
    }

    /// Builds a proposal set from anything decision-shaped: `(id, Action)`
    /// pairs propose silent decisions (the pre-028 meaning, preserved), and
    /// `(id, Decision)` pairs carry a message.
    pub fn from_actions<D: Into<Decision>>(
        actions: impl IntoIterator<Item = (KittyId, D)>,
    ) -> Self {
        let mut joint = Self::new();
        for (id, decision) in actions {
            joint.propose(id, decision);
        }
        joint
    }

    /// Proposes a decision for `kitty_id` -- a bare `Action` proposes it
    /// silently. A second proposal for the same kitty replaces the first
    /// (last write wins).
    pub fn propose(&mut self, kitty_id: KittyId, decision: impl Into<Decision>) {
        self.entries
            .insert(kitty_id, ProposalEntry::Decision(decision.into()));
    }

    /// Records that a proposal for `kitty_id` arrived but could not be
    /// parsed. The kitty idles this tick, marked `SubstitutedIdle`.
    pub fn propose_malformed(&mut self, kitty_id: KittyId) {
        self.entries.insert(kitty_id, ProposalEntry::Malformed);
    }

    pub fn get(&self, kitty_id: KittyId) -> Option<&ProposalEntry> {
        self.entries.get(&kitty_id)
    }

    /// Every kitty id with an entry, ascending.
    pub fn ids(&self) -> impl Iterator<Item = KittyId> + '_ {
        self.entries.keys().copied()
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
}

/// One kitty's row of the tick report: the proposed / validated / applied
/// triple that makes validation rejections and duration rewrites visible
/// (spec 014 FR-003), plus the provenance mark and the decision seed the
/// kitty was dealt this tick.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct KittyTickRecord {
    pub kitty_id: KittyId,
    pub proposed: Action,
    pub validated: Action,
    pub applied: Action,
    /// Spec 028: the message the decision carried, and the one that actually
    /// emitted. An illegal message shows as proposed != applied (Silent) --
    /// there is no separate message provenance; activity provenance is
    /// untouched by the channel.
    #[serde(default)]
    pub proposed_message: Option<MessageKind>,
    #[serde(default)]
    pub applied_message: Option<MessageKind>,
    pub provenance: Provenance,
    pub decision_seed: u64,
}

/// The honest record of one tick (spec 014 FR-003): every kitty in the
/// roster appears exactly once, in stable id order, every tick.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct TickReport {
    pub records: Vec<KittyTickRecord>,
    /// Distress events this tick produced.
    pub distress_events: Vec<DistressEvent>,
    /// Activities that ended this tick, with their true spans.
    pub activity_endings: Vec<ActivityEnd>,
    /// Proposal entries naming kitty ids not in the roster, ascending.
    pub unconsumed: Vec<KittyId>,
}

impl TickReport {
    pub fn record(&self, kitty_id: KittyId) -> Option<&KittyTickRecord> {
        self.records.iter().find(|r| r.kitty_id == kitty_id)
    }
}

/// What the budgetless behavior-driven driver hands back: the tick report,
/// plus the proposals it dispatched — the parity capture (research.md R4).
/// Feeding `proposals` into [`World::tick_with_proposals`] on a same-seed
/// world reproduces this tick byte-identically (SC-001).
#[derive(Debug, Clone)]
pub struct DrivenTick {
    pub report: TickReport,
    pub proposals: JointProposal,
}

/// Advances the world one behavior-driven tick on the **budgetless** path
/// (spec 014 FR-017): every behavior resolves with panic isolation and
/// fallback but no wall clock, and the dispatched proposals come back with
/// the report. Same law as [`World::tick`], different dispatch — from the
/// same seed the two produce byte-identical worlds.
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_legacy_mapping_rides_the_channel() {
        // Transitional (spec 028): from_legacy lifts the retiring
        // turn-spending meow onto the two-channel shape -- the message
        // rides, the turn is idle -- and leaves everything else silent.
        let d = Decision::from_legacy(Action::Meow {
            message: MessageKind::WantPlay,
        });
        assert_eq!(
            (d.activity, d.message),
            (Action::Idle, Some(MessageKind::WantPlay))
        );
        assert_eq!(
            Decision::from_legacy(Action::Eat),
            Decision::silent(Action::Eat)
        );
        // A bare activity converts silently -- the typed-driver promise.
        assert_eq!(Decision::from(Action::Eat).message, None);
    }
}

pub fn drive_tick(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> DrivenTick {
    let resolved = resolve_decisions(world, registry, config);
    let decisions: Vec<(KittyId, Decision)> =
        resolved.iter().map(|r| (r.kitty_id, r.decision)).collect();
    let outcome = world.run_applied_phases_from_decisions(&decisions, config);

    // `resolved` is already in stable id order (the resolver iterates the
    // roster), so the records need no re-sort.
    let records = outcome.records(
        resolved
            .iter()
            .map(|r| (r.kitty_id, r.decision, r.provenance, r.seed)),
    );

    DrivenTick {
        report: TickReport {
            records,
            distress_events: outcome.distress_events,
            activity_endings: outcome.activity_endings,
            unconsumed: Vec::new(),
        },
        proposals: JointProposal::from_actions(decisions),
    }
}
