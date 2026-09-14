//! Every TOML the repo ships must load through BOTH config surfaces.
//!
//! The core sweep (cloudkitty-core/tests/shipped_configs.rs) deserializes
//! `Config` alone and never sees the `[rl]` blocks -- yet the frozen
//! evals/v3 exams carry `[rl.eval]` and `[rl.reward]`, and those files are
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

/// Mirrors the core sweep's gitignore filter (handover (e), 2026-09-13):
/// drops the files git ignores so a lab checkout's gitignored record
/// configs of earlier engine generations cannot redden the sweep;
/// untracked-but-NOT-ignored files stay in scope. If git is unavailable or
/// errors, the list is left unfiltered, so CI behavior is unchanged.
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
    drop_gitignored(&root, &mut files);
    assert!(
        files.iter().any(|p| p.ends_with("cloudkitty.toml")),
        "the served config is in the sweep"
    );
    assert!(
        files
            .iter()
            .any(|p| { p.parent().is_some_and(|d| d.ends_with("evals/v3")) }),
        "the frozen exams (evals/v3, spec 051) are in the sweep"
    );
    for file in files {
        let text = std::fs::read_to_string(&file).unwrap();
        cloudkitty_rl::config::load_configs_from_str(&text)
            .unwrap_or_else(|e| panic!("{} no longer loads: {e}", file.display()));
    }
}

/// Removes the self-test's scratch subtree even when the test panics.
struct RemoveOnDrop(PathBuf);
impl Drop for RemoveOnDrop {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// Self-test for this file's `drop_gitignored` (mirrors the core sweep's):
/// plants a gitignored, deliberately unparseable TOML under a swept root
/// and proves the filter -- and only the filter -- keeps it out. The
/// fixture sits under a `raw/` directory (gitignored at the root:
/// `experiments/**/raw/`), so the concurrently-running sweep filters it by
/// path and never reads it; the directory name is unique to this binary so
/// the core sweep's self-test can never share the path.
#[test]
fn the_rl_sweep_drops_gitignored_files_and_only_those() {
    let root = repo_root();
    let scratch = root.join("experiments/sweep-skip-selftest-rl");
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
