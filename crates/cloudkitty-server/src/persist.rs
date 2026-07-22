//! Saving and resuming a world.
//!
//! The whole `World` -- RNG state included -- goes to a single JSON file, so a
//! restart continues the same future rather than merely the same positions.
//!
//! Writes are atomic: serialize to a sibling temp file, then rename. A crash
//! mid-write therefore leaves the previous save intact rather than a half-written
//! one. Losing up to one save interval is acceptable; losing the world is not.
//!
//! Loading is deliberately strict. A snapshot that fails validation aborts startup
//! with an explanation instead of being silently discarded -- an operator should
//! never lose a world without being asked.

use std::path::{Path, PathBuf};

use cloudkitty_core::{invariants, Config, World};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum PersistError {
    #[error("could not read snapshot {path}: {source}")]
    Read {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },

    #[error("could not write snapshot {path}: {source}")]
    Write {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },

    #[error("snapshot {path} is not valid CloudKitty JSON: {source}")]
    Parse {
        path: PathBuf,
        #[source]
        source: serde_json::Error,
    },

    #[error(
        "snapshot {path} was saved for a different configuration \
         (snapshot: {found}, current: {expected}).\n\
         Change the config back, point --snapshot at a different file, \
         or start a new world with --fresh."
    )]
    Incompatible {
        path: PathBuf,
        found: String,
        expected: String,
    },

    #[error(
        "snapshot {path} violates the constitution and was not loaded: {detail}.\n\
         This world cannot be resumed safely; start a new one with --fresh."
    )]
    Unlawful { path: PathBuf, detail: String },
}

/// Writes `world` to `path` atomically.
pub fn save(world: &World, path: &Path) -> Result<(), PersistError> {
    let json = serde_json::to_vec_pretty(world).map_err(|source| PersistError::Parse {
        path: path.to_path_buf(),
        source,
    })?;

    // The temp file must share a directory with the target so the rename stays on
    // one filesystem and therefore stays atomic.
    let tmp = temp_path(path);
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent).map_err(|source| PersistError::Write {
                path: parent.to_path_buf(),
                source,
            })?;
        }
    }

    std::fs::write(&tmp, &json).map_err(|source| PersistError::Write {
        path: tmp.clone(),
        source,
    })?;
    std::fs::rename(&tmp, path).map_err(|source| PersistError::Write {
        path: path.to_path_buf(),
        source,
    })?;

    Ok(())
}

/// Loads a world and refuses anything that would resume badly.
pub fn load_and_validate(path: &Path, config: &Config) -> Result<World, PersistError> {
    let bytes = std::fs::read(path).map_err(|source| PersistError::Read {
        path: path.to_path_buf(),
        source,
    })?;

    let mut world: World =
        serde_json::from_slice(&bytes).map_err(|source| PersistError::Parse {
            path: path.to_path_buf(),
            source,
        })?;

    let expected = config.fingerprint();
    if world.config_fingerprint != expected {
        return Err(PersistError::Incompatible {
            path: path.to_path_buf(),
            found: world.config_fingerprint.clone(),
            expected,
        });
    }

    // Kitty order is load-bearing for determinism; re-establish it rather than
    // trusting the file.
    world.kitties.sort_by_key(|k| k.id);

    // Behaviors are configuration, not world state (spec 014 review): the
    // config named them at generate time and stays their source of truth on
    // resume. Without this re-stamp, an operator's behavior edit — most
    // pointedly seating a policy (`behavior = "policy:<name>"`) — would be
    // validated and logged at startup yet silently lose to the string
    // persisted in the snapshot, and a snapshot naming a behavior the
    // config no longer registers would quietly run the fallback forever.
    for kitty in &mut world.kitties {
        if let Some(configured) = config.kitties.iter().find(|kc| kc.id == kitty.id) {
            kitty.behavior = configured.behavior.clone();
        }
    }

    if let Err(violation) = invariants::check(&world, config) {
        return Err(PersistError::Unlawful {
            path: path.to_path_buf(),
            detail: violation.to_string(),
        });
    }

    Ok(world)
}

fn temp_path(path: &Path) -> PathBuf {
    let mut tmp = path.as_os_str().to_os_string();
    tmp.push(".tmp");
    PathBuf::from(tmp)
}

/// Moves an existing snapshot aside before a fresh world claims its path.
///
/// `--fresh` ignores the old world at startup, but without this the new world
/// would overwrite it at its first save -- and a sandbox whose whole ethos is
/// that worlds are never lost by accident should not lose one to a flag. The
/// old file is renamed (atomically, same directory) to
/// `<name>.<unix-seconds>.bak` and the caller logs where it went.
///
/// Returns `Ok(None)` when there was nothing to back up.
pub fn backup_aside(path: &Path) -> Result<Option<PathBuf>, PersistError> {
    if !path.exists() {
        return Ok(None);
    }

    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);

    // A same-second collision (test suites, rapid restarts) must not clobber an
    // earlier backup: probe for a free name.
    let mut backup = backup_path(path, stamp, 0);
    let mut attempt = 1u32;
    while backup.exists() {
        backup = backup_path(path, stamp, attempt);
        attempt += 1;
    }

    std::fs::rename(path, &backup).map_err(|source| PersistError::Write {
        path: backup.clone(),
        source,
    })?;

    Ok(Some(backup))
}

fn backup_path(path: &Path, stamp: u64, attempt: u32) -> PathBuf {
    let mut name = path.as_os_str().to_os_string();
    if attempt == 0 {
        name.push(format!(".{stamp}.bak"));
    } else {
        name.push(format!(".{stamp}-{attempt}.bak"));
    }
    PathBuf::from(name)
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::test_support::test_config;

    fn temp_dir(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("cloudkitty-test-{name}"));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).expect("temp dir");
        dir
    }

    #[test]
    fn a_saved_world_round_trips_exactly() {
        let dir = temp_dir("roundtrip");
        let path = dir.join("snapshot.json");
        let config = test_config();
        let world = World::generate(&config);

        save(&world, &path).expect("save");
        let loaded = load_and_validate(&path, &config).expect("load");

        assert_eq!(loaded.tick, world.tick);
        assert_eq!(loaded.kitties.len(), world.kitties.len());
        assert_eq!(
            serde_json::to_string(&loaded.rng).unwrap(),
            serde_json::to_string(&world.rng).unwrap(),
            "the RNG state must survive, or the future would diverge"
        );
    }

    #[test]
    fn saving_leaves_no_temp_file_behind() {
        let dir = temp_dir("no-temp");
        let path = dir.join("snapshot.json");
        let config = test_config();
        save(&World::generate(&config), &path).expect("save");

        assert!(path.exists());
        assert!(
            !temp_path(&path).exists(),
            "the temp file is renamed, not left lying around"
        );
    }

    #[test]
    fn overwriting_an_existing_snapshot_works() {
        let dir = temp_dir("overwrite");
        let path = dir.join("snapshot.json");
        let config = test_config();

        let world = World::generate(&config);
        save(&world, &path).expect("first save");
        save(&world, &path).expect("second save must not trip over the first");
        assert!(load_and_validate(&path, &config).is_ok());
    }

    #[test]
    fn a_resumed_world_takes_its_behaviors_from_the_config() {
        // Spec 014 review: editing a kitty's behavior (e.g. seating a
        // policy) must take effect on restart — the persisted string loses.
        let dir = temp_dir("restamp");
        let path = dir.join("snapshot.json");
        let config = test_config();
        save(&World::generate(&config), &path).expect("save");

        let mut edited = test_config();
        edited.kitties[0].behavior = "policy:trained".into();

        let world = load_and_validate(&path, &edited).expect("load");
        let kitty = world
            .kitties
            .iter()
            .find(|k| k.id == edited.kitties[0].id)
            .unwrap();
        assert_eq!(kitty.behavior, "policy:trained");
        // Untouched kitties keep their configured behavior too.
        assert_eq!(world.kitties[1].behavior, edited.kitties[1].behavior);
    }

    #[test]
    fn a_snapshot_from_another_world_shape_is_refused() {
        let dir = temp_dir("incompatible");
        let path = dir.join("snapshot.json");
        let config = test_config();
        save(&World::generate(&config), &path).expect("save");

        let mut changed = test_config();
        changed.world.width += 8; // different fingerprint

        let err = load_and_validate(&path, &changed).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("different configuration"), "{msg}");
        assert!(
            msg.contains("--fresh"),
            "tells the operator what to do: {msg}"
        );
    }

    #[test]
    fn an_unlawful_snapshot_is_refused_rather_than_discarded() {
        let dir = temp_dir("unlawful");
        let path = dir.join("snapshot.json");
        let config = test_config();

        // Hand-craft a world that breaks Article III.
        let mut world = World::generate(&config);
        world.kitties.truncate(1);
        std::fs::write(&path, serde_json::to_vec(&world).unwrap()).unwrap();

        let err = load_and_validate(&path, &config).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("violates the constitution"), "{msg}");
        assert!(msg.contains("Article III"), "{msg}");
    }

    #[test]
    fn corrupt_json_is_reported_clearly() {
        let dir = temp_dir("corrupt");
        let path = dir.join("snapshot.json");
        std::fs::write(&path, b"{ this is not json").unwrap();

        let err = load_and_validate(&path, &test_config()).unwrap_err();
        assert!(err.to_string().contains("not valid CloudKitty JSON"));
    }

    #[test]
    fn backup_aside_preserves_the_old_world() {
        let dir = temp_dir("backup");
        let path = dir.join("snapshot.json");
        let config = test_config();
        let world = World::generate(&config);
        save(&world, &path).expect("save");
        let original = std::fs::read(&path).unwrap();

        let backup = backup_aside(&path)
            .expect("backup")
            .expect("there was a file");

        assert!(
            !path.exists(),
            "the original path is free for the fresh world"
        );
        assert!(backup.exists());
        assert_eq!(
            std::fs::read(&backup).unwrap(),
            original,
            "the backup is byte-identical to the old world"
        );
        let name = backup.file_name().unwrap().to_string_lossy().into_owned();
        assert!(name.starts_with("snapshot.json."), "{name}");
        assert!(name.ends_with(".bak"), "{name}");
    }

    #[test]
    fn backup_aside_with_nothing_to_back_up_is_a_quiet_no_op() {
        let dir = temp_dir("backup-noop");
        let path = dir.join("snapshot.json");
        assert!(backup_aside(&path).expect("ok").is_none());
    }

    #[test]
    fn rapid_backups_never_clobber_each_other() {
        let dir = temp_dir("backup-rapid");
        let path = dir.join("snapshot.json");
        let config = test_config();
        let world = World::generate(&config);

        // Three fresh starts within the same second: three distinct backups.
        let mut backups = Vec::new();
        for _ in 0..3 {
            save(&world, &path).expect("save");
            backups.push(backup_aside(&path).unwrap().unwrap());
        }
        let unique: std::collections::BTreeSet<_> = backups.iter().collect();
        assert_eq!(unique.len(), 3, "backups: {backups:?}");
        for b in &backups {
            assert!(b.exists());
        }
    }

    #[test]
    fn a_missing_snapshot_reports_a_read_error() {
        let dir = temp_dir("missing");
        let path = dir.join("nope.json");
        let err = load_and_validate(&path, &test_config()).unwrap_err();
        assert!(matches!(err, PersistError::Read { .. }));
    }
}
