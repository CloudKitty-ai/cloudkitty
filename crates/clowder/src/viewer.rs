//! One connection's life: first-paint GET, WebSocket subscribe, read loop,
//! and (for a stall-selected viewer) the deliberate stop that fills kernel
//! buffers. Everything a connection measures flows into its [`ConnStats`]
//! (FR-001, FR-004, FR-007).

use std::sync::atomic::{AtomicBool, AtomicU8, Ordering};
use std::sync::Arc;
use std::time::Instant;

use futures::StreamExt;
use tokio_tungstenite::connect_async;

use crate::http;
use crate::metrics::{Class, ConnStats, EndReason, TickStep};
use crate::scan;
use crate::swarm::Shared;

/// A live connection the sampler can read: its class (mutable, for the
/// viewer→stalled transition) and its counters.
pub struct ConnHandle {
    pub id: u64,
    class: AtomicU8,
    pub stats: Arc<ConnStats>,
    pub open: AtomicBool,
    pub end: std::sync::Mutex<EndReason>,
}

impl ConnHandle {
    pub fn new(id: u64, class: Class) -> Arc<ConnHandle> {
        Arc::new(ConnHandle {
            id,
            class: AtomicU8::new(class as u8),
            stats: ConnStats::new(),
            open: AtomicBool::new(false),
            end: std::sync::Mutex::new(EndReason::Open),
        })
    }

    pub fn class(&self) -> Class {
        match self.class.load(Ordering::Relaxed) {
            0 => Class::Viewer,
            1 => Class::Stalled,
            _ => Class::Poller,
        }
    }

    fn set_class(&self, c: Class) {
        self.class.store(c as u8, Ordering::Relaxed);
    }

    fn finish(&self, reason: EndReason) {
        self.open.store(false, Ordering::Relaxed);
        *self.end.lock().unwrap() = reason;
    }
}

/// Run one viewer to completion or until the run's shutdown fires. `stall_at`
/// (seconds since run start) turns this viewer into a stalled consumer at that
/// moment: it stops reading, so its socket backs up and its measurements move
/// to the stalled class (research R8, SC-006).
pub async fn run_viewer(shared: Arc<Shared>, handle: Arc<ConnHandle>, stall_at: Option<f64>) {
    let connect_start = Instant::now();

    // First paint: the real viewer fetches /world once before subscribing.
    if let Err(e) = http::get(&shared.target.host, shared.target.port, "/world").await {
        handle.stats.errors.fetch_add(1, Ordering::Relaxed);
        handle.finish(EndReason::Refused);
        if e.contains("Too many open files") {
            shared.selfwatch.note_emfile();
        }
        return;
    }

    // Subscribe.
    let ws = match connect_async(&shared.target.ws_url).await {
        Ok((ws, _resp)) => ws,
        Err(e) => {
            handle.stats.errors.fetch_add(1, Ordering::Relaxed);
            handle.finish(EndReason::Refused);
            if e.to_string().contains("Too many open files") {
                shared.selfwatch.note_emfile();
            }
            return;
        }
    };

    let handshake_us = connect_start.elapsed().as_micros() as u64;
    handle
        .stats
        .handshake_us
        .store(handshake_us.max(1), Ordering::Relaxed);
    handle.open.store(true, Ordering::Relaxed);

    let (_write, mut read) = ws.split();
    let mut shutdown = shared.shutdown.subscribe();
    let mut last_msg = Instant::now();
    let mut first_validated = false;
    let mut stalled = false;

    loop {
        // A stalled viewer stops reading entirely and just holds the socket
        // open until the run ends.
        if !stalled {
            if let Some(at) = stall_at {
                if shared.elapsed_s() >= at {
                    handle.set_class(Class::Stalled);
                    stalled = true;
                }
            }
        }
        if stalled {
            tokio::select! {
                _ = shutdown.recv() => { handle.finish(EndReason::ClosedByRun); return; }
                _ = tokio::time::sleep(std::time::Duration::from_millis(200)) => { continue; }
            }
        }

        tokio::select! {
            _ = shutdown.recv() => {
                handle.finish(EndReason::ClosedByRun);
                return;
            }
            msg = read.next() => {
                match msg {
                    Some(Ok(m)) if m.is_text() || m.is_binary() => {
                        let data = m.into_data();
                        let now = Instant::now();
                        let gap_us = now.duration_since(last_msg).as_micros() as u64;
                        last_msg = now;

                        let tick = if !first_validated {
                            match scan::validate_first(&data) {
                                Some(t) => { first_validated = true; Some(t) }
                                None => None,
                            }
                        } else {
                            scan::scan_tick(&data)
                        };

                        match tick {
                            Some(t) => {
                                let step = handle.stats.record_update(t, data.len(), gap_us);
                                // Only a healthy viewer feeds the cadence reference.
                                if handle.class() == Class::Viewer && matches!(step, TickStep::Contiguous | TickStep::First) {
                                    shared.cadence.observe(handle.id, t, shared.elapsed_ms(), shared.cadence_stale_ms());
                                }
                            }
                            None => {
                                // A data frame with no parseable tick -- whether
                                // it is the first frame (not a CloudKitty world
                                // payload) or a later one (schema drift) -- is a
                                // payload problem, not a server-side drop or a
                                // handshake failure. Record the drift note (which
                                // explains the ended connection) and end as an
                                // ordinary run-side close so it feeds neither
                                // degradation signature.
                                handle.stats.errors.fetch_add(1, Ordering::Relaxed);
                                shared.note_schema_drift();
                                handle.finish(EndReason::ClosedByRun);
                                return;
                            }
                        }
                    }
                    Some(Ok(_)) => { /* ping/pong/close frame control; ignore */ }
                    Some(Err(_)) => {
                        handle.stats.errors.fetch_add(1, Ordering::Relaxed);
                        handle.finish(EndReason::ServerClosed);
                        return;
                    }
                    None => {
                        handle.finish(EndReason::ServerClosed);
                        return;
                    }
                }
            }
        }
    }
}

/// One poller request against a read endpoint (FR-006). Records latency into a
/// shared poller histogram via the swarm.
pub async fn run_poll(shared: Arc<Shared>, path: String) {
    match http::get(&shared.target.host, shared.target.port, &path).await {
        Ok(r) if (200..300).contains(&r.status) => shared.record_poll(r.elapsed_ms, false),
        Ok(_) => shared.record_poll(0.0, true),
        Err(_) => shared.record_poll(0.0, true),
    }
}
