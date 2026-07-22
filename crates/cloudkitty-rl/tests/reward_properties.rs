//! Reward property tests (spec 014 FR-008, T022): strictly increasing in
//! every kitty's happiness, concave, finite at zero via ε, and the pinned
//! behaviors at p = 1 (plain average), p = 0 (Nash), p = −8 (approaching
//! the least-happy kitty).

use cloudkitty_rl::reward::welfare_aggregate;
use proptest::prelude::*;

const EPS: f64 = 0.01;

fn arb_roster() -> impl Strategy<Value = Vec<f64>> {
    prop::collection::vec(0.0f64..=1.0, 2..=6)
}

proptest! {
    #[test]
    fn strictly_increasing_in_every_kitty(h in arb_roster(), p in -8.0f64..=1.0) {
        let base = welfare_aggregate(&h, p, EPS);
        for i in 0..h.len() {
            if h[i] >= 0.999 { continue; }
            let mut better = h.clone();
            better[i] += 0.001;
            let improved = welfare_aggregate(&better, p, EPS);
            prop_assert!(
                improved > base,
                "raising kitty {} ({} -> {}) did not raise welfare ({} -> {}) at p={}",
                i, h[i], better[i], base, improved, p
            );
        }
    }

    #[test]
    fn concave_along_segments(a in arb_roster(), t in 0.05f64..=0.95, p in -8.0f64..=1.0) {
        // Concavity: W(t·a + (1−t)·b) ≥ t·W(a) + (1−t)·W(b). Use b = the
        // roster reversed, which keeps lengths equal.
        let b: Vec<f64> = a.iter().rev().copied().collect();
        let mid: Vec<f64> = a.iter().zip(&b).map(|(x, y)| t * x + (1.0 - t) * y).collect();
        let lhs = welfare_aggregate(&mid, p, EPS);
        let rhs = t * welfare_aggregate(&a, p, EPS) + (1.0 - t) * welfare_aggregate(&b, p, EPS);
        prop_assert!(lhs >= rhs - 1e-9, "not concave at p={p}: {lhs} < {rhs}");
    }

    #[test]
    fn finite_value_and_gradient_at_zero(h in arb_roster(), p in -8.0f64..=1.0) {
        let mut with_zero = h.clone();
        with_zero[0] = 0.0;
        let w = welfare_aggregate(&with_zero, p, EPS);
        prop_assert!(w.is_finite());
        // A finite one-sided gradient: a small improvement changes welfare
        // by a bounded amount.
        let mut nudged = with_zero.clone();
        nudged[0] = 1e-6;
        let dw = welfare_aggregate(&nudged, p, EPS) - w;
        prop_assert!(dw.is_finite() && (0.0..1.0).contains(&dw));
    }
}

#[test]
fn the_three_pinned_exponents_behave_as_documented() {
    let h = [0.25, 0.5, 1.0];

    // p = 1: the plain average (ε cancels exactly).
    let avg = welfare_aggregate(&h, 1.0, EPS);
    assert!((avg - (0.25 + 0.5 + 1.0) / 3.0).abs() < 1e-12, "{avg}");

    // p = 0: the geometric mean of (h + ε), minus ε.
    let nash = welfare_aggregate(&h, 0.0, EPS);
    let expected = ((0.25f64 + EPS) * (0.5 + EPS) * (1.0 + EPS)).powf(1.0 / 3.0) - EPS;
    assert!((nash - expected).abs() < 1e-12, "{nash} vs {expected}");
    assert!(nash < avg, "Nash is inequality-averse: below the average");

    // p = -8: dominated by the least-happy kitty.
    let maxmin = welfare_aggregate(&h, -8.0, EPS);
    assert!(maxmin < nash);
    assert!(
        (maxmin - 0.25).abs() < 0.15,
        "close to the minimum: {maxmin}"
    );

    // And helping the least-happy kitty moves p=-8 welfare far more than
    // helping the happiest.
    let help_worst = welfare_aggregate(&[0.35, 0.5, 1.0], -8.0, EPS) - maxmin;
    let help_best = welfare_aggregate(&[0.25, 0.5, 1.0], -8.0, EPS) - maxmin;
    assert!(help_worst > 10.0 * help_best.max(1e-15));
}
