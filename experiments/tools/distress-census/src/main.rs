//! Retro-replay with a distress-tick counter (exp-004 §9.2 work).
//!
//! Re-executes historical kitty-eval runs — same artifact bytes, same
//! config, same seeds — through the *same library code path* kitty-eval
//! uses (`harness::run_one_with`), and counts what the original report
//! never recorded: per kitty × need, the total ticks spent at or above
//! the distress threshold, and how many distinct episodes carried them.
//!
//! Because the engine guarantees a run is a pure function of (artifact,
//! config, seed), the counters read off ticks identical to the ones the
//! original evals saw. The proof rides along: every field the original
//! report *did* record (max_distress_age, low_share, welfare, fallbacks)
//! is re-emitted here, and the companion verify step demands they match
//! the committed JSONs exactly — a faithful replay reproduces its past
//! before its new columns are believed.
//!
//! Counting convention: the observer sees the post-tick world, so a tick
//! counts for (kitty, need) when the need sits at/above the threshold
//! after the tick resolves. Episodes are edge-triggered on the same
//! signal (below → at/above), mirroring the engine's own `in_distress`
//! edge rule.

use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

use cloudkitty_core::{BehaviorRegistry, NeedKind};
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::load_configs_from_str;
use cloudkitty_rl::harness::{run_one_with, EvalRequest, RosterMode, RunOutcome};
use serde::Serialize;

#[derive(Serialize, Default, Clone)]
struct NeedCount {
    ticks: u64,
    episodes: u64,
}

#[derive(Serialize)]
struct KittyDistress {
    kitty_id: u32,
    name: String,
    by_need: BTreeMap<&'static str, NeedCount>,
    total_ticks: u64,
    /// Share of the run's ticks this kitty spent with >=1 need in
    /// distress (ticks where *any* need is at/above threshold).
    any_need_ticks: u64,
}

#[derive(Serialize)]
struct RunRecord {
    seed: u64,
    distress: Vec<KittyDistress>,
    /// The full original-shape outcome, for the fidelity check.
    outcome: RunOutcome,
}

#[derive(Serialize)]
struct Output {
    artifact: String,
    subject: String,
    config: String,
    config_sha256: String,
    distress_threshold: f32,
    ticks: u64,
    seeds: Vec<u64>,
    runs: Vec<RunRecord>,
}

fn need_name(kind: NeedKind) -> &'static str {
    match kind {
        NeedKind::Eat => "eat",
        NeedKind::Drink => "drink",
        NeedKind::Sleep => "sleep",
        NeedKind::Play => "play",
        NeedKind::Cuddle => "cuddle",
        NeedKind::Bath => "bath",
    }
}

struct Args {
    artifact: String,
    config: PathBuf,
    seed_start: u64,
    seed_count: u64,
    ticks: u64,
    out: PathBuf,
}

fn parse_args() -> Args {
    let mut artifact = None;
    let mut config = None;
    let mut seed_start = None;
    let mut seed_count = 30u64;
    let mut ticks = 20_000u64;
    let mut out = None;
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--artifact" => artifact = Some(value("--artifact")),
            "--config" => config = Some(PathBuf::from(value("--config"))),
            "--seed-start" => {
                seed_start = Some(value("--seed-start").parse().expect("--seed-start: u64"))
            }
            "--seed-count" => {
                seed_count = value("--seed-count").parse().expect("--seed-count: u64")
            }
            "--ticks" => ticks = value("--ticks").parse().expect("--ticks: u64"),
            "--out" => out = Some(PathBuf::from(value("--out"))),
            other => panic!("unknown flag {other}"),
        }
    }
    Args {
        artifact: artifact.expect("--artifact is required"),
        config: config.expect("--config is required"),
        seed_start: seed_start.expect("--seed-start is required"),
        seed_count,
        ticks,
        out: out.expect("--out is required"),
    }
}

fn main() {
    let args = parse_args();
    let bytes = fs::read(&args.config)
        .unwrap_or_else(|e| panic!("reading {}: {e}", args.config.display()));
    let config_sha256 = cloudkitty_rl::suite::sha256_hex(&bytes);
    let text = String::from_utf8(bytes).expect("config is UTF-8");
    let (core, rl) = load_configs_from_str(&text).expect("config parses and validates");
    let threshold = core.thresholds.distress;

    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = PolicyBehavior::from_artifact_path(&args.artifact, &rl, false)
        .unwrap_or_else(|e| panic!("loading {}: {e:?}", args.artifact));
    let subject = format!("policy:{}", args.artifact);
    registry.register(subject.clone(), std::sync::Arc::new(behavior));

    let seeds: Vec<u64> = (args.seed_start..args.seed_start + args.seed_count).collect();
    let mut runs = Vec::new();
    for &seed in &seeds {
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: Some(&subject),
            roster: RosterMode::AllSubject,
            seed,
            ticks: args.ticks,
        };
        // Counter state, keyed by roster order (stable across the run:
        // Article II, the roster never changes).
        let mut ids: Vec<(u32, String)> = Vec::new();
        let mut ticks_at: Vec<[u64; 6]> = Vec::new();
        let mut episodes: Vec<[u64; 6]> = Vec::new();
        let mut above: Vec<[bool; 6]> = Vec::new();
        let mut any_ticks: Vec<u64> = Vec::new();

        let outcome = run_one_with(&request, |world| {
            if ids.is_empty() {
                for k in &world.kitties {
                    ids.push((k.id, k.name.clone()));
                    ticks_at.push([0; 6]);
                    episodes.push([0; 6]);
                    above.push([false; 6]);
                    any_ticks.push(0);
                }
            }
            for (i, k) in world.kitties.iter().enumerate() {
                let mut any = false;
                for (j, kind) in NeedKind::ALL.into_iter().enumerate() {
                    let hot = k.needs.get(kind) >= threshold;
                    if hot {
                        ticks_at[i][j] += 1;
                        any = true;
                        if !above[i][j] {
                            episodes[i][j] += 1;
                        }
                    }
                    above[i][j] = hot;
                }
                if any {
                    any_ticks[i] += 1;
                }
            }
        });

        let distress = ids
            .iter()
            .enumerate()
            .map(|(i, (id, name))| KittyDistress {
                kitty_id: *id,
                name: name.clone(),
                by_need: NeedKind::ALL
                    .into_iter()
                    .enumerate()
                    .map(|(j, kind)| {
                        (
                            need_name(kind),
                            NeedCount {
                                ticks: ticks_at[i][j],
                                episodes: episodes[i][j],
                            },
                        )
                    })
                    .collect(),
                total_ticks: ticks_at[i].iter().sum(),
                any_need_ticks: any_ticks[i],
            })
            .collect();
        runs.push(RunRecord {
            seed,
            distress,
            outcome,
        });
    }

    if let Some(dir) = args.out.parent() {
        if !dir.as_os_str().is_empty() {
            fs::create_dir_all(dir).expect("creating output directory");
        }
    }
    let output = Output {
        artifact: args.artifact,
        subject,
        config: args.config.display().to_string(),
        config_sha256,
        distress_threshold: threshold,
        ticks: args.ticks,
        seeds,
        runs,
    };
    fs::write(
        &args.out,
        serde_json::to_string_pretty(&output).expect("output serializes") + "\n",
    )
    .expect("writing output");
    let total: u64 = output
        .runs
        .iter()
        .flat_map(|r| r.distress.iter().map(|d| d.total_ticks))
        .sum();
    println!(
        "{}: {} runs, {} distress-ticks total -> {}",
        output.subject,
        output.runs.len(),
        total,
        args.out.display()
    );
}
