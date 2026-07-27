//! The counterfactual twin probe (exp-001 prereg §6).
//!
//! Measures the environment's credit horizon: run a behavior-driven world to
//! a substitution tick t, clone it, replace exactly one kitty's proposal
//! with idle in the twin, then run both forward under live behaviors and
//! record the signed divergence of the team reward and per-kitty happiness.
//!
//! Two engine guarantees make the measurement exact: bit-identical replay
//! (`DrivenTick::proposals` fed to `tick_with_proposals` reproduces the tick
//! byte-for-byte, SC-001), and the state-independent RNG draw shape (FR-002),
//! which keeps the twins' random streams synchronized after they diverge —
//! every difference is causally attributable to the one substitution.
//!
//! Methodology notes (see exp-001 prereg §6 and §10.2):
//! - Report the *signed* diff; the systematic credit signal is the
//!   across-sample mean of signed traces (chaotic diffusion averages out).
//! - A substitution whose applied action equals the base's is a degenerate
//!   sample (duration enforcement rewrote both, twins are bit-identical
//!   forever): skipped and counted. The skip rate itself measures the
//!   density of genuine decision points.
//! - `--only-action <classes>` (comma-separated wire names) oversamples rare
//!   action classes: the substituted kitty is chosen among those whose base
//!   applied action matches, and non-matching ticks are skipped before the
//!   trace is paid for. Filtered skips are counted separately from
//!   degenerates and excluded from the decision-point density.
//! - `--quiet` suppresses the carriage-return progress line (which pollutes
//!   captured output); the summary and shortfall warning still print.

use std::collections::BTreeMap;
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::sync::Arc;

use cloudkitty_core::seam::{drive_tick, JointProposal, ProposalEntry};
use cloudkitty_core::{Action, BehaviorRegistry, Config, KittyId, World};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::episode::action_wire_name;
use cloudkitty_rl::reward::{team_reward, unclamped_happiness};
use serde::Serialize;

#[derive(Serialize)]
struct SampleRecord {
    schema: u32,
    config: String,
    world_seed: u64,
    /// The substitution tick (world tick at which the twin's proposal for
    /// `kitty_id` was replaced with idle).
    t: u64,
    kitty_id: KittyId,
    base_applied: &'static str,
    twin_applied: &'static str,
    /// Signed team-reward diff (base − twin), index k = ticks since the
    /// substitution tick inclusive (k = 0 is the substitution tick itself).
    dr: Vec<f64>,
    /// Signed per-kitty unclamped-happiness diff (base − twin), same axis.
    dh: BTreeMap<KittyId, Vec<f64>>,
}

#[derive(Serialize)]
struct Summary {
    valid_samples: usize,
    degenerate_skipped: usize,
    /// Attempts skipped because no kitty's applied action matched
    /// `--only-action` that tick. Not decision-point evidence, so excluded
    /// from `decision_point_density`.
    filtered_out: usize,
    attempts: usize,
    decision_point_density: f64,
    only_action: Vec<String>,
    config: String,
    world_seeds: Vec<u64>,
    t_min: u64,
    t_max: u64,
    trace_len: usize,
    probe_seed: u64,
    out: String,
}

/// SplitMix64: the probe's own deterministic sampling stream, fully
/// separate from any engine RNG.
struct SplitMix(u64);

impl SplitMix {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    fn below(&mut self, n: u64) -> u64 {
        self.next() % n
    }
}

struct Args {
    config: PathBuf,
    seeds: Vec<u64>,
    samples: usize,
    t_min: u64,
    t_max: u64,
    trace_len: usize,
    probe_seed: u64,
    out: PathBuf,
    /// Wire names to oversample; empty = accept every action class.
    only_action: Vec<String>,
    quiet: bool,
}

/// Every wire name `action_wire_name` can produce; guards `--only-action`
/// against typos that would otherwise filter out every sample silently.
const WIRE_NAMES: [&str; 11] = [
    "move", "rest", "sleep", "groom", "eat", "drink", "chase", "play", "purr", "meow", "idle",
];

fn parse_args() -> Args {
    let mut args = Args {
        config: PathBuf::from("training.toml"),
        seeds: vec![101, 102, 103],
        samples: 60,
        t_min: 100,
        t_max: 1100,
        trace_len: 600,
        probe_seed: 42,
        out: PathBuf::from("twin-probe.jsonl"),
        only_action: Vec::new(),
        quiet: false,
    };
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--config" => args.config = PathBuf::from(value("--config")),
            "--seeds" => {
                args.seeds = value("--seeds")
                    .split(',')
                    .map(|s| s.trim().parse().expect("--seeds: u64 list"))
                    .collect()
            }
            "--samples" => args.samples = value("--samples").parse().expect("--samples: usize"),
            "--t-min" => args.t_min = value("--t-min").parse().expect("--t-min: u64"),
            "--t-max" => args.t_max = value("--t-max").parse().expect("--t-max: u64"),
            "--trace-len" => {
                args.trace_len = value("--trace-len").parse().expect("--trace-len: usize")
            }
            "--probe-seed" => {
                args.probe_seed = value("--probe-seed").parse().expect("--probe-seed: u64")
            }
            "--out" => args.out = PathBuf::from(value("--out")),
            "--only-action" => {
                args.only_action = value("--only-action")
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .collect()
            }
            "--quiet" => args.quiet = true,
            other => panic!("unknown flag {other}"),
        }
    }
    assert!(args.t_min < args.t_max, "--t-min must be below --t-max");
    assert!(
        !args.seeds.is_empty(),
        "--seeds must name at least one seed"
    );
    for name in &args.only_action {
        assert!(
            WIRE_NAMES.contains(&name.as_str()),
            "--only-action: unknown action class {name:?} (expected one of {WIRE_NAMES:?})"
        );
    }
    args
}

/// Appends one tick's signed diffs to the traces. Kitties are matched by id
/// across the two snapshots; the roster is identical by construction
/// (Article II: it never changes).
fn record_diff(
    base: &World,
    twin: &World,
    core: &Config,
    rl: &RlConfig,
    dr: &mut Vec<f64>,
    dh: &mut BTreeMap<KittyId, Vec<f64>>,
) {
    let bs = base.snapshot();
    let ts = twin.snapshot();
    dr.push(team_reward(&bs, core, &rl.reward) - team_reward(&ts, core, &rl.reward));
    let weights = &core.happiness.weights;
    for bk in &bs.kitties {
        let tk = ts
            .kitties
            .iter()
            .find(|k| k.id == bk.id)
            .expect("twin roster matches base roster");
        let diff =
            unclamped_happiness(&bk.needs, weights) - unclamped_happiness(&tk.needs, weights);
        dh.entry(bk.id).or_default().push(diff);
    }
}

fn main() {
    let args = parse_args();
    let text = fs::read_to_string(&args.config)
        .unwrap_or_else(|e| panic!("reading {}: {e}", args.config.display()));
    let base_cfg: Config = toml::from_str(&text).expect("config parses as engine TOML");
    base_cfg
        .validate()
        .expect("config passes engine validation");
    let rl = RlConfig::from_toml_str(&text).expect("[rl] blocks parse and validate");
    let registry = BehaviorRegistry::with_builtins();

    if let Some(dir) = args.out.parent() {
        if !dir.as_os_str().is_empty() {
            fs::create_dir_all(dir).expect("creating output directory");
        }
    }
    let mut out = fs::File::create(&args.out)
        .unwrap_or_else(|e| panic!("creating {}: {e}", args.out.display()));

    let mut rng = SplitMix(args.probe_seed);
    let mut valid = 0usize;
    let mut degenerate = 0usize;
    let mut filtered = 0usize;
    let mut attempts = 0usize;
    // Rejection sampling against a rare action class burns attempts on
    // filtered ticks; give the filtered path a much longer leash.
    let max_attempts = args.samples * if args.only_action.is_empty() { 6 } else { 200 };

    while valid < args.samples && attempts < max_attempts {
        attempts += 1;
        let world_seed = args.seeds[(attempts - 1) % args.seeds.len()];
        let t = args.t_min + rng.below(args.t_max - args.t_min);

        let mut cfg = base_cfg.clone();
        cfg.world.seed = world_seed;
        let config = Arc::new(cfg);
        let mut base = World::generate(&config);
        let kitty_ids: Vec<KittyId> = base.snapshot().kitties.iter().map(|k| k.id).collect();
        let kitty = kitty_ids[rng.below(kitty_ids.len() as u64) as usize];

        for _ in 0..t {
            let _ = drive_tick(&mut base, &registry, &config);
        }

        // Branch: clone before the substitution tick, then take that tick on
        // both sides — base behavior-driven, twin via the seam with exactly
        // one proposal replaced. The parity guarantee makes the substitution
        // the twins' only difference.
        let mut twin = base.clone();
        let driven = drive_tick(&mut base, &registry, &config);

        // With a class filter, re-choose the substituted kitty among those
        // whose applied action matched this tick (the pre-drawn `kitty` keeps
        // the unfiltered path's draw sequence unchanged). Skipping here is
        // cheap: the 2×trace_len forward ticks were never paid for.
        let kitty = if args.only_action.is_empty() {
            kitty
        } else {
            let candidates: Vec<KittyId> = kitty_ids
                .iter()
                .copied()
                .filter(|id| {
                    driven.report.record(*id).is_some_and(|rec| {
                        args.only_action
                            .iter()
                            .any(|n| n == action_wire_name(&rec.applied))
                    })
                })
                .collect();
            match candidates.len() {
                0 => {
                    filtered += 1;
                    continue;
                }
                n => candidates[rng.below(n as u64) as usize],
            }
        };

        let mut subbed = JointProposal::new();
        for id in driven.proposals.ids() {
            match driven.proposals.get(id) {
                Some(ProposalEntry::Action(a)) if id == kitty => {
                    let _ = a;
                    subbed.propose(id, Action::Idle);
                }
                Some(ProposalEntry::Action(a)) => subbed.propose(id, *a),
                Some(ProposalEntry::Malformed) => subbed.propose_malformed(id),
                None => {}
            }
        }
        let twin_report = twin.tick_with_proposals(&subbed, &config);

        let base_rec = driven.report.record(kitty).expect("kitty is in the roster");
        let twin_rec = twin_report.record(kitty).expect("kitty is in the roster");
        if base_rec.applied == twin_rec.applied {
            degenerate += 1;
            continue;
        }

        let mut dr = Vec::with_capacity(args.trace_len);
        let mut dh: BTreeMap<KittyId, Vec<f64>> = BTreeMap::new();
        record_diff(&base, &twin, &config, &rl, &mut dr, &mut dh);
        for _ in 1..args.trace_len {
            let _ = drive_tick(&mut base, &registry, &config);
            let _ = drive_tick(&mut twin, &registry, &config);
            record_diff(&base, &twin, &config, &rl, &mut dr, &mut dh);
        }

        let record = SampleRecord {
            schema: 1,
            config: args.config.display().to_string(),
            world_seed,
            t,
            kitty_id: kitty,
            base_applied: action_wire_name(&base_rec.applied),
            twin_applied: action_wire_name(&twin_rec.applied),
            dr,
            dh,
        };
        serde_json::to_writer(&mut out, &record).expect("writing sample record");
        out.write_all(b"\n").expect("writing sample record");
        valid += 1;
        if !args.quiet {
            eprint!(
                "\rvalid {valid}/{} (degenerate {degenerate}, filtered {filtered})",
                args.samples
            );
        }
    }
    if !args.quiet {
        eprintln!();
    }

    let unfiltered_attempts = attempts - filtered;
    let summary = Summary {
        valid_samples: valid,
        degenerate_skipped: degenerate,
        filtered_out: filtered,
        attempts,
        decision_point_density: if unfiltered_attempts > 0 {
            valid as f64 / unfiltered_attempts as f64
        } else {
            0.0
        },
        only_action: args.only_action.clone(),
        config: args.config.display().to_string(),
        world_seeds: args.seeds.clone(),
        t_min: args.t_min,
        t_max: args.t_max,
        trace_len: args.trace_len,
        probe_seed: args.probe_seed,
        out: args.out.display().to_string(),
    };
    println!(
        "{}",
        serde_json::to_string_pretty(&summary).expect("summary")
    );
    if valid < args.samples {
        eprintln!(
            "warning: only {valid}/{} valid samples after {attempts} attempts",
            args.samples
        );
    }
}
