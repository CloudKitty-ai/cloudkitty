//! Clowder: the CloudKitty viewer load benchmark (spec 029).
//!
//! How many concurrent viewers can a server sustain, and how does it fail past
//! that? Clowder drives real viewer traffic (first-paint GET, then the `/ws`
//! subscription) in five shapes and measures everything from outside -- the
//! tick number every payload carries gives skips, lag, and the world's cadence
//! -- with no server or engine change. See contracts/cli.md and
//! contracts/record-format.md.

mod health;
mod http;
mod metrics;
mod modes;
mod record;
mod scan;
mod selfwatch;
mod swarm;
mod target;
mod viewer;

use std::process::ExitCode;
use std::sync::{Arc, Mutex};

use health::{evaluate, HealthThresholds, Signature};
use metrics::IntervalRow;
use modes::{IdGen, Plan};
use record::Record;
use swarm::{sample_loop, Shared};
use target::{Target, TargetIdentity};

const VERSION: &str = concat!("clowder ", env!("CARGO_PKG_VERSION"));

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let rt = tokio::runtime::Runtime::new().expect("tokio runtime");
    match rt.block_on(run(args)) {
        Ok(code) => code,
        Err(Usage(msg)) => {
            eprintln!("{msg}");
            ExitCode::from(1)
        }
    }
}

/// A usage/configuration error (exit 1).
struct Usage(String);

/// The parsed command line.
struct Cli {
    mode: String,
    plan: Plan,
    target_raw: String,
    allow_remote: bool,
    interval_s: f64,
    out: Option<String>,
    repeat: u32,
}

async fn run(args: Vec<String>) -> Result<ExitCode, Usage> {
    let cli = parse(&args)?;
    let target = Target::parse(&cli.target_raw, cli.allow_remote).map_err(Usage)?;

    // Identity stamp: fetch /config and /world once. A target unreachable at
    // the start is a setup error, not a measured interruption.
    let cfg = http::get(&target.host, target.port, "/config")
        .await
        .map_err(|e| Usage(format!("cannot reach target {}: {e}", cli.target_raw)))?;
    let world = http::get(&target.host, target.port, "/world")
        .await
        .map_err(|e| Usage(format!("cannot reach target {}: {e}", cli.target_raw)))?;
    if cfg.status != 200 || world.status != 200 {
        return Err(Usage(format!(
            "target returned HTTP {} / {} for /config / /world; not a CloudKitty server?",
            cfg.status, world.status
        )));
    }
    let identity = TargetIdentity::from_bodies(&cfg.body, &world.body);
    let nominal_tick_ms = identity.tick_ms.map(|m| m as f64).unwrap_or(800.0);

    let mut ceilings: Vec<u64> = Vec::new();
    let mut worst: u8 = 0;
    for rep in 1..=cli.repeat {
        let out = out_path(&cli, rep);
        let (code, ceiling) = run_once(&cli, &target, &identity, nominal_tick_ms, &out).await;
        worst = worst.max(code);
        if let Some(c) = ceiling {
            ceilings.push(c);
        }
    }
    if cli.repeat > 1 {
        report_repeat_agreement(&ceilings);
    }
    Ok(ExitCode::from(worst))
}

/// SC-003: two runs of the same scenario should agree on the ceiling within
/// ±10%. Printed when --repeat > 1.
fn report_repeat_agreement(ceilings: &[u64]) {
    if ceilings.len() < 2 {
        println!("repeat: fewer than two ceilings to compare");
        return;
    }
    let min = *ceilings.iter().min().unwrap() as f64;
    let max = *ceilings.iter().max().unwrap() as f64;
    let spread = if max > 0.0 { (max - min) / max } else { 0.0 };
    let verdict = if spread <= 0.10 {
        "within ±10%"
    } else {
        "OUTSIDE ±10%"
    };
    println!(
        "repeat: ceilings {ceilings:?} — spread {:.1}% ({verdict})",
        spread * 100.0
    );
}

/// One run of the scenario against the target; writes a record and returns the
/// exit code.
async fn run_once(
    cli: &Cli,
    target: &Target,
    identity: &TargetIdentity,
    nominal_tick_ms: f64,
    out: &str,
) -> (u8, Option<u64>) {
    let shared = Shared::new(target.clone(), nominal_tick_ms);
    let ids = IdGen::default();
    let rows: Arc<Mutex<Vec<IntervalRow>>> = Arc::new(Mutex::new(Vec::new()));

    // The sampler runs concurrently, pushing interval rows into `rows`.
    let sink_rows = rows.clone();
    let plan_hold = cli.plan.hold_s;
    let step_of = move |t: f64| -> Option<u32> {
        if plan_hold > 0.0 {
            Some((t / plan_hold) as u32 + 1)
        } else {
            None
        }
    };
    let sampler = {
        let s = shared.clone();
        let interval = cli.interval_s;
        tokio::spawn(async move {
            sample_loop(
                s,
                interval,
                move |batch| sink_rows.lock().unwrap().extend(batch),
                step_of,
            )
            .await;
        })
    };

    // Ctrl-C shuts the run down gracefully (its own outcome, not the target's).
    let interrupted = Arc::new(std::sync::atomic::AtomicBool::new(false));
    {
        let s = shared.clone();
        let flag = interrupted.clone();
        tokio::spawn(async move {
            if tokio::signal::ctrl_c().await.is_ok() {
                flag.store(true, std::sync::atomic::Ordering::Relaxed);
                s.shutdown();
            }
        });
    }

    // The poller mix runs concurrently with the viewer traffic (FR-006), so it
    // must start before the scheduler, not after it returns.
    let pollers = modes::spawn_pollers(&shared, &cli.plan);

    // Drive the traffic shape.
    match cli.mode.as_str() {
        "ramp" => modes::ramp(shared.clone(), &cli.plan, rows.clone(), &ids).await,
        "soak" => modes::soak(shared.clone(), &cli.plan, &ids).await,
        "spike" => modes::spike(shared.clone(), &cli.plan, &ids).await,
        "slow-consumer" => modes::slow_consumer(shared.clone(), &cli.plan, &ids).await,
        "churn" => modes::churn(shared.clone(), &cli.plan, &ids).await,
        _ => unreachable!("mode validated in parse()"),
    }

    // Traffic done: stop the swarm and the sampler.
    shared.shutdown();
    let _ = sampler.await;
    if let Some(p) = pollers {
        p.abort();
    }

    let all: Vec<IntervalRow> = rows.lock().unwrap().clone();
    finalize(cli, target, identity, &shared, nominal_tick_ms, all, out)
}

/// Derive summaries, classify, write the record, print the human summary, and
/// choose the exit code (FR-010, FR-012, FR-014).
fn finalize(
    cli: &Cli,
    target: &Target,
    identity: &TargetIdentity,
    shared: &Arc<Shared>,
    nominal_tick_ms: f64,
    mut all: Vec<IntervalRow>,
    out: &str,
) -> (u8, Option<u64>) {
    let mut rec = Record::new(
        VERSION,
        &now_iso8601(),
        &cli.mode,
        &scenario_lines(cli),
        &cli.plan.thresholds,
        &target.http_base,
        identity,
        Some(shared.selfwatch.limit()),
    );

    let interval_rows: Vec<IntervalRow> = all
        .iter()
        .filter(|r| r.scope == "interval")
        .cloned()
        .collect();

    // Per-step summaries (ramp only) and the run summary, derived from
    // interval rows -- never measured independently.
    let mut ceiling: Option<u64> = None;
    if cli.mode == "ramp" {
        let max_step = interval_rows
            .iter()
            .filter_map(|r| r.step)
            .max()
            .unwrap_or(0);
        for step in 1..=max_step {
            let step_rows: Vec<IntervalRow> = interval_rows
                .iter()
                .filter(|r| r.step == Some(step))
                .cloned()
                .collect();
            if step_rows.is_empty() {
                continue;
            }
            let v = evaluate(&step_rows, Some(nominal_tick_ms), &cli.plan.thresholds);
            let conns = step_rows.iter().map(|r| r.conns_open).max().unwrap_or(0);
            all.push(summary_row("step", Some(step), conns, &step_rows));
            if v.healthy {
                ceiling = Some(conns);
            }
        }
    }

    let run_verdict = evaluate(&interval_rows, Some(nominal_tick_ms), &cli.plan.thresholds);
    let run_conns = interval_rows
        .iter()
        .map(|r| r.conns_open)
        .max()
        .unwrap_or(0);
    all.push(summary_row("run", None, run_conns, &interval_rows));

    // Cadence-reference promotions, if any, are noted after the data.
    let promos = shared.cadence_promotions();
    if promos > 0 {
        rec.note(&format!("cadence reference promoted {promos} time(s)"));
    }
    if shared.schema_drifted() {
        rec.note("a payload could not be parsed for its tick (schema drift)");
    }

    // Outcome and exit code.
    let server_closed = interval_rows.iter().map(|r| r.unexpected_ends).sum::<u64>();
    let any_invalid = interval_rows.iter().any(|r| !r.valid);
    let all_invalid = !interval_rows.is_empty() && interval_rows.iter().all(|r| !r.valid);

    let (outcome, code): (&str, u8) = if server_closed > 0 && server_mass_dropped(&interval_rows) {
        ("interrupted", 3)
    } else if all_invalid {
        ("invalidated", 2)
    } else {
        ("completed", 0)
    };

    let mut classification: Vec<String> = run_verdict
        .signatures
        .iter()
        .map(|s| s.label().to_string())
        .collect();
    if any_invalid
        && !classification
            .iter()
            .any(|c| c == Signature::GeneratorBottleneck.label())
    {
        classification.push(Signature::GeneratorBottleneck.label().to_string());
    }

    for r in &all {
        rec.push_row(r.clone());
    }
    rec.finish(outcome, &classification);

    if let Err(e) = std::fs::write(out, rec.serialize()) {
        eprintln!("could not write record {out}: {e}");
        return (1, None);
    }

    print_summary(cli, out, ceiling, &run_verdict, outcome, run_conns);
    (code, ceiling)
}

/// A heuristic for "the server dropped everyone": more than half of the peak
/// open connections ended unexpectedly.
fn server_mass_dropped(rows: &[IntervalRow]) -> bool {
    let peak = rows.iter().map(|r| r.conns_open).max().unwrap_or(0);
    let unexpected: u64 = rows.iter().map(|r| r.unexpected_ends).sum();
    peak > 0 && unexpected * 2 > peak
}

fn summary_row(scope: &str, step: Option<u32>, conns: u64, rows: &[IntervalRow]) -> IntervalRow {
    IntervalRow {
        t: rows.last().map(|r| r.t).unwrap_or(0.0),
        scope: scope.to_string(),
        step,
        class: "all".into(),
        conns_open: conns,
        conns_target: rows.iter().map(|r| r.conns_target).max().unwrap_or(0),
        updates: rows.iter().map(|r| r.updates).sum(),
        skips: rows.iter().map(|r| r.skips).sum(),
        bytes: rows.iter().map(|r| r.bytes).sum(),
        errors: rows.iter().map(|r| r.errors).sum(),
        unexpected_ends: rows.iter().map(|r| r.unexpected_ends).sum(),
        cadence_ms: rows.iter().rev().find_map(|r| r.cadence_ms),
        valid: rows.iter().all(|r| r.valid),
        ..Default::default()
    }
}

fn print_summary(
    cli: &Cli,
    out: &str,
    ceiling: Option<u64>,
    verdict: &health::StepVerdict,
    outcome: &str,
    run_conns: u64,
) {
    println!("clowder {} — {outcome}", cli.mode);
    if cli.mode == "ramp" {
        match ceiling {
            Some(c) if c >= cli.plan.viewers => {
                println!("  reached {c} viewers, all steps healthy")
            }
            Some(c) => {
                let first = verdict.first_degraded.map(|s| s.label()).unwrap_or("—");
                println!("  ceiling {c} healthy viewers; degraded first on {first}");
            }
            None => println!("  no step held healthy"),
        }
    } else {
        println!("  {run_conns} peak viewers");
        if verdict.healthy {
            println!("  healthy under the thresholds in effect");
        } else {
            let sigs: Vec<&str> = verdict.signatures.iter().map(|s| s.label()).collect();
            println!("  degradation: {}", sigs.join(", "));
        }
        if cli.mode == "slow-consumer" {
            // SC-006: did stalling one group harm the healthy bystanders? The
            // health verdict already covers the viewer class only, so a healthy
            // verdict here IS the bystander-unharmed finding; say so plainly,
            // and name the refutation when it does not hold.
            if verdict.healthy {
                println!("  bystanders unharmed: healthy viewers skipped nothing while stalled viewers were shed");
            } else if verdict.signatures.contains(&Signature::SkippedUpdates) {
                println!(
                    "  bystanders HARMED: healthy viewers skipped updates while others stalled"
                );
            }
        }
    }
    println!("  record: {out}");
}

fn scenario_lines(cli: &Cli) -> Vec<String> {
    let p = &cli.plan;
    let mut v = vec![
        format!("mode={}", cli.mode),
        format!("target={}", cli.target_raw),
        format!("interval={}", cli.interval_s),
        format!("repeat={}", cli.repeat),
    ];
    match cli.mode.as_str() {
        "ramp" => v.push(format!(
            "to={} step={} step_interval={} hold={}",
            p.viewers, p.step, p.step_interval_s, p.hold_s
        )),
        "slow-consumer" => v.push(format!(
            "viewers={} stall_fraction={} stall_after={} duration={}",
            p.viewers, p.stall_fraction, p.stall_after_s, p.duration_s
        )),
        "churn" => v.push(format!(
            "viewers={} churn_rate={} duration={}",
            p.viewers, p.churn_rate, p.duration_s
        )),
        _ => v.push(format!("viewers={} duration={}", p.viewers, p.duration_s)),
    }
    if p.poll_rate > 0.0 {
        v.push(format!(
            "poll_rate={} poll_endpoints={}",
            p.poll_rate,
            p.poll_endpoints.join("|")
        ));
    }
    v
}

fn out_path(cli: &Cli, rep: u32) -> String {
    let base = cli
        .out
        .clone()
        .unwrap_or_else(|| format!("clowder-{}-{}.csv", cli.mode, now_compact()));
    if cli.repeat > 1 {
        if let Some(stripped) = base.strip_suffix(".csv") {
            format!("{stripped}-{rep}.csv")
        } else {
            format!("{base}-{rep}")
        }
    } else {
        base
    }
}

// --- CLI parsing ---

fn parse(args: &[String]) -> Result<Cli, Usage> {
    if args.is_empty() || args[0] == "--help" || args[0] == "-h" {
        return Err(Usage(usage()));
    }
    let mode = args[0].clone();
    if !matches!(
        mode.as_str(),
        "ramp" | "spike" | "slow-consumer" | "churn" | "soak"
    ) {
        return Err(Usage(format!("unknown mode '{mode}'\n{}", usage())));
    }

    // Defaults (contracts/cli.md).
    let mut plan = Plan {
        viewers: 0,
        step: 25,
        step_interval_s: 5.0,
        hold_s: if mode == "ramp" { 30.0 } else { 0.0 },
        duration_s: default_duration(&mode),
        stall_fraction: 0.1,
        stall_after_s: 10.0,
        churn_rate: 5.0,
        poll_rate: 0.0,
        poll_endpoints: vec!["/world".into(), "/kitties".into(), "/config".into()],
        thresholds: HealthThresholds::default(),
    };
    let mut target_raw = "http://127.0.0.1:8090".to_string();
    let mut allow_remote = false;
    let mut interval_s = 1.0;
    let mut out = None;
    let mut repeat = 1u32;
    let mut have_viewers = false;

    let mut it = args[1..].iter();
    while let Some(flag) = it.next() {
        let mut val = |name: &str| -> Result<String, Usage> {
            match it.next() {
                Some(v) if !v.starts_with("--") => Ok(v.clone()),
                _ => Err(Usage(format!("{name} requires a value"))),
            }
        };
        match flag.as_str() {
            "--to" => {
                plan.viewers = pnum(&val("--to")?, "--to")?;
                have_viewers = true;
            }
            "--viewers" => {
                plan.viewers = pnum(&val("--viewers")?, "--viewers")?;
                have_viewers = true;
            }
            "--step" => plan.step = pnum(&val("--step")?, "--step")?,
            "--step-interval" => {
                plan.step_interval_s = pfloat(&val("--step-interval")?, "--step-interval")?
            }
            "--hold" => plan.hold_s = pfloat(&val("--hold")?, "--hold")?,
            "--duration" => plan.duration_s = pfloat(&val("--duration")?, "--duration")?,
            "--stall-fraction" => plan.stall_fraction = pfrac(&val("--stall-fraction")?)?,
            "--stall-after" => {
                plan.stall_after_s = pfloat(&val("--stall-after")?, "--stall-after")?
            }
            "--churn-rate" => plan.churn_rate = pfloat(&val("--churn-rate")?, "--churn-rate")?,
            "--poll-rate" => plan.poll_rate = pfloat(&val("--poll-rate")?, "--poll-rate")?,
            "--poll-endpoints" => {
                plan.poll_endpoints = val("--poll-endpoints")?
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .collect()
            }
            "--target" => target_raw = val("--target")?,
            "--allow-remote" => allow_remote = true,
            "--interval" => interval_s = pfloat(&val("--interval")?, "--interval")?,
            "--out" => out = Some(val("--out")?),
            "--repeat" => repeat = pnum(&val("--repeat")?, "--repeat")? as u32,
            "--max-skips" => plan.thresholds.max_skips = pnum(&val("--max-skips")?, "--max-skips")?,
            "--cadence-tolerance" => {
                plan.thresholds.cadence_tolerance =
                    pfloat(&val("--cadence-tolerance")?, "--cadence-tolerance")?
            }
            "--max-handshake-failures" => {
                plan.thresholds.max_handshake_failures = pnum(
                    &val("--max-handshake-failures")?,
                    "--max-handshake-failures",
                )?
            }
            "--max-unexpected-ends" => {
                plan.thresholds.max_unexpected_ends =
                    pnum(&val("--max-unexpected-ends")?, "--max-unexpected-ends")?
            }
            "--help" | "-h" => return Err(Usage(usage())),
            other => return Err(Usage(format!("unknown flag '{other}'\n{}", usage()))),
        }
    }

    if !have_viewers || plan.viewers == 0 {
        let f = if mode == "ramp" { "--to" } else { "--viewers" };
        return Err(Usage(format!("{mode} requires {f} <N> with N >= 1")));
    }
    if interval_s <= 0.0 {
        return Err(Usage("--interval must be > 0".into()));
    }
    if repeat == 0 {
        return Err(Usage("--repeat must be >= 1".into()));
    }
    if mode == "ramp" && plan.hold_s <= 0.0 {
        return Err(Usage("--hold must be > 0".into()));
    }
    if mode != "ramp" && plan.duration_s <= 0.0 {
        return Err(Usage("--duration must be > 0".into()));
    }

    Ok(Cli {
        mode,
        plan,
        target_raw,
        allow_remote,
        interval_s,
        out,
        repeat,
    })
}

fn default_duration(mode: &str) -> f64 {
    match mode {
        "spike" => 60.0,
        "slow-consumer" | "churn" | "soak" => 120.0,
        _ => 0.0,
    }
}

fn pnum(s: &str, flag: &str) -> Result<u64, Usage> {
    s.parse()
        .map_err(|_| Usage(format!("{flag}: '{s}' is not a non-negative integer")))
}
fn pfloat(s: &str, flag: &str) -> Result<f64, Usage> {
    let v: f64 = s
        .parse()
        .map_err(|_| Usage(format!("{flag}: '{s}' is not a number")))?;
    if v < 0.0 {
        return Err(Usage(format!("{flag}: must be >= 0")));
    }
    Ok(v)
}
fn pfrac(s: &str) -> Result<f64, Usage> {
    let v: f64 = s
        .parse()
        .map_err(|_| Usage(format!("--stall-fraction: '{s}' is not a number")))?;
    if !(0.0..=1.0).contains(&v) {
        return Err(Usage("--stall-fraction must be in [0, 1]".into()));
    }
    Ok(v)
}

fn usage() -> String {
    "\
clowder <MODE> --target <URL> [flags]   (spec 029)

MODES
  ramp           --to N [--step 25] [--step-interval 5] [--hold 30]
  spike          --viewers N [--duration 60]
  slow-consumer  --viewers N [--stall-fraction 0.1] [--stall-after 10] [--duration 120]
  churn          --viewers N [--churn-rate 5] [--duration 120]
  soak           --viewers N [--duration 120]

COMMON
  --target URL (default http://127.0.0.1:8090)   --allow-remote
  --poll-rate R  --poll-endpoints /world,/kitties,/config
  --interval 1   --repeat 1   --out PATH
  --max-skips 0  --cadence-tolerance 0.05  --max-handshake-failures 0  --max-unexpected-ends 0

Targets are LOCAL by default; --allow-remote is for a server you own.
The live world is NEVER a permitted target.

EXIT  0 completed · 1 usage/config · 2 invalidated by a generator bottleneck · 3 interrupted by target failure"
        .to_string()
}

// --- time helpers (no chrono dependency) ---

fn now_epoch_secs() -> i64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}

fn now_compact() -> String {
    now_epoch_secs().to_string()
}

/// UTC ISO-8601 without chrono: civil date from Unix days (Hinnant's algorithm).
fn now_iso8601() -> String {
    let secs = now_epoch_secs();
    let days = secs.div_euclid(86_400);
    let sod = secs.rem_euclid(86_400);
    let (y, m, d) = civil_from_days(days);
    let (hh, mm, ss) = (sod / 3600, (sod % 3600) / 60, sod % 60);
    format!("{y:04}-{m:02}-{d:02}T{hh:02}:{mm:02}:{ss:02}Z")
}

fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = (if mp < 10 { mp + 3 } else { mp - 9 }) as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}
