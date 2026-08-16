//! CloudKitty's server: the world's only owner, and a window onto it.
//!
//! The binary is a thin wrapper around this crate so integration tests can stand
//! up a real server -- simulation, REST and WebSocket -- on an ephemeral port.

pub mod api;
pub mod persist;
pub mod sim_task;
pub mod ws;

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::Arc;

use anyhow::Context;
use axum::http::{header, HeaderValue};
use axum::routing::get;
use axum::Router;
use cloudkitty_core::behavior::ScriptBehavior;
use cloudkitty_core::{BehaviorRegistry, Config};
use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::policy::PolicyArtifact;
use tower::ServiceBuilder;
use tower_http::cors::CorsLayer;
use tower_http::services::ServeDir;
use tower_http::set_header::SetResponseHeaderLayer;

use crate::api::AppState;

/// One row of the model registry (spec 034): what a certified artifact is,
/// in words a viewer can read. Keyed by sha256 in `registry.toml`; the
/// `display` line is served verbatim as each kitty's `behavior_description`.
#[derive(Debug, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RegistryRow {
    pub architecture: String,
    pub recipe: String,
    pub display: String,
}

#[derive(Debug, serde::Deserialize)]
#[serde(deny_unknown_fields)]
struct RegistryFile {
    #[serde(default)]
    artifact: BTreeMap<String, RegistryRow>,
}

/// Loads the model registry that lives beside an artifact (spec 034, research
/// D2): `registry.toml` in the artifact's parent directory — `policies/
/// registry.toml` in this repository, a fixture's own file in tests. The
/// registry travels with the artifacts it describes; a missing file, a parse
/// failure, or an empty required field is an error naming exactly what was
/// looked for and where.
pub fn load_registry_beside(artifact: &Path) -> anyhow::Result<BTreeMap<String, RegistryRow>> {
    let dir = artifact.parent().unwrap_or_else(|| Path::new("."));
    let registry_path = dir.join("registry.toml");
    let text = std::fs::read_to_string(&registry_path).with_context(|| {
        format!(
            "no model registry at {} (spec 034: every certified artifact's directory \
             carries a registry.toml, and every artifact gets a row in the PR that lands it)",
            registry_path.display()
        )
    })?;
    let parsed: RegistryFile = toml::from_str(&text)
        .with_context(|| format!("could not parse {}", registry_path.display()))?;
    for (sha, row) in &parsed.artifact {
        for (field, value) in [
            ("architecture", &row.architecture),
            ("recipe", &row.recipe),
            ("display", &row.display),
        ] {
            if value.trim().is_empty() {
                anyhow::bail!(
                    "{}: row {sha} has an empty {field} — every registry field is required",
                    registry_path.display()
                );
            }
        }
    }
    Ok(parsed.artifact)
}

/// Stamps `behavior_description` onto every kitty (spec 034): the registry
/// display line for a policy seat, `"Scripted"` for a builtin, `None` for a
/// plugin (an external process has no certification record). Called once on
/// the world the server is about to run — fresh or resumed alike, so the
/// registry stays authoritative over whatever a snapshot froze. Overwrites
/// unconditionally, including back to `None`: a stale description must not
/// survive a seat change.
pub fn stamp_behavior_descriptions(
    world: &mut cloudkitty_core::World,
    registry: &BehaviorRegistry,
    policy_displays: &BTreeMap<String, String>,
) {
    for kitty in &mut world.kitties {
        kitty.behavior_description = if kitty.behavior.starts_with("policy:") {
            // Registration refused startup unless every seated policy had a
            // registry row, so this lookup only misses for a behavior name
            // the config validation would already have rejected.
            policy_displays.get(&kitty.behavior).cloned()
        } else if registry
            .get(&kitty.behavior)
            .is_some_and(|b| b.is_builtin())
        {
            Some("Scripted".to_string())
        } else {
            None
        };
    }
}

/// Registers every policy behavior the config names (spec 014 FR-016) and
/// returns the served display line per registered behavior (spec 034).
///
/// A kitty whose behavior is `policy:<name>` resolves through the
/// `[rl.policy.<name>]` block in the same TOML text: the artifact is
/// loaded, fully validated against the compiled schema versions, and
/// content-hashed — logged here, before any tick — and the behavior is
/// registered under its full `policy:<name>`. The artifact's sha256 must
/// also have a row in the model registry beside it, whose `display` line is
/// what viewers read (spec 034 FR-007: no row, no boot — the registry
/// cannot be silently skipped). Any failure stops startup with an error
/// naming the config field, the same doctrine as an unknown behavior name.
pub fn register_policy_behaviors(
    registry: &mut BehaviorRegistry,
    config: &Config,
    rl: &RlConfig,
) -> anyhow::Result<BTreeMap<String, String>> {
    let mut displays = BTreeMap::new();
    let policy_names: std::collections::BTreeSet<&str> = config
        .kitties
        .iter()
        .filter_map(|k| k.behavior.strip_prefix("policy:"))
        .collect();
    if policy_names.is_empty() {
        return Ok(displays);
    }
    for name in policy_names {
        let policy = rl.policy.get(name).ok_or_else(|| {
            anyhow::anyhow!(
                "a kitty names behavior 'policy:{name}' but there is no                  [rl.policy.{name}] block with an artifact path"
            )
        })?;
        let expectations = PolicyBehavior::expectations(rl);
        let artifact = PolicyArtifact::load(Path::new(&policy.artifact), &expectations)
            .with_context(|| format!("[rl.policy.{name}].artifact ({})", policy.artifact))?;
        let rows = load_registry_beside(Path::new(&policy.artifact)).with_context(|| {
            // The full refusal contract (spec 034 §4): config field, artifact
            // path, sha256 — in the missing-file shape too, not just the
            // missing-row one.
            format!(
                "[rl.policy.{name}].artifact ({}) sha256 {}",
                policy.artifact, artifact.sha256
            )
        })?;
        let row = rows.get(&artifact.sha256).ok_or_else(|| {
            anyhow::anyhow!(
                "[rl.policy.{name}].artifact ({}): sha256 {} has no row in the model \
                 registry beside it — a certified artifact gets its registry row in the \
                 PR that lands it, and seating one without a row refuses startup \
                 (spec 034 FR-007)",
                policy.artifact,
                artifact.sha256
            )
        })?;
        tracing::info!(
            policy = name,
            artifact = %policy.artifact,
            sha256 = %artifact.sha256,
            display = %row.display,
            observation_schema = artifact.observation_schema(),
            action_schema = artifact.action_schema(),
            mask_schema = artifact.mask_schema(),
            supported_versions = ?cloudkitty_rl::policy::SUPPORTED_VERSIONS,
            // The seated selection mode, so the startup record is never
            // ambiguous about which distribution ran (issue #70 doctrine)
            // and an incident can be reproduced with kitty-eval --sample
            // (or without) instead of guessing from a config that may
            // have changed since.
            sample = policy.sample,
            "policy artifact validated"
        );
        displays.insert(format!("policy:{name}"), row.display.clone());
        let behavior = PolicyBehavior::new(artifact, rl.clone(), policy.sample);
        registry.register(format!("policy:{name}"), Arc::new(behavior));
    }
    Ok(displays)
}

/// External plugin declarations — `[plugins.<name>]` blocks parsed from the
/// same TOML file as everything else, into a struct the served `Config`
/// never contains: program paths and arguments must not be reachable
/// through `GET /config` (spec 016 FR-014, the `[rl.*]` doctrine).
#[derive(Debug, Default, serde::Deserialize)]
pub struct PluginsConfig {
    #[serde(default)]
    pub plugins: std::collections::BTreeMap<String, PluginEntry>,
}

/// One plugin: the program to run and its arguments. `command` must be a
/// path to an existing executable file (a shebang script, or an interpreter
/// given by absolute path with the script in `args`) — name-only PATH
/// lookups are refused so startup validation means something.
#[derive(Debug, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PluginEntry {
    pub command: String,
    #[serde(default)]
    pub args: Vec<String>,
}

/// Registers a [`ScriptBehavior`] per `[plugins.<name>]` block, validating
/// at startup what can be validated at startup (spec 016 FR-011): a missing
/// program is a config error before any tick, not a per-tick surprise.
/// Runs after policy registration and before behavior-name validation, so a
/// kitty may name a plugin exactly as it names any other behavior — and a
/// plugin may not *shadow* one: registration is last-write-wins, so without
/// the collision check a `[plugins.playful]` block would silently replace
/// the builtin and every kitty configured `playful` would be driven by an
/// external process nobody asked for.
pub fn register_plugin_behaviors(
    registry: &mut BehaviorRegistry,
    plugins: &PluginsConfig,
) -> anyhow::Result<()> {
    for (name, entry) in &plugins.plugins {
        if registry.get(name).is_some() {
            anyhow::bail!(
                "[plugins.{name}] collides with an existing behavior named {name:?} \
                 (a builtin or policy behavior); pick a different plugin name"
            );
        }
        let command = Path::new(&entry.command);
        let metadata = match std::fs::metadata(command) {
            Ok(metadata) if metadata.is_file() => metadata,
            _ => anyhow::bail!(
                "[plugins.{name}].command ({}) does not exist or is not a file",
                entry.command
            ),
        };
        // The docs promise "an existing executable file... validated at
        // startup" — a missing exec bit is startup-detectable, so it must
        // be a startup error, not a per-tick launch failure (FR-011). In
        // the interpreter-plus-script form the command IS the interpreter,
        // which is exactly the thing that must be executable.
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            if metadata.permissions().mode() & 0o111 == 0 {
                anyhow::bail!(
                    "[plugins.{name}].command ({}) is not executable (chmod +x it, \
                     or use an interpreter path as the command with the script in args)",
                    entry.command
                );
            }
        }
        #[cfg(not(unix))]
        let _ = metadata;
        tracing::info!(
            plugin = %name,
            command = %entry.command,
            args = ?entry.args,
            "plugin behavior registered"
        );
        registry.register(
            name.clone(),
            Arc::new(ScriptBehavior::new(
                name.clone(),
                command,
                entry.args.clone(),
            )),
        );
    }
    Ok(())
}

/// The complete application: read-only API, live updates, and the viewer itself.
pub fn build_router(state: AppState, client_dir: &Path) -> Router {
    // `no-cache` means "revalidate every time", not "never cache": the browser
    // still holds the bytes but asks before reusing them, and ServeDir's
    // Last-Modified turns that into a cheap 304 when nothing changed. Without
    // this, browsers apply heuristic freshness to the bare Last-Modified and
    // can keep serving a stale viewer for hours after the files change on
    // disk (found 2026-07-21: a freshly shipped purr cue invisible behind a
    // cached pre-ship app.js).
    let fresh_static = ServiceBuilder::new()
        .layer(SetResponseHeaderLayer::overriding(
            header::CACHE_CONTROL,
            HeaderValue::from_static("no-cache"),
        ))
        .service(ServeDir::new(client_dir));

    Router::new()
        .route("/world", get(api::get_world))
        .route("/kitties", get(api::get_kitties))
        .route("/kitties/:id", get(api::get_kitty))
        .route("/events/distress", get(api::get_distress))
        .route("/events/activity", get(api::get_activity_ends))
        .route("/config", get(api::get_config))
        .route("/ws", get(ws::ws_handler))
        // Anything else is a static file: index.html, app.js, render.js.
        .fallback_service(fresh_static)
        .layer(CorsLayer::permissive())
        .with_state(state)
}

#[cfg(test)]
mod plugin_registration_tests {
    use super::*;

    #[test]
    fn a_missing_plugin_program_fails_startup_with_a_clear_error() {
        // Spec 016 FR-011: detectable config errors stop the world before it
        // starts, naming the field and the path.
        let plugins: PluginsConfig =
            toml::from_str("[plugins.ghost]\ncommand = \"/definitely/not/a/real/program\"\n")
                .unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        let err = register_plugin_behaviors(&mut registry, &plugins).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[plugins.ghost].command"), "{msg}");
        assert!(msg.contains("/definitely/not/a/real/program"), "{msg}");
    }

    /// A per-process fixture dir: two concurrent `cargo test` runs on one
    /// machine must not share (and delete) each other's files.
    fn fixture_dir(label: &str) -> std::path::PathBuf {
        let dir =
            std::env::temp_dir().join(format!("cloudkitty-016-{label}-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    #[test]
    fn a_real_program_registers_under_its_config_name() {
        // Any existing executable file passes the startup check; whether it
        // is a *working* advisor is a per-tick question with a per-tick
        // fallback.
        let dir = fixture_dir("plugin-registers");
        let program = dir.join("demo.sh");
        std::fs::write(&program, "#!/bin/sh\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&program, std::fs::Permissions::from_mode(0o755)).unwrap();
        }

        let toml_text = format!("[plugins.demo]\ncommand = {:?}\n", program);
        let plugins: PluginsConfig = toml::from_str(&toml_text).unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        register_plugin_behaviors(&mut registry, &plugins).unwrap();
        assert!(registry.get("demo").is_some(), "the plugin is a behavior");

        std::fs::remove_dir_all(&dir).ok();
    }

    #[cfg(unix)]
    #[test]
    fn a_non_executable_program_fails_startup_with_a_clear_error() {
        // Review 2026-07-23: the docs promise "an existing executable file
        // ... validated at startup" — a forgotten chmod +x must be a
        // startup error, never a silent per-tick launch failure.
        let dir = fixture_dir("plugin-noexec");
        let program = dir.join("forgot-chmod.py");
        std::fs::write(&program, "#!/usr/bin/env python3\n").unwrap();

        let toml_text = format!("[plugins.brain]\ncommand = {:?}\n", program);
        let plugins: PluginsConfig = toml::from_str(&toml_text).unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        let err = register_plugin_behaviors(&mut registry, &plugins).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[plugins.brain].command"), "{msg}");
        assert!(msg.contains("not executable"), "{msg}");

        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn a_row_resolves_beside_the_artifact() {
        let dir = fixture_dir("registry-happy");
        std::fs::write(
            dir.join("registry.toml"),
            "[artifact.\"abc123\"]\narchitecture = \"MLP\"\nrecipe = \"BC+PPO\"\ndisplay = \"MLP · BC+PPO\"\n",
        )
        .unwrap();
        let rows = load_registry_beside(&dir.join("model.ckpolicy")).unwrap();
        assert_eq!(rows.get("abc123").unwrap().display, "MLP · BC+PPO");
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn a_missing_registry_names_the_looked_for_path() {
        let dir = fixture_dir("registry-missing");
        let err = load_registry_beside(&dir.join("model.ckpolicy")).unwrap_err();
        let msg = format!("{err:#}");
        assert!(msg.contains("no model registry"), "{msg}");
        assert!(msg.contains("registry.toml"), "{msg}");
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn an_unknown_registry_field_is_refused() {
        // The PR #114 strictness doctrine: an unspecced key refuses to load.
        let dir = fixture_dir("registry-unknown");
        std::fs::write(
            dir.join("registry.toml"),
            "[artifact.\"abc\"]\narchitecture = \"MLP\"\nrecipe = \"BC\"\ndisplay = \"x\"\nnickname = \"y\"\n",
        )
        .unwrap();
        let err = load_registry_beside(&dir.join("model.ckpolicy")).unwrap_err();
        assert!(format!("{err:#}").contains("could not parse"), "{err:#}");
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn an_empty_registry_field_is_refused_naming_row_and_field() {
        let dir = fixture_dir("registry-empty-field");
        std::fs::write(
            dir.join("registry.toml"),
            "[artifact.\"abc\"]\narchitecture = \"MLP\"\nrecipe = \"BC\"\ndisplay = \"  \"\n",
        )
        .unwrap();
        let err = load_registry_beside(&dir.join("model.ckpolicy")).unwrap_err();
        let msg = format!("{err:#}");
        assert!(msg.contains("abc") && msg.contains("display"), "{msg}");
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn the_stamp_maps_every_seat_kind() {
        // Spec 034 FR-005: policy → the registry's display line, builtin →
        // "Scripted", plugin/unknown → None (overwriting anything stale).
        let config = cloudkitty_core::test_support::test_config();
        let mut world = cloudkitty_core::World::generate(&config);
        world.kitties[0].behavior = "policy:trained".into();
        world.kitties[1].behavior = "needs_driven".into();
        world.kitties[1].behavior_description = Some("stale".into());
        let registry = BehaviorRegistry::with_builtins();
        let displays: std::collections::BTreeMap<String, String> =
            [("policy:trained".to_string(), "Test · BC+PPO".to_string())].into();
        stamp_behavior_descriptions(&mut world, &registry, &displays);
        assert_eq!(
            world.kitties[0].behavior_description.as_deref(),
            Some("Test · BC+PPO")
        );
        assert_eq!(
            world.kitties[1].behavior_description.as_deref(),
            Some("Scripted")
        );
        world.kitties[1].behavior = "advisor".into();
        stamp_behavior_descriptions(&mut world, &registry, &displays);
        assert_eq!(world.kitties[1].behavior_description, None);
    }

    #[test]
    fn a_plugin_may_not_shadow_an_existing_behavior() {
        // Code review 2026-07-23: registration is last-write-wins, so a
        // colliding name would silently replace the builtin — every kitty
        // configured with it would be driven by an external process with no
        // warning. Collisions are a startup error instead.
        let plugins: PluginsConfig =
            toml::from_str("[plugins.playful]\ncommand = \"/bin/echo\"\n").unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        let err = register_plugin_behaviors(&mut registry, &plugins).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[plugins.playful]"), "{msg}");
        assert!(msg.contains("collides"), "{msg}");
        // The builtin survives untouched.
        assert!(registry.get("playful").unwrap().is_builtin());
    }

    #[test]
    fn an_unknown_plugin_field_is_a_startup_error_not_a_surprise() {
        let parsed: Result<PluginsConfig, _> =
            toml::from_str("[plugins.demo]\ncommand = \"/bin/echo\"\nworkdir = \"/tmp\"\n");
        assert!(parsed.is_err(), "unknown [plugins] fields are refused");
    }
}
