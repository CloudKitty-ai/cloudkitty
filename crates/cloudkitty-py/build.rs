//! Embeds the engine build's git commit so the module can expose it as
//! `cloudkitty.ENGINE_COMMIT` (owner kickoff 2026-10-16). The binding
//! compiles the engine crates from the same workspace tree, so the
//! workspace commit IS the engine build's identity.
//!
//! Shape: 40-hex commit, `-dirty` appended when the build tree has
//! uncommitted changes, `"unknown"` when git is unavailable (a build
//! outside the repo). The stamp is read when this script runs: HEAD moves
//! re-run it (the rerun-if below), while a dirty-state-only change does
//! not — the `-dirty` marker is honest as of the last rebuild, and the
//! builds that matter (CI, the lab's maturin rebinds) start clean or
//! rebuild from scratch.

use std::process::Command;

fn git(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    if !out.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn main() {
    // HEAD lives in the worktree's own git dir (a worktree's `.git` is a
    // file pointing there), so resolve it rather than assuming `.git/HEAD`.
    // HEAD alone is not enough: it usually holds a ref NAME, and a commit
    // moves the ref under the common dir's refs/ (or packed-refs) without
    // touching HEAD — a stale stamp is exactly the lying provenance this
    // script exists to kill, so watch all three.
    if let Some(dir) = git(&["rev-parse", "--absolute-git-dir"]) {
        println!("cargo:rerun-if-changed={dir}/HEAD");
    }
    if let Some(common) = git(&["rev-parse", "--path-format=absolute", "--git-common-dir"]) {
        println!("cargo:rerun-if-changed={common}/refs");
        println!("cargo:rerun-if-changed={common}/packed-refs");
    }
    let commit = match git(&["rev-parse", "HEAD"]) {
        Some(sha) => {
            let dirty = git(&["status", "--porcelain"])
                .map(|s| !s.is_empty())
                .unwrap_or(false);
            if dirty {
                format!("{sha}-dirty")
            } else {
                sha
            }
        }
        None => "unknown".to_string(),
    };
    println!("cargo:rustc-env=CLOUDKITTY_ENGINE_COMMIT={commit}");
}
