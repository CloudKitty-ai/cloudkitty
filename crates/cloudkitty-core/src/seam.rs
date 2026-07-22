//! The joint-action seam (spec 014): drive the world from outside, honestly.
//!
//! This module is the engine-side surface external drivers build on. It knows
//! nothing about observations, rewards, or policies — it speaks proposals,
//! the same language behaviors do (Article IV). Two things live here:
//!
//! - the types the seam trades in ([`Provenance`], [`ResolvedDecision`], and —
//!   as the seam lands — the joint proposal and tick report), and
//! - the budgetless behavior-driven driver, which resolves every behavior
//!   without the wall-clock budget (FR-017) and returns the proposals it
//!   dispatched — the parity capture (research.md R4).

use serde::{Deserialize, Serialize};

use crate::action::Action;
use crate::kitty::KittyId;

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
