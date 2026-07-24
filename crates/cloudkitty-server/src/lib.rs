//! CloudKitty's server: the world's only owner, and a window onto it.
//!
//! The binary is a thin wrapper around this crate so integration tests can stand
//! up a real server -- simulation, REST and WebSocket -- on an ephemeral port.

pub mod api;
pub mod persist;
pub mod sim_task;
pub mod ws;

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

/// Registers every policy behavior the config names (spec 014 FR-016).
///
/// A kitty whose behavior is `policy:<name>` resolves through the
/// `[rl.policy.<name>]` block in the same TOML text: the artifact is
/// loaded, fully validated against the compiled schema versions, and
/// content-hashed — logged here, before any tick — and the behavior is
/// registered under its full `policy:<name>`. Any failure stops startup
/// with an error naming the config field, the same doctrine as an unknown
/// behavior name.
pub fn register_policy_behaviors(
    registry: &mut BehaviorRegistry,
    config: &Config,
    rl: &RlConfig,
) -> anyhow::Result<()> {
    let policy_names: std::collections::BTreeSet<&str> = config
        .kitties
        .iter()
        .filter_map(|k| k.behavior.strip_prefix("policy:"))
        .collect();
    if policy_names.is_empty() {
        return Ok(());
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
        tracing::info!(
            policy = name,
            artifact = %policy.artifact,
            sha256 = %artifact.sha256,
            observation_schema = artifact.header.observation_schema,
            action_schema = artifact.header.action_schema,
            mask_schema = artifact.header.mask_schema,
            "policy artifact validated"
        );
        let behavior = PolicyBehavior::new(artifact, rl.clone(), policy.sample);
        registry.register(format!("policy:{name}"), Arc::new(behavior));
    }
    Ok(())
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
/// kitty may name a plugin exactly as it names any other behavior.
pub fn register_plugin_behaviors(
    registry: &mut BehaviorRegistry,
    plugins: &PluginsConfig,
) -> anyhow::Result<()> {
    for (name, entry) in &plugins.plugins {
        let command = Path::new(&entry.command);
        if !command.is_file() {
            anyhow::bail!(
                "[plugins.{name}].command ({}) does not exist or is not a file",
                entry.command
            );
        }
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
        let plugins: PluginsConfig = toml::from_str(
            "[plugins.ghost]\ncommand = \"/definitely/not/a/real/program\"\n",
        )
        .unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        let err = register_plugin_behaviors(&mut registry, &plugins).unwrap_err();
        let msg = err.to_string();
        assert!(msg.contains("[plugins.ghost].command"), "{msg}");
        assert!(msg.contains("/definitely/not/a/real/program"), "{msg}");
    }

    #[test]
    fn a_real_program_registers_under_its_config_name() {
        // Any existing file passes the startup check; whether it is a
        // *working* advisor is a per-tick question with a per-tick fallback.
        let dir = std::env::temp_dir().join("cloudkitty-016-plugin-test");
        std::fs::create_dir_all(&dir).unwrap();
        let program = dir.join("demo.sh");
        std::fs::write(&program, "#!/bin/sh\n").unwrap();

        let toml_text = format!("[plugins.demo]\ncommand = {:?}\n", program);
        let plugins: PluginsConfig = toml::from_str(&toml_text).unwrap();
        let mut registry = BehaviorRegistry::with_builtins();
        register_plugin_behaviors(&mut registry, &plugins).unwrap();
        assert!(registry.get("demo").is_some(), "the plugin is a behavior");

        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn an_unknown_plugin_field_is_a_startup_error_not_a_surprise() {
        let parsed: Result<PluginsConfig, _> = toml::from_str(
            "[plugins.demo]\ncommand = \"/bin/echo\"\nworkdir = \"/tmp\"\n",
        );
        assert!(parsed.is_err(), "unknown [plugins] fields are refused");
    }
}
