//! Every TOML the repo ships must load through BOTH config surfaces.
//!
//! The core sweep (cloudkitty-core/tests/shipped_configs.rs) deserializes
//! `Config` alone and never sees the `[rl]` blocks -- yet the frozen
//! evals/v2 exams carry `[rl.eval]` and `[rl.reward]`, and those files are
//! sha-pinned and uneditable. With `deny_unknown_fields` on the rl structs
//! (2026-08-06 handoff item 2), a stray key there would slip past the core
//! sweep and permanently strand a certification exam. This sweep closes
//! that hole: the full loader, both surfaces, over the same file set.

use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .unwrap()
}

/// Mirrors the core sweep's collection rules: `*.toml` minus tool
/// manifests, repo root non-recursive (untracked scratch dirs may hold
/// deliberately-retired configs), evals/experiments/specs recursive.
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
            && name != "rust-toolchain.toml"
        {
            out.push(path);
        }
    }
}

/// Mirrors the core sweep's exclusion rule (spec 028): the root manifest
/// names pinned-generation directories -- frozen records of earlier engine
/// generations -- and nothing else may appear there.
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
fn every_shipped_toml_loads_through_both_config_surfaces() {
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
    assert!(
        files
            .iter()
            .any(|p| { p.parent().is_some_and(|d| d.ends_with("evals/v2")) }),
        "the frozen exams (evals/v2, the 3.0 cut) are in the sweep"
    );
    for file in files {
        let text = std::fs::read_to_string(&file).unwrap();
        cloudkitty_rl::config::load_configs_from_str(&text)
            .unwrap_or_else(|e| panic!("{} no longer loads: {e}", file.display()));
    }
}
