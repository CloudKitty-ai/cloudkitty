//! The team reward (spec 014 FR-008/FR-009), computed entirely outside the
//! engine.
//!
//! Each kitty's happiness is recomputed **unclamped** from its needs and the
//! configured weights (`100 − Σ need × weight`, no floor) so the training
//! signal keeps its gradient below the engine's display floor; the engine's
//! clamped happiness stays authoritative for everything the engine does.
//! The aggregate is a power mean with exponent p ≤ 1 over the **full
//! roster** (scripted kitties included, FR-020): p = 1 the plain average,
//! p = 0 Nash welfare (geometric mean, the default), large negative p
//! approaching the least-happy kitty. The configured offset ε keeps value
//! and gradient finite at zero happiness; it is added before and subtracted
//! after, so full happiness scores exactly 1.

use cloudkitty_core::needs::{NeedWeights, Needs};
use cloudkitty_core::world::WorldSnapshot;
use cloudkitty_core::Config;

use crate::config::RewardConfig;

/// A kitty's happiness with no floor: `100 − Σ need × weight`, in [0, 100]
/// arithmetically (needs and weights are bounded) but never clamped by a
/// display floor.
pub fn unclamped_happiness(needs: &Needs, weights: &NeedWeights) -> f64 {
    let weighted: f64 = cloudkitty_core::needs::NeedKind::ALL
        .iter()
        .map(|k| needs.get(*k) as f64 * weights.get(*k) as f64)
        .sum();
    100.0 - weighted
}

/// The inequality-averse welfare aggregate of normalized happiness values
/// (each in [0, 1]): `M_p(h + ε) − ε`. Strictly increasing in every entry;
/// concave for p ≤ 1.
pub fn welfare_aggregate(normalized: &[f64], p: f64, epsilon: f64) -> f64 {
    if normalized.is_empty() {
        return 0.0;
    }
    let n = normalized.len() as f64;
    let shifted = normalized.iter().map(|h| h + epsilon);
    let mean = if p == 0.0 {
        // Nash welfare: the geometric mean.
        (shifted.map(|v| v.ln()).sum::<f64>() / n).exp()
    } else {
        (shifted.map(|v| v.powf(p)).sum::<f64>() / n).powf(1.0 / p)
    };
    mean - epsilon
}

/// The team welfare of a roster: one scalar over every kitty (FR-020).
pub fn team_welfare_of(
    kitties: &[cloudkitty_core::kitty::Kitty],
    core: &Config,
    cfg: &RewardConfig,
) -> f64 {
    let normalized: Vec<f64> = kitties
        .iter()
        .map(|k| unclamped_happiness(&k.needs, &core.happiness.weights) / 100.0)
        .collect();
    welfare_aggregate(&normalized, cfg.p, cfg.epsilon)
}

/// The team reward for a frozen snapshot: one scalar, broadcast to every
/// agent. Level mode; delta and shaping are the episode's bookkeeping.
pub fn team_reward(snapshot: &WorldSnapshot, core: &Config, cfg: &RewardConfig) -> f64 {
    team_welfare_of(&snapshot.kitties, core, cfg)
}

/// The shaping potential Φ(s) (FR-009): −coefficient × (active distress
/// entries / roster). Potential-based shaping adds `gamma·Φ(s′) − Φ(s)`,
/// leaving the optimal policy provably unchanged.
pub fn shaping_potential(snapshot: &WorldSnapshot, coefficient: f64) -> f64 {
    if snapshot.kitties.is_empty() {
        return 0.0;
    }
    let distressed: usize = snapshot.kitties.iter().map(|k| k.in_distress.len()).sum();
    -coefficient * distressed as f64 / snapshot.kitties.len() as f64
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nash_is_the_geometric_mean_and_full_happiness_scores_one() {
        let all_full = [1.0, 1.0, 1.0, 1.0];
        let w = welfare_aggregate(&all_full, 0.0, 0.01);
        assert!((w - 1.0).abs() < 1e-12, "got {w}");

        // p = 1 is the plain average.
        let mixed = [0.2, 0.8];
        let avg = welfare_aggregate(&mixed, 1.0, 0.01);
        assert!((avg - 0.5).abs() < 1e-12, "got {avg}");
    }

    #[test]
    fn zero_happiness_stays_finite_via_epsilon() {
        let with_zero = [0.0, 1.0];
        let w = welfare_aggregate(&with_zero, 0.0, 0.01);
        assert!(w.is_finite());
        assert!(w > 0.0 - 0.01);

        let very_negative_p = welfare_aggregate(&with_zero, -8.0, 0.01);
        assert!(very_negative_p.is_finite());
    }
}
