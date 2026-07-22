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
    config_text: &str,
) -> anyhow::Result<()> {
    let policy_names: std::collections::BTreeSet<&str> = config
        .kitties
        .iter()
        .filter_map(|k| k.behavior.strip_prefix("policy:"))
        .collect();
    if policy_names.is_empty() {
        return Ok(());
    }
    let rl = RlConfig::from_toml_str(config_text)
        .with_context(|| "the [rl] configuration does not parse")?;
    for name in policy_names {
        let policy = rl.policy.get(name).ok_or_else(|| {
            anyhow::anyhow!(
                "a kitty names behavior 'policy:{name}' but there is no                  [rl.policy.{name}] block with an artifact path"
            )
        })?;
        let expectations = PolicyBehavior::expectations(&rl);
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
