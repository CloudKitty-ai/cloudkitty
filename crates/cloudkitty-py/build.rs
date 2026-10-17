//! Embeds the engine build's git commit so the module can expose it as
//! `cloudkitty.ENGINE_COMMIT` (owner kickoff 2026-10-16). The binding
//! compiles the engine crates from the same workspace tree, so the
//! workspace commit IS the engine build's identity.
//!
//! Shape: 40-hex commit, `-dirty` appended when the build has
//! engine-relevant uncommitted changes (anything under `crates/` or the
//! workspace manifests — dirt in experiments/ or client/ does not change
//! this binary, and a marker that fires on every lab raw would be noise
//! nobody reads), `"unknown"` when git is unavailable (a build outside
//! the repo). A failed dirty probe (e.g. a concurrent git holding
//! index.lock) stamps `-dirty`: the honest default is the conservative
//! one. The stamp refreshes whenever this script re-runs — on any
//! `crates/` source change (the rerun-if on `..`) or any commit (the git
//! watches) — so an incremental rebind after editing engine source
//! re-stamps rather than carrying a stale clean SHA (PR #452 review,
//! finding 1).

use std::process::Command;

fn git(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    if !out.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn main() {
    // The engine source: any change under crates/ must re-run this script,
    // or an incremental rebuild would recompile the engine while the stamp
    // keeps the old clean SHA — the lying provenance this script exists to
    // kill. (cwd is CARGO_MANIFEST_DIR = crates/cloudkitty-py, so `..` is
    // crates/; target/ lives at the workspace root, outside the watch.)
    println!("cargo:rerun-if-changed=..");
    // HEAD lives in the worktree's own git dir (a worktree's `.git` is a
    // file pointing there), so resolve it rather than assuming `.git/HEAD`.
    // HEAD alone is not enough: it usually holds a ref NAME, and a commit
    // moves the ref under the common dir's refs/heads (or packed-refs)
    // without touching HEAD. refs/heads rather than all of refs/: fetches
    // (refs/remotes) and tags cannot move the stamp, so watching them is
    // pure rebuild churn on a five-thread shared checkout.
    if let Some(dir) = git(&["rev-parse", "--absolute-git-dir"]) {
        println!("cargo:rerun-if-changed={dir}/HEAD");
    }
    if let Some(common) = git(&["rev-parse", "--path-format=absolute", "--git-common-dir"]) {
        println!("cargo:rerun-if-changed={common}/refs/heads");
        println!("cargo:rerun-if-changed={common}/packed-refs");
    }
    let commit = match git(&["rev-parse", "HEAD"]) {
        Some(sha) => {
            // Engine-scoped dirty: crates/ plus the workspace manifests.
            // Untracked files under those paths count (a new source file
            // is real dirt). Fail-open goes TOWARD -dirty, never clean.
            let dirty = git(&[
                "status",
                "--porcelain",
                "--",
                "..",
                "../../Cargo.toml",
                "../../Cargo.lock",
            ])
            .map(|s| !s.is_empty())
            .unwrap_or(true);
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
