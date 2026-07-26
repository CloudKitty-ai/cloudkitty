//! `kitty-eval`: scores any brain against the welfare bar the repository
//! already trusts (spec 014 US3, contracts/evaluation-harness.md), on the
//! budgetless headless path (FR-017).
//!
//! ```text
//! kitty-eval --brain needs_driven | --artifact path/to/policy.ckpolicy
//!            [--config cloudkitty.toml] [--seeds 1,2,...] [--ticks 20000]
//!            [--roster all-policy | mixed | both] [--json out.json]
//! ```
//!
//! Exit codes: 0 success; 1 usage/validation error; 2 nonzero fallback
//! count on a policy scoring run (FR-013 — the run fails rather than
//! reporting the fallback's welfare as the policy's); 3 determinism
//! self-check failure.

use std::process::ExitCode;
use std::sync::Arc;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::Config;
use cloudkitty_rl::cli_support;
use cloudkitty_rl::config::{load_configs_from_path, RlConfig};
use cloudkitty_rl::harness::{EvalRequest, RosterMode, RunOutcome};
use cloudkitty_rl::suite;
use serde::Serialize;

#[derive(Debug)]
struct Args {
    brain: Option<String>,
    artifact: Option<String>,
    config: Option<String>,
    seeds: Option<Vec<u64>>,
    ticks: Option<u64>,
    roster: Option<String>,
    json: Option<String>,
    suite: Option<String>,
    enforce_sign_test: bool,
}

fn parse_args() -> Result<Args, String> {
    let mut args = Args {
        brain: None,
        artifact: None,
        config: None,
        seeds: None,
        ticks: None,
        roster: None,
        json: None,
        suite: None,
        enforce_sign_test: false,
    };
    let mut argv = std::env::args().skip(1);
    while let Some(flag) = argv.next() {
        let mut value = |name: &str| {
            argv.next()
                .ok_or_else(|| format!("{name} requires a value"))
        };
        match flag.as_str() {
            "--brain" => args.brain = Some(value("--brain")?),
            "--artifact" => args.artifact = Some(value("--artifact")?),
            "--config" => args.config = Some(value("--config")?),
            "--ticks" => {
                args.ticks = Some(
                    value("--ticks")?
                        .parse()
                        .map_err(|e| format!("--ticks: {e}"))?,
                )
            }
            "--seeds" => {
                let list = value("--seeds")?;
                let seeds: Result<Vec<u64>, _> =
                    list.split(',').map(|s| s.trim().parse()).collect();
                args.seeds = Some(seeds.map_err(|e| format!("--seeds: {e}"))?);
            }
            "--roster" => args.roster = Some(value("--roster")?),
            "--json" => args.json = Some(value("--json")?),
            "--suite" => args.suite = Some(value("--suite")?),
            // Tighten-only (spec 017 FR-015): promotes the sign test from
            // warn to gate for this run; nothing can loosen a frozen gate.
            "--enforce" => match value("--enforce")?.as_str() {
                "sign-test" => args.enforce_sign_test = true,
                other => return Err(format!("--enforce: unknown check '{other}' (sign-test)")),
            },
            "--help" | "-h" => {
                return Err("usage: kitty-eval --brain NAME | --artifact PATH \
                            [--config cloudkitty.toml] [--seeds 1,2,...] [--ticks 20000] \
                            [--roster all-policy|mixed|both] [--json out.json]\n       \
                            kitty-eval --suite evals/v1 (--brain NAME | --artifact PATH) \
                            [--enforce sign-test] [--json out.json]"
                    .to_string())
            }
            other => return Err(format!("unknown flag {other}")),
        }
    }
    // A suite is a fixed instrument (spec 017 R1): per-exam seeds and ticks
    // are frozen in each exam's own [rl.eval]. Exploration uses --config.
    if args.suite.is_some() {
        for (flag, set) in [
            ("--config", args.config.is_some()),
            ("--seeds", args.seeds.is_some()),
            ("--ticks", args.ticks.is_some()),
            ("--roster", args.roster.is_some()),
        ] {
            if set {
                return Err(format!(
                    "{flag} cannot be combined with --suite: a suite is a fixed instrument; \
                     to explore, point --config at any exam file directly"
                ));
            }
        }
    } else if args.enforce_sign_test {
        return Err("--enforce applies to suite runs only (pass --suite)".to_string());
    }
    Ok(args)
}

#[derive(Serialize)]
struct EvalOutput {
    subject: String,
    ticks: u64,
    seeds: Vec<u64>,
    runs: Vec<RunOutcome>,
    baseline_runs: Vec<RunOutcome>,
    paired: Vec<cloudkitty_rl::harness::PairedDelta>,
}

fn human_report(output: &EvalOutput) {
    let stdout = std::io::stdout();
    human_report_to(&mut stdout.lock(), output).expect("writing report to stdout");
}

/// Writer-based body of [`human_report`], mirroring the suite's shape
/// (spec 018 research D4) so the assembled certification report is
/// capturable in-process.
fn human_report_to(w: &mut dyn std::io::Write, output: &EvalOutput) -> std::io::Result<()> {
    writeln!(
        w,
        "== kitty-eval: {} ({} ticks/seed) ==",
        output.subject, output.ticks
    )?;
    for run in &output.runs {
        cli_support::print_run_panel(w, run, true)?;
    }
    writeln!(w, "-- paired vs needs_driven baseline --")?;
    cli_support::print_paired(w, &output.paired, "baseline", "")?;
    // One aggregate per roster mode: an all-policy score and the mixed
    // deployment reality are different claims and never blend (spec 014
    // review).
    for mode in [RosterMode::AllSubject, RosterMode::Mixed] {
        let deltas: Vec<f64> = output
            .paired
            .iter()
            .filter(|p| p.roster == mode)
            .map(|p| p.delta)
            .collect();
        if !deltas.is_empty() {
            let mean: f64 = deltas.iter().sum::<f64>() / deltas.len() as f64;
            writeln!(
                w,
                "aggregate delta [{mode:?}] {mean:+.4} over {} seeds",
                deltas.len()
            )?;
        }
    }
    Ok(())
}

/// Resolves `--brain`/`--artifact` into a registered subject, returning
/// `(name, is_policy)`. One ladder for both CLI modes (spec 018 FR-001);
/// `bind_candidate` carries the suite mode's extra behavior — registering
/// the subject under the reserved candidate seat name (spec 017 FR-011)
/// with the collision guard. The caller picks the `RlConfig` used for
/// artifact validation: certification mode passes the loaded config, the
/// suite passes defaults (per-exam RlConfigs govern scoring, not loading —
/// the compiled schema constants are global).
fn resolve_subject(
    registry: &mut BehaviorRegistry,
    args: &Args,
    rl: &RlConfig,
    bind_candidate: bool,
) -> Result<(String, bool), ExitCode> {
    match (&args.brain, &args.artifact) {
        (Some(_), Some(_)) | (None, None) => {
            eprintln!("kitty-eval: pass exactly one of --brain or --artifact");
            Err(ExitCode::from(1))
        }
        (Some(brain), None) => {
            let Some(behavior) = registry.get(brain) else {
                let mut names = registry.names();
                names.sort();
                eprintln!(
                    "kitty-eval: unknown brain '{brain}'; must be one of: {}",
                    names.join(", ")
                );
                return Err(ExitCode::from(1));
            };
            if bind_candidate {
                // Alias the built-in as the candidate: the exam machinery
                // never requires a trained artifact (spec 017 SC-007,
                // research.md R4).
                registry.register(suite::CANDIDATE_BEHAVIOR, behavior);
            }
            Ok((brain.clone(), false))
        }
        (None, Some(path)) => {
            match cloudkitty_rl::behavior::PolicyBehavior::from_artifact_path(path, rl) {
                Ok(behavior) => {
                    let behavior: Arc<_> = Arc::new(behavior);
                    let name = format!("policy:{path}");
                    if bind_candidate {
                        // An artifact literally named `candidate` makes
                        // `policy:{path}` collide with the alias; one
                        // registration suffices — the registry panics on
                        // duplicates by design (spec 017 review finding 1).
                        if name != suite::CANDIDATE_BEHAVIOR {
                            registry.register(name.clone(), behavior.clone());
                        }
                        registry.register(suite::CANDIDATE_BEHAVIOR, behavior);
                    } else {
                        registry.register(name.clone(), behavior);
                    }
                    Ok((name, true))
                }
                Err(e) => {
                    eprintln!("kitty-eval: artifact validation failed: {e}");
                    Err(ExitCode::from(1))
                }
            }
        }
    }
}

/// Writes the JSON report (spec 018 FR-005: message preserved verbatim).
fn write_json<T: Serialize>(path: &str, value: &T) -> Result<(), ExitCode> {
    match serde_json::to_string_pretty(value) {
        Ok(json) => {
            if let Err(e) = std::fs::write(path, json) {
                eprintln!("kitty-eval: cannot write {path}: {e}");
                return Err(ExitCode::from(1));
            }
            Ok(())
        }
        Err(e) => {
            eprintln!("kitty-eval: {e}");
            Err(ExitCode::from(1))
        }
    }
}

/// Exit-3 arm shared by both modes: the spec-pinned determinism-failure
/// message (contracts/suite-cli.md), single-sourced like its siblings.
fn determinism_exit(err: suite::SuiteRunError) -> ExitCode {
    let suite::SuiteRunError::Determinism { location, seed } = err;
    eprintln!("kitty-eval: determinism self-check failed on seed {seed} ({location})");
    ExitCode::from(3)
}

/// FR-013 gate, both modes: a policy run that ever took a fallback fails
/// rather than reporting the fallback's welfare as the policy's.
fn fallback_gate(is_policy: bool, fallbacks: u64) -> Option<ExitCode> {
    if is_policy && fallbacks > 0 {
        eprintln!(
            "kitty-eval: {fallbacks} fallback decisions during policy scoring — \
             the run fails rather than reporting the fallback's welfare as the policy's (FR-013)"
        );
        return Some(ExitCode::from(2));
    }
    None
}

/// The suite mode (spec 017): load, verify, score, report. Exit codes per
/// contracts/suite-cli.md — 1 usage/validation, 2 fallback-taken, 3
/// determinism, 4 mixed-roster verdict failure. Mechanical failures
/// dominate the verdict; between them the order follows where they occur:
/// 1 before anything runs, 3 aborts the run at the exam that produced it
/// (fallbacks are judged over the completed report, so a run that fails
/// determinism exits 3 regardless of fallbacks — the measurement is
/// untrustworthy either way, matching the single-config path), 2 over the
/// finished report, 4 last.
fn run_suite(dir: &str, args: &Args) -> ExitCode {
    let mut registry = BehaviorRegistry::with_builtins();
    let (subject_name, is_policy) =
        match resolve_subject(&mut registry, args, &RlConfig::default(), true) {
            Ok(subject) => subject,
            Err(code) => return code,
        };

    let loaded = match suite::load_suite(std::path::Path::new(dir)) {
        Ok(loaded) => loaded,
        Err(e) => {
            eprintln!("kitty-eval: {e}");
            return ExitCode::from(1);
        }
    };
    let subject = suite::SuiteSubject {
        registry: &registry,
        name: &subject_name,
        is_policy,
    };
    let report = match suite::score_suite(&loaded, &subject, args.enforce_sign_test) {
        Ok(report) => report,
        Err(err) => return determinism_exit(err),
    };

    suite::human_report(&report);
    if let Some(path) = &args.json {
        if let Err(code) = write_json(path, &report) {
            return code;
        }
    }

    if let Some(code) = fallback_gate(is_policy, suite::total_fallbacks(&report)) {
        return code;
    }
    if suite::verdict_failed(&report) {
        eprintln!(
            "kitty-eval: the mixed-roster exam failed its verdict — anchored to its own \
             all-scripted baseline, never the default world's bounds (spec 017 FR-010)"
        );
        return ExitCode::from(4);
    }
    ExitCode::SUCCESS
}

fn main() -> ExitCode {
    let args = match parse_args() {
        Ok(args) => args,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(1);
        }
    };

    if let Some(dir) = &args.suite {
        return run_suite(dir, &args);
    }

    let (core, rl): (Config, RlConfig) = match &args.config {
        Some(path) => match load_configs_from_path(path) {
            Ok(pair) => pair,
            Err(e) => {
                eprintln!("kitty-eval: {e}");
                return ExitCode::from(1);
            }
        },
        None => (Config::default(), RlConfig::default()),
    };
    let mut registry = BehaviorRegistry::with_builtins();

    // Resolve the subject: a built-in name, or a policy artifact loaded
    // through the same validation as server startup (US4).
    let (subject_name, is_policy) = match resolve_subject(&mut registry, &args, &rl, false) {
        Ok(subject) => subject,
        Err(code) => return code,
    };
    let seeds = args.seeds.unwrap_or_else(|| rl.eval.seeds.clone());
    let ticks = args.ticks.unwrap_or(rl.eval.ticks);

    // Policy scoring runs both roster modes by default (FR-013); built-in
    // scoring defaults to all-subject.
    let modes: Vec<RosterMode> = match (args.roster.as_deref().unwrap_or("both"), is_policy) {
        ("all-policy", _) => vec![RosterMode::AllSubject],
        ("mixed", _) => vec![RosterMode::Mixed],
        ("both", true) => vec![RosterMode::AllSubject, RosterMode::Mixed],
        ("both", false) => vec![RosterMode::AllSubject],
        (other, _) => {
            eprintln!("kitty-eval: unknown --roster '{other}' (all-policy | mixed | both)");
            return ExitCode::from(1);
        }
    };

    // The scoring sequence — baseline once, per-mode runs, first-seed
    // determinism self-check, pairing — is the library's single
    // implementation (spec 018 FR-004), shared with the suite's standard
    // exams.
    let base = EvalRequest {
        core: &core,
        rl: &rl,
        registry: &registry,
        subject: Some(&subject_name),
        roster: RosterMode::AllSubject,
        seed: 0,
        ticks,
    };
    let sweep = match cli_support::run_subject_over_modes(&base, &modes, &seeds, |mode| {
        format!("{mode:?}")
    }) {
        Ok(sweep) => sweep,
        Err(err) => return determinism_exit(err),
    };

    let output = EvalOutput {
        subject: subject_name,
        ticks,
        seeds,
        runs: sweep.runs,
        baseline_runs: sweep.baseline_runs,
        paired: sweep.paired,
    };
    human_report(&output);
    if let Some(path) = &args.json {
        if let Err(code) = write_json(path, &output) {
            return code;
        }
    }

    let total_fallbacks: u64 = output.runs.iter().map(|r| r.fallback_count).sum();
    if let Some(code) = fallback_gate(is_policy, total_fallbacks) {
        return code;
    }
    ExitCode::SUCCESS
}
