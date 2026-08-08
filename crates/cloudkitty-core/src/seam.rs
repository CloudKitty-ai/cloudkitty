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
use crate::world::World;

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
    pub action: Action,
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
    Action(Action),
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

    pub fn from_actions(actions: impl IntoIterator<Item = (KittyId, Action)>) -> Self {
        let mut joint = Self::new();
        for (id, action) in actions {
            joint.propose(id, action);
        }
        joint
    }

    /// Proposes `action` for `kitty_id`. A second proposal for the same kitty
    /// replaces the first (last write wins).
    pub fn propose(&mut self, kitty_id: KittyId, action: Action) {
        self.entries.insert(kitty_id, ProposalEntry::Action(action));
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
pub fn drive_tick(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> DrivenTick {
    let resolved = resolve_decisions(world, registry, config);
    let decisions: Vec<(KittyId, Action)> =
        resolved.iter().map(|r| (r.kitty_id, r.action)).collect();
    let outcome = world.run_applied_phases(&decisions, config);

    // `resolved` is already in stable id order (the resolver iterates the
    // roster), so the records need no re-sort.
    let records = outcome.records(
        resolved
            .iter()
            .map(|r| (r.kitty_id, r.action, r.provenance, r.seed)),
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
