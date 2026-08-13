//! Shared run state and the interval sampler.
//!
//! [`Shared`] is the one context every viewer, poller, and the scheduler hold.
//! The sampler wakes once per interval, snapshots the live connection registry,
//! diffs it against the previous snapshot, and emits one [`IntervalRow`] per
//! active class -- the single measurement path all five modes reuse (FR-007,
//! FR-008, FR-010).

use std::collections::{HashMap, HashSet};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Instant;

use tokio::sync::broadcast;

use crate::metrics::{CadenceReference, Histogram, IntervalRow};
use crate::selfwatch::SelfWatch;
use crate::target::Target;
use crate::viewer::ConnHandle;

pub struct Shared {
    pub target: Target,
    pub cadence: CadenceReference,
    pub selfwatch: SelfWatch,
    pub shutdown: broadcast::Sender<()>,
    /// The one TLS connector for the whole run (`Some` iff the target is TLS),
    /// built once and shared -- never rebuilt per connection.
    tls_connector: Option<native_tls::TlsConnector>,
    /// Viewers skip the first-paint GET and subscribe straight to /ws.
    skip_first_paint: bool,
    run_start: Instant,
    nominal_tick_ms: f64,
    registry: Mutex<Vec<Arc<ConnHandle>>>,
    conns_target: AtomicU64,
    /// The ramp step currently being HELD (0 = none / establishment). The
    /// scheduler owns the truth; the sampler reads it rather than guessing the
    /// step from a time formula, which cannot know the establishment phase.
    current_step: AtomicU64,
    poll_hist: Mutex<Histogram>,
    poll_errors: AtomicU64,
    schema_drift: AtomicBool,
}

impl Shared {
    pub fn new(
        target: Target,
        nominal_tick_ms: f64,
        tls_connector: Option<native_tls::TlsConnector>,
        skip_first_paint: bool,
    ) -> Arc<Shared> {
        let (shutdown, _) = broadcast::channel(1);
        Arc::new(Shared {
            target,
            cadence: CadenceReference::default(),
            selfwatch: SelfWatch::new(),
            shutdown,
            tls_connector,
            skip_first_paint,
            run_start: Instant::now(),
            nominal_tick_ms,
            registry: Mutex::new(Vec::new()),
            conns_target: AtomicU64::new(0),
            current_step: AtomicU64::new(0),
            poll_hist: Mutex::new(Histogram::default()),
            poll_errors: AtomicU64::new(0),
            schema_drift: AtomicBool::new(false),
        })
    }

    pub fn elapsed_s(&self) -> f64 {
        self.run_start.elapsed().as_secs_f64()
    }

    pub fn elapsed_ms(&self) -> u64 {
        self.run_start.elapsed().as_millis() as u64
    }

    /// A cadence reference is stale after ~3 nominal ticks of silence; the next
    /// healthy viewer is then promoted.
    pub fn cadence_stale_ms(&self) -> u64 {
        (self.nominal_tick_ms * 3.0).max(1000.0) as u64
    }

    pub fn nominal_tick_ms(&self) -> f64 {
        self.nominal_tick_ms
    }

    /// The shared TLS connector, or None for a plain-http target.
    pub fn tls_connector(&self) -> Option<&native_tls::TlsConnector> {
        self.tls_connector.as_ref()
    }

    pub fn skip_first_paint(&self) -> bool {
        self.skip_first_paint
    }

    pub fn register(&self, handle: Arc<ConnHandle>) {
        self.registry.lock().unwrap().push(handle);
    }

    pub fn set_target_conns(&self, n: u64) {
        self.conns_target.store(n, Ordering::Relaxed);
    }

    /// The ramp scheduler marks the step it is holding (None during cohort
    /// establishment, so those rows are excluded from per-step summaries).
    pub fn set_step(&self, step: Option<u32>) {
        self.current_step
            .store(step.map(|s| s as u64).unwrap_or(0), Ordering::Relaxed);
    }

    pub fn current_step(&self) -> Option<u32> {
        match self.current_step.load(Ordering::Relaxed) {
            0 => None,
            s => Some(s as u32),
        }
    }

    pub fn record_poll(&self, ms: f64, error: bool) {
        if error {
            self.poll_errors.fetch_add(1, Ordering::Relaxed);
        } else {
            self.poll_hist.lock().unwrap().record(ms);
        }
    }

    /// Take this interval's poller latency distribution, resetting it so each
    /// interval reports its own samples rather than a lifetime sum (matching
    /// every other class's per-interval delta).
    pub fn drain_poll_hist(&self) -> Histogram {
        std::mem::take(&mut self.poll_hist.lock().unwrap())
    }

    pub fn poll_errors_total(&self) -> u64 {
        self.poll_errors.load(Ordering::Relaxed)
    }

    pub fn note_schema_drift(&self) {
        self.schema_drift.store(true, Ordering::Relaxed);
    }

    pub fn schema_drifted(&self) -> bool {
        self.schema_drift.load(Ordering::Relaxed)
    }

    /// Stop every connection.
    pub fn shutdown(&self) {
        let _ = self.shutdown.send(());
    }

    pub fn cadence_promotions(&self) -> u64 {
        self.cadence.promotions()
    }
}

/// The sampler's carried-over per-connection totals, so each interval reports a
/// delta rather than a running sum.
#[derive(Default)]
struct Prev {
    updates: u64,
    skips: u64,
    bytes: u64,
    errors: u64,
}

/// One class's accumulation for a single interval.
#[derive(Default)]
struct ClassAcc {
    updates: u64,
    skips: u64,
    bytes: u64,
    errors: u64,
    conns_open: u64,
    handshake_failures: u64,
    unexpected_ends: u64,
    handshake: Histogram,
    gap: Histogram,
}

/// Runs the sampler until `shutdown`, pushing rows through `sink`. Returns
/// nothing; the caller owns the collected rows via the sink closure.
pub async fn sample_loop(
    shared: Arc<Shared>,
    interval_s: f64,
    mut sink: impl FnMut(Vec<IntervalRow>),
) {
    let mut shutdown = shared.shutdown.subscribe();
    let mut prev: HashMap<u64, Prev> = HashMap::new();
    let mut handshakes_counted: HashSet<u64> = HashSet::new();
    let mut ends_counted: HashSet<u64> = HashSet::new();
    let mut prev_poll_errors = 0u64;
    let period = std::time::Duration::from_secs_f64(interval_s);
    let mut next = Instant::now() + period;

    loop {
        let slept = tokio::select! {
            _ = shutdown.recv() => false,
            _ = tokio::time::sleep_until(tokio::time::Instant::from_std(next)) => true,
        };

        let now = Instant::now();
        let gen_lag_ms = (now.saturating_duration_since(next).as_secs_f64() * 1000.0).max(0.0);
        let t = shared.elapsed_s();

        let mut classes: HashMap<&'static str, ClassAcc> = HashMap::new();
        let mut open_total = 0u64;
        {
            // Prune connections that have closed AND been fully drained (no new
            // data this interval), so churn and long soaks don't grow the
            // sampler's per-interval work without bound -- the self-inflicted
            // overhead FR-011 exists to keep off the server's ledger.
            let mut prune: Vec<u64> = Vec::new();
            let mut reg = shared.registry.lock().unwrap();
            for h in reg.iter() {
                let cls = h.class().label();
                let acc = classes.entry(cls).or_default();
                let p = prev.entry(h.id).or_default();

                let u = h.stats.updates.load(Ordering::Relaxed);
                let s = h.stats.skips.load(Ordering::Relaxed);
                let b = h.stats.bytes.load(Ordering::Relaxed);
                let e = h.stats.errors.load(Ordering::Relaxed);
                let du = u - p.updates;
                acc.updates += du;
                acc.skips += s - p.skips;
                acc.bytes += b - p.bytes;
                acc.errors += e - p.errors;
                *p = Prev {
                    updates: u,
                    skips: s,
                    bytes: b,
                    errors: e,
                };

                let is_open = h.open.load(Ordering::Relaxed);
                if is_open {
                    acc.conns_open += 1;
                    open_total += 1;
                }
                // Handshake latency counted once, when the connection first opens.
                let hs = h.stats.handshake_us.load(Ordering::Relaxed);
                if hs > 0 && handshakes_counted.insert(h.id) {
                    acc.handshake.record(hs as f64 / 1000.0);
                }
                // Inter-update gap for connections that moved this interval.
                if du > 0 {
                    let g = h.stats.last_gap_us.load(Ordering::Relaxed);
                    if g > 0 {
                        acc.gap.record(g as f64 / 1000.0);
                    }
                }
                // A closed connection: bucket its end reason once (handshake
                // failure vs drop are distinct signatures), then prune it once
                // its final delta has been captured.
                if !is_open {
                    if ends_counted.insert(h.id) {
                        let end = h.end.lock().unwrap();
                        if end.is_handshake_failure() {
                            acc.handshake_failures += 1;
                        } else if end.is_drop() {
                            acc.unexpected_ends += 1;
                        }
                    }
                    if du == 0 {
                        prune.push(h.id);
                    }
                }
            }
            if !prune.is_empty() {
                let pset: std::collections::HashSet<u64> = prune.iter().copied().collect();
                reg.retain(|h| !pset.contains(&h.id));
                for id in &prune {
                    prev.remove(id);
                    handshakes_counted.remove(id);
                    ends_counted.remove(id);
                }
            }
        }

        shared.selfwatch.observe_conns(open_total);
        let headroom = shared.selfwatch.headroom(open_total);
        let lag_limit_ms = interval_s * 1000.0 * 0.25;
        let valid = !shared
            .selfwatch
            .interval_invalid(open_total, gen_lag_ms, lag_limit_ms);
        let cadence_ms = shared.cadence.period_ms();
        let target = shared.conns_target.load(Ordering::Relaxed);
        let step = shared.current_step();

        // Poller class: this interval's own samples (the histogram is drained
        // each interval) and this interval's error delta.
        let poll_this = shared.drain_poll_hist();
        let poll_total = shared.poll_errors_total();
        let poll_err = poll_total - prev_poll_errors;
        prev_poll_errors = poll_total;
        let (poll_p50, poll_p99) = (poll_this.percentile(0.5), poll_this.percentile(0.99));

        let mut rows = Vec::new();
        for (label, acc) in classes.iter() {
            let is_viewer = *label == "viewer";
            rows.push(IntervalRow {
                t,
                scope: "interval".into(),
                step,
                class: (*label).to_string(),
                conns_target: target,
                conns_open: acc.conns_open,
                updates: acc.updates,
                skips: acc.skips,
                bytes: acc.bytes,
                handshake_p50_ms: acc.handshake.percentile(0.5),
                handshake_p99_ms: acc.handshake.percentile(0.99),
                gap_p50_ms: acc.gap.percentile(0.5),
                gap_p99_ms: acc.gap.percentile(0.99),
                // Cadence rides on the healthy viewer class only.
                cadence_ms: if is_viewer { cadence_ms } else { None },
                poll_p50_ms: None,
                poll_p99_ms: None,
                poll_errors: 0,
                errors: acc.errors,
                handshake_failures: acc.handshake_failures,
                unexpected_ends: acc.unexpected_ends,
                gen_fd_headroom: headroom,
                gen_lag_ms: Some(gen_lag_ms),
                valid,
            });
        }
        if !poll_p50.is_none() || poll_err > 0 {
            rows.push(IntervalRow {
                t,
                scope: "interval".into(),
                step,
                class: "poller".into(),
                conns_target: target,
                poll_p50_ms: poll_p50,
                poll_p99_ms: poll_p99,
                poll_errors: poll_err,
                gen_fd_headroom: headroom,
                gen_lag_ms: Some(gen_lag_ms),
                valid,
                ..Default::default()
            });
        }
        if !rows.is_empty() {
            sink(rows);
        }

        if !slept {
            break; // shutdown fired
        }
        next += period;
        // If we fell badly behind, resync so we don't spin catching up.
        if next < Instant::now() {
            next = Instant::now() + period;
        }
    }
}
