//! CloudKitty's server: the world's only owner, and a window onto it.
//!
//! The binary is a thin wrapper around this crate so integration tests can stand
//! up a real server -- simulation, REST and WebSocket -- on an ephemeral port.

pub mod api;
pub mod persist;
pub mod sim_task;
pub mod ws;

use std::path::Path;

use axum::routing::get;
use axum::Router;
use tower_http::cors::CorsLayer;
use tower_http::services::ServeDir;

use crate::api::AppState;

/// The complete application: read-only API, live updates, and the viewer itself.
pub fn build_router(state: AppState, client_dir: &Path) -> Router {
    Router::new()
        .route("/world", get(api::get_world))
        .route("/kitties", get(api::get_kitties))
        .route("/kitties/:id", get(api::get_kitty))
        .route("/events/distress", get(api::get_distress))
        .route("/events/activity", get(api::get_activity_ends))
        .route("/config", get(api::get_config))
        .route("/ws", get(ws::ws_handler))
        // Anything else is a static file: index.html, app.js, render.js.
        .fallback_service(ServeDir::new(client_dir))
        .layer(CorsLayer::permissive())
        .with_state(state)
}
