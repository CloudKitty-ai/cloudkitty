//! Need-occupancy census by replay (exp-004 announce-threshold work).
//!
//! The scripted-side threshold analysis priced the meow announce
//! threshold on dataset v3's distributions. This tool produces the
//! policy-side counterpart: drive eval-shaped worlds through the same
//! library code path (`harness::run_one_with`) with a policy seated, and
//! record per kitty × need:
//!
//! - a 101-bin histogram of the post-tick need value (occupancy at any
//!   threshold and any quantile fall out in analysis),
//! - dwell dynamics at candidate announce thresholds (episodes, dwell
//!   ticks, emits under the 10-tick cooldown),
//! - the need value on the tick *before* the kitty entered the matching
//!   relief activity (initiation conditioning — the post-tick read would
//!   already include one tick of relief).
//!
//! Roster modes: `all-subject` seats the artifact everywhere (the
//! 4-agent future the owner is designing for); `from-config` runs the
//! config's own roster verbatim with the artifact registered under the
//! name the config uses (the deployed 2+2 composition today).

use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

use cloudkitty_core::{Activity, BehaviorRegistry, NeedKind};
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::load_configs_from_str;
use cloudkitty_rl::harness::{run_one_with, EvalRequest, RosterMode};
use serde::Serialize;

const NEED_NAMES: [&str; 6] = ["eat", "drink", "sleep", "play", "cuddle", "bath"];
const DWELL_THRESHOLDS: [f32; 4] = [25.0, 30.0, 40.0, 50.0];
const COOLDOWN: u64 = 10;

/// The relief activity whose *start* conditions each need's initiation
/// histogram. Sleep covers solo and co-sleep; cuddle is the rest duet.
fn relief_need(activity: &Activity) -> Option<usize> {
    match activity {
        Activity::Eating => Some(0),
        Activity::Drinking => Some(1),
        Activity::Sleeping { .. } => Some(2),
        Activity::Playing { .. } => Some(3),
        Activity::Resting {
            with_friend: Some(_),
        } => Some(4),
        Activity::Grooming { target: None } => Some(5),
        _ => None,
    }
}

#[derive(Serialize, Clone)]
struct DwellStat {
    threshold: f32,
    episodes: u64,
    dwell_ticks: u64,
    emits: u64,
}

#[derive(Serialize)]
struct KittyRecord {
    kitty_id: u32,
    name: String,
    behavior: String,
    ticks: u64,
    /// hist[need][bin], bin = floor(clamp(value, 0, 100)).
    need_hist: Vec<Vec<u64>>,
    /// init_hist[need][bin]: prev-tick need value when the matching
    /// relief activity started.
    init_hist: Vec<Vec<u64>>,
    dwell: Vec<Vec<DwellStat>>,
}

#[derive(Serialize)]
struct Output {
    artifact: String,
    config: String,
    config_sha256: String,
    roster: String,
    ticks: u64,
    seeds: Vec<u64>,
    kitties: Vec<KittyRecord>,
}

struct Args {
    artifact: String,
    register_as: Option<String>,
    config: PathBuf,
    roster: String,
    seed_start: u64,
    seed_count: u64,
    ticks: u64,
    out: PathBuf,
}

fn parse_args() -> Args {
    let mut a = Args {
        artifact: String::new(),
        register_as: None,
        config: PathBuf::new(),
        roster: "all-subject".into(),
        seed_start: 0,
        seed_count: 30,
        ticks: 20_000,
        out: PathBuf::new(),
    };
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--artifact" => a.artifact = value("--artifact"),
            "--register-as" => a.register_as = Some(value("--register-as")),
            "--config" => a.config = PathBuf::from(value("--config")),
            "--roster" => a.roster = value("--roster"),
            "--seed-start" => a.seed_start = value("--seed-start").parse().expect("u64"),
            "--seed-count" => a.seed_count = value("--seed-count").parse().expect("u64"),
            "--ticks" => a.ticks = value("--ticks").parse().expect("u64"),
            "--out" => a.out = PathBuf::from(value("--out")),
            other => panic!("unknown flag {other}"),
        }
    }
    assert!(!a.artifact.is_empty(), "--artifact is required");
    assert!(!a.out.as_os_str().is_empty(), "--out is required");
    assert!(
        a.roster == "all-subject" || a.roster == "from-config",
        "--roster all-subject | from-config"
    );
    a
}

fn main() {
    let args = parse_args();
    let bytes = fs::read(&args.config)
        .unwrap_or_else(|e| panic!("reading {}: {e}", args.config.display()));
    let config_sha256 = cloudkitty_rl::suite::sha256_hex(&bytes);
    let text = String::from_utf8(bytes).expect("config is UTF-8");
    let (core, rl) = load_configs_from_str(&text).expect("config parses and validates");

    let mut registry = BehaviorRegistry::with_builtins();
    let behavior = PolicyBehavior::from_artifact_path(&args.artifact, &rl, false)
        .unwrap_or_else(|e| panic!("loading {}: {e:?}", args.artifact));
    let name = args
        .register_as
        .clone()
        .unwrap_or_else(|| format!("policy:{}", args.artifact));
    registry.register(name.clone(), std::sync::Arc::new(behavior));

    let (subject, roster) = match args.roster.as_str() {
        "all-subject" => (Some(name.as_str()), RosterMode::AllSubject),
        _ => (None, RosterMode::FromConfig),
    };
    // FromConfig runs the config's roster verbatim; every behavior the
    // config names must resolve, including the policy seats — hence
    // --register-as with the config's own name (e.g. the served
    // "policy:e003-m0-g998-s3").
    if roster == RosterMode::FromConfig {
        for k in &core.kitties {
            assert!(
                registry.get(&k.behavior).is_some(),
                "kitty_{} names {:?}; register the artifact under that name \
                 with --register-as",
                k.id,
                k.behavior
            );
        }
    }

    let seeds: Vec<u64> = (args.seed_start..args.seed_start + args.seed_count).collect();
    // Accumulators keyed by roster index (Article II: stable roster).
    let mut ids: Vec<(u32, String, String)> = Vec::new();
    let mut hist: Vec<[[u64; 101]; 6]> = Vec::new();
    let mut init: Vec<[[u64; 101]; 6]> = Vec::new();
    let mut dwell: Vec<[[DwellStat; 4]; 6]> = Vec::new();
    let mut ticks_seen: Vec<u64> = Vec::new();

    for &seed in &seeds {
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject,
            roster,
            seed,
            ticks: args.ticks,
        };
        let mut prev_needs: Vec<[f32; 6]> = Vec::new();
        let mut prev_act: Vec<usize> = Vec::new(); // activity class index proxy
        let mut above: Vec<[[bool; 4]; 6]> = Vec::new();
        let mut run_len: Vec<[[u64; 4]; 6]> = Vec::new();

        let _ = run_one_with(&request, |world| {
            if ids.is_empty() {
                for k in &world.kitties {
                    ids.push((k.id, k.name.clone(), k.behavior.clone()));
                    hist.push([[0; 101]; 6]);
                    init.push([[0; 101]; 6]);
                    dwell.push(std::array::from_fn(|n| {
                        std::array::from_fn(|t| DwellStat {
                            threshold: DWELL_THRESHOLDS[t],
                            episodes: 0,
                            dwell_ticks: 0,
                            emits: 0,
                        })
                        .map(|s| DwellStat { threshold: DWELL_THRESHOLDS[0], ..s })
                    }));
                    // fix thresholds per column
                    let last = dwell.len() - 1;
                    for n in 0..6 {
                        for t in 0..4 {
                            dwell[last][n][t].threshold = DWELL_THRESHOLDS[t];
                        }
                    }
                    ticks_seen.push(0);
                }
            }
            if prev_needs.is_empty() {
                for k in &world.kitties {
                    prev_needs.push([0.0; 6]);
                    prev_act.push(activity_class(&k.activity));
                    above.push([[false; 4]; 6]);
                    run_len.push([[0; 4]; 6]);
                }
                // Seed prev from the first observed tick without counting a
                // transition on it.
                for (i, k) in world.kitties.iter().enumerate() {
                    for (j, kind) in NeedKind::ALL.into_iter().enumerate() {
                        prev_needs[i][j] = k.needs.get(kind);
                    }
                }
            }
            for (i, k) in world.kitties.iter().enumerate() {
                let act = activity_class(&k.activity);
                if act != prev_act[i] {
                    if let Some(j) = relief_need(&k.activity) {
                        let bin = (prev_needs[i][j].clamp(0.0, 100.0)) as usize;
                        init[i][j][bin.min(100)] += 1;
                    }
                }
                ticks_seen[i] += 1;
                for (j, kind) in NeedKind::ALL.into_iter().enumerate() {
                    let v = k.needs.get(kind);
                    hist[i][j][(v.clamp(0.0, 100.0)) as usize] += 1;
                    for (t, thr) in DWELL_THRESHOLDS.iter().enumerate() {
                        let hot = v >= *thr;
                        if hot {
                            run_len[i][j][t] += 1;
                            if !above[i][j][t] {
                                dwell[i][j][t].episodes += 1;
                            }
                        } else if above[i][j][t] {
                            let d = run_len[i][j][t];
                            dwell[i][j][t].dwell_ticks += d;
                            dwell[i][j][t].emits += d.div_ceil(COOLDOWN);
                            run_len[i][j][t] = 0;
                        }
                        above[i][j][t] = hot;
                    }
                    prev_needs[i][j] = v;
                }
                prev_act[i] = act;
            }
        });
        // flush open runs at horizon
        for i in 0..ids.len() {
            for j in 0..6 {
                for t in 0..4 {
                    if above[i][j][t] {
                        let d = run_len[i][j][t];
                        dwell[i][j][t].dwell_ticks += d;
                        dwell[i][j][t].emits += d.div_ceil(COOLDOWN);
                    }
                }
            }
        }
    }

    let kitties = ids
        .iter()
        .enumerate()
        .map(|(i, (id, name, behavior))| KittyRecord {
            kitty_id: *id,
            name: name.clone(),
            behavior: behavior.clone(),
            ticks: ticks_seen[i],
            need_hist: hist[i].iter().map(|h| h.to_vec()).collect(),
            init_hist: init[i].iter().map(|h| h.to_vec()).collect(),
            dwell: dwell[i]
                .iter()
                .map(|row| row.to_vec())
                .collect(),
        })
        .collect();

    if let Some(dir) = args.out.parent() {
        if !dir.as_os_str().is_empty() {
            fs::create_dir_all(dir).expect("creating output directory");
        }
    }
    let output = Output {
        artifact: args.artifact,
        config: args.config.display().to_string(),
        config_sha256,
        roster: args.roster,
        ticks: args.ticks,
        seeds,
        kitties,
    };
    fs::write(
        &args.out,
        serde_json::to_string(&output).expect("output serializes") + "\n",
    )
    .expect("writing output");
    println!("wrote {}", args.out.display());
    let _ = NEED_NAMES; // used by analysis; kept for the record
}

fn activity_class(a: &Activity) -> usize {
    match a {
        Activity::Idle => 0,
        Activity::Resting { .. } => 1,
        Activity::Sleeping { .. } => 2,
        Activity::Eating => 3,
        Activity::Drinking => 4,
        Activity::Playing { .. } => 5,
        Activity::Grooming { .. } => 6,
    }
}
