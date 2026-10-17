//! Embeds the engine build's git commit so meta.json can stamp
//! `engine_commit` (spec 062 FR-009): a trace's drawn starts tie to the
//! draw law's build. bc-collect compiles the engine crates from the same
//! repo tree, so the repo commit IS the engine identity — the same
//! semantics as `crates/cloudkitty-py/build.rs` (#452), with paths
//! adjusted for this standalone workspace (CARGO_MANIFEST_DIR is
//! `experiments/tools/bc-collect`, three levels below the repo root).
//!
//! Shape: 40-hex commit; `-dirty` when the build has engine-relevant
//! uncommitted changes (anything under `crates/`, the root workspace
//! manifests, or this tool itself — dirt in lab raws or client/ does not
//! change this binary); `"unknown"` when git is unavailable. A failed
//! dirty probe stamps `-dirty`: the honest default is the conservative
//! one.

use std::process::Command;

fn git(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    if !out.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn main() {
    // Any engine-source or own-source change must re-run this script, or an
    // incremental rebuild would carry a stale clean SHA (#452 finding 1).
    println!("cargo:rerun-if-changed=../../../crates");
    println!("cargo:rerun-if-changed=src");
    // Everything the dirty probe reads must also be watched, or an
    // uncommitted edit to it (a [workspace.dependencies] bump rebuilds the
    // engine via inheritance) relinks this binary under a cached clean
    // stamp — the #452 stale-SHA class (PR #458 review, finding 4). And
    // printing any rerun-if turns off the watch-everything default, so
    // build.rs must name itself.
    println!("cargo:rerun-if-changed=../../../Cargo.toml");
    println!("cargo:rerun-if-changed=../../../Cargo.lock");
    println!("cargo:rerun-if-changed=Cargo.toml");
    println!("cargo:rerun-if-changed=Cargo.lock");
    println!("cargo:rerun-if-changed=build.rs");
    // HEAD holds a ref NAME; a commit moves refs/heads (or packed-refs)
    // under the common dir without touching HEAD, so watch all three.
    if let Some(dir) = git(&["rev-parse", "--absolute-git-dir"]) {
        println!("cargo:rerun-if-changed={dir}/HEAD");
    }
    if let Some(common) = git(&["rev-parse", "--path-format=absolute", "--git-common-dir"]) {
        println!("cargo:rerun-if-changed={common}/refs/heads");
        println!("cargo:rerun-if-changed={common}/packed-refs");
    }
    let commit = match git(&["rev-parse", "HEAD"]) {
        Some(sha) => {
            let dirty = git(&[
                "status",
                "--porcelain",
                "--",
                "../../../crates",
                "../../../Cargo.toml",
                "../../../Cargo.lock",
                ".",
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
