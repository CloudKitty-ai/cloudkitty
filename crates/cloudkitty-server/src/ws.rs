//! Live world updates over a WebSocket.
//!
//! A viewer fetches `GET /world` once for its first paint, then subscribes here and
//! receives the full world after every tick. Payloads are identical to `/world`, so
//! the client has exactly one shape to render.
//!
//! Inbound messages are ignored: this socket is a window, not a control surface.
//! Because it rides a `watch` channel, a slow client simply skips to the newest
//! world rather than falling behind forever -- and a client that disappears cannot
//! affect the simulation at all.

use axum::extract::ws::{Message, WebSocket, WebSocketUpgrade};
use axum::extract::State;
use axum::response::Response;

use crate::api::AppState;

pub async fn ws_handler(ws: WebSocketUpgrade, State(state): State<AppState>) -> Response {
    ws.on_upgrade(move |socket| push_world_updates(socket, state))
}

async fn push_world_updates(mut socket: WebSocket, state: AppState) {
    let mut receiver = state.published.clone();
    tracing::debug!("a viewer is watching");

    loop {
        // The world is serialized once per tick by the publisher; every viewer
        // shares that string. Clone it inside a block so the channel borrow is
        // released before the await -- holding it across one would stall the
        // simulation's publisher.
        let payload = {
            let published = receiver.borrow_and_update();
            published.snapshot_json.clone()
        };

        match payload {
            Some(json) => {
                if socket.send(Message::Text(json.to_string())).await.is_err() {
                    // The viewer closed the tab; nothing to clean up.
                    break;
                }
            }
            None => {
                // The publisher already logged why; there is nothing to send.
                break;
            }
        }

        if receiver.changed().await.is_err() {
            // The simulation stopped, so there is nothing left to watch.
            break;
        }
    }

    tracing::debug!("a viewer stopped watching");
}
