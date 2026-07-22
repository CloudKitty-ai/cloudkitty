//! Paired-comparison stability (spec 014 US3, T036): repeat runs of the
//! same paired evaluation are identical — the budgetless path has no clock
//! to wander (FR-017).

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::harness::{paired_against_baseline, EvalRequest, RosterMode};

#[test]
fn the_paired_comparison_is_stable_across_repeat_runs() {
    let core = Config::default();
    let rl = RlConfig::default();
    let registry = BehaviorRegistry::with_builtins();
    let seeds = [3u64, 4, 5];

    let run = || {
        paired_against_baseline(
            &EvalRequest {
                core: &core,
                rl: &rl,
                registry: &registry,
                subject: Some("playful"),
                roster: RosterMode::AllSubject,
                seed: 0,
                ticks: 800,
            },
            &seeds,
        )
    };

    let (subject_a, baseline_a, deltas_a) = run();
    let (subject_b, baseline_b, deltas_b) = run();
    assert_eq!(subject_a, subject_b, "subject runs identical");
    assert_eq!(baseline_a, baseline_b, "baseline runs identical");
    assert_eq!(deltas_a, deltas_b, "paired deltas identical");

    // The pairing is per seed, and both sides of each pair share it.
    for (delta, &seed) in deltas_a.iter().zip(&seeds) {
        assert_eq!(delta.seed, seed);
        assert!(
            (delta.subject_welfare - delta.baseline_welfare - delta.delta).abs() < 1e-12,
            "delta arithmetic holds"
        );
    }
}
