//! The `[needy]` table (spec 067 FR-008, `contracts/needy-law.md` §8):
//! the parameters the two needy presets read. OPTIONAL by the 062–066
//! design — absent is the pre-067 engine byte for byte on every
//! serialized surface, and a needy seat with no table runs
//! [`NeedyConfig::default`], the coverage design of research D7. The
//! table is parameters, never a hazard: writing it with no needy seat is
//! valid and inert (the SEAT is the hazard, `welfare_hazard::HazardMode`).
//!
//! Nothing here hard-codes the engine's need count (FR-016): `mix` is
//! sized by `NeedKind::ALL.len()` at runtime, and the validator's message
//! for a wrong-length vector names that count.

use serde::{Deserialize, Serialize};

use crate::needs::NeedKind;

/// The `[needy]` table. Every field has a default, so a partial table
/// fills the rest from the coverage design.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct NeedyConfig {
    /// One weight per masked-need count: entry `k` is the weight of
    /// `m = k + 1`. Exactly `NeedKind::ALL.len()` entries; a zero
    /// excludes that count. Default `[0.5, 0.2, 0.15, 0.15, 0, …]`.
    pub mix: Vec<f32>,
    /// `needy` releases an episode when every masked need is at or
    /// above this level (ignored by `needy_hold`). Strictly above the
    /// off-beam sleep floor, or a masked sleep would release at once.
    pub release_level: f32,
    /// Both presets release an episode once this many ticks have passed
    /// since its onset.
    pub hold_ticks: u64,
    /// The rest gap drawn after a release, inclusive bounds in ticks.
    pub gap: GapRange,
    /// First-onset history levels as ascending tick edges: level `i` is
    /// `[edge_i, edge_{i+1})`; at least six edges (five levels). The
    /// default straddles the F-070 knee of the frozen head's grave read.
    pub onset_levels: Vec<u64>,
    /// One weight per level.
    pub onset_weights: Vec<f32>,
    /// How the first-onset tick is drawn within its level.
    pub onset_draw: OnsetDraw,
}

/// Inclusive tick bounds of the rest gap.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GapRange {
    pub min: u64,
    pub max: u64,
}

/// The within-level draw shape for the first onset (needy-law §3.1).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OnsetDraw {
    #[default]
    Flat,
    LogUniform,
}

impl Default for GapRange {
    fn default() -> Self {
        GapRange {
            min: 300,
            max: 1200,
        }
    }
}

impl Default for NeedyConfig {
    /// The coverage design (research D7, spec A4): single-need episodes
    /// half the time, the higher counts opened by a set's declaration;
    /// release at 90; a 1,500-tick hold; onset levels 0–2 / 2–10 /
    /// 10–50 / 50–200 / 200–20,000 weighted equally, drawn flat.
    fn default() -> Self {
        let count = NeedKind::ALL.len();
        let head = [0.5f32, 0.2, 0.15, 0.15];
        let mix = (0..count)
            .map(|k| head.get(k).copied().unwrap_or(0.0))
            .collect();
        NeedyConfig {
            mix,
            release_level: 90.0,
            hold_ticks: 1500,
            gap: GapRange::default(),
            onset_levels: vec![0, 2, 10, 50, 200, 20_000],
            onset_weights: vec![0.2; 5],
            onset_draw: OnsetDraw::Flat,
        }
    }
}

impl NeedyConfig {
    /// The number of first-onset levels (edges minus one; 0 for a
    /// malformed edge list, which validation refuses).
    pub fn level_count(&self) -> usize {
        self.onset_levels.len().saturating_sub(1)
    }
}
