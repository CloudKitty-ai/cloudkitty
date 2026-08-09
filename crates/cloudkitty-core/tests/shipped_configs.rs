//! Every TOML the repo ships must load through `Config` validation.
//!
//! Spec 022/023 review net: the loud-retirement posture only protects a
//! config that something actually parses, and the eval-suite manifest guard
//! compares bytes without parsing. This sweep is what catches a shipped
//! config that a future key migration misses (it would have caught three in
//! the 022/023 batch). TOMLs that are not world configs (tool manifests,
//! the eval-suite hash manifest) are excluded by name in `collect`.

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
