//! Episodes (spec 014 FR-010, FR-020): a seed, a horizon, and the rollout
//! between reset and truncation. Never persisted, never terminated.
//!
//! Mixed control: any subset of kitties is driven by named built-in
//! behaviors while the rest take external actions. Scripted kitties decide
//! from the same per-kitty decision streams the engine would deal them —
//! the episode deals each tick's seeds *before* the tick
//! ([`World::deal_decision_seeds`]) and applies them with
//! [`World::tick_with_proposals_seeded`], so the master RNG stream is
//! byte-identical to a behavior-driven run and mixed rollouts stay
//! bit-reproducible. The team reward always counts the full roster,
//! scripted kitties included.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::action::Action;
use cloudkitty_core::behavior::{resolve_one, BehaviorRegistry, DecisionContext};
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::rng::DecisionRng;
use cloudkitty_core::seam::{DealtSeeds, JointProposal, Provenance, TickReport};
use cloudkitty_core::world::World;
use cloudkitty_core::Config;
use thiserror::Error;

use crate::codec::{ActionCodec, MessageCodec};
use crate::config::{RewardMode, RlConfig};
use crate::global_state::encode_global_state;
use crate::mask::{legal_action_mask, legal_message_mask, mask_bytes};
use crate::observe::{encode_observation, Observation, TargetTable};
use crate::reward::{shaping_potential, team_reward};

#[derive(Debug, Error)]
pub enum EpisodeError {
    #[error("invalid engine config: {0}")]
    Config(String),
    #[error("invalid rl config: {0}")]
    RlConfig(#[from] crate::config::RlConfigError),
    #[error("control names unknown kitty id {0}")]
    UnknownKitty(KittyId),
    #[error("control for kitty {kitty} names unknown behavior '{name}'")]
    UnknownBehavior { kitty: KittyId, name: String },
    #[error("action index {index} for kitty {kitty} out of range (menu has {len} entries)")]
    ActionOutOfRange {
        kitty: KittyId,
        index: usize,
        len: usize,
    },
    #[error("message index {index} for kitty {kitty} out of range (head has {len} entries)")]
    MessageOutOfRange {
        kitty: KittyId,
        index: usize,
        len: usize,
    },
    #[error("step after truncation: reset the episode first")]
    SteppedAfterTruncation,
    #[error("world panicked and is poisoned until reset: {message}")]
    Panicked { message: String },
    #[error("reset() required first: {reason}")]
    ResetRequired { reason: &'static str },
}

/// Who decides for one kitty.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Control {
    /// The trainer supplies a menu index every step.
    External,
    /// A named built-in decides from the kitty's engine-dealt stream.
    Builtin(String),
}

/// Per-agent info returned with every reset and step (FR-003, FR-018).
#[derive(Debug, Clone)]
pub struct AgentInfo {
    /// Menu index of the action that actually applied, when the start-of-
    /// tick table can express it; None at reset or when inexpressible.
    pub applied_action: Option<usize>,
    /// The engine name of the applied action (its wire tag), e.g. "sleep".
    pub applied_action_name: Option<&'static str>,
    /// The wire name of the message that actually emitted (spec 028), e.g.
    /// "want_eat"; None at reset or when the applied message was Silent --
    /// including a proposed message enforcement downgraded.
    pub applied_message: Option<&'static str>,
    /// The wire name of the message the agent PROPOSED, before engine
    /// enforcement; None at reset, for a proposed Silent, or for a
    /// substituted idle (which never proposed anything -- the same honest
    /// bookkeeping as `survived`). Some here with `applied_message` None
    /// is exactly an enforcement downgrade, so quiet-by-choice and
    /// quiet-by-downgrade separate py-side (F-015's first-probe check and
    /// D1's channel-collapse diagnosis both read this seam).
    pub proposed_message: Option<&'static str>,
    /// Whether the proposal survived validation unchanged.
    pub survived: Option<bool>,
    /// The legal-action mask for the *next* decision (0/1 per menu entry).
    pub mask: Vec<u8>,
    /// The decision seed dealt for the next decision — deploy-time sampling
    /// and trainer exploration share this one stochasticity mechanism
    /// (FR-015).
    pub decision_seed: u64,
    /// How this kitty's last decision came to be (None at reset).
    pub provenance: Option<Provenance>,
}

/// What reset and step hand back. Terminations are constitutionally always
/// false (Article II) and deliberately absent; `truncated` flips to true
/// exactly at the horizon, for every agent at once.
#[derive(Debug, Clone)]
pub struct EpisodeStep {
    /// Per external agent.
    pub observations: BTreeMap<KittyId, Observation>,
    /// The one team scalar, broadcast to every external agent.
    pub reward: f64,
    pub truncated: bool,
    /// Per external agent.
    pub infos: BTreeMap<KittyId, AgentInfo>,
    /// The privileged critic view (FR-019) — training/evaluation only.
    pub global_state: Vec<f32>,
    /// The engine's honest record of the tick (empty records at reset).
    pub report: TickReport,
}

/// One seeded rollout environment. Config is immutable after construction —
/// a new config means a new episode.
pub struct Episode {
    core: Arc<Config>,
    rl: RlConfig,
    codec: ActionCodec,
    registry: BehaviorRegistry,
    control: BTreeMap<KittyId, Control>,
    horizon: u64,
    world: World,
    tick_in_episode: u64,
    truncated: bool,
    /// The original panic message after an engine panic mid-step left the
    /// world possibly inconsistent; further steps are refused with it, and
    /// reset heals (third review: the episode owns its own recovery, so
    /// the single-world and batched surfaces share one state machine).
    poisoned: Option<String>,
    /// Seeds dealt for the *next* tick's decisions. Always `Some` between
    /// calls; taken by value when the tick consumes it (the engine's
    /// DealtSeeds contract — a deal can never be skipped or reused).
    pending_seeds: Option<DealtSeeds>,
    /// Start-of-tick target tables from the last observation encoding, used
    /// to express applied actions back as menu indices.
    last_tables: BTreeMap<KittyId, TargetTable>,
    prev_level: f64,
    prev_potential: f64,
}

impl Episode {
    /// Builds an episode over `core` config with the `[rl.*]` blocks in
    /// `rl`. `control` maps kitty ids to who decides for them; unnamed
    /// kitties default to `External`. The world starts from the config's
    /// own seed; call [`Episode::reset`] to reseed.
    pub fn new(
        core: Config,
        rl: RlConfig,
        control: BTreeMap<KittyId, Control>,
    ) -> Result<Self, EpisodeError> {
        core.validate()
            .map_err(|e| EpisodeError::Config(e.to_string()))?;
        rl.validate()?;
        let registry = BehaviorRegistry::with_builtins();
        for (&kitty, choice) in &control {
            if !core.kitties.iter().any(|k| k.id == kitty) {
                return Err(EpisodeError::UnknownKitty(kitty));
            }
            if let Control::Builtin(name) = choice {
                if registry.get(name).is_none() {
                    return Err(EpisodeError::UnknownBehavior {
                        kitty,
                        name: name.clone(),
                    });
                }
            }
        }
        let codec = ActionCodec::v2(&rl.observation);
        let horizon = rl.episode.horizon;
        let core = Arc::new(core);
        let mut episode = Episode {
            world: World::generate(&core),
            core,
            rl,
            codec,
            registry,
            control,
            horizon,
            tick_in_episode: 0,
            truncated: false,
            poisoned: None,
            pending_seeds: None,
            last_tables: BTreeMap::new(),
            prev_level: 0.0,
            prev_potential: 0.0,
        };
        episode.arm();
        Ok(episode)
    }

    pub fn codec(&self) -> &ActionCodec {
        &self.codec
    }

    pub fn core_config(&self) -> &Arc<Config> {
        &self.core
    }

    pub fn rl_config(&self) -> &RlConfig {
        &self.rl
    }

    pub fn world(&self) -> &World {
        &self.world
    }

    /// Every kitty in the roster, stable id order.
    pub fn roster(&self) -> Vec<KittyId> {
        self.world.kitties.iter().map(|k| k.id).collect()
    }

    /// The externally controlled agents, stable id order — constant for the
    /// episode's life (Article II/III as API guarantees).
    pub fn external_agents(&self) -> Vec<KittyId> {
        self.roster()
            .into_iter()
            .filter(|id| !matches!(self.control.get(id), Some(Control::Builtin(_))))
            .collect()
    }

    /// Fresh world from `seed`; returns the initial observations, masks,
    /// seeds, and global state. Reward is 0 and the report empty — nothing
    /// has happened yet. Also heals a poisoned episode: the fresh world
    /// re-establishes every invariant a mid-tick panic may have broken.
    pub fn reset(&mut self, seed: u64) -> EpisodeStep {
        let mut config = (*self.core).clone();
        config.world.seed = seed;
        self.core = Arc::new(config);
        self.world = World::generate(&self.core);
        self.arm()
    }

    /// Post-generation bookkeeping shared by construction and reset: deal
    /// the first seeds, prime the reward baselines, clear any poison, and
    /// encode the initial step.
    fn arm(&mut self) -> EpisodeStep {
        self.tick_in_episode = 0;
        self.truncated = false;
        self.poisoned = None;
        self.pending_seeds = Some(self.world.deal_decision_seeds());
        let snapshot = self.world.snapshot();
        self.prev_level = team_reward(&snapshot, &self.core, &self.rl.reward);
        self.prev_potential =
            shaping_potential(&snapshot, self.rl.reward.shaping.distress_coefficient);
        self.collect_step(0.0, TickReport::default(), snapshot)
    }

    /// The seed the current world was generated from. Derived from the
    /// stored config (reset writes the seed there), so it can never drift
    /// from the world it describes.
    pub fn current_seed(&self) -> u64 {
        self.core.world.seed
    }

    /// Resets to the next seed in the deterministic reset chain
    /// ([`advance_seed`] of the current seed): a fresh episode every call,
    /// reproducible as a *sequence* — the same initial seed and reset
    /// pattern replay the same run of episodes. This is what an unseeded
    /// PettingZoo `reset()` should do; replaying one fixed seed forever
    /// silently collapses training-data diversity.
    pub fn reset_fresh(&mut self) -> EpisodeStep {
        let next = advance_seed(self.current_seed());
        self.reset(next)
    }

    /// [`Episode::reset`] / [`Episode::reset_fresh`] behind the panic guard
    /// every reset path must share (round-one review, 2026-07-24: the
    /// Python surface's solo reset lacked it while the batched reset had
    /// it — an asymmetry, not a design). The one panic an episode cannot
    /// catch from inside is a world-generation panic during its own reset;
    /// caught here, the episode is poisoned with the original message —
    /// further steps refused, any later successful reset heals — and the
    /// caller gets an error instead of an unwind.
    pub fn reset_caught(&mut self, seed: Option<u64>) -> Result<EpisodeStep, EpisodeError> {
        match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| match seed {
            Some(seed) => self.reset(seed),
            None => self.reset_fresh(),
        })) {
            Ok(step) => Ok(step),
            Err(payload) => {
                let message = panic_message(payload);
                self.poison(message.clone());
                Err(EpisodeError::Panicked { message })
            }
        }
    }

    /// One joint-action step. `actions` maps every external agent to a menu
    /// index; a missing entry lawfully substitutes idle (Article IV), an
    /// out-of-range index is a caller error.
    ///
    /// An engine panic mid-step (an invariant assertion, an internal
    /// expect) leaves the world possibly inconsistent: it poisons the
    /// episode, so further steps are refused with the original message
    /// and any reset heals.
    pub fn step(
        &mut self,
        actions: &BTreeMap<KittyId, (usize, usize)>,
    ) -> Result<EpisodeStep, EpisodeError> {
        if let Some(message) = &self.poisoned {
            return Err(EpisodeError::Panicked {
                message: message.clone(),
            });
        }
        if self.truncated {
            return Err(EpisodeError::SteppedAfterTruncation);
        }
        match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| self.step_inner(actions))) {
            Ok(result) => result,
            Err(payload) => {
                let message = panic_message(payload);
                self.poisoned = Some(message.clone());
                Err(EpisodeError::Panicked { message })
            }
        }
    }

    fn step_inner(
        &mut self,
        actions: &BTreeMap<KittyId, (usize, usize)>,
    ) -> Result<EpisodeStep, EpisodeError> {
        // Scripted kitties decide against the frozen start-of-tick world;
        // in the common all-external case nobody reads it, so don't take it.
        let scripted = self
            .control
            .values()
            .any(|c| matches!(c, Control::Builtin(_)));
        let snapshot = scripted.then(|| Arc::new(self.world.snapshot()));
        let mut proposals = JointProposal::new();
        let mut scripted_marks: BTreeMap<KittyId, Provenance> = BTreeMap::new();

        for id in self.roster() {
            match self.control.get(&id) {
                Some(Control::Builtin(name)) => {
                    let snapshot = snapshot.as_ref().expect("taken when anyone is scripted");
                    let seed = self
                        .pending_seeds
                        .as_ref()
                        .and_then(|dealt| dealt.seed_for(id))
                        .expect("seeds are dealt for every roster kitty");
                    let ctx = DecisionContext {
                        me: snapshot.kitty(id).cloned().expect("roster kitty"),
                        world: snapshot.clone(),
                        rng: DecisionRng::from_seed(seed),
                        config: self.core.clone(),
                    };
                    let (action, provenance) = resolve_one(self.registry.get(name), &ctx, seed);
                    proposals.propose(id, action);
                    scripted_marks.insert(id, provenance);
                }
                _ => {
                    if let Some(&(index, message_index)) = actions.get(&id) {
                        let table = self
                            .last_tables
                            .get(&id)
                            .expect("collect_step keeps a table for every external agent");
                        let activity = self.codec.decode(index, table).map_err(|_| {
                            EpisodeError::ActionOutOfRange {
                                kitty: id,
                                index,
                                len: self.codec.len(),
                            }
                        })?;
                        let message = MessageCodec::decode(message_index).map_err(|_| {
                            EpisodeError::MessageOutOfRange {
                                kitty: id,
                                index: message_index,
                                len: MessageCodec::LEN,
                            }
                        })?;
                        proposals.propose(id, cloudkitty_core::Decision { activity, message });
                    }
                    // A missing entry stays absent: the tick substitutes
                    // idle and marks it honestly.
                }
            }
        }

        let seeds = self
            .pending_seeds
            .take()
            .expect("seeds are dealt at reset and after every step");
        let mut report = self
            .world
            .tick_with_proposals_seeded(&proposals, seeds, &self.core);
        // The tick marks every present proposal PolicyMade — it cannot know
        // a scripted proposal came from the fallback. Restore the honest
        // dispatch provenance (FR-017: a broken advisor must never ride the
        // fallback unnoticed, mixed control included).
        if !scripted_marks.is_empty() {
            for record in &mut report.records {
                if let Some(mark) = scripted_marks.get(&record.kitty_id) {
                    record.provenance = *mark;
                }
            }
        }
        self.tick_in_episode += 1;
        self.truncated = self.tick_in_episode >= self.horizon;
        self.pending_seeds = Some(self.world.deal_decision_seeds());

        // Reward from the post-tick snapshot, full roster (FR-008/FR-020);
        // the same snapshot feeds the observation encoding below.
        let snapshot = self.world.snapshot();
        let level = team_reward(&snapshot, &self.core, &self.rl.reward);
        let mut reward = match self.rl.reward.mode {
            RewardMode::Level => level,
            RewardMode::Delta => level - self.prev_level,
        };
        if self.rl.reward.shaping.enabled {
            let potential =
                shaping_potential(&snapshot, self.rl.reward.shaping.distress_coefficient);
            reward += self.rl.reward.shaping.gamma * potential - self.prev_potential;
            self.prev_potential = potential;
        }
        self.prev_level = level;

        Ok(self.collect_step(reward, report, snapshot))
    }

    /// Encodes the post-tick views (from the snapshot the caller already
    /// took) and assembles the step result. Only external agents are
    /// encoded: scripted kitties consume no observation, mask, or table —
    /// their decisions come from the engine-dealt streams in `step`.
    fn collect_step(
        &mut self,
        reward: f64,
        report: TickReport,
        snapshot: cloudkitty_core::world::WorldSnapshot,
    ) -> EpisodeStep {
        let clock = self.episode_clock();
        let externals = self.external_agents();
        let mut observations = BTreeMap::new();
        let mut infos = BTreeMap::new();
        let mut new_tables = BTreeMap::new();

        for &id in &externals {
            let observation =
                encode_observation(&snapshot, id, &self.core, &self.rl.observation, clock);
            // The serialized mask is the two-head concat (mask schema 3):
            // [activity (menu_len) | message (16)] -- 50 at default slots.
            let mut mask =
                legal_action_mask(&snapshot, id, &observation.table, &self.codec, &self.core);
            mask.extend(legal_message_mask(&snapshot, id, &self.core));
            let record = report.record(id);
            let applied_action = record.and_then(|r| {
                self.last_tables
                    .get(&id)
                    .and_then(|table| self.codec.encode(&r.applied, table))
            });
            let info = AgentInfo {
                applied_action,
                applied_action_name: record.map(|r| action_wire_name(&r.applied)),
                applied_message: record
                    .and_then(|r| r.applied_message)
                    .map(|kind| kind.wire_name()),
                proposed_message: record
                    .filter(|r| r.provenance != Provenance::SubstitutedIdle)
                    .and_then(|r| r.proposed_message)
                    .map(|kind| kind.wire_name()),
                // Honest bookkeeping: a substituted idle never *proposed*
                // anything, so it has no survival verdict — None, not a
                // fabricated true (spec 014 review).
                survived: record.and_then(|r| {
                    if r.provenance == Provenance::SubstitutedIdle {
                        None
                    } else {
                        Some(r.validated == r.proposed)
                    }
                }),
                mask: mask_bytes(&mask),
                decision_seed: self
                    .pending_seeds
                    .as_ref()
                    .and_then(|dealt| dealt.seed_for(id))
                    .expect("seeds are dealt for every roster kitty"),
                // step() already restored honest scripted provenance into
                // the report, so the record is the single source here.
                provenance: record.map(|r| r.provenance),
            };
            new_tables.insert(id, observation.table.clone());
            observations.insert(id, observation);
            infos.insert(id, info);
        }
        self.last_tables = new_tables;

        let global_state = encode_global_state(
            &snapshot,
            &self.core,
            &self.rl.global_state,
            &self.rl.observation,
            clock,
        );

        EpisodeStep {
            observations,
            reward,
            truncated: self.truncated,
            infos,
            global_state,
            report,
        }
    }

    /// The episode clock in [0, 1]: ticks into the episode over horizon.
    fn episode_clock(&self) -> f32 {
        if self.horizon > 0 {
            self.tick_in_episode as f32 / self.horizon as f32
        } else {
            0.0
        }
    }

    /// The privileged critic view of the world as it stands (FR-019) — the
    /// identical encoding every step carries in
    /// [`EpisodeStep::global_state`], re-derivable on demand. Surfaces
    /// that expose a `state()` accessor read it from here, never from a
    /// re-implementation (third review).
    pub fn current_global_state(&self) -> Vec<f32> {
        encode_global_state(
            &self.world.snapshot(),
            &self.core,
            &self.rl.global_state,
            &self.rl.observation,
            self.episode_clock(),
        )
    }

    /// Marks the episode poisoned (crate-internal: the batched reset path
    /// catches world-generation panics outside `step` and records them
    /// here). Any successful reset heals.
    pub(crate) fn poison(&mut self, message: String) {
        self.poisoned = Some(message);
    }
}

/// The panic payload's message, kept verbatim for poison bookkeeping so
/// callers see the original failure, not a generic wrapper.
pub(crate) fn panic_message(payload: Box<dyn std::any::Any + Send>) -> String {
    if let Some(text) = payload.downcast_ref::<&str>() {
        (*text).to_string()
    } else if let Some(text) = payload.downcast_ref::<String>() {
        text.clone()
    } else {
        "non-string panic payload".to_string()
    }
}

/// One deterministic step of the unseeded-reset chain (splitmix64): fresh,
/// well-scattered seeds whose *sequence* is reproducible from the first.
pub fn advance_seed(seed: u64) -> u64 {
    let mut z = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

/// The engine action's wire name — a static match over the enum, pinned to
/// the serde tags by a unit test so it can never drift from the wire shape.
pub fn action_wire_name(action: &Action) -> &'static str {
    match action {
        Action::Move { .. } => "move",
        Action::Rest { .. } => "rest",
        Action::Sleep { .. } => "sleep",
        Action::Groom { .. } => "groom",
        Action::Eat => "eat",
        Action::Drink => "drink",
        Action::Chase(_) => "chase",
        Action::Play { .. } => "play",
        Action::Purr => "purr",
        Action::Meow { .. } => "meow",
        Action::Idle => "idle",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn action_wire_names_match_the_serde_tags_for_every_variant() {
        use cloudkitty_core::action::TargetRef;
        use cloudkitty_core::grid::Direction;
        use cloudkitty_core::meow::MessageKind;
        let samples = [
            Action::Move {
                direction: Direction::North,
            },
            Action::Rest { with: Some(2) },
            Action::Sleep { with: None },
            Action::Groom { target: Some(2) },
            Action::Eat,
            Action::Drink,
            Action::Chase(TargetRef::Kitty { id: 2 }),
            Action::Play {
                target: Some(TargetRef::Element { id: 7 }),
            },
            Action::Purr,
            Action::Meow {
                message: MessageKind::WantEat,
            },
            Action::Idle,
        ];
        for action in samples {
            let tag = serde_json::to_value(action).unwrap()["action"]
                .as_str()
                .unwrap()
                .to_string();
            assert_eq!(action_wire_name(&action), tag, "{action:?}");
        }
    }

    #[test]
    fn advance_seed_outputs_are_pinned() {
        // The unseeded-reset chain must mean the same thing in every build:
        // a typo'd constant would silently change every chain. These values
        // are the function's actual splitmix64 outputs, pinned.
        assert_eq!(advance_seed(0), 16294208416658607535);
        assert_eq!(advance_seed(1), 10451216379200822465);
        assert_eq!(advance_seed(20260718), 17473423497659790644);
        // Distinct starts stay distinct down the chain (no early merge).
        assert_ne!(advance_seed(advance_seed(1)), advance_seed(advance_seed(2)));
    }

    fn episode_all_external() -> Episode {
        Episode::new(Config::default(), RlConfig::default(), BTreeMap::new()).unwrap()
    }

    #[test]
    fn reset_returns_observations_masks_and_seeds_for_every_agent() {
        let mut episode = episode_all_external();
        let start = episode.reset(7);
        let agents = episode.external_agents();
        assert_eq!(agents.len(), episode.roster().len(), "all external");
        for id in &agents {
            let obs = start.observations.get(id).expect("observation");
            assert!(!obs.values.is_empty());
            let info = start.infos.get(id).expect("info");
            // Mask schema 3 (spec 033): [activity (menu) | message (16)].
            assert_eq!(info.mask.len(), episode.codec().len() + MessageCodec::LEN);
            assert!(info.mask.contains(&1), "mask never all-zero");
            assert_eq!(
                info.mask[episode.codec().len()],
                1,
                "Silent (message head index 0) is always legal"
            );
            assert!(info.applied_action.is_none(), "nothing applied at reset");
            assert!(info.applied_message.is_none(), "no message at reset");
        }
        assert_eq!(start.reward, 0.0);
        assert!(!start.truncated);
    }

    #[test]
    fn truncation_arrives_exactly_at_the_horizon_and_stepping_past_is_an_error() {
        let mut core = Config::default();
        core.world.seed = 5;
        let rl = RlConfig::from_toml_str("[rl.episode]\nhorizon = 3\n").unwrap();
        let mut episode = Episode::new(core, rl, BTreeMap::new()).unwrap();
        let idle: BTreeMap<KittyId, (usize, usize)> = episode
            .external_agents()
            .into_iter()
            .map(|id| (id, (33, 0))) // (idle, silent), v2 pair
            .collect();

        for expect_truncated in [false, false, true] {
            let step = episode.step(&idle).unwrap();
            assert_eq!(step.truncated, expect_truncated);
        }
        assert!(matches!(
            episode.step(&idle),
            Err(EpisodeError::SteppedAfterTruncation)
        ));
        let start = episode.reset(6);
        assert!(!start.truncated, "reset rearms the episode");
    }

    #[test]
    fn out_of_range_actions_are_a_caller_error_vacant_slots_are_not() {
        let mut episode = episode_all_external();
        episode.reset(3);
        let agents = episode.external_agents();
        let mut actions: BTreeMap<KittyId, (usize, usize)> =
            agents.iter().map(|&id| (id, (33, 0))).collect();
        actions.insert(agents[0], (34, 0));
        assert!(matches!(
            episode.step(&actions),
            Err(EpisodeError::ActionOutOfRange { index: 34, .. })
        ));

        // In-range indices naming vacant slots decode and lawfully idle.
        let mut actions: BTreeMap<KittyId, (usize, usize)> =
            agents.iter().map(|&id| (id, (33, 0))).collect();
        actions.insert(agents[0], (7, 0)); // rest with kitty slot 2 — vacant on a 3-kitty roster? (2 others)
        let step = episode.step(&actions).unwrap();
        let info = step.infos.get(&agents[0]).unwrap();
        assert_eq!(
            info.survived,
            Some(false),
            "the vacant target failed validation"
        );
    }

    #[test]
    fn a_poisoned_episode_refuses_steps_and_reset_revives_it() {
        // Third review: the poison/refuse/reset-revives state machine lives
        // in the episode itself, so the single-world Python surface and the
        // batched worker pool share the one recovery contract.
        let mut episode = episode_all_external();
        episode.reset(3);
        episode.poison("simulated engine panic".into());

        let refused = episode.step(&BTreeMap::new());
        assert!(
            matches!(refused, Err(EpisodeError::Panicked { ref message })
                if message == "simulated engine panic"),
            "a poisoned episode refuses to step, naming the original panic"
        );

        let revived = episode.reset(4);
        assert!(!revived.truncated);
        episode
            .step(&BTreeMap::new())
            .expect("stepping works again");
    }

    #[test]
    #[cfg(debug_assertions)]
    fn an_engine_panic_mid_step_poisons_instead_of_unwinding() {
        // A real invariant panic (not a simulated one): corrupt the world
        // so the tick's constitutional check fires. The step must come back
        // as Err(Panicked) with the engine's message, the next step must be
        // refused with the same message (not a second, misleading panic
        // about seeds), and reset must heal.
        //
        // Debug-only BY DESIGN, not by oversight (2026-08-06 handoff item
        // 1): the panic comes from `invariants::assert_or_report`, which
        // deliberately logs instead of panicking in release -- the served
        // binary must not die on a violation -- so in release the corrupted
        // world never panics and this test would fail on a healthy engine.
        // The poison/refuse/heal mechanics themselves are covered in both
        // profiles by the simulated-poison test above.
        let mut episode = episode_all_external();
        episode.reset(9);
        let (w, h) = (episode.world.width, episode.world.height);
        episode.world.kitties[0].pos = cloudkitty_core::grid::Position::new(w + 10, h + 10);

        let previous = std::panic::take_hook();
        std::panic::set_hook(Box::new(|_| {}));
        let first = episode.step(&BTreeMap::new());
        let second = episode.step(&BTreeMap::new());
        std::panic::set_hook(previous);

        let Err(EpisodeError::Panicked { message }) = first else {
            panic!("the corrupted world should have panicked the tick: {first:?}");
        };
        assert!(
            matches!(second, Err(EpisodeError::Panicked { message: ref again }) if *again == message),
            "the second step is refused with the original message"
        );
        let revived = episode.reset(10);
        assert!(!revived.truncated, "reset heals the poisoned episode");
        episode
            .step(&BTreeMap::new())
            .expect("stepping works again");
    }

    #[test]
    fn unknown_control_entries_are_rejected_at_construction() {
        let mut control = BTreeMap::new();
        control.insert(999, Control::External);
        assert!(matches!(
            Episode::new(Config::default(), RlConfig::default(), control),
            Err(EpisodeError::UnknownKitty(999))
        ));

        let mut control = BTreeMap::new();
        control.insert(1, Control::Builtin("telepathic".into()));
        assert!(matches!(
            Episode::new(Config::default(), RlConfig::default(), control),
            Err(EpisodeError::UnknownBehavior { .. })
        ));
    }
}
