//! Every TOML the repo ships must load through `Config` validation.
//!
//! Spec 022/023 review net: the loud-retirement posture only protects a
//! config that something actually parses, and the eval-suite manifest guard
//! compares bytes without parsing. This sweep is what catches a shipped
//! config that a future key migration misses (it would have caught three in
//! the 022/023 batch). TOMLs that are not world configs (tool manifests,
//! the eval-suite hash manifest, the compiler pin) are excluded by name in
//! `collect`.

use cloudkitty_core::Config;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .unwrap()
}

/// Collects `*.toml` under `dir`, skipping tool manifests. The repo root is
/// scanned non-recursively on purpose: untracked scratch directories (e.g.
/// the owner's worlds.backup/) may hold deliberately-retired configs.
fn collect(dir: &Path, recursive: bool, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();
        let name = entry.file_name();
        if path.is_dir() {
            if recursive && !name.to_string_lossy().starts_with('.') {
                collect(&path, true, out);
            }
        } else if path.extension().is_some_and(|e| e == "toml")
            && name != "Cargo.toml"
            && name != "pyproject.toml"
            && name != "manifest.toml"
            // The compiler pin. Same category as the manifests above -- a
            // root TOML that is not a world config -- and it lands in the
            // root sweep the moment it exists, which is how this test
            // caught it.
            && name != "rust-toolchain.toml"
        {
            out.push(path);
        }
    }
}

/// Pinned-generation directories the sweep skips (spec 028): the root
/// manifest names frozen records of earlier engine generations -- prereg
/// families, committed-results configs, measurement records. The manifest's
/// own rule: only pinned-generation dirs may appear there; everything new
/// is in scope by default.
fn excluded_dirs(root: &Path) -> Vec<PathBuf> {
    let manifest = root.join("config-sweep-exclusions.txt");
    let text = std::fs::read_to_string(&manifest)
        .unwrap_or_else(|e| panic!("{} unreadable: {e}", manifest.display()));
    text.lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .map(|l| {
            let dir = l.split_whitespace().next().unwrap();
            let path = root.join(dir);
            assert!(
                path.is_dir(),
                "manifest names a directory that does not exist: {dir}"
            );
            path
        })
        .collect()
}

/// Drops the files git ignores (handover (e), 2026-09-13): a lab checkout
/// carries gitignored record configs of earlier engine generations that no
/// longer parse, and the exclusion manifest cannot cover them -- it asserts
/// every named directory exists, and those records exist only on the lab
/// machine. Untracked-but-NOT-ignored files stay in scope (the manifest
/// header's rule: new experiment output loads on the current engine by
/// default). If git is unavailable or errors, the list is left unfiltered,
/// so CI behavior -- which only ever sees the tracked tree -- is unchanged.
fn drop_gitignored(root: &Path, files: &mut Vec<PathBuf>) {
    use std::io::Write;
    use std::process::{Command, Stdio};
    let Ok(mut child) = Command::new("git")
        .args(["check-ignore", "--stdin", "-z"])
        .current_dir(root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
    else {
        return;
    };
    let mut input = Vec::new();
    for f in files.iter() {
        input.extend_from_slice(f.as_os_str().as_encoded_bytes());
        input.push(0);
    }
    if child.stdin.take().unwrap().write_all(&input).is_err() {
        let _ = child.wait();
        return;
    }
    let Ok(out) = child.wait_with_output() else {
        return;
    };
    // check-ignore: 0 = some paths ignored, 1 = none; anything else means
    // the answer is unusable, and no filtering beats wrong filtering.
    if !matches!(out.status.code(), Some(0 | 1)) {
        return;
    }
    let ignored: std::collections::HashSet<&[u8]> = out
        .stdout
        .split(|b| *b == 0)
        .filter(|s| !s.is_empty())
        .collect();
    files.retain(|f| !ignored.contains(f.as_os_str().as_encoded_bytes()));
}

#[test]
fn every_shipped_toml_loads_through_validation() {
    let root = repo_root();
    let mut files = Vec::new();
    collect(&root, false, &mut files);
    for sub in ["evals", "experiments", "specs"] {
        let dir = root.join(sub);
        if dir.is_dir() {
            collect(&dir, true, &mut files);
        }
    }
    let excluded = excluded_dirs(&root);
    files.retain(|f| !excluded.iter().any(|dir| f.starts_with(dir)));
    drop_gitignored(&root, &mut files);
    assert!(
        files.iter().any(|p| p.ends_with("cloudkitty.toml")),
        "the served config is in the sweep"
    );
    for file in files {
        let text = std::fs::read_to_string(&file).unwrap();
        let config: Config = toml::from_str(&text)
            .unwrap_or_else(|e| panic!("{} no longer parses: {e}", file.display()));
        config
            .validate()
            .unwrap_or_else(|e| panic!("{} no longer validates: {e}", file.display()));
    }
}

/// Spec 041 US2 (the riders-partial contract) on the SERVED config: every
/// cuddle rider delivers less than the measured mean need (5.1, the
/// 2026-08-25 census) in one minimum-length scene from a single slot, and
/// the drip sits below the mutual within each activity (the comment-
/// carried convention). `rest_mutual_relief` is deliberately absent: the
/// specialist is supposed to saturate.
///
/// Written at the engine-sibling commit, where it is RED against the
/// un-repriced toml by design -- the reprice diff (a pure config change)
/// is what turns it green, which is this guard's rule-5 red/green cycle.
#[test]
fn the_served_cuddle_riders_are_partial_and_tier_ordered() {
    let text = std::fs::read_to_string(repo_root().join("cloudkitty.toml")).unwrap();
    let config: Config = toml::from_str(&text).unwrap();
    config.validate().expect("the served config validates");
    let a = &config.actions;
    const MEASURED_MEAN_CUDDLE_NEED: f32 = 5.1;

    let sleep_min = a.durations.sleep.min as f32;
    let cuddle_min = a.durations.cuddle.min as f32;
    // Spec 054: the flat groom_cuddle_relief (and its temporary 2.0 bump,
    // handoff 2026-08-31) is retired -- the served toml is scrubbed of the
    // key and the groomer is paid by the delivered-relief curve at engine
    // defaults (deliberately unpinned: the defaults ARE the calibration,
    // and pinning them would only add stamp-drift surface).
    assert!(
        !text.contains("groom_cuddle_relief ="),
        "the served toml must stay scrubbed of the retired flat dial"
    );
    assert_eq!(a.groom_cuddle_floor, 0.25, "served = engine default floor");
    assert_eq!(a.groom_cuddle_slope, 3.5, "served = engine default slope");
    assert_eq!(
        a.groom_cuddle_ceiling, 2.0,
        "served = engine default ceiling"
    );
    // The groom row returns to the rider loop (the retirement discharges
    // the handoff's restore note): the rider component of groom pay is the
    // charm FLOOR -- above-floor income is delivered-dirt-bounded, not a
    // rider -- and a minimum groom scene of floor ticks must not finish
    // the mean need.
    let bath_min = a.durations.bath.min as f32;
    for (name, per_scene) in [
        ("cosleep_drip_relief", a.cosleep_drip_relief * sleep_min),
        ("cosleep_mutual_relief", a.cosleep_mutual_relief * sleep_min),
        ("rest_drip_relief", a.rest_drip_relief * cuddle_min),
        (
            "groom_cuddle_floor (charm rider)",
            a.groom_cuddle_floor * bath_min,
        ),
    ] {
        assert!(
            per_scene < MEASURED_MEAN_CUDDLE_NEED,
            "{name}: a minimum scene delivers {per_scene} from one slot -- \
             a rider must not finish the mean need ({MEASURED_MEAN_CUDDLE_NEED})"
        );
    }
    assert!(
        a.cosleep_drip_relief < a.cosleep_mutual_relief,
        "cosleep tier order"
    );
    // US2/AC2's structural half: the served co-sleep edge over solo sleep
    // exists only while the drip pays something -- zero is a legal config
    // value, so the edge needs its own pin.
    assert!(
        a.cosleep_drip_relief > 0.0,
        "co-sleep must keep a strictly positive edge over solo sleep"
    );
    assert!(a.rest_drip_relief < a.rest_mutual_relief, "rest tier order");
}

/// Spec 054 SC-006: the frozen evals/v2 and current evals/v3 worlds pin
/// the retired flat `groom_cuddle_relief` -- they must keep loading
/// BYTE-UNCHANGED through the recognised-but-inert legacy key (the sweep
/// above already validates them; this guard pins that the legacy key is
/// really present and really inert, so a future "clean up the dead key"
/// pass cannot silently break the frozen suite).
#[test]
fn the_frozen_eval_suites_still_pin_the_legacy_groom_key_and_load() {
    let root = repo_root();
    let mut checked = 0;
    for suite in ["evals/v2", "evals/v3"] {
        for entry in std::fs::read_dir(root.join(suite)).unwrap() {
            let path = entry.unwrap().path();
            if path.extension().is_none_or(|e| e != "toml")
                || path.file_name().is_some_and(|n| n == "manifest.toml")
            {
                continue;
            }
            let text = std::fs::read_to_string(&path).unwrap();
            assert!(
                text.contains("groom_cuddle_relief"),
                "{} lost its legacy pin -- frozen suites are never edited",
                path.display()
            );
            let config: Config = toml::from_str(&text)
                .unwrap_or_else(|e| panic!("{} no longer parses: {e}", path.display()));
            config
                .validate()
                .unwrap_or_else(|e| panic!("{} no longer validates: {e}", path.display()));
            // Inert: whatever the pin says, the pay is the curve's.
            assert_eq!(
                config.actions.groom_cuddle_pay(0.0),
                config.actions.groom_cuddle_floor,
                "{}: the legacy pin must not move the curve",
                path.display()
            );
            checked += 1;
        }
    }
    assert_eq!(checked, 12, "both suites fully swept (6 worlds each)");
}

/// Removes the self-test's scratch subtree even when the test panics.
struct RemoveOnDrop(PathBuf);
impl Drop for RemoveOnDrop {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// Self-test for `drop_gitignored`: plants a gitignored, deliberately
/// unparseable TOML under a swept root and proves the filter -- and only
/// the filter -- keeps it out of the sweep. The fixture lives under a
/// `raw/` directory (gitignored at the root: `experiments/**/raw/`), so
/// the concurrently-running sweep test filters it by path and never reads
/// it; the directory name is unique to this binary so the rl sweep's
/// self-test can never share the path.
#[test]
fn the_sweep_drops_gitignored_files_and_only_those() {
    let root = repo_root();
    let scratch = root.join("experiments/sweep-skip-selftest-core");
    let _cleanup = RemoveOnDrop(scratch.clone());
    let dir = scratch.join("raw");
    std::fs::create_dir_all(&dir).unwrap();
    let fixture = dir.join("retired-generation.toml");
    std::fs::write(
        &fixture,
        "cuddle_relief = 1.0 # retired 2.x key: must never reach the parser\n",
    )
    .unwrap();

    let mut files = Vec::new();
    collect(&root.join("experiments"), true, &mut files);
    assert!(
        files.contains(&fixture),
        "collect sees the gitignored fixture pre-filter"
    );
    let tracked = root.join("cloudkitty.toml");
    files.push(tracked.clone());
    drop_gitignored(&root, &mut files);
    assert!(
        !files.contains(&fixture),
        "the gitignored fixture must be dropped from the sweep"
    );
    assert!(
        files.contains(&tracked),
        "a tracked config survives the filter"
    );
}
