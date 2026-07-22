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
use crate::reward::team_welfare_of;
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
        welfare_sum += team_welfare_of(&world.kitties, &config, &request.rl.reward);
        let roster_mean: f64 = world
            .kitties
            .iter()
            .map(|k| {
                crate::reward::unclamped_happiness(&k.needs, &config.happiness.weights) / 100.0
            })
            .sum::<f64>()
            / world.kitties.len().max(1) as f64;
        plain_sum += roster_mean;
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
    pub subject_welfare: f64,
    pub baseline_welfare: f64,
    pub delta: f64,
}

/// Evaluates `subject` and the `needs_driven` baseline over the seed set,
/// pairing per seed.
pub fn paired_against_baseline(
    request: &EvalRequest<'_>,
    seeds: &[u64],
) -> (Vec<RunOutcome>, Vec<RunOutcome>, Vec<PairedDelta>) {
    let mut subject_runs = Vec::with_capacity(seeds.len());
    let mut baseline_runs = Vec::with_capacity(seeds.len());
    let mut deltas = Vec::with_capacity(seeds.len());
    for &seed in seeds {
        let subject = run_one(&EvalRequest {
            seed,
            ..request.clone()
        });
        let baseline = run_one(&EvalRequest {
            seed,
            subject: Some("needs_driven"),
            roster: RosterMode::AllSubject,
            ..request.clone()
        });
        deltas.push(PairedDelta {
            seed,
            subject_welfare: subject.aggregates.team_welfare,
            baseline_welfare: baseline.aggregates.team_welfare,
            delta: subject.aggregates.team_welfare - baseline.aggregates.team_welfare,
        });
        subject_runs.push(subject);
        baseline_runs.push(baseline);
    }
    (subject_runs, baseline_runs, deltas)
}
