//! Generator self-blame: detecting when *Clowder* is the bottleneck, not the
//! server (FR-011). A load test that reports its own exhaustion as the
//! server's failure is worse than useless, so measurements taken while the
//! generator is strained are marked invalid rather than attributed.

use std::sync::atomic::{AtomicU64, Ordering};

/// The generator's file-descriptor ceiling (`RLIMIT_NOFILE`), read once. Every
/// connection is a descriptor, so this bounds concurrency before the server
/// ever does on an unprepared host (research R6).
pub fn nofile_limit() -> Option<u64> {
    // Safe: getrlimit fills a caller-owned struct and returns 0 on success.
    let mut lim = libc::rlimit {
        rlim_cur: 0,
        rlim_max: 0,
    };
    let rc = unsafe { libc::getrlimit(libc::RLIMIT_NOFILE, &mut lim) };
    if rc == 0 {
        // rlim_t is u64 on Linux and macOS but its exact type varies, so the
        // cast is kept and the same-type lint silenced rather than assumed.
        #[allow(clippy::unnecessary_cast)]
        Some(lim.rlim_cur as u64)
    } else {
        None
    }
}

/// Live generator-health signals the sampler consults each interval.
#[derive(Default)]
pub struct SelfWatch {
    limit: u64,
    /// Peak concurrent connections observed, a proxy for descriptors in use.
    peak_conns: AtomicU64,
    /// Count of EMFILE-shaped connection failures (out of descriptors).
    emfile_hits: AtomicU64,
}

impl SelfWatch {
    pub fn new() -> Self {
        SelfWatch {
            limit: nofile_limit().unwrap_or(0),
            ..Default::default()
        }
    }

    pub fn limit(&self) -> u64 {
        self.limit
    }

    pub fn observe_conns(&self, open: u64) {
        self.peak_conns.fetch_max(open, Ordering::Relaxed);
    }

    pub fn note_emfile(&self) {
        self.emfile_hits.fetch_add(1, Ordering::Relaxed);
    }

    /// Descriptors still available, if the limit is known.
    pub fn headroom(&self, open_conns: u64) -> Option<u64> {
        if self.limit == 0 {
            None
        } else {
            Some(self.limit.saturating_sub(open_conns))
        }
    }

    /// True when this interval's measurements should be invalidated (FR-011):
    /// we hit EMFILE, or we are within 20% of the descriptor ceiling, or the
    /// sampler woke late by more than `lag_limit_ms`. The caller passes the
    /// limit as a fraction of the interval, so the threshold scales with
    /// `--interval` rather than being fixed at one cadence.
    pub fn interval_invalid(&self, open_conns: u64, gen_lag_ms: f64, lag_limit_ms: f64) -> bool {
        if self.emfile_hits.load(Ordering::Relaxed) > 0 {
            return true;
        }
        if self.limit != 0 && open_conns as f64 > 0.8 * self.limit as f64 {
            return true;
        }
        gen_lag_ms > lag_limit_ms
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_a_descriptor_limit() {
        // On any dev/CI host this is a positive number; we only assert it is
        // readable and sane, not a specific value.
        if let Some(n) = nofile_limit() {
            assert!(n > 0);
        }
    }

    #[test]
    fn invalidates_on_emfile_and_near_the_ceiling() {
        let mut w = SelfWatch {
            limit: 100,
            ..Default::default()
        };
        assert!(!w.interval_invalid(50, 10.0, 250.0));
        assert!(w.interval_invalid(85, 10.0, 250.0)); // >80% of 100
        assert!(w.interval_invalid(50, 400.0, 250.0)); // sampler lag past limit
        assert!(!w.interval_invalid(50, 400.0, 1250.0)); // same lag, 5s interval
        w = SelfWatch {
            limit: 100,
            ..Default::default()
        };
        w.note_emfile();
        assert!(w.interval_invalid(1, 0.0, 250.0)); // any EMFILE poisons the interval
    }

    #[test]
    fn headroom_needs_a_known_limit() {
        let w = SelfWatch {
            limit: 0,
            ..Default::default()
        };
        assert_eq!(w.headroom(10), None);
        let w = SelfWatch {
            limit: 256,
            ..Default::default()
        };
        assert_eq!(w.headroom(6), Some(250));
    }
}
