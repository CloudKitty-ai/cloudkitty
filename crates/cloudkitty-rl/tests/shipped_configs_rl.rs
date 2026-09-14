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

/// Drops the files git ignores (handover (e), 2026-09-13): a lab checkout
/// carries gitignored record configs of earlier engine generations that no
/// longer parse, and the exclusion manifest cannot cover them -- it asserts
/// every named directory exists, and those records exist only on the lab
/// machine. Untracked-but-NOT-ignored files stay in scope (the manifest
/// header's rule: new experiment output loads on the current engine by
/// default). If git is unavailable or errors, the list is left unfiltered,
/// so CI behavior -- which only ever sees the tracked tree -- is unchanged.
/// Known cost: check-ignore honors the machine's global excludes
/// (core.excludesFile, .git/info/exclude), so a broad personal ignore rule
/// shrinks a local sweep silently; CI, which filters nothing, is the
/// backstop.
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
    // The question is written from its own thread: past ~64KB of pipe
    // traffic a write-everything-then-read protocol deadlocks (git stops
    // draining stdin once its stdout pipe fills), and a deadlock here is
    // an unkillable hang, never a red.
    let mut stdin = child.stdin.take().unwrap();
    let writer = std::thread::spawn(move || stdin.write_all(&input).is_ok());
    let Ok(out) = child.wait_with_output() else {
        let _ = writer.join();
        return;
    };
    let asked_everything = writer.join().unwrap_or(false);
    // check-ignore: 0 = some paths ignored, 1 = none; any other exit -- or
    // a half-delivered question -- means the answer is unusable, and no
    // filtering beats wrong filtering.
    if !asked_everything || !matches!(out.status.code(), Some(0 | 1)) {
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

/// Removes the self-test's scratch repo even when the test panics.
struct RemoveOnDrop(PathBuf);
impl Drop for RemoveOnDrop {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

/// Self-test for `drop_gitignored`, in a throwaway `git init` repo under
/// the system temp dir: the sweep test runs concurrently in this binary
/// and must never see the fixtures, and this checkout's own ignore rules
/// must never shape the result. Three-way contract: a gitignored file is
/// dropped; a TRACKED file survives even when an ignore rule matches it
/// (check-ignore must consult the index); an untracked-but-not-ignored
/// file survives (new experiment output is in scope by default). A bulk
/// all-ignored batch rides along because past ~64KB of pipe traffic a
/// naive write-then-read protocol deadlocks -- under that bug this test
/// hangs rather than fails, which is still the only layer that can see
/// it. If git itself is unusable the test skips: the filter is fail-open
/// by design, and a git-less environment is the unfiltered world where
/// the sweep behaves exactly as it did before the filter existed.
#[test]
fn the_filter_drops_gitignored_files_and_nothing_else() {
    let scratch = std::env::temp_dir().join(format!(
        "cloudkitty-sweep-selftest-rl-{}",
        std::process::id()
    ));
    let _ = std::fs::remove_dir_all(&scratch);
    let _cleanup = RemoveOnDrop(scratch.clone());
    let raw = scratch.join("raw");
    std::fs::create_dir_all(&raw).unwrap();
    std::fs::write(
        scratch.join(".gitignore"),
        "raw/\ntracked-but-ignored.toml\n",
    )
    .unwrap();
    let ignored_file = raw.join("retired-generation.toml");
    std::fs::write(&ignored_file, "cuddle_relief = 1.0 # retired 2.x key\n").unwrap();
    let tracked = scratch.join("tracked-but-ignored.toml");
    std::fs::write(&tracked, "# the index must win over the ignore rule\n").unwrap();
    let untracked = scratch
        .join("untracked-experiment-output.toml")
        .to_path_buf();
    std::fs::write(&untracked, "# untracked-not-ignored: in scope by default\n").unwrap();
    let git = |args: &[&str]| {
        std::process::Command::new("git")
            .args(args)
            .current_dir(&scratch)
            .output()
            .is_ok_and(|o| o.status.success())
    };
    if !git(&["init", "-q"]) {
        eprintln!("skipping: git unusable here, and the filter is fail-open without it");
        return;
    }
    // A developer's global excludes must not reach into the fixture repo.
    assert!(git(&["config", "core.excludesFile", "/dev/null"]));
    // Index-only: check-ignore consults the index, no commit needed; -f
    // because git add itself refuses an ignore-matched path.
    assert!(git(&[
        "add",
        "-f",
        ".gitignore",
        "tracked-but-ignored.toml"
    ]));

    let mut files = vec![ignored_file.clone(), tracked.clone(), untracked.clone()];
    // check-ignore answers from patterns, so the bulk paths need not exist.
    for i in 0..3000 {
        files.push(raw.join(format!("bulk-{i}.toml")));
    }
    drop_gitignored(&scratch, &mut files);
    assert!(
        !files.contains(&ignored_file),
        "the gitignored fixture must be dropped from the sweep"
    );
    assert!(
        files.contains(&tracked),
        "a tracked config survives the filter even when an ignore rule matches it"
    );
    assert!(
        files.contains(&untracked),
        "an untracked-but-not-ignored file survives the filter"
    );
    assert_eq!(files.len(), 2, "the bulk gitignored batch is fully dropped");
}
