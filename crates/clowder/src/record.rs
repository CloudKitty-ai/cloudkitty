//! The run record: one CSV file (contracts/record-format.md).
//!
//! A `#`-prefixed preamble carries the identity stamp and scenario; then one
//! header row; then interval/step/run rows on a single schema distinguished by
//! a `scope` column. `#` lines may also appear after the last row (the outcome
//! and any cadence-reference note), and a parser skips every `#` line wherever
//! it sits.

use std::fmt::Write as _;

use crate::health::HealthThresholds;
use crate::metrics::IntervalRow;
use crate::target::TargetIdentity;

/// The 23-column schema v1, append-only (contract). The header row IS the
/// schema declaration; there is no version key in the preamble.
pub const COLUMNS: &[&str] = &[
    "t",
    "scope",
    "step",
    "class",
    "conns_target",
    "conns_open",
    "updates",
    "skips",
    "bytes",
    "handshake_p50_ms",
    "handshake_p99_ms",
    "gap_p50_ms",
    "gap_p99_ms",
    "cadence_ms",
    "poll_p50_ms",
    "poll_p99_ms",
    "poll_errors",
    "errors",
    "handshake_failures",
    "unexpected_ends",
    "gen_fd_headroom",
    "gen_lag_ms",
    "valid",
];

fn opt(v: Option<f64>) -> String {
    match v {
        Some(x) => format!("{x:.3}"),
        None => String::new(),
    }
}

fn opt_u(v: Option<u64>) -> String {
    v.map(|x| x.to_string()).unwrap_or_default()
}

/// Render one row as a CSV line matching [`COLUMNS`] exactly. Every column is
/// present; inapplicable ones are empty.
pub fn row_line(r: &IntervalRow) -> String {
    let mut s = String::new();
    let _ = write!(
        s,
        "{:.3},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
        r.t,
        r.scope,
        r.step.map(|x| x.to_string()).unwrap_or_default(),
        r.class,
        r.conns_target,
        r.conns_open,
        r.updates,
        r.skips,
        r.bytes,
        opt(r.handshake_p50_ms),
        opt(r.handshake_p99_ms),
        opt(r.gap_p50_ms),
        opt(r.gap_p99_ms),
        opt(r.cadence_ms),
        opt(r.poll_p50_ms),
        opt(r.poll_p99_ms),
        r.poll_errors,
        r.errors,
        r.handshake_failures,
        r.unexpected_ends,
        opt_u(r.gen_fd_headroom),
        opt(r.gen_lag_ms),
        r.valid,
    );
    s
}

/// Assembles the record incrementally, then serializes it as one string the
/// caller writes to `--out`.
pub struct Record {
    preamble: Vec<String>,
    rows: Vec<IntervalRow>,
    trailer: Vec<String>,
}

impl Record {
    // The preamble genuinely carries this many distinct facts (contract); a
    // struct would just be unpacked at the one call site.
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        tool_version: &str,
        started_at: &str,
        mode: &str,
        scenario_lines: &[String],
        thresholds: &HealthThresholds,
        target: &str,
        id: &TargetIdentity,
        nofile_limit: Option<u64>,
    ) -> Record {
        let mut p = Vec::new();
        p.push(format!("# clowder: {tool_version}"));
        p.push(format!("# started_at: {started_at}"));
        p.push(format!("# mode: {mode}"));
        for line in scenario_lines {
            p.push(format!("# scenario: {line}"));
        }
        let mark = if thresholds.is_default() {
            ""
        } else {
            " (non-default)"
        };
        p.push(format!(
            "# health_thresholds: max_skips={} cadence_tolerance={} max_handshake_failures={} max_unexpected_ends={}{}",
            thresholds.max_skips,
            thresholds.cadence_tolerance,
            thresholds.max_handshake_failures,
            thresholds.max_unexpected_ends,
            mark
        ));
        p.push(format!("# target: {target}"));
        p.push(format!("# config_sha256: {}", id.config_sha256));
        p.push(format!("# tick_ms: {}", opt_u(id.tick_ms)));
        p.push(format!(
            "# roster_size: {}",
            id.roster_size.map(|x| x.to_string()).unwrap_or_default()
        ));
        p.push(format!(
            "# world_dims: {}",
            id.world_dims
                .map(|(w, h)| format!("{w}x{h}"))
                .unwrap_or_default()
        ));
        p.push(format!("# first_payload_bytes: {}", id.first_payload_bytes));
        p.push(format!("# nofile_limit: {}", opt_u(nofile_limit)));
        Record {
            preamble: p,
            rows: Vec::new(),
            trailer: Vec::new(),
        }
    }

    pub fn push_row(&mut self, r: IntervalRow) {
        self.rows.push(r);
    }

    /// A `# note:` line appended after the data (e.g. cadence-reference
    /// promotion). Parsers skip it like any `#` line.
    pub fn note(&mut self, text: &str) {
        self.trailer.push(format!("# note: {text}"));
    }

    /// Written at run end: outcome and the classification list.
    pub fn finish(&mut self, outcome: &str, classification: &[String]) {
        self.trailer.push(format!("# outcome: {outcome}"));
        let cls = if classification.is_empty() {
            "healthy".to_string()
        } else {
            classification.join(",")
        };
        self.trailer.push(format!("# classification: {cls}"));
    }

    pub fn serialize(&self) -> String {
        let mut out = String::new();
        for line in &self.preamble {
            out.push_str(line);
            out.push('\n');
        }
        out.push_str(&COLUMNS.join(","));
        out.push('\n');
        for r in &self.rows {
            out.push_str(&row_line(r));
            out.push('\n');
        }
        for line in &self.trailer {
            out.push_str(line);
            out.push('\n');
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn identity() -> TargetIdentity {
        TargetIdentity {
            config_sha256: "abc123".into(),
            tick_ms: Some(200),
            roster_size: Some(2),
            world_dims: Some((12, 12)),
            first_payload_bytes: 400,
        }
    }

    #[test]
    fn every_row_has_every_column() {
        let r = IntervalRow {
            t: 1.0,
            scope: "interval".into(),
            class: "viewer".into(),
            valid: true,
            ..Default::default()
        };
        let line = row_line(&r);
        // 22 columns => 21 commas.
        assert_eq!(line.matches(',').count(), COLUMNS.len() - 1);
    }

    #[test]
    fn preamble_marks_non_default_thresholds() {
        let t = HealthThresholds {
            max_skips: 3,
            ..Default::default()
        };
        let rec = Record::new(
            "clowder 0.1.0",
            "2026-08-12T00:00:00Z",
            "ramp",
            &["--to 100".into()],
            &t,
            "http://127.0.0.1:8090",
            &identity(),
            Some(256),
        );
        let s = rec.serialize();
        assert!(s.contains("(non-default)"));
        assert!(s.contains("# config_sha256: abc123"));
        assert!(s.contains("# scenario: --to 100"));
    }

    #[test]
    fn default_thresholds_are_not_marked() {
        let rec = Record::new(
            "c",
            "t",
            "soak",
            &[],
            &HealthThresholds::default(),
            "http://127.0.0.1:8090",
            &identity(),
            None,
        );
        let s = rec.serialize();
        assert!(!s.contains("(non-default)"));
        assert!(s.contains("# nofile_limit: \n") || s.contains("# nofile_limit: "));
    }

    #[test]
    fn header_row_declares_the_schema_and_outcome_trails() {
        let mut rec = Record::new(
            "c",
            "t",
            "soak",
            &[],
            &HealthThresholds::default(),
            "x",
            &identity(),
            None,
        );
        rec.push_row(IntervalRow {
            t: 0.0,
            scope: "interval".into(),
            class: "viewer".into(),
            valid: true,
            ..Default::default()
        });
        rec.note("cadence reference promoted at t=5.0");
        rec.finish("completed", &[]);
        let s = rec.serialize();
        let header = s.lines().find(|l| l.starts_with("t,scope")).unwrap();
        assert_eq!(header, COLUMNS.join(","));
        assert!(s.contains("# note: cadence reference promoted at t=5.0"));
        assert!(s.contains("# outcome: completed"));
        assert!(s.contains("# classification: healthy"));
    }
}
