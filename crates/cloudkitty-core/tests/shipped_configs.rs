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
    let bath_min = a.durations.bath.min as f32;
    let cuddle_min = a.durations.cuddle.min as f32;
    for (name, per_scene) in [
        ("cosleep_drip_relief", a.cosleep_drip_relief * sleep_min),
        ("cosleep_mutual_relief", a.cosleep_mutual_relief * sleep_min),
        ("groom_cuddle_relief", a.groom_cuddle_relief * bath_min),
        ("rest_drip_relief", a.rest_drip_relief * cuddle_min),
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
