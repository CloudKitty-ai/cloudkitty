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
use cloudkitty_core::{
    ActivityEnd, Config, DistressEvent, Kitty, KittyId, RefusalEvent, WorldSnapshot,
};
use serde_json::json;
use tokio::sync::watch;

use crate::sim_task::Published;

#[derive(Clone)]
pub struct AppState {
    pub published: watch::Receiver<Arc<Published>>,
    pub config: Arc<Config>,
    /// Spec 040: the watchdog's latest welfare surface, served on /welfare.
    pub welfare: watch::Receiver<Arc<crate::watchdog::WelfareStatus>>,
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

/// Spec 040 FR-003: the standing welfare watch's current surface — every
/// live distress age, the alarm threshold, and whether an alarm is live.
/// A healthy world answers with the healthy shape, never an error.
pub async fn get_welfare(
    State(state): State<AppState>,
) -> Json<Arc<crate::watchdog::WelfareStatus>> {
    Json(state.welfare.borrow().clone())
}

/// Finished activities with the true tick spans they ran (spec 006): the
/// final tick of a scene clears the clock it stamped, so snapshots alone
/// cannot show how long a scene lasted -- these events can. Oldest first.
pub async fn get_activity_ends(State(state): State<AppState>) -> Json<Arc<Vec<ActivityEnd>>> {
    Json(state.current().activity_ends.clone())
}

/// The refusal window with its own bound (spec 046, envelope added at the
/// review-medium pass): `capacity` says how many events the ring holds
/// before wrapping, so a consumer can tell a truncated window from a short
/// history without hard-coding the knob's default (the /welfare threshold
/// precedent; `/config` omits `refusal_retention` at its default).
#[derive(serde::Serialize)]
pub struct RefusalWindow {
    pub capacity: usize,
    pub events: Arc<Vec<RefusalEvent>>,
}

/// Refusals (spec 046): every non-Idle proposal validation resolved to
/// Idle — the kitty, the proposal verbatim, the tick, whether a
/// continuing scene absorbed it (the kitty was mid-scene, minimum met or
/// not), and since spec 049 (T093) the `reason` (`partner_absent`,
/// `partner_busy`, `other`). A signal for the census, never read by the engine
/// (Article I). Full ring under `events`, oldest first, beside the ring's
/// `capacity`.
pub async fn get_refusals(State(state): State<AppState>) -> Json<RefusalWindow> {
    let published = state.current();
    Json(RefusalWindow {
        capacity: published.refusal_capacity,
        events: published.refusals.clone(),
    })
}

pub async fn get_config(State(state): State<AppState>) -> Json<Arc<Config>> {
    Json(state.config.clone())
}
