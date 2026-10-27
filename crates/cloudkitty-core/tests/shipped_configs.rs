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
///
/// Symlinks are skipped entirely (2026-10-15): a symlink in the tree is
/// untracked scratch pointing elsewhere, so nothing behind it is a config
/// the repo ships — and following one also poisons `drop_gitignored`:
/// `git check-ignore` dies with "pathspec is beyond a symbolic link"
/// (exit 128) on ANY such path in the batch, which switches off all
/// gitignore filtering and lets ignored retired configs red the sweep on
/// a lab checkout while CI stays green.
fn collect(dir: &Path, recursive: bool, out: &mut Vec<PathBuf>) {
    for entry in std::fs::read_dir(dir).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();
        let name = entry.file_name();
        if path.is_symlink() {
            continue;
        }
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
        if let Err(message) = check_file(&root, &file) {
            panic!("{message}");
        }
    }
}

/// One file through the sweep: it parses, it validates (which is where an
/// unacknowledged hazardous mode under `experiments/` is refused, spec 066
/// FR-004), and outside `experiments/` it activates no hazardous mode
/// (FR-005). The sweep loop and the self-test below share this body, so
/// the self-test guards the loop's actual rule (PR #469 review).
fn check_file(root: &Path, file: &Path) -> Result<(), String> {
    let text =
        std::fs::read_to_string(file).map_err(|e| format!("{} unreadable: {e}", file.display()))?;
    let config: Config =
        toml::from_str(&text).map_err(|e| format!("{} no longer parses: {e}", file.display()))?;
    config
        .validate()
        .map_err(|e| format!("{} no longer validates: {e}", file.display()))?;
    match hazard_outside_experiments(root, file, &config) {
        Some(message) => Err(message),
        None => Ok(()),
    }
}

/// Spec 066 FR-005 (guard-law §5): outside `<root>/experiments/` no
/// tracked config may activate a welfare-hazardous mode — the served
/// world (`cloudkitty.toml`, `training.toml`) and the frozen exams can
/// never be hazardous, acknowledged or not. Files under `experiments/`
/// are governed by the acknowledgement law through the load itself
/// (`validate()` above), so nothing more is asked of them here. Returns
/// the sweep's failure message, or `None` when the file passes.
fn hazard_outside_experiments(root: &Path, file: &Path, config: &Config) -> Option<String> {
    if file.starts_with(root.join("experiments")) {
        return None;
    }
    let active = config.active_hazards();
    if active.is_empty() {
        return None;
    }
    let names: Vec<&str> = active.iter().map(|(mode, _)| mode.name()).collect();
    Some(format!(
        "{}: welfare-hazardous mode(s) {} active outside experiments/ (spec 066 FR-005)",
        file.display(),
        names.join(", ")
    ))
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
        "cloudkitty-sweep-selftest-core-{}",
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

/// Self-test for `hazard_outside_experiments` (spec 066 US3) on a scratch
/// tree, so rule 5 gets its red without staging a hazardous file in the
/// real tree: the same acknowledged distressed-start bytes are refused
/// under `scratch/specs/` and pass under `scratch/experiments/`; a clean
/// config under `scratch/specs/` passes.
#[test]
fn hazardous_configs_are_refused_outside_experiments() {
    let scratch = std::env::temp_dir().join(format!(
        "cloudkitty-core-sweep-hazard-selftest-{}",
        std::process::id()
    ));
    let _ = std::fs::remove_dir_all(&scratch);
    let _cleanup = RemoveOnDrop(scratch.clone());
    std::fs::create_dir_all(scratch.join("specs")).unwrap();
    std::fs::create_dir_all(scratch.join("experiments")).unwrap();
    let hazardous = cloudkitty_core::test_support::complete_toml(
        "[initial_needs]\ncuddle = 92.0\n[welfare_hazard]\nacknowledged = [\"initial_needs\"]\n",
    );
    let unacknowledged =
        cloudkitty_core::test_support::complete_toml("[initial_needs]\ncuddle = 92.0\n");
    let clean = cloudkitty_core::test_support::complete_toml("");
    // A lookalike: a path that CONTAINS "experiments" but is not under
    // `<root>/experiments/` must still be refused (component match, not
    // substring).
    std::fs::create_dir_all(scratch.join("specs/experiments-notes")).unwrap();
    let outside = scratch.join("specs/x.toml");
    let lookalike = scratch.join("specs/experiments-notes/x.toml");
    let inside = scratch.join("experiments/x.toml");
    let inside_unacknowledged = scratch.join("experiments/y.toml");
    let clean_outside = scratch.join("specs/clean.toml");
    std::fs::write(&outside, &hazardous).unwrap();
    std::fs::write(&lookalike, &hazardous).unwrap();
    std::fs::write(&inside, &hazardous).unwrap();
    std::fs::write(&inside_unacknowledged, &unacknowledged).unwrap();
    std::fs::write(&clean_outside, &clean).unwrap();

    let refused = check_file(&scratch, &outside)
        .expect_err("a hazardous config outside experiments/ is refused");
    assert!(
        refused.contains("specs/x.toml")
            && refused.contains("initial_needs")
            && refused.contains("outside experiments/"),
        "the message names the file and the mode: {refused}"
    );
    let refused = check_file(&scratch, &lookalike).expect_err(
        "a lookalike path (specs/experiments-notes/) is outside experiments/ and refused",
    );
    assert!(refused.contains("outside experiments/"), "{refused}");
    check_file(&scratch, &inside).expect("the same bytes inside experiments/ pass the sweep rule");
    let through_the_load = check_file(&scratch, &inside_unacknowledged)
        .expect_err("inside experiments/ an UNACKNOWLEDGED hazard is refused through the load");
    assert!(
        through_the_load.contains("[welfare_hazard]")
            && !through_the_load.contains("outside experiments/"),
        "refused by validation, not by the path rule: {through_the_load}"
    );
    check_file(&scratch, &clean_outside).expect("a clean config outside experiments/ passes");

    // Spec 067: a needy seat is a mode too — refused outside experiments/
    // naming `needy`, passed inside when acknowledged, refused inside
    // through the load when not. No new helper: the rule is 066's.
    let needy_toml = |acknowledged: bool| {
        let mut c = cloudkitty_core::Config::default();
        c.kitties[0].behavior = "needy".into();
        if acknowledged {
            c.welfare_hazard = Some(cloudkitty_core::config::WelfareHazardConfig {
                acknowledged: vec!["needy".into()],
            });
        }
        toml::to_string(&c).unwrap()
    };
    let needy_outside = scratch.join("specs/needy.toml");
    let needy_inside = scratch.join("experiments/needy.toml");
    let needy_unacknowledged = scratch.join("experiments/needy-unacknowledged.toml");
    std::fs::write(&needy_outside, needy_toml(true)).unwrap();
    std::fs::write(&needy_inside, needy_toml(true)).unwrap();
    std::fs::write(&needy_unacknowledged, needy_toml(false)).unwrap();
    let refused = check_file(&scratch, &needy_outside)
        .expect_err("a needy seat outside experiments/ is refused");
    assert!(
        refused.contains("specs/needy.toml")
            && refused.contains("mode(s) needy active outside experiments/"),
        "the message names the file and the needy mode: {refused}"
    );
    check_file(&scratch, &needy_inside)
        .expect("an acknowledged needy seat inside experiments/ passes the sweep rule");
    let through_the_load = check_file(&scratch, &needy_unacknowledged)
        .expect_err("inside experiments/ an UNACKNOWLEDGED needy seat is refused through the load");
    assert!(
        through_the_load.contains("[welfare_hazard]") && through_the_load.contains("'needy'"),
        "refused by validation, naming the mode: {through_the_load}"
    );
}

/// Self-test for `collect`'s symlink rule (found 2026-10-15 on the lab
/// checkout): neither a symlinked directory nor a symlinked file enters
/// the sweep. Anything beyond a symlink is scratch pointing elsewhere,
/// and one such path in the check-ignore batch kills the WHOLE gitignore
/// filter ("fatal: pathspec ... is beyond a symbolic link", exit 128,
/// which the fail-open contract turns into no filtering at all) — so the
/// skip has to happen at collection time.
#[cfg(unix)]
#[test]
fn collect_never_follows_a_symlink() {
    let scratch = std::env::temp_dir().join(format!(
        "cloudkitty-sweep-symlink-selftest-{}",
        std::process::id()
    ));
    let _ = std::fs::remove_dir_all(&scratch);
    let _cleanup = RemoveOnDrop(scratch.clone());
    let scan = scratch.join("scan");
    let target = scratch.join("target");
    std::fs::create_dir_all(scan.join("real")).unwrap();
    std::fs::create_dir_all(&target).unwrap();
    let shipped = scan.join("real/shipped.toml");
    std::fs::write(&shipped, "# a real config in scope\n").unwrap();
    std::fs::write(
        target.join("retired.toml"),
        "cuddle_relief = 1.0 # beyond a symlink: never parsed\n",
    )
    .unwrap();
    std::os::unix::fs::symlink(&target, scan.join("linked-dir")).unwrap();
    std::os::unix::fs::symlink(target.join("retired.toml"), scan.join("linked.toml")).unwrap();

    let mut files = Vec::new();
    collect(&scan, true, &mut files);

    assert_eq!(
        files,
        vec![shipped],
        "exactly the real config: a symlinked directory and a symlinked \
         file are both outside the sweep"
    );
}
