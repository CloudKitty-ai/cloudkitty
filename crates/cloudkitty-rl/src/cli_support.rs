//! CLI support: the shared rendering and orchestration surface behind
//! `kitty-eval`'s two modes (spec 018).
//!
//! **Standing** (contracts/cli-support.md): internal plumbing for the
//! certification CLI, *not* a stability promise. This module exists so the
//! binary and the suite render and orchestrate through one implementation;
//! its signatures may change whenever both consumers move together. Future
//! promotions for the CLI's benefit join this module rather than scattering
//! `pub` elsewhere (owner ruling, spec 018 Clarifications 2026-07-26).

use std::io::{self, Write};

use crate::harness::{pair_runs, run_many, EvalRequest, PairedDelta, RosterMode, RunOutcome};
use crate::suite::SuiteRunError;

/// The result of sweeping one subject across roster modes: the
/// mode-independent baseline, every mode's runs in mode order, and the
/// paired deltas against the baseline.
pub struct ModeSweep {
    pub baseline_runs: Vec<RunOutcome>,
    pub runs: Vec<RunOutcome>,
    pub paired: Vec<PairedDelta>,
}

/// The baseline-once / per-mode / first-seed-self-checked / paired scoring
/// sequence — the one implementation (spec 018 FR-004) behind both the
/// suite's standard exams and certification mode (single-config).
/// `location` names the failing context for a determinism error in each
/// caller's own words.
pub fn run_subject_over_modes(
    base: &EvalRequest<'_>,
    modes: &[RosterMode],
    seeds: &[u64],
    location: impl Fn(RosterMode) -> String,
) -> Result<ModeSweep, SuiteRunError> {
    // The baseline is mode-independent, computed once (spec 014 review).
    let baseline_runs = run_many(&base.baseline(), seeds);
    let mut runs = Vec::new();
    let mut paired = Vec::new();
    for mode in modes {
        let request = EvalRequest {
            roster: *mode,
            ..base.clone()
        };
        let subject_runs = run_many(&request, seeds);
        // Determinism self-check, per roster mode: mixed dispatch is a
        // different code path and deserves its own re-run (spec 014 second
        // review) — the first seed, repeated, must agree with itself
        // exactly.
        if let Some(first) = seeds.first() {
            crate::suite::self_check(
                &EvalRequest {
                    seed: *first,
                    ..request.clone()
                },
                &subject_runs[0],
                location(*mode),
            )?;
        }
        paired.extend(pair_runs(&subject_runs, &baseline_runs));
        runs.extend(subject_runs);
    }
    Ok(ModeSweep {
        baseline_runs,
        runs,
        paired,
    })
}

/// One run's panel: header, per-kitty welfare lines, max distress age,
/// optionally the default-world welfare-bounds verdict, fallback lines.
///
/// `default_world_bounds` is the single deliberate divergence between the
/// CLI's two modes (spec 018 FR-002): certification mode (single-config)
/// passes `true` and gets the PASS / BOUND VIOLATED block; the suite passes
/// `false` — deliberately no "welfare bounds" verdict line there, because
/// those bounds are the default world's, and a suite exam is not the
/// default world (spec 017 FR-003, research R11).
pub fn print_run_panel(
    w: &mut dyn Write,
    run: &RunOutcome,
    default_world_bounds: bool,
) -> io::Result<()> {
    writeln!(
        w,
        "seed {} [{:?}]: team welfare {:.4}, plain mean {:.4}, least-happy mean {:.1}, fallbacks {}",
        run.seed,
        run.roster,
        run.aggregates.team_welfare,
        run.aggregates.plain_mean,
        run.aggregates.least_happy_mean,
        run.fallback_count
    )?;
    for kitty in &run.report.kitties {
        writeln!(
            w,
            "  {:<10} mean {:>5.1}  low-share {:>5.2}%  longest-low {:>3}  floor {}",
            kitty.name,
            kitty.mean_happiness,
            kitty.low_share * 100.0,
            kitty.max_low_streak,
            kitty.floor_touches
        )?;
    }
    // The census line (spec 028): one row, only what is nonzero. Printed
    // BEFORE the distress-age line, whose position anchors the panel's
    // certification bounds-block contract.
    let census: Vec<String> = run
        .report
        .distress_census
        .iter()
        .filter(|k| !k.by_need.is_empty())
        .map(|k| {
            let parts: Vec<String> = k
                .by_need
                .iter()
                .map(|(need, c)| format!("{need} {}t/{}e", c.ticks, c.episodes))
                .collect();
            format!("{} [{}]", k.name, parts.join(", "))
        })
        .collect();
    if census.is_empty() {
        writeln!(w, "  distress census clean")?;
    } else {
        writeln!(w, "  distress census {}", census.join("; "))?;
    }
    writeln!(w, "  max distress age {}", run.report.max_distress_age)?;
    if default_world_bounds {
        let violations = run.report.violations();
        if violations.is_empty() {
            writeln!(w, "  welfare bounds: PASS")?;
        } else {
            for violation in &violations {
                writeln!(w, "  BOUND VIOLATED: {violation}")?;
            }
        }
    }
    for fallback in &run.fallbacks {
        writeln!(
            w,
            "  FALLBACK: kitty {} took {} fallback decisions (first at ticks {:?})",
            fallback.kitty_id, fallback.count, fallback.first_ticks
        )?;
    }
    Ok(())
}

/// The selection stamp fragment appended wherever the subject is named
/// (issue #70; SC-004 amendment 2026-07-29): `" (greedy selection)"`,
/// `" (sampled selection)"`, or nothing for built-in subjects. One
/// implementation so the two report modes cannot drift.
pub fn selection_note(selection: Option<&str>) -> String {
    selection
        .map(|s| format!(" ({s} selection)"))
        .unwrap_or_default()
}

/// Paired subject-vs-baseline delta lines. `prefix` preserves the two
/// modes' byte streams (`"  "` in the suite report, `""` in certification
/// mode); `baseline_label` names the comparison roster. `selection` stamps
/// every line with the subject's selection mode — each paired line is a
/// quotable certification line and must carry its own distribution label
/// (issue #70); built-ins pass `None` and their bytes are unchanged.
pub fn print_paired(
    w: &mut dyn Write,
    paired: &[PairedDelta],
    baseline_label: &str,
    prefix: &str,
    selection: Option<&str>,
) -> io::Result<()> {
    let note = selection_note(selection);
    for pair in paired {
        writeln!(
            w,
            "{prefix}seed {} [{:?}]: subject{note} {:.4} vs {baseline_label} {:.4} (delta {:+.4})",
            pair.seed, pair.roster, pair.subject_welfare, pair.baseline_welfare, pair.delta
        )?;
    }
    Ok(())
}
