//! Needs and happiness.
//!
//! Article I: needs are bounded pressures, never negative states. `Need` clamps on
//! every mutation so no arithmetic anywhere in the engine can push a kitty outside
//! `[0, 100]`, and happiness is clamped to a floor so it can never reach zero.

use serde::{Deserialize, Serialize};

pub const NEED_MIN: f32 = 0.0;
pub const NEED_MAX: f32 = 100.0;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum NeedKind {
    Eat,
    Drink,
    Sleep,
    Play,
    Cuddle,
    Bath,
}

impl NeedKind {
    pub const ALL: [NeedKind; 6] = [
        NeedKind::Eat,
        NeedKind::Drink,
        NeedKind::Sleep,
        NeedKind::Play,
        NeedKind::Cuddle,
        NeedKind::Bath,
    ];

    pub fn as_str(&self) -> &'static str {
        match self {
            NeedKind::Eat => "eat",
            NeedKind::Drink => "drink",
            NeedKind::Sleep => "sleep",
            NeedKind::Play => "play",
            NeedKind::Cuddle => "cuddle",
            NeedKind::Bath => "bath",
        }
    }
}

/// A single need pressure, always within `[0, 100]`.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Need(f32);

impl Need {
    pub fn new(value: f32) -> Self {
        Need(Self::clamp(value))
    }

    pub fn value(&self) -> f32 {
        self.0
    }

    /// Adds `delta` (positive to raise pressure, negative to relieve it), clamping.
    /// NaN deltas are ignored rather than poisoning the value.
    pub fn add(&mut self, delta: f32) {
        if delta.is_nan() {
            return;
        }
        self.0 = Self::clamp(self.0 + delta);
    }

    fn clamp(value: f32) -> f32 {
        if value.is_nan() {
            return NEED_MIN;
        }
        value.clamp(NEED_MIN, NEED_MAX)
    }
}

impl Default for Need {
    fn default() -> Self {
        Need(0.0)
    }
}

/// The six needs of a kitty.
#[derive(Debug, Clone, Copy, PartialEq, Default, Serialize, Deserialize)]
pub struct Needs {
    pub eat: Need,
    pub drink: Need,
    pub sleep: Need,
    pub play: Need,
    pub cuddle: Need,
    pub bath: Need,
}

impl Needs {
    pub fn get(&self, kind: NeedKind) -> f32 {
        match kind {
            NeedKind::Eat => self.eat.value(),
            NeedKind::Drink => self.drink.value(),
            NeedKind::Sleep => self.sleep.value(),
            NeedKind::Play => self.play.value(),
            NeedKind::Cuddle => self.cuddle.value(),
            NeedKind::Bath => self.bath.value(),
        }
    }

    pub fn add(&mut self, kind: NeedKind, delta: f32) {
        match kind {
            NeedKind::Eat => self.eat.add(delta),
            NeedKind::Drink => self.drink.add(delta),
            NeedKind::Sleep => self.sleep.add(delta),
            NeedKind::Play => self.play.add(delta),
            NeedKind::Cuddle => self.cuddle.add(delta),
            NeedKind::Bath => self.bath.add(delta),
        }
    }

    /// The need under the most pressure; ties break by `NeedKind::ALL` order so the
    /// result never depends on iteration nondeterminism.
    pub fn highest_pressure(&self) -> (NeedKind, f32) {
        let mut best = (NeedKind::Eat, self.get(NeedKind::Eat));
        for kind in NeedKind::ALL.into_iter().skip(1) {
            let v = self.get(kind);
            if v > best.1 {
                best = (kind, v);
            }
        }
        best
    }

    pub fn all(&self) -> [(NeedKind, f32); 6] {
        NeedKind::ALL.map(|k| (k, self.get(k)))
    }
}

/// Per-need weights used to compute happiness. Validated to sum to 1.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct NeedWeights {
    pub eat: f32,
    pub drink: f32,
    pub sleep: f32,
    pub play: f32,
    pub cuddle: f32,
    pub bath: f32,
}

impl NeedWeights {
    pub fn get(&self, kind: NeedKind) -> f32 {
        match kind {
            NeedKind::Eat => self.eat,
            NeedKind::Drink => self.drink,
            NeedKind::Sleep => self.sleep,
            NeedKind::Play => self.play,
            NeedKind::Cuddle => self.cuddle,
            NeedKind::Bath => self.bath,
        }
    }

    pub fn sum(&self) -> f32 {
        NeedKind::ALL.iter().map(|k| self.get(*k)).sum()
    }
}

impl Default for NeedWeights {
    fn default() -> Self {
        Self {
            eat: 0.25,
            drink: 0.25,
            sleep: 0.15,
            play: 0.15,
            cuddle: 0.10,
            bath: 0.10,
        }
    }
}

/// The weighted-need happiness before any floor: `100 - Σ need × weight`.
/// The one implementation of the formula (spec 014 review): the engine's
/// displayed happiness clamps it (Article I's floor), and the RL reward
/// reads it raw so the training signal keeps its gradient below the floor.
pub fn raw_happiness(needs: &Needs, weights: &NeedWeights) -> f32 {
    let weighted: f32 = NeedKind::ALL
        .iter()
        .map(|k| needs.get(*k) * weights.get(*k))
        .sum();
    100.0 - weighted
}

/// Happiness = 100 - weighted average of needs, clamped to `floor` (Article I: it
/// can never reach zero).
pub fn happiness(needs: &Needs, weights: &NeedWeights, floor: f32) -> f32 {
    raw_happiness(needs, weights).clamp(floor, 100.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn need_clamps_at_both_ends() {
        let mut n = Need::new(50.0);
        n.add(-100.0);
        assert_eq!(n.value(), 0.0, "needs never go negative");

        n.add(1000.0);
        assert_eq!(n.value(), 100.0, "needs never exceed 100");

        assert_eq!(Need::new(-5.0).value(), 0.0);
        assert_eq!(Need::new(150.0).value(), 100.0);
    }

    #[test]
    fn need_ignores_nan() {
        let mut n = Need::new(42.0);
        n.add(f32::NAN);
        assert_eq!(n.value(), 42.0);
        assert_eq!(Need::new(f32::NAN).value(), 0.0);
    }

    #[test]
    fn happiness_is_full_when_all_needs_are_zero() {
        let needs = Needs::default();
        let h = happiness(&needs, &NeedWeights::default(), 5.0);
        assert_eq!(h, 100.0);
    }

    #[test]
    fn happiness_respects_the_floor() {
        let maxed = Needs {
            eat: Need::new(100.0),
            drink: Need::new(100.0),
            sleep: Need::new(100.0),
            play: Need::new(100.0),
            cuddle: Need::new(100.0),
            bath: Need::new(100.0),
        };
        // Raw would be 100 - 100 = 0; the floor lifts it.
        let h = happiness(&maxed, &NeedWeights::default(), 5.0);
        assert_eq!(h, 5.0);
        assert!(h > 0.0, "Article I: happiness can never reach zero");
    }

    #[test]
    fn happiness_uses_configured_weights() {
        let mut needs = Needs::default();
        needs.add(NeedKind::Eat, 100.0);
        // Default eat weight is 0.25 => 100 - 25 = 75.
        let h = happiness(&needs, &NeedWeights::default(), 5.0);
        assert!((h - 75.0).abs() < f32::EPSILON, "got {h}");
    }

    #[test]
    fn highest_pressure_breaks_ties_deterministically() {
        let mut needs = Needs::default();
        needs.add(NeedKind::Play, 40.0);
        needs.add(NeedKind::Bath, 40.0);
        // Play precedes Bath in NeedKind::ALL, so it wins the tie every time.
        assert_eq!(needs.highest_pressure().0, NeedKind::Play);

        needs.add(NeedKind::Drink, 90.0);
        assert_eq!(needs.highest_pressure(), (NeedKind::Drink, 90.0));
    }

    #[test]
    fn default_weights_sum_to_one() {
        assert!((NeedWeights::default().sum() - 1.0).abs() < 1e-6);
    }
}
