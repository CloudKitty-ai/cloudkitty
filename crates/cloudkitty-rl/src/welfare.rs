//! The long-run welfare metrics (spec 014 T033, research.md R7): mean
//! happiness, low-happiness streaks and share, floor touches, pinned
//! streaks, distress age — lifted from the CI welfare suite into one shared
//! module, consumed by both the long-run test and the evaluation harness,
//! so the gate and the scorecard are the same code.
//!
//! The bounds are the trusted bar (specs 004/006, re-baselined 2026-07-19);
//! the 004 baselines are hard floors — tightening is the only direction
//! these constants may move, enforced at compile time below.

use std::collections::BTreeMap;

use cloudkitty_core::element::ElementType;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use serde::Serialize;

pub const LOW_HAPPINESS: f32 = 45.0;
/// No low-happiness stretch may exceed this many consecutive ticks.
pub const MAX_LOW_STREAK: u64 = 20;
/// At most this share of ticks below LOW_HAPPINESS, per kitty.
pub const MAX_LOW_SHARE: f64 = 0.01;
/// No need this close to its cap for more than MAX_PINNED_STREAK
/// consecutive ticks while zero-distance relief for it exists.
pub const NEAR_CAP: f32 = 99.0;
pub const MAX_PINNED_STREAK: u64 = 25;
/// No distress older than this, and mean happiness at least the minimum.
pub const MAX_DISTRESS_AGE: u64 = 150;
pub const MIN_MEAN_HAPPINESS: f32 = 70.0;

// The 004 baselines, never to be loosened past (006 SC-003).
const SPEC_004_MAX_LOW_STREAK: u64 = 100;
const SPEC_004_MAX_LOW_SHARE: f64 = 0.05;
const SPEC_004_MAX_PINNED_STREAK: u64 = 25;
const SPEC_004_MAX_DISTRESS_AGE: u64 = 150;
const SPEC_004_MIN_MEAN_HAPPINESS: f32 = 65.0;

const _: () = assert!(MAX_LOW_STREAK <= SPEC_004_MAX_LOW_STREAK);
const _: () = assert!(MAX_LOW_SHARE <= SPEC_004_MAX_LOW_SHARE);
const _: () = assert!(MAX_PINNED_STREAK <= SPEC_004_MAX_PINNED_STREAK);
const _: () = assert!(MAX_DISTRESS_AGE <= SPEC_004_MAX_DISTRESS_AGE);
const _: () = assert!(MIN_MEAN_HAPPINESS >= SPEC_004_MIN_MEAN_HAPPINESS);

/// The definition of "relief at zero travel distance" for `kind`
/// (spec 004 SC-003).
pub fn zero_distance_relief_exists(world: &World, kitty_idx: usize, kind: NeedKind) -> bool {
    let kitty = &world.kitties[kitty_idx];
    match kind {
        // Grooming and napping happen anywhere; solo play makes play the same.
        NeedKind::Bath | NeedKind::Sleep | NeedKind::Play => true,
        NeedKind::Cuddle => world
            .kitties
            .iter()
            .any(|other| other.id != kitty.id && kitty.pos.is_adjacent(&other.pos)),
        // Spec 024 reconciliation: the metric asks the SAME question the
        // engine answers -- the nearest adjacent bowl, filtered for
        // servings (World::adjacent_stocked_chow, the arm `Eat` validates
        // against). Pre-024 this counted any adjacent Chow, so a cat
        // starved beside an empty bowl accrued pinned-streak blame for a
        // relief the engine would refuse -- the exact divergence class the
        // equivalence guardrail exists to catch, found while planning it.
        NeedKind::Eat => world.adjacent_stocked_chow(kitty.pos).is_some(),
        NeedKind::Drink => world
            .elements
            .iter()
            .any(|e| e.element_type() == ElementType::Water && kitty.pos.is_adjacent(&e.pos)),
    }
}

/// Streaming accumulator: construct on the generated world, call
/// [`WelfareAccumulator::observe`] after every tick, then
/// [`WelfareAccumulator::report`].
pub struct WelfareAccumulator {
    floor: f32,
    ticks: u64,
    ids: Vec<KittyId>,
    names: Vec<String>,
    low_streak: Vec<u64>,
    max_low_streak: Vec<u64>,
    low_ticks: Vec<u64>,
    happiness_sum: Vec<f64>,
    floor_touches: Vec<u64>,
    max_distress_age: u64,
    pinned_streaks: BTreeMap<(usize, NeedKind), u64>,
    max_pinned: BTreeMap<(usize, NeedKind), u64>,
}

impl WelfareAccumulator {
    pub fn new(world: &World, config: &Config) -> Self {
        let n = world.kitties.len();
        WelfareAccumulator {
            floor: config.happiness.floor,
            ticks: 0,
            ids: world.kitties.iter().map(|k| k.id).collect(),
            names: world.kitties.iter().map(|k| k.name.clone()).collect(),
            low_streak: vec![0; n],
            max_low_streak: vec![0; n],
            low_ticks: vec![0; n],
            happiness_sum: vec![0.0; n],
            floor_touches: vec![0; n],
            max_distress_age: 0,
            pinned_streaks: BTreeMap::new(),
            max_pinned: BTreeMap::new(),
        }
    }

    /// Records one post-tick observation of the world.
    pub fn observe(&mut self, world: &World) {
        self.ticks += 1;
        let n = self.ids.len();
        for idx in 0..n {
            let kitty = &world.kitties[idx];
            self.happiness_sum[idx] += kitty.happiness as f64;

            if kitty.happiness <= self.floor {
                self.floor_touches[idx] += 1;
            }
            if kitty.happiness < LOW_HAPPINESS {
                self.low_ticks[idx] += 1;
                self.low_streak[idx] += 1;
                self.max_low_streak[idx] = self.max_low_streak[idx].max(self.low_streak[idx]);
            } else {
                self.low_streak[idx] = 0;
            }

            for since in kitty.distress_since.values() {
                self.max_distress_age =
                    self.max_distress_age.max(world.tick.saturating_sub(*since));
            }
        }

        // Pinned needs read positions, so they observe after the kitty pass.
        for idx in 0..n {
            for kind in NeedKind::ALL {
                let key = (idx, kind);
                let pinned = world.kitties[idx].needs.get(kind) >= NEAR_CAP
                    && zero_distance_relief_exists(world, idx, kind);
                let streak = self.pinned_streaks.entry(key).or_insert(0);
                if pinned {
                    *streak += 1;
                    let best = self.max_pinned.entry(key).or_insert(0);
                    *best = (*best).max(*streak);
                } else {
                    *streak = 0;
                }
            }
        }
    }

    pub fn report(&self) -> WelfareReport {
        let ticks = self.ticks.max(1);
        let kitties = (0..self.ids.len())
            .map(|idx| KittyWelfare {
                kitty_id: self.ids[idx],
                name: self.names[idx].clone(),
                mean_happiness: self.happiness_sum[idx] / ticks as f64,
                max_low_streak: self.max_low_streak[idx],
                low_share: self.low_ticks[idx] as f64 / ticks as f64,
                floor_touches: self.floor_touches[idx],
            })
            .collect();
        let pinned = self
            .max_pinned
            .iter()
            .filter(|(_, &streak)| streak > 0)
            .map(|(&(idx, kind), &streak)| PinnedStreak {
                kitty_id: self.ids[idx],
                need: kind.as_str().to_string(),
                streak,
            })
            .collect();
        WelfareReport {
            ticks: self.ticks,
            kitties,
            max_distress_age: self.max_distress_age,
            pinned,
        }
    }
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct KittyWelfare {
    pub kitty_id: KittyId,
    pub name: String,
    pub mean_happiness: f64,
    pub max_low_streak: u64,
    pub low_share: f64,
    pub floor_touches: u64,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct PinnedStreak {
    pub kitty_id: KittyId,
    pub need: String,
    pub streak: u64,
}

/// The scorecard: every metric the CI suite guards.
#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct WelfareReport {
    pub ticks: u64,
    pub kitties: Vec<KittyWelfare>,
    pub max_distress_age: u64,
    pub pinned: Vec<PinnedStreak>,
}

impl WelfareReport {
    /// Every violated bound, human-phrased; empty means the run met the bar.
    pub fn violations(&self) -> Vec<String> {
        let mut violations = Vec::new();
        for k in &self.kitties {
            if k.max_low_streak > MAX_LOW_STREAK {
                violations.push(format!(
                    "{} was below {LOW_HAPPINESS} happiness for {} consecutive ticks (limit {MAX_LOW_STREAK})",
                    k.name, k.max_low_streak
                ));
            }
            if k.floor_touches > 0 {
                violations.push(format!(
                    "{} touched the happiness floor {} times (limit 0)",
                    k.name, k.floor_touches
                ));
            }
            if k.low_share > MAX_LOW_SHARE {
                violations.push(format!(
                    "{} spent {:.1}% of ticks below {LOW_HAPPINESS} (limit {:.0}%)",
                    k.name,
                    k.low_share * 100.0,
                    MAX_LOW_SHARE * 100.0
                ));
            }
            if k.mean_happiness < MIN_MEAN_HAPPINESS as f64 {
                violations.push(format!(
                    "{}'s mean happiness {:.1} fell short of {MIN_MEAN_HAPPINESS}",
                    k.name, k.mean_happiness
                ));
            }
        }
        if self.max_distress_age > MAX_DISTRESS_AGE {
            violations.push(format!(
                "a distress went unresolved for {} ticks (limit {MAX_DISTRESS_AGE})",
                self.max_distress_age
            ));
        }
        for p in &self.pinned {
            if p.streak > MAX_PINNED_STREAK {
                violations.push(format!(
                    "kitty {}'s {} need sat within 1.0 of the cap for {} consecutive ticks \
                     while zero-distance relief existed (limit {MAX_PINNED_STREAK})",
                    p.kitty_id, p.need, p.streak
                ));
            }
        }
        violations
    }
}
