//! Per-connection measurement and the 1 Hz interval sampler.
//!
//! Every viewer owns a [`ConnStats`] of atomic counters it updates as messages
//! arrive; the sampler snapshots all of them once per interval, diffs against
//! the previous snapshot, and emits one [`IntervalRow`] per active class
//! (FR-007, FR-008, FR-010). Latency distributions use hand-rolled log-spaced
//! buckets rather than a histogram crate (research R4, stdlib-first).

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;

/// Which population a connection belongs to. A stalled viewer's pre-stall
/// measurements stay in `Viewer`; it moves to `Stalled` at the stall moment
/// (research R8, SC-006).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Class {
    Viewer,
    Stalled,
    Poller,
}

impl Class {
    pub fn label(self) -> &'static str {
        match self {
            Class::Viewer => "viewer",
            Class::Stalled => "stalled",
            Class::Poller => "poller",
        }
    }
}

/// Why a connection ended. "Unexpected" for FR-016 = `ServerClosed`, `Error`,
/// or `Refused`; `ClosedByRun` and `Open` are not.
#[derive(Clone, Debug)]
pub enum EndReason {
    Open,
    ClosedByRun,
    ServerClosed,
    Error,
    Refused,
}

impl EndReason {
    pub fn is_unexpected(&self) -> bool {
        matches!(
            self,
            EndReason::ServerClosed | EndReason::Error | EndReason::Refused
        )
    }
}

/// A log-spaced latency histogram in milliseconds. Bucket `k` holds samples in
/// `[2^k, 2^(k+1))` ms, clamped to [`BUCKETS`]; enough resolution for a load
/// report without storing raw samples (whose memory would grow with viewers x
/// ticks -- the failure FR-011 exists to avoid).
const BUCKETS: usize = 24; // up to ~2^24 ms ≈ 4.7 hours, far past any real value

#[derive(Clone)]
pub struct Histogram {
    counts: [u64; BUCKETS],
    total: u64,
}

impl Default for Histogram {
    fn default() -> Self {
        Self {
            counts: [0; BUCKETS],
            total: 0,
        }
    }
}

impl Histogram {
    pub fn record(&mut self, ms: f64) {
        let bucket = if ms < 1.0 {
            0
        } else {
            ((ms.log2()) as usize + 1).min(BUCKETS - 1)
        };
        self.counts[bucket] += 1;
        self.total += 1;
    }

    /// The lower edge (ms) of the bucket holding the `q` quantile. A
    /// conservative, monotone readout: percentiles never overstate speed.
    pub fn percentile(&self, q: f64) -> Option<f64> {
        if self.total == 0 {
            return None;
        }
        let target = (q * self.total as f64).ceil() as u64;
        let mut seen = 0u64;
        for (k, &c) in self.counts.iter().enumerate() {
            seen += c;
            if seen >= target {
                return Some(if k == 0 { 0.0 } else { 2f64.powi(k as i32) });
            }
        }
        None
    }
}

/// One connection's live counters. Cheap atomics so the read loop never locks.
#[derive(Default)]
pub struct ConnStats {
    pub updates: AtomicU64,
    pub skips: AtomicU64,
    pub bytes: AtomicU64,
    pub last_tick: AtomicU64,
    pub have_tick: AtomicBool,
    pub errors: AtomicU64,
    /// Handshake latency in microseconds, recorded once at connect (0 = unset).
    pub handshake_us: AtomicU64,
    /// Most recent inter-update gap in microseconds, for the interval sampler.
    pub last_gap_us: AtomicU64,
}

impl ConnStats {
    pub fn new() -> Arc<Self> {
        Arc::new(Self::default())
    }

    /// Record a received update carrying `tick`; returns the skip count this
    /// update implies (gap in the tick sequence). A decreasing tick means the
    /// world reset -- reported to the caller as a signal, not counted as skips.
    pub fn record_update(&self, tick: u64, bytes: usize, gap_us: u64) -> TickStep {
        self.updates.fetch_add(1, Ordering::Relaxed);
        self.bytes.fetch_add(bytes as u64, Ordering::Relaxed);
        self.last_gap_us.store(gap_us, Ordering::Relaxed);
        let had = self.have_tick.swap(true, Ordering::Relaxed);
        let prev = self.last_tick.swap(tick, Ordering::Relaxed);
        if !had {
            return TickStep::First;
        }
        if tick < prev {
            return TickStep::Reset;
        }
        let gap = tick - prev;
        if gap > 1 {
            let skipped = gap - 1;
            self.skips.fetch_add(skipped, Ordering::Relaxed);
            TickStep::Skipped(skipped)
        } else {
            TickStep::Contiguous
        }
    }
}

/// What one update's tick number meant relative to the previous.
#[derive(Debug, PartialEq, Eq)]
pub enum TickStep {
    First,
    Contiguous,
    Skipped(u64),
    Reset,
}

/// The cadence reference: one healthy connection whose tick timing gives the
/// world's observed tick period (FR-008). If it is lost, the next healthy
/// viewer is promoted and the promotion is noted in the record.
#[derive(Default)]
pub struct CadenceReference {
    id: AtomicU64, // connection id + 1; 0 = unset
    last_tick: AtomicU64,
    last_at_ms: AtomicU64,
    period_ms: AtomicU64, // last observed ms-per-tick * 1000, fixed-point
    promotions: AtomicU64,
}

impl CadenceReference {
    /// Offer a healthy update from connection `id` at `now_ms`. The first
    /// healthy connection to call becomes the reference; others are ignored
    /// until the reference goes silent past `stale_ms`, when the next caller
    /// is promoted.
    pub fn observe(&self, id: u64, tick: u64, now_ms: u64, stale_ms: u64) {
        let cur = self.id.load(Ordering::Relaxed);
        let is_ref = cur == id + 1;
        if !is_ref {
            let stale = cur == 0
                || now_ms.saturating_sub(self.last_at_ms.load(Ordering::Relaxed)) > stale_ms;
            if !stale {
                return;
            }
            // Promote this connection.
            if cur != 0 {
                self.promotions.fetch_add(1, Ordering::Relaxed);
            }
            self.id.store(id + 1, Ordering::Relaxed);
            self.last_tick.store(tick, Ordering::Relaxed);
            self.last_at_ms.store(now_ms, Ordering::Relaxed);
            return;
        }
        let prev_tick = self.last_tick.swap(tick, Ordering::Relaxed);
        let prev_ms = self.last_at_ms.swap(now_ms, Ordering::Relaxed);
        if tick > prev_tick {
            let dt = now_ms.saturating_sub(prev_ms);
            let period = (dt as f64) / ((tick - prev_tick) as f64);
            self.period_ms
                .store((period * 1000.0) as u64, Ordering::Relaxed);
        }
    }

    /// The observed tick period in ms, if the reference has seen two ticks.
    pub fn period_ms(&self) -> Option<f64> {
        let p = self.period_ms.load(Ordering::Relaxed);
        if p == 0 {
            None
        } else {
            Some(p as f64 / 1000.0)
        }
    }

    pub fn promotions(&self) -> u64 {
        self.promotions.load(Ordering::Relaxed)
    }
}

/// One emitted measurement row (data-model.md § IntervalRow). `scope`
/// distinguishes interval rows from derived step/run summaries; unused columns
/// are empty strings at write time, never omitted.
#[derive(Clone, Debug, Default)]
pub struct IntervalRow {
    pub t: f64,
    pub scope: String,
    pub step: Option<u32>,
    pub class: String,
    pub conns_target: u64,
    pub conns_open: u64,
    pub updates: u64,
    pub skips: u64,
    pub bytes: u64,
    pub handshake_p50_ms: Option<f64>,
    pub handshake_p99_ms: Option<f64>,
    pub gap_p50_ms: Option<f64>,
    pub gap_p99_ms: Option<f64>,
    pub cadence_ms: Option<f64>,
    pub poll_p50_ms: Option<f64>,
    pub poll_p99_ms: Option<f64>,
    pub poll_errors: u64,
    pub errors: u64,
    pub unexpected_ends: u64,
    pub gen_fd_headroom: Option<u64>,
    pub gen_lag_ms: Option<f64>,
    pub valid: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skips_are_gaps_in_the_tick_sequence() {
        let s = ConnStats::default();
        assert_eq!(s.record_update(5, 100, 0), TickStep::First);
        assert_eq!(s.record_update(6, 100, 0), TickStep::Contiguous);
        assert_eq!(s.record_update(9, 100, 0), TickStep::Skipped(2));
        assert_eq!(s.skips.load(Ordering::Relaxed), 2);
        assert_eq!(s.record_update(4, 100, 0), TickStep::Reset);
        // A reset does not add to skips.
        assert_eq!(s.skips.load(Ordering::Relaxed), 2);
    }

    #[test]
    fn histogram_percentiles_are_monotone_and_conservative() {
        let mut h = Histogram::default();
        for _ in 0..90 {
            h.record(3.0); // bucket 2 -> lower edge 4.0
        }
        for _ in 0..10 {
            h.record(1000.0);
        }
        let p50 = h.percentile(0.5).unwrap();
        let p99 = h.percentile(0.99).unwrap();
        assert!(p50 <= p99, "p50 {p50} must not exceed p99 {p99}");
        assert!(p50 <= 4.0);
        assert!(p99 >= 512.0);
    }

    #[test]
    fn empty_histogram_has_no_percentile() {
        assert_eq!(Histogram::default().percentile(0.5), None);
    }

    #[test]
    fn cadence_reference_promotes_only_when_stale() {
        let c = CadenceReference::default();
        c.observe(0, 10, 1000, 500);
        c.observe(0, 11, 1800, 500); // ~800ms/tick
        assert!((c.period_ms().unwrap() - 800.0).abs() < 1.0);
        // A different connection is ignored while the reference is fresh.
        c.observe(1, 50, 1850, 500);
        assert_eq!(c.promotions(), 0);
        // After the reference goes stale, the next caller is promoted.
        c.observe(1, 60, 3000, 500);
        assert_eq!(c.promotions(), 1);
    }
}
