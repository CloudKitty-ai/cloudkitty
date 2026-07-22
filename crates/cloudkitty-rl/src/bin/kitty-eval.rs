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
use cloudkitty_rl::config::{load_configs_from_path, RlConfig};
use cloudkitty_rl::harness::{paired_against_baseline, EvalRequest, RosterMode, RunOutcome};
use serde::Serialize;

#[derive(Debug)]
struct Args {
    brain: Option<String>,
    artifact: Option<String>,
    config: Option<String>,
    seeds: Option<Vec<u64>>,
    ticks: Option<u64>,
    roster: String,
    json: Option<String>,
}

fn parse_args() -> Result<Args, String> {
    let mut args = Args {
        brain: None,
        artifact: None,
        config: None,
        seeds: None,
        ticks: None,
        roster: "both".to_string(),
        json: None,
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
            "--roster" => args.roster = value("--roster")?,
            "--json" => args.json = Some(value("--json")?),
            "--help" | "-h" => {
                return Err("usage: kitty-eval --brain NAME | --artifact PATH \
                            [--config cloudkitty.toml] [--seeds 1,2,...] [--ticks 20000] \
                            [--roster all-policy|mixed|both] [--json out.json]"
                    .to_string())
            }
            other => return Err(format!("unknown flag {other}")),
        }
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
    println!(
        "== kitty-eval: {} ({} ticks/seed) ==",
        output.subject, output.ticks
    );
    for run in &output.runs {
        println!(
            "seed {} [{:?}]: team welfare {:.4}, plain mean {:.4}, least-happy mean {:.1}, \
             fallbacks {}",
            run.seed,
            run.roster,
            run.aggregates.team_welfare,
            run.aggregates.plain_mean,
            run.aggregates.least_happy_mean,
            run.fallback_count
        );
        for kitty in &run.report.kitties {
            println!(
                "  {:<10} mean {:>5.1}  low-share {:>5.2}%  longest-low {:>3}  floor {}",
                kitty.name,
                kitty.mean_happiness,
                kitty.low_share * 100.0,
                kitty.max_low_streak,
                kitty.floor_touches
            );
        }
        println!("  max distress age {}", run.report.max_distress_age);
        let violations = run.report.violations();
        if violations.is_empty() {
            println!("  welfare bounds: PASS");
        } else {
            for violation in &violations {
                println!("  BOUND VIOLATED: {violation}");
            }
        }
        for fallback in &run.fallbacks {
            println!(
                "  FALLBACK: kitty {} took {} fallback decisions (first at ticks {:?})",
                fallback.kitty_id, fallback.count, fallback.first_ticks
            );
        }
    }
    println!("-- paired vs needs_driven baseline --");
    for pair in &output.paired {
        println!(
            "seed {}: subject {:.4} vs baseline {:.4} (delta {:+.4})",
            pair.seed, pair.subject_welfare, pair.baseline_welfare, pair.delta
        );
    }
    let mean_delta: f64 =
        output.paired.iter().map(|p| p.delta).sum::<f64>() / output.paired.len().max(1) as f64;
    println!(
        "aggregate delta {mean_delta:+.4} over {} seeds",
        output.paired.len()
    );
}

fn main() -> ExitCode {
    let args = match parse_args() {
        Ok(args) => args,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(1);
        }
    };

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
    let seeds = args.seeds.unwrap_or_else(|| rl.eval.seeds.clone());
    let ticks = args.ticks.unwrap_or(rl.eval.ticks);
    let mut registry = BehaviorRegistry::with_builtins();

    // Resolve the subject: a built-in name, or a policy artifact loaded
    // through the same validation as server startup (US4).
    let (subject_name, is_policy) = match (&args.brain, &args.artifact) {
        (Some(_), Some(_)) | (None, None) => {
            eprintln!("kitty-eval: pass exactly one of --brain or --artifact");
            return ExitCode::from(1);
        }
        (Some(brain), None) => {
            if registry.get(brain).is_none() {
                let mut names = registry.names();
                names.sort();
                eprintln!(
                    "kitty-eval: unknown brain '{brain}'; must be one of: {}",
                    names.join(", ")
                );
                return ExitCode::from(1);
            }
            (brain.clone(), false)
        }
        (None, Some(path)) => {
            match cloudkitty_rl::behavior::PolicyBehavior::from_artifact_path(path, &rl) {
                Ok(behavior) => {
                    let name = format!("policy:{path}");
                    registry.register(name.clone(), Arc::new(behavior));
                    (name, true)
                }
                Err(e) => {
                    eprintln!("kitty-eval: artifact validation failed: {e}");
                    return ExitCode::from(1);
                }
            }
        }
    };

    // Policy scoring runs both roster modes by default (FR-013); built-in
    // scoring defaults to all-subject.
    let modes: Vec<RosterMode> = match (args.roster.as_str(), is_policy) {
        ("all-policy", _) => vec![RosterMode::AllSubject],
        ("mixed", _) => vec![RosterMode::Mixed],
        ("both", true) => vec![RosterMode::AllSubject, RosterMode::Mixed],
        ("both", false) => vec![RosterMode::AllSubject],
        (other, _) => {
            eprintln!("kitty-eval: unknown --roster '{other}' (all-policy | mixed | both)");
            return ExitCode::from(1);
        }
    };

    let mut runs = Vec::new();
    let mut baseline_runs = Vec::new();
    let mut paired = Vec::new();
    for mode in &modes {
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some(&subject_name),
            roster: *mode,
            seed: 0,
            ticks,
        };
        let (mut s, mut b, mut d) = paired_against_baseline(&request, &seeds);
        // Determinism self-check: the first seed, repeated, must agree with
        // itself exactly.
        if let Some(first) = seeds.first() {
            let again = cloudkitty_rl::harness::run_one(&EvalRequest {
                seed: *first,
                ..request.clone()
            });
            if again != s[0] {
                eprintln!("kitty-eval: determinism self-check failed on seed {first}");
                return ExitCode::from(3);
            }
        }
        runs.append(&mut s);
        baseline_runs.append(&mut b);
        paired.append(&mut d);
    }

    let output = EvalOutput {
        subject: subject_name,
        ticks,
        seeds,
        runs,
        baseline_runs,
        paired,
    };
    human_report(&output);
    if let Some(path) = &args.json {
        match serde_json::to_string_pretty(&output) {
            Ok(json) => {
                if let Err(e) = std::fs::write(path, json) {
                    eprintln!("kitty-eval: cannot write {path}: {e}");
                    return ExitCode::from(1);
                }
            }
            Err(e) => {
                eprintln!("kitty-eval: {e}");
                return ExitCode::from(1);
            }
        }
    }

    let total_fallbacks: u64 = output.runs.iter().map(|r| r.fallback_count).sum();
    if is_policy && total_fallbacks > 0 {
        eprintln!(
            "kitty-eval: {total_fallbacks} fallback decisions during policy scoring — \
             the run fails rather than reporting the fallback's welfare as the policy's (FR-013)"
        );
        return ExitCode::from(2);
    }
    ExitCode::SUCCESS
}
