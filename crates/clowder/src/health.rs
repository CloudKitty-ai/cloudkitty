//! The health definition and the degradation taxonomy.
//!
//! FR-016: a ramp step is healthy iff, across the whole hold, healthy viewers
//! skipped nothing, the observed tick cadence stayed within tolerance, no
//! handshake failed, and no connection ended unexpectedly. Every threshold is
//! a run parameter; the defaults define the published ceiling. FR-012: when a
//! step (or run) is not healthy, the failure is named from a closed set of
//! signatures shared by the record and the human summary.

use crate::metrics::IntervalRow;

/// The FR-016 thresholds. Defaults are the strict published-ceiling values; a
/// record produced under other values marks them non-default (contract).
#[derive(Clone, Debug)]
pub struct HealthThresholds {
    pub max_skips: u64,
    pub cadence_tolerance: f64,
    pub max_handshake_failures: u64,
    pub max_unexpected_ends: u64,
}

impl Default for HealthThresholds {
    fn default() -> Self {
        HealthThresholds {
            max_skips: 0,
            cadence_tolerance: 0.05,
            max_handshake_failures: 0,
            max_unexpected_ends: 0,
        }
    }
}

impl HealthThresholds {
    pub fn is_default(&self) -> bool {
        let d = HealthThresholds::default();
        self.max_skips == d.max_skips
            && (self.cadence_tolerance - d.cadence_tolerance).abs() < f64::EPSILON
            && self.max_handshake_failures == d.max_handshake_failures
            && self.max_unexpected_ends == d.max_unexpected_ends
    }
}

/// A named failure pattern (FR-012). `GeneratorBottleneck` overrides
/// attribution: it is never the server's fault.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Signature {
    SkippedUpdates,
    RisingLag,
    UnstableCadence,
    HandshakeFailures,
    ConnectionDrops,
    ServerUnresponsive,
    GeneratorBottleneck,
}

impl Signature {
    pub fn label(self) -> &'static str {
        match self {
            Signature::SkippedUpdates => "skipped_updates",
            Signature::RisingLag => "rising_lag",
            Signature::UnstableCadence => "unstable_cadence",
            Signature::HandshakeFailures => "handshake_failures",
            Signature::ConnectionDrops => "connection_drops",
            Signature::ServerUnresponsive => "server_unresponsive",
            Signature::GeneratorBottleneck => "generator_bottleneck",
        }
    }
}

/// The verdict on one step's worth of interval rows.
#[derive(Clone, Debug)]
pub struct StepVerdict {
    pub healthy: bool,
    pub signatures: Vec<Signature>,
    pub first_degraded: Option<Signature>,
}

/// Evaluate a step (or any window) against the thresholds, over its VALID
/// interval rows only (FR-011: invalid rows never decide health). `nominal_ms`
/// is the world's advertised tick period, for the cadence check.
pub fn evaluate(
    rows: &[IntervalRow],
    nominal_ms: Option<f64>,
    t: &HealthThresholds,
) -> StepVerdict {
    let valid: Vec<&IntervalRow> = rows.iter().filter(|r| r.valid).collect();

    // If the generator invalidated everything, that is the finding -- the
    // server is not implicated.
    if !rows.is_empty() && valid.is_empty() {
        return StepVerdict {
            healthy: false,
            signatures: vec![Signature::GeneratorBottleneck],
            first_degraded: Some(Signature::GeneratorBottleneck),
        };
    }

    let mut sigs = Vec::new();

    let healthy_skips: u64 = valid
        .iter()
        .filter(|r| r.class == "viewer" || r.class == "all")
        .map(|r| r.skips)
        .sum();
    if healthy_skips > t.max_skips {
        sigs.push(Signature::SkippedUpdates);
    }

    // Handshake failures are connections that never established (FR-016),
    // distinct from mid-stream drops and from schema drift -- the raw `errors`
    // column conflated all three.
    let handshake_fail: u64 = valid.iter().map(|r| r.handshake_failures).sum();
    if handshake_fail > t.max_handshake_failures {
        sigs.push(Signature::HandshakeFailures);
    }

    let unexpected: u64 = valid.iter().map(|r| r.unexpected_ends).sum();
    if unexpected > t.max_unexpected_ends {
        sigs.push(Signature::ConnectionDrops);
    }

    if let Some(nominal) = nominal_ms {
        let worst = valid
            .iter()
            .filter_map(|r| r.cadence_ms)
            .map(|c| (c - nominal).abs() / nominal)
            .fold(0.0f64, f64::max);
        if worst > t.cadence_tolerance {
            sigs.push(Signature::UnstableCadence);
        }
        // Rising lag: a healthy viewer's tail inter-update gap running well
        // past the tick period means updates are arriving late even when the
        // tick sequence has no holes (distinct from skips).
        let laggy = valid
            .iter()
            .filter(|r| r.class == "viewer" || r.class == "all")
            .filter_map(|r| r.gap_p99_ms)
            .any(|g| g > 2.0 * nominal);
        if laggy {
            sigs.push(Signature::RisingLag);
        }
    }

    // A window with open connections but zero updates on valid rows reads as
    // the server having stopped answering.
    let had_conns = valid.iter().any(|r| r.conns_open > 0);
    let any_updates = valid.iter().any(|r| r.updates > 0);
    if had_conns && !any_updates {
        sigs.push(Signature::ServerUnresponsive);
    }

    // Any invalid interval mixed in flags generator strain alongside whatever
    // the valid rows showed.
    if rows.iter().any(|r| !r.valid) {
        sigs.push(Signature::GeneratorBottleneck);
    }

    StepVerdict {
        healthy: sigs.is_empty(),
        first_degraded: sigs.first().copied(),
        signatures: sigs,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn row(class: &str, skips: u64, cadence: f64, valid: bool) -> IntervalRow {
        IntervalRow {
            class: class.to_string(),
            skips,
            updates: 5,
            conns_open: 10,
            cadence_ms: Some(cadence),
            valid,
            ..Default::default()
        }
    }

    #[test]
    fn a_clean_step_is_healthy() {
        let rows = vec![row("viewer", 0, 800.0, true), row("viewer", 0, 802.0, true)];
        let v = evaluate(&rows, Some(800.0), &HealthThresholds::default());
        assert!(v.healthy, "signatures: {:?}", v.signatures);
    }

    #[test]
    fn one_skip_fails_at_default_thresholds() {
        let rows = vec![row("viewer", 0, 800.0, true), row("viewer", 1, 800.0, true)];
        let v = evaluate(&rows, Some(800.0), &HealthThresholds::default());
        assert!(!v.healthy);
        assert_eq!(v.first_degraded, Some(Signature::SkippedUpdates));
    }

    #[test]
    fn cadence_beyond_tolerance_is_unstable() {
        // 900ms observed vs 800 nominal = 12.5% > 5%.
        let rows = vec![row("viewer", 0, 900.0, true)];
        let v = evaluate(&rows, Some(800.0), &HealthThresholds::default());
        assert!(v.signatures.contains(&Signature::UnstableCadence));
    }

    #[test]
    fn all_invalid_blames_the_generator_not_the_server() {
        let rows = vec![row("viewer", 99, 2000.0, false)];
        let v = evaluate(&rows, Some(800.0), &HealthThresholds::default());
        assert!(!v.healthy);
        assert_eq!(v.signatures, vec![Signature::GeneratorBottleneck]);
    }

    #[test]
    fn loosened_skip_threshold_tolerates_skips() {
        let rows = vec![row("viewer", 3, 800.0, true)];
        let t = HealthThresholds {
            max_skips: 5,
            ..Default::default()
        };
        assert!(!t.is_default());
        assert!(evaluate(&rows, Some(800.0), &t).healthy);
    }

    #[test]
    fn stalled_class_skips_do_not_fail_the_step() {
        // SC-006: a stalled viewer's skips are its own; healthy viewers clean.
        let rows = vec![
            row("viewer", 0, 800.0, true),
            row("stalled", 40, 800.0, true),
        ];
        let v = evaluate(&rows, Some(800.0), &HealthThresholds::default());
        assert!(
            v.healthy,
            "stalled skips must not fail the step: {:?}",
            v.signatures
        );
    }
}
