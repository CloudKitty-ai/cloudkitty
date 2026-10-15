//! Spec 061: the stuck detector at decoding.
//!
//! The twin-fragility ruling's option 3 (GEN2-INPUTS, 2026-09-16): a
//! greedy deterministic policy in a state the world keeps returning it
//! to makes the same choice forever, and nothing breaks the loop. This
//! module watches every mind-class seat for the replay-verified stuck
//! signature — confined to the configured radius of a window anchor for
//! a window of ticks while one need holds a window-length armed
//! scene-free streak — and, when enforcing, substitutes that seat's next
//! proposal with the scripted needs-driven brain's decision for one tick
//! (Article IV's own named fallback; owner 2026-10-15: "scripted (needs
//! driven) until LLMs/two-tier fallback exists").
//!
//! Two halves, so no detector state lives in the decision path:
//!
//! - [`StuckDetector`] observes `&World` after each tick (the watchdog's
//!   pattern — the post-tick world IS the next tick's start-of-tick
//!   snapshot) and emits the next tick's fire plans into shared state.
//! - [`StuckGuard`] wraps each mind-class seat's registered behavior in
//!   EVERY mode, forwarding when idle. On its seat's fire tick it calls
//!   the inner advisor first (the record's "proposal replaced" — FR-011
//!   cannot be met otherwise), then substitutes in enforce or returns
//!   the inner decision untouched in observe.
//!
//! Determinism (FR-008): the wrapper can only reach `ctx.rng`, the
//! per-kitty per-tick stream that is discarded after the decision; the
//! master `SimRng` lives in `World` and is unreachable from here by
//! type. The substitute is a function of the start-of-tick snapshot and
//! that dealt stream, so replays reproduce identical fires and
//! substitutes. In observe mode nothing the engine reads changes at all.
//!
//! Configuration rides the server-owned `[stuck_detector]` toml table
//! (the `[watchdog]` foreign-table pattern): the engine `Config` and
//! `engine_defaults_sha256` are untouched by construction.
//!
//! Doctrine rule 6: no free-register kind is named anywhere in this
//! module outside `#[cfg(test)]` — the FR-005 guard is a test pinning
//! the needs-driven brain's free-register silence, not an inline filter.

use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::sync::{Arc, Mutex};

use async_trait::async_trait;
use cloudkitty_core::behavior::teacher::Teacher;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::seam::Decision;
use cloudkitty_core::{Activity, Behavior, DecisionContext, Kitty, KittyId, Position, World};
use serde::{Deserialize, Serialize};

#[derive(Debug, thiserror::Error)]
pub enum StuckConfigError {
    #[error("{0}")]
    Message(String),
    #[error("{field} = {value}: {expected}")]
    Invalid {
        field: String,
        value: String,
        expected: String,
    },
}

/// The detector's enablement (spec 061 FR-010, clarified option B).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum StuckMode {
    /// No tracking, no records, no behavior change.
    Off,
    /// The signature is tracked and every completed fire recorded with
    /// full attribution, but no proposal is substituted: on a budgetless
    /// run the world is tick-for-tick identical to off.
    Observe,
    /// Fires substitute the seat's proposal with the scripted brain's
    /// decision for that one tick.
    Enforce,
}

/// The `[stuck_detector]` table. Absent = these defaults: shipped
/// configuration-armed but DARK (FR-009, clarified option A — mode off,
/// armed at the Gen 2 seating). Window, armed line and radius defaults
/// are the measured choices of the spec's verification record
/// (specs/061-stuck-detector/research.md R4).
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields, default)]
pub struct StuckConfig {
    /// off / observe / enforce. The served Gen 1 default is off.
    pub mode: StuckMode,
    /// The signature window in ticks: confinement must hold this many
    /// consecutive ticks AND some one need must hold an armed
    /// scene-free streak this long. 30 is where the verification's
    /// borderline scripted fires vanish while the one real episode on
    /// record still fires.
    pub window: u64,
    /// A need is armed at or above this value. 75 is Article I's
    /// safeguard threshold: above it a reachable relief resource is
    /// guaranteed to exist, so a confined armed cat is by construction
    /// refusing reachable relief.
    pub armed_line: f64,
    /// Manhattan confinement radius around the window anchor. 1 is the
    /// replay-verified value; other values are accepted but unverified
    /// against the recorded arms.
    pub radius: u32,
    /// Capacity of the recent-fires ring served on GET /stuck.
    pub recent_fires: usize,
}

impl Default for StuckConfig {
    fn default() -> Self {
        Self {
            mode: StuckMode::Off,
            window: 30,
            armed_line: 75.0,
            radius: 1,
            recent_fires: 256,
        }
    }
}

#[derive(Debug, Default, Deserialize)]
struct FileWithStuck {
    #[serde(default)]
    stuck_detector: Option<StuckConfig>,
}

impl StuckConfig {
    /// Extracts and validates the `[stuck_detector]` table from a full
    /// config file's TOML text; everything else in the file is someone
    /// else's business. A file with no table yields the documented
    /// defaults.
    pub fn from_toml_str(text: &str) -> Result<Self, StuckConfigError> {
        let file: FileWithStuck =
            toml::from_str(text).map_err(|e| StuckConfigError::Message(e.to_string()))?;
        let config = file.stuck_detector.unwrap_or_default();
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<(), StuckConfigError> {
        let invalid = |field: &str, value: String, expected: &str| {
            Err(StuckConfigError::Invalid {
                field: format!("[stuck_detector] {field}"),
                value,
                expected: expected.to_string(),
            })
        };
        if self.window < 2 {
            return invalid("window", self.window.to_string(), "a 1-tick window is noise; must be at least 2");
        }
        if !(self.armed_line > 0.0 && self.armed_line <= 100.0) {
            return invalid(
                "armed_line",
                self.armed_line.to_string(),
                "needs are 0-100; the armed line must be in (0, 100]",
            );
        }
        if self.radius == 0 {
            return invalid("radius", "0".to_string(), "must be at least 1 tile");
        }
        if self.recent_fires == 0 {
            return invalid("recent_fires", "0".to_string(), "must hold at least 1 record");
        }
        Ok(())
    }
}

/// The need a seat's OWN activity is relieving, if any. The engine's
/// `Activity::governing_need` names whose need ends the scene — for
/// grooming WITH a target that is the groomed friend's bath, not the
/// groomer's — so a targeted groom must not clear the groomer's streak
/// (spec FR-002; the 2026-10-15 re-verification ran exactly this rule).
fn own_relief(activity: &Activity) -> Option<NeedKind> {
    match activity {
        Activity::Grooming { target: Some(_) } => None,
        other => other.governing_need(),
    }
}

/// Per-seat window state (data-model.md): the whole signature memory.
#[derive(Debug, Default, Clone)]
struct SeatSignature {
    anchor: Option<Position>,
    confined: u64,
    streaks: BTreeMap<NeedKind, u64>,
}

/// A completed signature, carried from observer to wrapper and into the
/// fire record.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FirePlan {
    /// The decision tick this fire substitutes: plans are matched
    /// against `ctx.world.tick`, the start-of-tick snapshot's stamp.
    pub target_tick: u64,
    pub window: u64,
    pub anchor: Position,
    pub confined_span: u64,
    pub armed_need: NeedKind,
    pub need_value: f32,
}

impl SeatSignature {
    /// One observed tick of the verified FR-001/FR-002 rule. Returns the
    /// completed signature when both window conditions close this tick.
    /// The post-fire reset IS FR-007's stand-down: a refire needs a
    /// fresh full window by construction.
    fn step(&mut self, kitty: &Kitty, config: &StuckConfig) -> Option<(Position, u64, NeedKind, f32)> {
        let escaped = match self.anchor {
            None => true,
            Some(anchor) => anchor.manhattan_distance(&kitty.pos) > config.radius,
        };
        if escaped {
            self.anchor = Some(kitty.pos);
            self.confined = 1;
            self.streaks.clear();
        } else {
            self.confined += 1;
        }

        let in_scene = kitty.activity.is_in_progress();
        let relief = own_relief(&kitty.activity);
        for kind in NeedKind::ALL {
            if in_scene {
                if relief == Some(kind) {
                    // The seat's own scene is relieving this need.
                    self.streaks.remove(&kind);
                }
                // Any other scene: the streak pauses. Strict
                // any-scene-resets semantics are wrong by measurement
                // (verification-2026-10-13.md): the one real episode on
                // record carries 1-2 tick play flickers.
            } else if f64::from(kitty.needs.get(kind)) >= config.armed_line {
                *self.streaks.entry(kind).or_insert(0) += 1;
            } else {
                self.streaks.remove(&kind);
            }
        }

        if self.confined >= config.window {
            for kind in NeedKind::ALL {
                if self.streaks.get(&kind).copied().unwrap_or(0) >= config.window {
                    let anchor = self.anchor.expect("confined implies an anchor");
                    let span = self.confined;
                    let value = kitty.needs.get(kind);
                    self.anchor = None;
                    self.confined = 0;
                    self.streaks.clear();
                    return Some((anchor, span, kind, value));
                }
            }
        }
        None
    }
}

/// One recorded perturbation event (FR-011): full attribution, every
/// field mandatory at construction (SC-003).
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct FireRecord {
    /// The decision tick the substitution applied to (the start-of-tick
    /// snapshot's stamp; the applied action lands in the world state
    /// published as tick + 1).
    pub tick: u64,
    pub kitty: KittyId,
    pub name: String,
    pub mode: StuckMode,
    pub window: u64,
    /// The window-anchor tile, `[x, y]`.
    pub anchor: [u32; 2],
    pub confined_span: u64,
    pub armed_need: NeedKind,
    pub need_value: f32,
    /// The inner advisor's decision. `null` only when the inner
    /// `try_decide` yielded no proposal (a failed plugin exchange) —
    /// the log line flattens that case to `"none"`.
    pub proposal_replaced: Option<Decision>,
    /// The scripted brain's decision: applied in enforce, computed for
    /// the record (and NOT applied) in observe.
    pub substitute: Decision,
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Serialize)]
pub struct SeatFireCounts {
    pub enforced: u64,
    pub observed: u64,
}

/// Everything fires write, behind one lock: the bounded ring and the
/// per-seat counts. The wrapper writes on fire ticks only; the observer
/// reads when building the status surface.
#[derive(Debug, Default)]
struct FireLog {
    ring: VecDeque<FireRecord>,
    counts: BTreeMap<KittyId, SeatFireCounts>,
}

/// State shared between the observer (writer of plans) and the guard
/// wrappers (consumers of plans, writers of records). One per server.
pub struct StuckShared {
    config: StuckConfig,
    plans: Mutex<BTreeMap<KittyId, FirePlan>>,
    log: Mutex<FireLog>,
}

impl StuckShared {
    pub fn new(config: StuckConfig) -> Arc<Self> {
        Arc::new(Self {
            config,
            plans: Mutex::new(BTreeMap::new()),
            log: Mutex::new(FireLog::default()),
        })
    }

    pub fn config(&self) -> StuckConfig {
        self.config
    }

    /// Consumes the seat's plan if one targets exactly this decision
    /// tick. A plan for a past tick is left for the observer to expire.
    fn take_plan(&self, kitty: KittyId, decision_tick: u64) -> Option<FirePlan> {
        let mut plans = self.plans.lock().expect("stuck plan lock");
        match plans.get(&kitty) {
            Some(plan) if plan.target_tick == decision_tick => plans.remove(&kitty),
            _ => None,
        }
    }

    fn record(&self, record: FireRecord) {
        let mut log = self.log.lock().expect("stuck log lock");
        let counts = log.counts.entry(record.kitty).or_default();
        match record.mode {
            StuckMode::Enforce => counts.enforced += 1,
            StuckMode::Observe => counts.observed += 1,
            StuckMode::Off => unreachable!("an off detector records nothing"),
        }
        log.ring.push_back(record);
        while log.ring.len() > self.config.recent_fires {
            log.ring.pop_front();
        }
    }
}

/// One `armed` row on GET /stuck: a tracked seat's live trigger state
/// (FR-012 — the forward hook the deferred distress intervention keys
/// on without re-deriving the rule).
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct ArmedRow {
    pub kitty: KittyId,
    pub name: String,
    pub confined: u64,
    pub hottest_need: Option<NeedKind>,
    pub streak: u64,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct SeatRow {
    pub kitty: KittyId,
    pub name: String,
    pub enforced: u64,
    pub observed: u64,
}

/// What GET /stuck serves (contract §2). With mode off: config echo and
/// empty collections — the surface exists dark (FR-009).
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct StuckStatus {
    pub mode: StuckMode,
    pub window: u64,
    pub armed_line: f64,
    pub radius: u32,
    pub per_seat: Vec<SeatRow>,
    pub armed: Vec<ArmedRow>,
    pub recent: Vec<FireRecord>,
}

impl StuckStatus {
    pub fn dark(config: StuckConfig) -> Self {
        Self {
            mode: config.mode,
            window: config.window,
            armed_line: config.armed_line,
            radius: config.radius,
            per_seat: Vec::new(),
            armed: Vec::new(),
            recent: Vec::new(),
        }
    }
}

/// The post-tick observer (the watchdog's pattern): reads `&World`,
/// advances per-seat signatures, emits next-tick fire plans. `&World`
/// is the whole non-interference argument on this half — it cannot
/// mutate the simulation and cannot reach the master RNG.
pub struct StuckDetector {
    shared: Arc<StuckShared>,
    /// Plugin behavior names declared `class = "mind"`; policy seats are
    /// mind-class by their `policy:` prefix (research.md R6).
    mind_plugins: BTreeSet<String>,
    signatures: BTreeMap<KittyId, SeatSignature>,
}

impl StuckDetector {
    pub fn new(shared: Arc<StuckShared>, mind_plugins: BTreeSet<String>) -> Self {
        Self {
            shared,
            mind_plugins,
            signatures: BTreeMap::new(),
        }
    }

    /// FR-003's boundary: `policy:*` or a plugin declared mind. Scripted
    /// seats and built-ins have no entry anywhere in the detector.
    fn is_mind(&self, behavior: &str) -> bool {
        behavior.starts_with("policy:") || self.mind_plugins.contains(behavior)
    }

    /// Reads the world after a tick, advances every tracked signature,
    /// installs the next tick's fire plans, and returns the status
    /// surface. With mode off this tracks nothing and serves the dark
    /// shape.
    pub fn observe(&mut self, world: &World) -> StuckStatus {
        let config = self.shared.config;
        if config.mode == StuckMode::Off {
            return StuckStatus::dark(config);
        }

        // A plan for a decision tick that has already run and was not
        // consumed (served-path bench) expires here: the signature state
        // was reset at emission, so a still-stuck episode re-accumulates
        // and fires again after a fresh full window (research.md R2).
        self.shared
            .plans
            .lock()
            .expect("stuck plan lock")
            .retain(|_, plan| plan.target_tick >= world.tick);

        let mut armed = Vec::new();
        let mut tracked_now = BTreeSet::new();
        for kitty in world.kitties.iter() {
            if !self.is_mind(&kitty.behavior) {
                continue;
            }
            tracked_now.insert(kitty.id);
            let signature = self.signatures.entry(kitty.id).or_default();
            if let Some((anchor, span, need, value)) = signature.step(kitty, &config) {
                self.shared.plans.lock().expect("stuck plan lock").insert(
                    kitty.id,
                    FirePlan {
                        // The post-tick world's stamp IS the stamp the
                        // next decisions' start-of-tick snapshot carries.
                        target_tick: world.tick,
                        window: config.window,
                        anchor,
                        confined_span: span,
                        armed_need: need,
                        need_value: value,
                    },
                );
            }
            let (hottest_need, streak) = signature
                .streaks
                .iter()
                .max_by_key(|(_, count)| **count)
                .map(|(kind, count)| (Some(*kind), *count))
                .unwrap_or((None, 0));
            armed.push(ArmedRow {
                kitty: kitty.id,
                name: kitty.name.clone(),
                confined: signature.confined,
                hottest_need,
                streak,
            });
        }
        // A reseated world drops stale seats (Article II says kitties
        // never vanish, but seats can be reconfigured on restart).
        self.signatures.retain(|id, _| tracked_now.contains(id));

        let log = self.shared.log.lock().expect("stuck log lock");
        let per_seat = world
            .kitties
            .iter()
            .filter(|k| self.is_mind(&k.behavior))
            .map(|k| {
                let counts = log.counts.get(&k.id).copied().unwrap_or_default();
                SeatRow {
                    kitty: k.id,
                    name: k.name.clone(),
                    enforced: counts.enforced,
                    observed: counts.observed,
                }
            })
            .collect();
        StuckStatus {
            mode: config.mode,
            window: config.window,
            armed_line: config.armed_line,
            radius: config.radius,
            per_seat,
            armed,
            recent: log.ring.iter().cloned().collect(),
        }
    }
}

/// The guard wrapper (the `SeatClassed` pattern): wraps every mind-class
/// seat's registered behavior in every mode, forwarding when it has
/// nothing to do. Forwards `try_decide` per the wrapper-author contract
/// in `behavior/mod.rs`, and `is_builtin` so the budget treats the seat
/// as its inner advisor is treated.
pub struct StuckGuard {
    inner: Arc<dyn Behavior>,
    shared: Arc<StuckShared>,
}

impl StuckGuard {
    pub fn new(inner: Arc<dyn Behavior>, shared: Arc<StuckShared>) -> Self {
        Self { inner, shared }
    }

    /// The fire path, shared by both trait methods. `inner` is the inner
    /// advisor's verdict for this tick, already computed (inner FIRST:
    /// the record's "proposal replaced" exists only if the mind ran;
    /// research.md R3). Returns what dispatch should use.
    async fn fire(
        &self,
        ctx: &DecisionContext,
        plan: FirePlan,
        inner: Option<Decision>,
    ) -> Option<Decision> {
        let mode = self.shared.config.mode;
        if mode == StuckMode::Off {
            // Unreachable in practice (an off observer emits no plans),
            // but a decision thread must never panic over a plan that
            // slipped through: forward the mind's verdict untouched.
            return inner;
        }
        // The substitute draws only from ctx.rng, the per-decision
        // stream discarded after this tick's decision (FR-008).
        let substitute = Teacher::NEEDS_DRIVEN.decide(ctx).await;
        let record = FireRecord {
            tick: plan.target_tick,
            kitty: ctx.me.id,
            name: ctx.me.name.clone(),
            mode,
            window: plan.window,
            anchor: [plan.anchor.x, plan.anchor.y],
            confined_span: plan.confined_span,
            armed_need: plan.armed_need,
            need_value: plan.need_value,
            proposal_replaced: inner,
            substitute,
        };
        log_fire(&record);
        self.shared.record(record);
        match mode {
            StuckMode::Enforce => Some(substitute),
            // Observe: the mind's own verdict stands, `None` included —
            // the engine's uniform fallback rule must see it unchanged.
            StuckMode::Observe => inner,
            StuckMode::Off => inner,
        }
    }
}

#[async_trait]
impl Behavior for StuckGuard {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        match self.shared.take_plan(ctx.me.id, ctx.world.tick) {
            None => self.inner.decide(ctx).await,
            Some(plan) => {
                let inner = self.inner.decide(ctx).await;
                self.fire(ctx, plan, Some(inner))
                    .await
                    .expect("a Some inner always yields a decision")
            }
        }
    }

    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Decision> {
        match self.shared.take_plan(ctx.me.id, ctx.world.tick) {
            None => self.inner.try_decide(ctx).await,
            Some(plan) => {
                let inner = self.inner.try_decide(ctx).await;
                self.fire(ctx, plan, inner).await
            }
        }
    }

    fn is_builtin(&self) -> bool {
        self.inner.is_builtin()
    }
}

/// Renders one fire as a structured serving-log line (contract §3: these
/// flattened field names are what the corpus INVESTIGATE consumer and
/// the Gen 2 battery re-read parse; a rename is a breaking change).
/// WARN for an enforced substitution, INFO for an observe-only record.
fn log_fire(record: &FireRecord) {
    let replaced = match &record.proposal_replaced {
        Some(decision) => format!("{:?}", decision.activity),
        None => "none".to_string(),
    };
    let replaced_message = record
        .proposal_replaced
        .and_then(|d| d.message)
        .map(|m| format!("{m:?}"))
        .unwrap_or_default();
    let substitute = format!("{:?}", record.substitute.activity);
    let substitute_message = record
        .substitute
        .message
        .map(|m| format!("{m:?}"))
        .unwrap_or_default();
    match record.mode {
        StuckMode::Enforce => tracing::warn!(
            kitty = record.kitty,
            name = %record.name,
            tick = record.tick,
            mode = "enforce",
            window = record.window,
            anchor_x = record.anchor[0],
            anchor_y = record.anchor[1],
            confined_span = record.confined_span,
            armed_need = ?record.armed_need,
            need_value = record.need_value,
            proposal_replaced = %replaced,
            replaced_message = %replaced_message,
            substitute = %substitute,
            substitute_message = %substitute_message,
            "stuck fire"
        ),
        StuckMode::Observe => tracing::info!(
            kitty = record.kitty,
            name = %record.name,
            tick = record.tick,
            mode = "observe",
            window = record.window,
            anchor_x = record.anchor[0],
            anchor_y = record.anchor[1],
            confined_span = record.confined_span,
            armed_need = ?record.armed_need,
            need_value = record.need_value,
            proposal_replaced = %replaced,
            replaced_message = %replaced_message,
            substitute = %substitute,
            substitute_message = %substitute_message,
            "stuck fire (observe-only)"
        ),
        StuckMode::Off => unreachable!("an off detector records nothing"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use cloudkitty_core::action::Action;
    use cloudkitty_core::behavior::BehaviorRegistry;
    use cloudkitty_core::config::KittyConfig;
    use cloudkitty_core::grid::Direction;
    use cloudkitty_core::meow::MessageKind;
    use cloudkitty_core::seam::drive_tick;
    use cloudkitty_core::test_support::test_config;
    use cloudkitty_core::Config;

    fn cfg(mode: StuckMode, window: u64, armed_line: f64) -> StuckConfig {
        StuckConfig {
            mode,
            window,
            armed_line,
            ..StuckConfig::default()
        }
    }

    // ---------- T004: the [stuck_detector] table ----------

    #[test]
    fn absent_table_yields_the_documented_defaults() {
        let config = StuckConfig::from_toml_str("[world]\nseed = 1\n").unwrap();
        assert_eq!(config, StuckConfig::default());
        assert_eq!(config.mode, StuckMode::Off, "shipped dark (FR-009)");
        assert_eq!(
            (config.window, config.armed_line, config.radius, config.recent_fires),
            (30, 75.0, 1, 256),
            "the measured defaults of research.md R4"
        );
    }

    #[test]
    fn invalid_values_fail_at_load_naming_the_key() {
        for (toml, needle) in [
            ("[stuck_detector]\nwobble = 3\n", "wobble"),
            ("[stuck_detector]\nwindow = 1\n", "window"),
            ("[stuck_detector]\narmed_line = 0.0\n", "armed_line"),
            ("[stuck_detector]\narmed_line = 100.5\n", "armed_line"),
            ("[stuck_detector]\nradius = 0\n", "radius"),
            ("[stuck_detector]\nrecent_fires = 0\n", "recent_fires"),
            ("[stuck_detector]\nmode = \"on\"\n", "mode"),
        ] {
            let err = StuckConfig::from_toml_str(toml)
                .expect_err(&format!("{toml:?} must fail at load"));
            assert!(
                err.to_string().contains(needle),
                "{toml:?} error must name {needle}: {err}"
            );
        }
    }

    // ---------- T005: the signature engine ----------

    /// A synthetic seat for driving the state machine directly: one real
    /// kitty, mutated per tick.
    fn seat() -> Kitty {
        let config = test_config();
        let world = World::generate(&config);
        let mut kitty = world.kitties[0].clone();
        kitty.activity = Activity::Idle;
        kitty.pos = Position::new(8, 8);
        kitty
    }

    fn arm(kitty: &mut Kitty, kind: NeedKind) {
        kitty.needs.add(kind, 200.0); // clamps at 100: armed at any line
    }

    #[test]
    fn the_synthetic_pacer_fires_every_window_at_every_swept_setting() {
        // Parity with stuck_rule_replay.py's selftest: the two-tile
        // pacer fires exactly 200 // window times — the post-fire reset
        // alone spaces refires, no extra stand-down tick (FR-007).
        for window in [20u64, 30, 50] {
            for armed_line in [75.0, 90.0] {
                let config = cfg(StuckMode::Enforce, window, armed_line);
                let mut signature = SeatSignature::default();
                let mut kitty = seat();
                arm(&mut kitty, NeedKind::Eat);
                let mut fires = 0;
                for t in 0..200u64 {
                    kitty.pos = Position::new(10 + (t % 2) as u32, 10);
                    if signature.step(&kitty, &config).is_some() {
                        fires += 1;
                    }
                }
                assert_eq!(
                    fires,
                    200 / window,
                    "window {window} armed {armed_line}: the pacer fires every full window"
                );
            }
        }
    }

    #[test]
    fn a_scene_flicker_pauses_the_streak_and_the_strict_reset_is_rejected() {
        // The one real episode on record carries 1-2 tick play flickers;
        // a strict any-scene-resets gate masks it at window >= 30
        // (verification-2026-10-13.md). Here: a 2-tick flicker delays
        // the fire by exactly its own length, never by a fresh window.
        let config = cfg(StuckMode::Enforce, 30, 75.0);
        let mut signature = SeatSignature::default();
        let mut kitty = seat();
        arm(&mut kitty, NeedKind::Eat);
        let mut fire_at = None;
        for t in 0..60u64 {
            kitty.activity = if (10..12).contains(&t) {
                Activity::Playing { target: None }
            } else {
                Activity::Idle
            };
            if signature.step(&kitty, &config).is_some() && fire_at.is_none() {
                fire_at = Some(t);
            }
        }
        // 30 armed scene-free ticks need 32 steps (2 paused): fire on
        // the 32nd step, index 31. A strict gate would push it to 41.
        assert_eq!(fire_at, Some(31), "the flicker pauses, never resets");
    }

    #[test]
    fn own_relief_clears_but_grooming_another_only_pauses() {
        // FR-002's own-relief rule: a targeted groom governs the
        // FRIEND's bath, so the groomer's own bath streak must survive
        // it; a self-groom is the seat's own relief and clears.
        let fire_after = |groom_target: Option<KittyId>| {
            let config = cfg(StuckMode::Enforce, 20, 75.0);
            let mut signature = SeatSignature::default();
            let mut kitty = seat();
            arm(&mut kitty, NeedKind::Bath);
            let mut fire_at = None;
            for t in 0..60u64 {
                kitty.activity = if t == 10 {
                    Activity::Grooming { target: groom_target }
                } else {
                    Activity::Idle
                };
                if signature.step(&kitty, &config).is_some() && fire_at.is_none() {
                    fire_at = Some(t);
                }
            }
            fire_at.expect("both arms fire eventually")
        };
        assert_eq!(
            fire_after(Some(2)),
            20,
            "groom-other pauses: 20 armed ticks need 21 steps (one paused), fire at index 20"
        );
        assert_eq!(
            fire_after(None),
            30,
            "self-groom clears: 20 fresh armed ticks after the clear, fire at index 30"
        );
    }

    #[test]
    fn below_the_line_clears_only_on_a_scene_free_tick() {
        // FR-002: a scene-free below-line tick clears the streak; the
        // same value seen during a non-relieving scene only pauses.
        let fire_after = |dip_in_scene: bool| {
            let config = cfg(StuckMode::Enforce, 20, 75.0);
            let mut signature = SeatSignature::default();
            let mut kitty = seat();
            arm(&mut kitty, NeedKind::Eat);
            let mut fire_at = None;
            for t in 0..60u64 {
                if t == 10 {
                    kitty.needs.add(NeedKind::Eat, -60.0); // below 75
                    kitty.activity = if dip_in_scene {
                        Activity::Playing { target: None }
                    } else {
                        Activity::Idle
                    };
                } else if t == 11 {
                    kitty.needs.add(NeedKind::Eat, 200.0); // re-armed
                    kitty.activity = Activity::Idle;
                }
                if signature.step(&kitty, &config).is_some() && fire_at.is_none() {
                    fire_at = Some(t);
                }
            }
            fire_at.expect("both arms fire eventually")
        };
        assert_eq!(fire_after(true), 20, "an in-scene dip pauses");
        assert_eq!(fire_after(false), 30, "a scene-free dip clears");
    }

    #[test]
    fn escaping_the_radius_resets_the_anchor_and_the_window() {
        let config = cfg(StuckMode::Enforce, 20, 75.0);
        let mut signature = SeatSignature::default();
        let mut kitty = seat();
        arm(&mut kitty, NeedKind::Eat);
        let mut fire_at = None;
        for t in 0..60u64 {
            // Ten ticks at the anchor, then a 3-tile jump, then still.
            kitty.pos = if t < 10 {
                Position::new(8, 8)
            } else {
                Position::new(11, 8)
            };
            if signature.step(&kitty, &config).is_some() && fire_at.is_none() {
                fire_at = Some(t);
            }
        }
        assert_eq!(
            fire_at,
            Some(29),
            "confinement never accumulates across an escape: 20 fresh ticks from the new anchor"
        );
    }

    #[test]
    fn arming_mid_window_starts_the_streak_at_the_crossing() {
        let config = cfg(StuckMode::Enforce, 20, 75.0);
        let mut signature = SeatSignature::default();
        let mut kitty = seat(); // needs start well below 75 (asserted)
        assert!(
            NeedKind::ALL.iter().all(|k| kitty.needs.get(*k) < 75.0),
            "fixture precondition: nothing armed at the start"
        );
        let mut fire_at = None;
        for t in 0..60u64 {
            if t == 10 {
                arm(&mut kitty, NeedKind::Eat);
            }
            if signature.step(&kitty, &config).is_some() && fire_at.is_none() {
                fire_at = Some(t);
            }
        }
        assert_eq!(
            fire_at,
            Some(29),
            "the streak starts at the crossing, not retroactively: fire 20 ticks after arming"
        );
    }

    // ---------- T006: the observer ----------

    /// A config whose roster holds one policy seat (mind), one scripted
    /// hold seat, far apart.
    fn observer_config() -> Config {
        let mut config = test_config();
        config.kitties = vec![
            KittyConfig::new(1, "Pacer", 3, 3, "policy:dither"),
            KittyConfig::new(2, "Holder", 12, 12, "hold"),
        ];
        config
    }

    #[test]
    fn only_mind_class_seats_are_tracked() {
        let config = observer_config();
        let mut world = World::generate(&config);
        world.kitties[1].behavior = "plugmind".to_string();
        let shared = StuckShared::new(cfg(StuckMode::Observe, 20, 75.0));
        // Declared mind plugins extend the policy: prefix rule (R6).
        let mut detector = StuckDetector::new(
            shared.clone(),
            ["plugmind".to_string()].into_iter().collect(),
        );
        let status = detector.observe(&world);
        let tracked: Vec<KittyId> = status.per_seat.iter().map(|r| r.kitty).collect();
        assert_eq!(tracked, vec![1, 2], "policy:* and class=mind plugins, nothing else");

        world.kitties[1].behavior = "needs_driven".to_string();
        let status = detector.observe(&world);
        let tracked: Vec<KittyId> = status.per_seat.iter().map(|r| r.kitty).collect();
        assert_eq!(tracked, vec![1], "a scripted seat has no entry anywhere (FR-003)");
        assert!(status.armed.iter().all(|row| row.kitty == 1));
    }

    #[test]
    fn a_plan_targets_the_next_decision_tick_and_expires_unconsumed() {
        let config = observer_config();
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        let shared = StuckShared::new(cfg(StuckMode::Enforce, 20, 75.0));
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        // Hold the world still by hand: observe() is the only mover of
        // detector state, and world.tick is ours to stamp.
        for t in 1..=20u64 {
            world.tick = t;
            detector.observe(&world);
        }
        {
            let plans = shared.plans.lock().unwrap();
            let plan = plans.get(&1).expect("20 confined armed observations complete the window");
            assert_eq!(
                plan.target_tick, 20,
                "the post-tick stamp IS the next decisions' snapshot stamp"
            );
            assert_eq!(plan.anchor, world.kitties[0].pos);
            assert_eq!(plan.confined_span, 20);
            assert_eq!(plan.armed_need, NeedKind::Eat);
        }
        // Nobody consumed it (a benched seat, served path): the next
        // observation expires it, and the reset state re-accumulates.
        world.tick = 21;
        detector.observe(&world);
        assert!(
            shared.plans.lock().unwrap().get(&1).is_none(),
            "an unconsumed plan expires rather than firing late"
        );
    }

    #[test]
    fn off_mode_tracks_nothing_and_serves_the_dark_shape() {
        let config = observer_config();
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        let shared = StuckShared::new(cfg(StuckMode::Off, 20, 75.0));
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());
        for t in 1..=60u64 {
            world.tick = t;
            let status = detector.observe(&world);
            assert_eq!(status.mode, StuckMode::Off);
            assert!(status.per_seat.is_empty() && status.armed.is_empty() && status.recent.is_empty());
        }
        assert!(shared.plans.lock().unwrap().is_empty(), "off emits no plans ever");
    }

    // ---------- T007/T009: the guard wrapper, through real dispatch ----------

    /// The state-dependent doctored mind (quickstart §1): dithers
    /// East/West only on its home row, idles anywhere else — one
    /// scripted step off the row genuinely ends the dither loop.
    struct HomeDither {
        home_y: u32,
    }

    #[async_trait]
    impl Behavior for HomeDither {
        async fn decide(&self, ctx: &DecisionContext) -> Decision {
            if ctx.me.pos.y == self.home_y {
                let direction = if ctx.me.pos.x % 2 == 0 {
                    Direction::East
                } else {
                    Direction::West
                };
                Decision::silent(Action::move_to(direction))
            } else {
                Decision::silent(Action::Idle)
            }
        }
    }

    /// A scripted anchor that never moves (for boxing and boundaries).
    struct HoldStill;

    #[async_trait]
    impl Behavior for HoldStill {
        async fn decide(&self, _ctx: &DecisionContext) -> Decision {
            Decision::silent(Action::Idle)
        }
    }

    fn registry_with(
        shared: Option<&Arc<StuckShared>>,
        dither_home_y: u32,
    ) -> BehaviorRegistry {
        let mut registry = BehaviorRegistry::with_builtins();
        let dither: Arc<dyn Behavior> = Arc::new(HomeDither { home_y: dither_home_y });
        match shared {
            Some(shared) => registry.register(
                "policy:dither".to_string(),
                Arc::new(StuckGuard::new(dither, shared.clone())),
            ),
            None => registry.register("policy:dither".to_string(), dither),
        }
        registry.register("hold".to_string(), Arc::new(HoldStill));
        registry
    }

    /// Drives `ticks` world ticks with the observer in the loop, exactly
    /// as sim_task wires it, returning the dispatched decision per tick
    /// for the watched seat.
    fn run_world(
        world: &mut World,
        registry: &BehaviorRegistry,
        config: &Arc<Config>,
        detector: &mut StuckDetector,
        seat: KittyId,
        ticks: u64,
    ) -> Vec<(u64, Decision)> {
        let mut dispatched = Vec::new();
        for _ in 0..ticks {
            let decision_tick = world.tick;
            let driven = drive_tick(world, registry, config);
            let record = driven
                .report
                .record(seat)
                .expect("the watched seat decided");
            dispatched.push((
                decision_tick,
                Decision {
                    activity: record.proposed,
                    message: record.proposed_message,
                },
            ));
            detector.observe(world);
        }
        dispatched
    }

    #[test]
    fn enforce_fires_on_the_exact_tick_and_dispatch_applies_the_substitute() {
        let window = 20u64;
        let config = Arc::new(observer_config());
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        let shared = StuckShared::new(cfg(StuckMode::Enforce, window, 75.0));
        let registry = registry_with(Some(&shared), 3);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        let dispatched = run_world(&mut world, &registry, &config, &mut detector, 1, 3 * window);

        let records: Vec<FireRecord> =
            shared.log.lock().unwrap().ring.iter().cloned().collect();
        assert!(!records.is_empty(), "the dither loop fires");
        // Exactness (analysis C2): the first observation runs after the
        // first tick (world.tick == 1), so the window completes at the
        // observation stamped `window`, and that IS the decision tick it
        // substitutes. An equality — a late fire fails here.
        assert_eq!(records[0].tick, window, "fires on the exact predicted tick");
        for record in &records {
            assert_eq!(record.mode, StuckMode::Enforce);
            assert_eq!(record.armed_need, NeedKind::Eat);
            assert_eq!(record.window, window);
            assert!(record.confined_span >= window);
            let (_, dispatched_then) = dispatched
                .iter()
                .find(|(t, _)| *t == record.tick)
                .expect("the fire tick was dispatched");
            assert_eq!(
                *dispatched_then, record.substitute,
                "on a fire tick dispatch uses the scripted substitute"
            );
            let inner = record.proposal_replaced.expect("the mind proposed");
            assert_ne!(
                inner, record.substitute,
                "fixture sanity: the recorded inner proposal is the dither, not the substitute"
            );
        }
        // FR-007: refires only after a fresh full window — never on
        // consecutive ticks.
        for pair in records.windows(2) {
            assert!(
                pair[1].tick - pair[0].tick >= window,
                "refire gap {} < window {window}",
                pair[1].tick - pair[0].tick
            );
        }
        // Negative sanity on the fixture itself: before the first fire,
        // every dispatched decision was the dither's own.
        for (t, decision) in &dispatched {
            if *t < window {
                assert!(
                    matches!(decision.activity, Action::Move { .. }),
                    "pre-fire tick {t}: the mind's dither was dispatched"
                );
            }
        }
    }

    #[test]
    fn two_seats_sharing_one_wrapped_instance_each_fire_on_their_own_window() {
        let window = 20u64;
        let mut config = observer_config();
        config.kitties = vec![
            KittyConfig::new(1, "PacerA", 3, 3, "policy:dither"),
            KittyConfig::new(2, "PacerB", 12, 3, "policy:dither"),
        ];
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        arm(&mut world.kitties[1], NeedKind::Drink);
        let shared = StuckShared::new(cfg(StuckMode::Enforce, window, 75.0));
        let registry = registry_with(Some(&shared), 3);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        for _ in 0..2 * window {
            drive_tick(&mut world, &registry, &config, );
            detector.observe(&world);
        }
        let records: Vec<FireRecord> =
            shared.log.lock().unwrap().ring.iter().cloned().collect();
        let seats: BTreeSet<KittyId> = records.iter().map(|r| r.kitty).collect();
        assert_eq!(
            seats,
            [1, 2].into_iter().collect(),
            "one shared Arc serves both seats, each with its own window"
        );
        for record in &records {
            let expected_need = if record.kitty == 1 { NeedKind::Eat } else { NeedKind::Drink };
            assert_eq!(record.armed_need, expected_need, "per-seat attribution never crosses");
        }
    }

    #[test]
    fn a_boxed_in_seat_fires_and_resolves_through_the_ordinary_path() {
        // Spec edge case: no legal move, the substitute resolves to a
        // safe outcome through ordinary validation, the fire is still
        // recorded, and there is no in-tick retry (one record per fire).
        let window = 20u64;
        let mut config = observer_config();
        config.kitties = vec![
            KittyConfig::new(1, "Boxed", 5, 5, "policy:dither"),
            KittyConfig::new(2, "N", 5, 4, "hold"),
            KittyConfig::new(3, "S", 5, 6, "hold"),
            KittyConfig::new(4, "W", 4, 5, "hold"),
            KittyConfig::new(5, "E", 6, 5, "hold"),
        ];
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        let shared = StuckShared::new(cfg(StuckMode::Enforce, window, 75.0));
        let registry = registry_with(Some(&shared), 5);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        for _ in 0..window + 2 {
            drive_tick(&mut world, &registry, &config);
            detector.observe(&world);
        }
        let records: Vec<FireRecord> =
            shared.log.lock().unwrap().ring.iter().cloned().collect();
        assert_eq!(records.len(), 1, "one fire, no in-tick retry");
        assert_eq!(records[0].tick, window);
        assert_eq!(
            world.kitties[0].pos,
            Position::new(5, 5),
            "boxed in: every move (the dither's and any substitute's) was refused"
        );
    }

    // ---------- T014: non-interference (off and observe are inert) ----------

    fn fingerprint(world: &World) -> String {
        serde_json::to_string(world).expect("worlds serialize")
    }

    #[test]
    fn off_paired_worlds_are_byte_identical_with_the_wrapper_in_place() {
        // The off pairing exercises the real forwarding path (analysis
        // C4): mind seats are WRAPPED and the detector constructed, mode
        // off — against a bare registry with no detector at all.
        let config = Arc::new(observer_config());
        let mut plain_world = World::generate(&config);
        let mut guarded_world = World::generate(&config);
        let plain = registry_with(None, 3);
        let shared = StuckShared::new(cfg(StuckMode::Off, 20, 75.0));
        let guarded = registry_with(Some(&shared), 3);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        for _ in 0..2000 {
            drive_tick(&mut plain_world, &plain, &config);
            drive_tick(&mut guarded_world, &guarded, &config);
            detector.observe(&guarded_world);
        }
        assert_eq!(
            fingerprint(&plain_world),
            fingerprint(&guarded_world),
            "an off detector changes nothing, wrapper included"
        );
        assert!(shared.log.lock().unwrap().ring.is_empty(), "and records nothing");
    }

    #[test]
    fn observe_mode_is_byte_identical_to_off_while_recording_the_fire() {
        // FR-008's extension made testable: on the budgetless path an
        // observe-mode world is tick-for-tick the plain world, while the
        // fire record exists with full attribution.
        let window = 20u64;
        let config = Arc::new(observer_config());
        let mut plain_world = World::generate(&config);
        let mut observed_world = World::generate(&config);
        arm(&mut plain_world.kitties[0], NeedKind::Eat);
        arm(&mut observed_world.kitties[0], NeedKind::Eat);
        let plain = registry_with(None, 3);
        let shared = StuckShared::new(cfg(StuckMode::Observe, window, 75.0));
        let observed = registry_with(Some(&shared), 3);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        for _ in 0..3 * window {
            drive_tick(&mut plain_world, &plain, &config);
            drive_tick(&mut observed_world, &observed, &config);
            detector.observe(&observed_world);
        }
        assert_eq!(
            fingerprint(&plain_world),
            fingerprint(&observed_world),
            "observe substitutes nothing: the applied decisions are the mind's own"
        );
        let records: Vec<FireRecord> =
            shared.log.lock().unwrap().ring.iter().cloned().collect();
        assert!(!records.is_empty(), "while the fires are on the record");
        assert_eq!(records[0].mode, StuckMode::Observe);
        assert_eq!(records[0].tick, window, "same exact fire tick as enforce would see");
        assert!(records[0].proposal_replaced.is_some(), "full attribution (SC-003)");
    }

    // ---------- T016 (unit): the scripted boundary ----------

    #[test]
    fn a_scripted_seat_in_the_loop_shape_is_invisible_to_the_detector() {
        // SC-005 by construction AND by assertion: a held, armed,
        // confined scripted seat never appears in tracking, plans,
        // records, or any status collection.
        let mut config = observer_config();
        config.kitties = vec![
            KittyConfig::new(1, "Held", 5, 5, "hold"),
            KittyConfig::new(2, "AlsoHeld", 12, 12, "hold"),
        ];
        let config = Arc::new(config);
        let mut world = World::generate(&config);
        arm(&mut world.kitties[0], NeedKind::Eat);
        let shared = StuckShared::new(cfg(StuckMode::Enforce, 20, 75.0));
        let registry = registry_with(Some(&shared), 3);
        let mut detector = StuckDetector::new(shared.clone(), BTreeSet::new());

        let mut last = StuckStatus::dark(shared.config());
        for _ in 0..60 {
            drive_tick(&mut world, &registry, &config);
            last = detector.observe(&world);
        }
        assert!(last.per_seat.is_empty(), "no seat row");
        assert!(last.armed.is_empty(), "no trigger row");
        assert!(last.recent.is_empty(), "no fire");
        assert!(shared.plans.lock().unwrap().is_empty(), "no plan");
    }

    // ---------- FR-005: the substitute never speaks the free register ----------

    #[test]
    fn the_needs_driven_substitute_never_emits_a_free_register_kind() {
        // Doctrine rule 6: the kinds are named HERE, in test code, and
        // nowhere else in this module. The existing teacher.rs pin
        // covers Teacher::GEN2; this one pins the substitute brain.
        let config = Arc::new(test_config());
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let mut checked = 0u32;
        for _ in 0..500 {
            let driven = drive_tick(&mut world, &registry, &config);
            for record in &driven.report.records {
                if let Some(message) = record.proposed_message {
                    checked += 1;
                    assert!(
                        !matches!(
                            message,
                            MessageKind::Mew
                                | MessageKind::Chirp
                                | MessageKind::Trill
                                | MessageKind::Ekekek
                        ),
                        "a scripted brain spoke the free register: {message:?}"
                    );
                }
            }
        }
        assert!(checked > 0, "the sweep saw real messages, or this test is vacuous");
    }
}
