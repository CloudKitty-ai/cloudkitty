//! Spec 067 FR-011, the collector's own rule-5 red (Experiments' consent
//! 2026-10-26, condition 1), widened by the owner's observer-stream ruling
//! (2026-10-27: nothing that acts learns from a needy world): a config
//! seating a needy kitty records NO demonstration row from ANY seat, the
//! refusal is logged once, meta.json names the seat that does not teach
//! (condition 2), and `--trace` keeps every seat's rows.
//!
//! The control is the same config with that seat on `teacher`, the first
//! onset placed past the end of the run: until its first onset a needy
//! seat decides as the teacher, so the two worlds are the same world (spec
//! 067 SC-002) and only the refusal differs.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn repo_config() -> String {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../cloudkitty.toml");
    fs::read_to_string(path).expect("the served config is readable")
}

/// The served config with its first kitty on `behavior`; a needy seat
/// gets an out-of-reach first onset and its exact acknowledgement.
fn seat_first_kitty(behavior: &str) -> String {
    let text = repo_config();
    let (head, tail) = text
        .split_once("behavior = \"")
        .expect("a kitty behaviour line");
    let rest = tail.split_once('"').expect("closing quote").1;
    let mut out = format!("{head}behavior = \"{behavior}\"{rest}");
    if behavior == "needy" {
        out.push_str(
            "\n[needy]\nonset_levels = [1000, 1001, 1002, 1003, 1004, 1005]\n\
             \n[welfare_hazard]\nacknowledged = [\"needy\"]\n",
        );
    }
    out
}

/// The data of a little-endian npy file after its header.
fn npy_data(path: &Path) -> Vec<u8> {
    let bytes = fs::read(path).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
    assert_eq!(&bytes[..6], b"\x93NUMPY", "an npy file");
    let header_len = u16::from_le_bytes([bytes[8], bytes[9]]) as usize;
    bytes[10 + header_len..].to_vec()
}

fn u32s(path: &Path) -> Vec<u32> {
    npy_data(path)
        .chunks_exact(4)
        .map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect()
}

fn u16s(path: &Path) -> Vec<u16> {
    npy_data(path)
        .chunks_exact(2)
        .map(|c| u16::from_le_bytes([c[0], c[1]]))
        .collect()
}

struct Run {
    rollout: PathBuf,
    stderr: String,
}

const TICKS: usize = 60;

fn collect(scratch: &Path, name: &str, config: &str) -> Run {
    let config_path = scratch.join(format!("{name}.toml"));
    fs::write(&config_path, config).unwrap();
    let out_dir = scratch.join(name);
    let output = Command::new(env!("CARGO_BIN_EXE_bc-collect"))
        .args(["--config", config_path.to_str().unwrap()])
        .args(["--rollouts", "1", "--ticks", &TICKS.to_string(), "--trace"])
        .arg("--out-dir")
        .arg(&out_dir)
        .output()
        .expect("the collector runs");
    let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
    assert!(
        output.status.success(),
        "{name}: collector failed: {stderr}"
    );
    Run {
        rollout: out_dir.join("config-00-rollout-00"),
        stderr,
    }
}

#[test]
fn a_needy_world_records_no_rows_from_any_seat_and_the_run_says_so() {
    let scratch = std::env::temp_dir().join(format!("bc-collect-needy-{}", std::process::id()));
    let _ = fs::remove_dir_all(&scratch);
    fs::create_dir_all(&scratch).unwrap();

    let needy = collect(&scratch, "needy", &seat_first_kitty("needy"));
    let teacher = collect(&scratch, "teacher", &seat_first_kitty("teacher"));

    let (kn, kt) = (
        u32s(&needy.rollout.join("kitty.npy")),
        u32s(&teacher.rollout.join("kitty.npy")),
    );
    let ln = u16s(&needy.rollout.join("label.npy"));
    let roster: Vec<u32> = (1..=5).collect();
    for id in &roster {
        assert!(
            kt.contains(id),
            "staged: on teacher, seat {id} records rows"
        );
    }
    assert!(
        kn.is_empty() && ln.is_empty(),
        "no seat records a demonstration row in a needy world: {} rows",
        kn.len()
    );
    for (run, name) in [(&needy, "needy"), (&teacher, "teacher")] {
        let trace = u32s(&run.rollout.join("trace_kitty.npy"));
        for id in &roster {
            assert_eq!(
                trace.iter().filter(|k| *k == id).count(),
                TICKS,
                "{name}: the trace keeps seat {id} on every tick"
            );
        }
    }

    let meta = fs::read_to_string(needy.rollout.join("meta.json")).unwrap();
    assert!(
        meta.contains("\"teachers_refused\": [1]"),
        "meta.json names the refused seat: {meta}"
    );
    let plain_meta = fs::read_to_string(teacher.rollout.join("meta.json")).unwrap();
    assert!(
        plain_meta.contains("\"teachers_refused\": []"),
        "and says none when none: {plain_meta}"
    );
    assert_eq!(
        needy
            .stderr
            .matches("refusing teacher rows for seat(s) [1]")
            .count(),
        1,
        "the refusal is logged once: {}",
        needy.stderr
    );
    assert!(!teacher.stderr.contains("refusing teacher rows"));
    let _ = fs::remove_dir_all(&scratch);
}
