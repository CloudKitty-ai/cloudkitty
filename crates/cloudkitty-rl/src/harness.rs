//! The evaluation runner behind `kitty-eval` (spec 014 FR-013, US3):
//! budgetless headless runs (FR-017) scored with the shared welfare module,
//! so the CI gate and the scorecard are the same code.

use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::seam::{drive_tick, Provenance};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use serde::Serialize;

use crate::config::RlConfig;
use crate::reward::roster_welfare;
use crate::welfare::{WelfareAccumulator, WelfareReport};

/// Which kitties the scored subject drives.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RosterMode {
    /// Every kitty runs the subject.
    AllSubject,
    /// The deployment reality: the first kitty runs the subject, everyone
    /// else runs `needs_driven`.
    Mixed,
}

/// One evaluation run request. `subject` names a registered behavior (a
/// built-in, or a policy behavior registered by the caller — US4).
#[derive(Clone)]
pub struct EvalRequest<'a> {
    pub core: &'a Config,
    pub rl: &'a RlConfig,
    pub registry: &'a BehaviorRegistry,
    /// The behavior name under evaluation; None scores the config's own
    /// roster unchanged (the welfare suite's exact scenario).
    pub subject: Option<&'a str>,
    pub roster: RosterMode,
    pub seed: u64,
    pub ticks: u64,
}

impl<'a> EvalRequest<'a> {
    /// The one definition of the comparison baseline (FR-013): the same
    /// evaluation with the all-`needs_driven` roster.
    pub fn baseline(&self) -> EvalRequest<'a> {
        EvalRequest {
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            ..self.clone()
        }
    }
}

/// Aggregates reported beside the scorecard (FR-013): the configured
/// team-welfare aggregate with the plain mean and the least-happy kitty's
/// mean beside it — fairness visible, not just scored.
#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct WelfareAggregates {
    /// Mean over ticks of the configured power-mean welfare (Nash default).
    pub team_welfare: f64,
    /// Mean over ticks and kitties of normalized happiness.
    pub plain_mean: f64,
    /// The least-happy kitty's mean happiness (0..100).
    pub least_happy_mean: f64,
}

/// One kitty's fallback accounting: which kitty, how many decisions, and
/// the first few ticks it happened (FR-013: the report says which and when).
#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct FallbackRecord {
    pub kitty_id: KittyId,
    pub count: u64,
    pub first_ticks: Vec<u64>,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct RunOutcome {
    pub seed: u64,
    pub ticks: u64,
    pub roster: RosterMode,
    pub report: WelfareReport,
    pub aggregates: WelfareAggregates,
    /// Total fallback-taken decisions across the run.
    pub fallback_count: u64,
    pub fallbacks: Vec<FallbackRecord>,
}

/// Runs one seeded, budgetless, behavior-driven evaluation.
pub fn run_one(request: &EvalRequest<'_>) -> RunOutcome {
    run_one_with(request, |_| {})
}

/// `run_one` with a per-tick observer: called once per completed tick with
/// the post-tick world (spec 017 R6 — suite-side metrics like
/// duet-participation shares ride here, so the shared welfare module and
/// the run loop stay single-sourced).
pub fn run_one_with(request: &EvalRequest<'_>, mut observer: impl FnMut(&World)) -> RunOutcome {
    let mut config = request.core.clone();
    config.world.seed = request.seed;
    if let Some(subject) = request.subject {
        for (index, kitty) in config.kitties.iter_mut().enumerate() {
            kitty.behavior = match request.roster {
                RosterMode::AllSubject => subject.to_string(),
                RosterMode::Mixed if index == 0 => subject.to_string(),
                RosterMode::Mixed => "needs_driven".to_string(),
            };
        }
    }
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let mut accumulator = WelfareAccumulator::new(&world, &config);
    let mut welfare_sum = 0.0f64;
    let mut plain_sum = 0.0f64;
    let mut fallback_count = 0u64;
    let mut fallbacks: std::collections::BTreeMap<KittyId, FallbackRecord> = Default::default();

    for _ in 0..request.ticks {
        let driven = drive_tick(&mut world, request.registry, &config);
        for record in &driven.report.records {
            if record.provenance == Provenance::FallbackTaken {
                fallback_count += 1;
                let entry = fallbacks.entry(record.kitty_id).or_insert(FallbackRecord {
                    kitty_id: record.kitty_id,
                    count: 0,
                    first_ticks: Vec::new(),
                });
                entry.count += 1;
                if entry.first_ticks.len() < 10 {
                    entry.first_ticks.push(world.tick.saturating_sub(1));
                }
            }
        }
        accumulator.observe(&world);
        let (welfare, plain) = roster_welfare(&world.kitties, &config, &request.rl.reward);
        welfare_sum += welfare;
        plain_sum += plain;
        observer(&world);
    }

    let report = accumulator.report();
    let least_happy_mean = report
        .kitties
        .iter()
        .map(|k| k.mean_happiness)
        .fold(f64::INFINITY, f64::min);
    let ticks = request.ticks.max(1) as f64;

    RunOutcome {
        seed: request.seed,
        ticks: request.ticks,
        roster: request.roster,
        report,
        aggregates: WelfareAggregates {
            team_welfare: welfare_sum / ticks,
            plain_mean: plain_sum / ticks,
            least_happy_mean: if least_happy_mean.is_finite() {
                least_happy_mean
            } else {
                0.0
            },
        },
        fallback_count,
        fallbacks: fallbacks.into_values().collect(),
    }
}

/// A paired same-seed comparison against a baseline (FR-013).
#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct PairedDelta {
    pub seed: u64,
    /// Which roster mode the subject ran (the baseline is always the
    /// all-`needs_driven` roster).
    pub roster: RosterMode,
    pub subject_welfare: f64,
    pub baseline_welfare: f64,
    pub delta: f64,
}

/// Evaluates the subject over the seed set (one run per seed).
pub fn run_many(request: &EvalRequest<'_>, seeds: &[u64]) -> Vec<RunOutcome> {
    seeds
        .iter()
        .map(|&seed| {
            run_one(&EvalRequest {
                seed,
                ..request.clone()
            })
        })
        .collect()
}

/// Pairs subject runs against baseline runs seed by seed.
pub fn pair_runs(subjects: &[RunOutcome], baselines: &[RunOutcome]) -> Vec<PairedDelta> {
    subjects
        .iter()
        .zip(baselines)
        .map(|(subject, baseline)| {
            debug_assert_eq!(subject.seed, baseline.seed, "pairing is per seed");
            PairedDelta {
                seed: subject.seed,
                roster: subject.roster,
                subject_welfare: subject.aggregates.team_welfare,
                baseline_welfare: baseline.aggregates.team_welfare,
                delta: subject.aggregates.team_welfare - baseline.aggregates.team_welfare,
            }
        })
        .collect()
}

/// Evaluates `subject` and the `needs_driven` baseline over the seed set,
/// pairing per seed.
pub fn paired_against_baseline(
    request: &EvalRequest<'_>,
    seeds: &[u64],
) -> (Vec<RunOutcome>, Vec<RunOutcome>, Vec<PairedDelta>) {
    let subject_runs = run_many(request, seeds);
    let baseline_runs = run_many(&request.baseline(), seeds);
    let deltas = pair_runs(&subject_runs, &baseline_runs);
    (subject_runs, baseline_runs, deltas)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::RlConfig;

    #[test]
    fn the_observer_fires_once_per_completed_tick() {
        let core = Config::default();
        let rl = RlConfig::default();
        let registry = BehaviorRegistry::with_builtins();
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            seed: 7,
            ticks: 25,
        };
        let mut seen = Vec::new();
        let observed = run_one_with(&request, |world| seen.push(world.tick));
        assert_eq!(seen.len(), 25, "one observation per tick");
        assert!(
            seen.windows(2).all(|w| w[0] < w[1]),
            "the observer sees an advancing world"
        );
        // The observer is pure observation: the outcome is the plain run's.
        assert_eq!(observed, run_one(&request));
    }
}
