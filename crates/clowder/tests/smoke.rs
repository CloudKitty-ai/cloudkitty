//! The integration smoke test (spec 029 T018/T019, research R10).
//!
//! Boots the REAL `cloudkitty-server` binary on `127.0.0.1:0` with the
//! committed scripted-only tiny world, reads the chosen port from the server's
//! startup log line (there is no address endpoint), runs a seconds-long
//! micro-ramp, and asserts exit 0 + a record that parses per the contract.
//! It does NOT assert zero skips: a fast test tick on a shared runner can drop
//! an update to a scheduler stall, which would flake. A second test kills the
//! server mid-run and asserts the interrupted-target path (exit 3).
//!
//! Both exercise the server binary unmodified, preserving FR-009.

// boot_server returns the Child for the caller to kill()+wait(); clippy cannot
// see the wait across the function boundary, and OS cleanup covers the panic
// paths in a test.
#![allow(clippy::zombie_processes)]

use std::io::Read;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

/// The built `cloudkitty-server` binary, found beside this test binary in the
/// workspace target directory (target/debug/deps/<test> -> target/debug/).
fn server_bin() -> PathBuf {
    let mut dir = std::env::current_exe().expect("test exe path");
    dir.pop(); // the test binary's file name
    if dir.ends_with("deps") {
        dir.pop();
    }
    let bin = dir.join(format!("cloudkitty-server{}", std::env::consts::EXE_SUFFIX));
    assert!(
        bin.exists(),
        "server binary not found at {bin:?}; run `cargo build` first"
    );
    bin
}

fn tiny_world() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/tiny-world.toml")
}

fn clowder_bin() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_clowder"))
}

/// Boot the server and return (child, port, logfile). The log (stdout+stderr)
/// is redirected to a temp file we poll for the bound port.
fn boot_server(snapshot: &PathBuf) -> (Child, u16, tempfile::NamedTempFile) {
    let log = tempfile::NamedTempFile::new().expect("temp log");
    let out = log.reopen().expect("reopen log for stdout");
    let err = log.reopen().expect("reopen log for stderr");
    let child = Command::new(server_bin())
        .arg("--config")
        .arg(tiny_world())
        .arg("--snapshot")
        .arg(snapshot)
        .arg("--fresh")
        .stdout(Stdio::from(out))
        .stderr(Stdio::from(err))
        .spawn()
        .expect("spawn server");

    let deadline = Instant::now() + Duration::from_secs(15);
    loop {
        let mut s = String::new();
        log.reopen().unwrap().read_to_string(&mut s).ok();
        if let Some(port) = parse_port(&s) {
            return (child, port, log);
        }
        assert!(
            Instant::now() < deadline,
            "server never logged a port; log:\n{s}"
        );
        std::thread::sleep(Duration::from_millis(100));
    }
}

fn parse_port(log: &str) -> Option<u16> {
    let marker = "http://127.0.0.1:";
    let idx = log.find(marker)? + marker.len();
    let rest = &log[idx..];
    let end = rest
        .find(|c: char| !c.is_ascii_digit())
        .unwrap_or(rest.len());
    rest[..end].parse().ok()
}

#[test]
fn micro_ramp_completes_and_the_record_parses() {
    let snap = std::env::temp_dir().join("clowder-smoke-ramp.json");
    let (mut server, port, _log) = boot_server(&snap);

    let record = std::env::temp_dir().join("clowder-smoke-ramp.csv");
    let status = Command::new(clowder_bin())
        .args([
            "ramp",
            "--to",
            "20",
            "--step",
            "10",
            "--hold",
            "2",
            "--target",
            &format!("http://127.0.0.1:{port}"),
            "--out",
            record.to_str().unwrap(),
        ])
        .status()
        .expect("run clowder");

    let _ = server.kill();
    let _ = server.wait();

    assert_eq!(status.code(), Some(0), "ramp should complete (exit 0)");

    let body = std::fs::read_to_string(&record).expect("record written");
    assert_record_parses(&body);
    assert!(
        body.contains("# outcome: completed"),
        "outcome should be completed:\n{}",
        tail(&body)
    );
    // Identity stamp landed.
    assert!(body.contains("# tick_ms: 200"));
    assert!(body.contains("# roster_size: 2"));
    assert!(body.contains("# config_sha256: "));
    // Cadence tracked the world.
    assert!(
        body.lines()
            .any(|l| l.contains(",viewer,") && l.contains("200")),
        "cadence near 200ms expected"
    );
}

#[test]
fn killing_the_server_mid_run_is_an_interruption() {
    let snap = std::env::temp_dir().join("clowder-smoke-interrupt.json");
    let (mut server, port, _log) = boot_server(&snap);

    let record = std::env::temp_dir().join("clowder-smoke-interrupt.csv");
    let mut run = Command::new(clowder_bin())
        .args([
            "soak",
            "--viewers",
            "15",
            "--duration",
            "8",
            "--target",
            &format!("http://127.0.0.1:{port}"),
            "--out",
            record.to_str().unwrap(),
        ])
        .spawn()
        .expect("spawn clowder");

    // Let the swarm establish, then kill the target out from under it.
    std::thread::sleep(Duration::from_secs(2));
    let _ = server.kill();
    let _ = server.wait();

    let status = run.wait().expect("clowder finishes");
    let body = std::fs::read_to_string(&record).unwrap_or_default();
    // The record is preserved with the connections it saw before the drop.
    assert_record_parses(&body);
    assert_eq!(
        status.code(),
        Some(3),
        "a target that dies mid-run is exit 3:\n{}",
        tail(&body)
    );
    assert!(body.contains("# outcome: interrupted"));
}

/// Every data row has exactly the contract's column count, and the header is
/// the schema declaration.
fn assert_record_parses(body: &str) {
    let header = body
        .lines()
        .find(|l| l.starts_with("t,scope,"))
        .expect("header row");
    let cols = header.split(',').count();
    assert_eq!(cols, 23, "schema v1 has 23 columns");
    for line in body.lines() {
        if line.starts_with('#') || line.starts_with("t,scope,") || line.trim().is_empty() {
            continue;
        }
        assert_eq!(
            line.split(',').count(),
            cols,
            "every row has every column: {line}"
        );
    }
}

fn tail(s: &str) -> String {
    s.lines().rev().take(6).collect::<Vec<_>>().join("\n")
}
