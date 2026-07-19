//! The read-only HTTP API.
//!
//! Every handler reads the latest published snapshot and returns it as-is. There
//! are no mutating endpoints: viewers watch the world, they do not touch it
//! (Article V).
//!
//! Greebles appear in these payloads exactly like any other element. Their
//! invisibility is a rendering rule in the client, never a filter here -- which is
//! what lets a kitty visibly chase "nothing" while the data says otherwise.

use std::sync::Arc;

use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::Json;
use cloudkitty_core::{Config, DistressEvent, Kitty, KittyId, WorldSnapshot};
use serde_json::json;
use tokio::sync::watch;

use crate::sim_task::Published;

#[derive(Clone)]
pub struct AppState {
    pub published: watch::Receiver<Arc<Published>>,
    pub config: Arc<Config>,
}

impl AppState {
    pub fn current(&self) -> Arc<Published> {
        self.published.borrow().clone()
    }
}

/// `{ "error": "..." }`, the one error shape this API produces.
pub struct ApiError {
    status: StatusCode,
    message: String,
}

impl ApiError {
    pub fn not_found(message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::NOT_FOUND,
            message: message.into(),
        }
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        (self.status, Json(json!({ "error": self.message }))).into_response()
    }
}

/// The full world: grid, kitties, elements (greebles included), recent meows.
pub async fn get_world(State(state): State<AppState>) -> Json<Arc<WorldSnapshot>> {
    Json(state.current().snapshot.clone())
}

pub async fn get_kitties(State(state): State<AppState>) -> Json<Vec<Kitty>> {
    Json(state.current().snapshot.kitties.clone())
}

pub async fn get_kitty(
    State(state): State<AppState>,
    Path(id): Path<KittyId>,
) -> Result<Json<Kitty>, ApiError> {
    state
        .current()
        .snapshot
        .kitty(id)
        .cloned()
        .map(Json)
        .ok_or_else(|| ApiError::not_found(format!("no kitty with id {id}")))
}

/// Distress events: a signal for whoever is watching, never a punishment for the
/// kitty (Article I). Edge-triggered, oldest first.
pub async fn get_distress(State(state): State<AppState>) -> Json<Arc<Vec<DistressEvent>>> {
    Json(state.current().distress.clone())
}

pub async fn get_config(State(state): State<AppState>) -> Json<Arc<Config>> {
    Json(state.config.clone())
}
