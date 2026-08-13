//! The traffic shapes. Each scheduler spawns connections against the shared
//! swarm and returns when its traffic is done; the sampler runs concurrently
//! and stops when the run shuts down (FR-002..FR-006).

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use crate::health::{evaluate, HealthThresholds};
use crate::metrics::{Class, EndReason, IntervalRow};
use crate::swarm::Shared;
use crate::viewer::{run_poll, run_viewer, ConnHandle};

/// Everything the schedulers need from the CLI, resolved to concrete values.
pub struct Plan {
    pub viewers: u64,
    pub step: u64,
    pub step_interval_s: f64,
    pub hold_s: f64,
    pub duration_s: f64,
    pub stall_fraction: f64,
    pub stall_after_s: f64,
    pub churn_rate: f64,
    pub poll_rate: f64,
    pub poll_endpoints: Vec<String>,
    pub thresholds: HealthThresholds,
    /// Stop a ramp after this many seconds even if it has not reached `--to`
    /// or a degraded step (so a run that outpaces the generator still ends and
    /// writes its record).
    pub max_duration_s: Option<f64>,
    /// Skip the first-paint `GET /world`, subscribing straight to `/ws`. Halves
    /// the per-viewer TLS handshake cost when the generator is CPU-bound and you
    /// are hunting the server's ceiling rather than mimicking a browser.
    pub skip_first_paint: bool,
}

/// A monotonically increasing connection id.
#[derive(Default)]
pub struct IdGen(std::sync::atomic::AtomicU64);
impl IdGen {
    fn next(&self) -> u64 {
        self.0.fetch_add(1, Ordering::Relaxed)
    }
}

/// Spawn one viewer and register it. Returns the join handle.
fn spawn_viewer(
    shared: &Arc<Shared>,
    ids: &IdGen,
    class: Class,
    stall_at: Option<f64>,
) -> tokio::task::JoinHandle<()> {
    let handle = ConnHandle::new(ids.next(), class);
    shared.register(handle.clone());
    let s = shared.clone();
    tokio::spawn(async move { run_viewer(s, handle, stall_at).await })
}

/// Start the background poller driver if a rate is set (FR-006). It issues GETs
/// across the endpoints until shutdown.
pub fn spawn_pollers(shared: &Arc<Shared>, plan: &Plan) -> Option<tokio::task::JoinHandle<()>> {
    if plan.poll_rate <= 0.0 || plan.poll_endpoints.is_empty() {
        return None;
    }
    let s = shared.clone();
    let endpoints = plan.poll_endpoints.clone();
    let gap = Duration::from_secs_f64(1.0 / plan.poll_rate);
    let mut shutdown = shared.shutdown.subscribe();
    Some(tokio::spawn(async move {
        let mut i = 0usize;
        loop {
            tokio::select! {
                _ = shutdown.recv() => return,
                _ = tokio::time::sleep(gap) => {
                    let path = endpoints[i % endpoints.len()].clone();
                    i += 1;
                    let s2 = s.clone();
                    tokio::spawn(async move { run_poll(s2, path).await });
                }
            }
        }
    }))
}

/// Ramp: grow concurrency a step at a time, holding each step, stopping at the
/// target or the first step that fails the health definition (FR-002).
pub async fn ramp(
    shared: Arc<Shared>,
    plan: &Plan,
    rows: Arc<Mutex<Vec<IntervalRow>>>,
    ids: &IdGen,
) {
    let mut open = 0u64;
    let mut step_num = 0u32;
    while open < plan.viewers {
        // Stop if the ramp has run past its time budget (the generator may never
        // reach `--to`); finalize still writes the record for what it reached.
        if let Some(max) = plan.max_duration_s {
            if shared.elapsed_s() >= max {
                return;
            }
        }
        step_num += 1;
        let want = (open + plan.step).min(plan.viewers);
        // Establish the new cohort, paced across step_interval. These rows are
        // NOT part of the step's hold, so the step tag stays None here.
        shared.set_step(None);
        let cohort = want - open;
        let pace = if cohort > 0 {
            plan.step_interval_s / cohort as f64
        } else {
            0.0
        };
        for _ in 0..cohort {
            spawn_viewer(&shared, ids, Class::Viewer, None);
            if pace > 0.0 {
                tokio::time::sleep(Duration::from_secs_f64(pace)).await;
            }
        }
        open = want;
        shared.set_target_conns(open);

        // Hold and measure: tag these interval rows with the step being held.
        shared.set_step(Some(step_num));
        let hold_start = shared.elapsed_s();
        tokio::time::sleep(Duration::from_secs_f64(plan.hold_s)).await;

        // Evaluate the step just held, over its interval rows.
        let step_rows: Vec<IntervalRow> = rows
            .lock()
            .unwrap()
            .iter()
            .filter(|r| r.scope == "interval" && r.t >= hold_start)
            .cloned()
            .collect();
        let verdict = evaluate(&step_rows, Some(shared.nominal_tick_ms()), &plan.thresholds);
        if !verdict.healthy {
            return; // first degraded step: stop here (FR-002)
        }
    }
}

/// Soak: hold a fixed concurrency for the duration (SC-005 smoke shape).
pub async fn soak(shared: Arc<Shared>, plan: &Plan, ids: &IdGen) {
    for _ in 0..plan.viewers {
        spawn_viewer(&shared, ids, Class::Viewer, None);
    }
    shared.set_target_conns(plan.viewers);
    tokio::time::sleep(Duration::from_secs_f64(plan.duration_s)).await;
}

/// Spike: establish all connections as fast as possible, then observe (FR-003).
pub async fn spike(shared: Arc<Shared>, plan: &Plan, ids: &IdGen) {
    shared.set_target_conns(plan.viewers);
    for _ in 0..plan.viewers {
        spawn_viewer(&shared, ids, Class::Viewer, None);
    }
    tokio::time::sleep(Duration::from_secs_f64(plan.duration_s)).await;
}

/// Slow-consumer: a fraction of viewers stop reading after a healthy period
/// (FR-004, SC-006).
pub async fn slow_consumer(shared: Arc<Shared>, plan: &Plan, ids: &IdGen) {
    let stall_count = (plan.viewers as f64 * plan.stall_fraction).round() as u64;
    shared.set_target_conns(plan.viewers);
    for i in 0..plan.viewers {
        let stall_at = if i < stall_count {
            Some(plan.stall_after_s)
        } else {
            None
        };
        spawn_viewer(&shared, ids, Class::Viewer, stall_at);
    }
    tokio::time::sleep(Duration::from_secs_f64(plan.duration_s)).await;
}

/// Churn: hold a steady concurrency while connections continuously arrive and
/// depart at a rate, each arrival paying the full first-paint cost (FR-005).
pub async fn churn(shared: Arc<Shared>, plan: &Plan, ids: &IdGen) {
    shared.set_target_conns(plan.viewers);
    // Steady-state lifetime: at rate r, holding N alive means each lives N/r.
    let full_life = (plan.viewers as f64 / plan.churn_rate.max(0.001)).max(1.0);
    // Prime the population with STAGGERED lifetimes spread across (0, full_life],
    // so the primed cohort departs one-at-a-time at the churn rate instead of
    // all at once -- otherwise concurrency collapses to zero at t=full_life.
    for i in 0..plan.viewers {
        let frac = (i + 1) as f64 / plan.viewers as f64;
        spawn_churned(&shared, ids, full_life * frac);
    }
    let gap = Duration::from_secs_f64(1.0 / plan.churn_rate.max(0.001));
    let mut shutdown = shared.shutdown.subscribe();
    let end = shared.elapsed_s() + plan.duration_s;
    loop {
        tokio::select! {
            _ = shutdown.recv() => return,
            _ = tokio::time::sleep(gap) => {
                if shared.elapsed_s() >= end { return; }
                spawn_churned(&shared, ids, full_life);
            }
        }
    }
}

/// A churned connection lives for `life_s` seconds, then departs -- so arrivals
/// and departures balance around the steady-state population.
fn spawn_churned(shared: &Arc<Shared>, ids: &IdGen, life_s: f64) {
    let handle = ConnHandle::new(ids.next(), Class::Viewer);
    shared.register(handle.clone());
    let life = Duration::from_secs_f64(life_s);
    let s = shared.clone();
    let done = Arc::new(AtomicBool::new(false));
    let d2 = done.clone();
    let h2 = handle.clone();
    tokio::spawn(async move {
        tokio::select! {
            _ = run_viewer(s, handle, None) => { d2.store(true, Ordering::Relaxed); }
            _ = tokio::time::sleep(life) => {
                // Departure: mark the socket closed and let the task drop it.
                if !d2.load(Ordering::Relaxed) {
                    h2.mark_departed();
                }
            }
        }
    });
    let _ = done;
}

impl ConnHandle {
    /// A churn departure: an ordinary, run-initiated close, not a server fault.
    pub fn mark_departed(&self) {
        self.open.store(false, Ordering::Relaxed);
        *self.end.lock().unwrap() = EndReason::ClosedByRun;
    }
}
