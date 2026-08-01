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
