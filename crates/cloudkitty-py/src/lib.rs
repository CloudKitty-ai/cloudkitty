//! CloudKitty's Python surface: a logic-free PyO3 wrapper over
//! `cloudkitty-rl` (spec 014 FR-011/FR-012).
//!
//! Nothing in this crate computes anything the Rust side does not already
//! compute (FR-007): it constructs environments, forwards calls, and copies
//! fixed-size vectors out as NumPy arrays. The GIL is released for the
//! duration of engine work in `reset` and `step`.
//!
//! The `ParallelEnv` speaks the PettingZoo parallel convention duck-typed:
//! `reset(seed)`, `step(actions)`, `agents`, `possible_agents`,
//! `observation_space(agent)`, `action_space(agent)`, and `state()` for the
//! privileged global state (training only — FR-019). Terminations are
//! constitutionally always False (Article II as an API guarantee);
//! truncations flip together exactly at the horizon.

use std::collections::BTreeMap;
use std::sync::Mutex;

use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::seam::Provenance;
use cloudkitty_core::Config;
use cloudkitty_rl::config::{load_configs_from_path, load_configs_from_str, RlConfig};
use cloudkitty_rl::episode::{AgentInfo, Control, Episode, EpisodeError, EpisodeStep};
use cloudkitty_rl::global_state::global_state_len;
use cloudkitty_rl::observe::observation_len;
use cloudkitty_rl::vector::VectorizedEnvironment;
use numpy::{IntoPyArray, PyArray1, PyArray2, PyArrayMethods};
use pyo3::exceptions::{PyIndexError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// The PettingZoo parallel step tuple:
/// (observations, rewards, terminations, truncations, infos).
type StepTuple<'py> = (
    Bound<'py, PyDict>,
    Bound<'py, PyDict>,
    Bound<'py, PyDict>,
    Bound<'py, PyDict>,
    Bound<'py, PyDict>,
);

fn agent_name(id: KittyId) -> String {
    format!("kitty_{id}")
}

fn parse_agent(name: &str) -> Option<KittyId> {
    let id: KittyId = name.strip_prefix("kitty_")?.parse().ok()?;
    // Strict round trip (spec 014 review): "kitty_01" and "kitty_+1" must
    // not silently alias onto "kitty_1" — non-canonical spellings are
    // unknown agents, reported as such.
    (agent_name(id) == name).then_some(id)
}

fn provenance_str(p: Provenance) -> &'static str {
    match p {
        Provenance::PolicyMade => "policy",
        Provenance::FallbackTaken => "fallback",
        Provenance::SubstitutedIdle => "substituted_idle",
    }
}

fn episode_err(e: EpisodeError) -> PyErr {
    match e {
        // Both halves of the pair raise IndexError on a bad index, matching
        // VectorEnv's pre-check -- one exception type per fault class.
        EpisodeError::ActionOutOfRange { .. } | EpisodeError::MessageOutOfRange { .. } => {
            PyIndexError::new_err(e.to_string())
        }
        EpisodeError::SteppedAfterTruncation | EpisodeError::Panicked { .. } => {
            PyRuntimeError::new_err(e.to_string())
        }
        other => PyValueError::new_err(other.to_string()),
    }
}

/// Builds the (core, rl) config pair from the constructor arguments.
fn load_configs(
    config_path: Option<&str>,
    config_toml: Option<&str>,
) -> PyResult<(Config, RlConfig)> {
    match (config_path, config_toml) {
        (Some(path), None) => {
            load_configs_from_path(path).map_err(|e| PyValueError::new_err(e.to_string()))
        }
        (None, Some(text)) => {
            load_configs_from_str(text).map_err(|e| PyValueError::new_err(e.to_string()))
        }
        (None, None) => Ok((Config::default(), RlConfig::default())),
        (Some(_), Some(_)) => Err(PyValueError::new_err(
            "pass config_path or config_toml, not both",
        )),
    }
}

fn parse_control(control: Option<&Bound<'_, PyDict>>) -> PyResult<BTreeMap<KittyId, Control>> {
    let mut map = BTreeMap::new();
    if let Some(dict) = control {
        for (key, value) in dict.iter() {
            let id: KittyId = if let Ok(id) = key.extract::<KittyId>() {
                id
            } else {
                let name: String = key.extract()?;
                parse_agent(&name)
                    .ok_or_else(|| PyValueError::new_err(format!("unknown agent key '{name}'")))?
            };
            let choice: String = value.extract()?;
            let control = if choice == "external" {
                Control::External
            } else {
                Control::Builtin(choice)
            };
            map.insert(id, control);
        }
    }
    Ok(map)
}

fn info_to_py<'py>(py: Python<'py>, info: &AgentInfo) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("applied_action", info.applied_action)?;
    dict.set_item("applied_action_name", info.applied_action_name)?;
    dict.set_item("applied_message", info.applied_message)?;
    dict.set_item("proposed_message", info.proposed_message)?;
    dict.set_item("survived", info.survived)?;
    dict.set_item("mask", info.mask.clone().into_pyarray(py))?;
    dict.set_item("decision_seed", info.decision_seed)?;
    dict.set_item("provenance", info.provenance.map(provenance_str))?;
    Ok(dict)
}

fn observations_to_py<'py>(py: Python<'py>, step: &EpisodeStep) -> PyResult<Bound<'py, PyDict>> {
    let obs = PyDict::new(py);
    for (id, observation) in &step.observations {
        obs.set_item(agent_name(*id), observation.values.clone().into_pyarray(py))?;
    }
    Ok(obs)
}

fn infos_to_py<'py>(py: Python<'py>, step: &EpisodeStep) -> PyResult<Bound<'py, PyDict>> {
    let infos = PyDict::new(py);
    for (id, info) in &step.infos {
        infos.set_item(agent_name(*id), info_to_py(py, info)?)?;
    }
    Ok(infos)
}

/// A space description: `gymnasium.spaces` objects when gymnasium is
/// importable, plain dicts otherwise (duck-typed convention, FR-011).
fn box_space(py: Python<'_>, len: usize) -> PyResult<Py<PyAny>> {
    match py.import("gymnasium.spaces") {
        Ok(spaces) => {
            let numpy = py.import("numpy")?;
            let kwargs = PyDict::new(py);
            kwargs.set_item("low", -1.0)?;
            kwargs.set_item("high", 4.0)?;
            kwargs.set_item("shape", (len,))?;
            kwargs.set_item("dtype", numpy.getattr("float32")?)?;
            Ok(spaces.getattr("Box")?.call((), Some(&kwargs))?.unbind())
        }
        Err(_) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "box")?;
            dict.set_item("low", -1.0)?;
            dict.set_item("high", 4.0)?;
            dict.set_item("shape", (len,))?;
            dict.set_item("dtype", "float32")?;
            Ok(dict.unbind().into())
        }
    }
}

/// The two-head action space (spec 028): MultiDiscrete([menu, head]),
/// with the same dict fallback shape when gymnasium is absent.
fn multi_discrete_space(py: Python<'_>, nvec: [usize; 2]) -> PyResult<Py<PyAny>> {
    match py.import("gymnasium.spaces") {
        Ok(spaces) => Ok(spaces
            .getattr("MultiDiscrete")?
            .call1((nvec.to_vec(),))?
            .unbind()),
        Err(_) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "multi_discrete")?;
            dict.set_item("nvec", nvec.to_vec())?;
            Ok(dict.unbind().into())
        }
    }
}

/// The PettingZoo-parallel CloudKitty environment (one world).
///
/// `dict` gives instances a `__dict__`: ecosystem tooling decorates env
/// objects with bookkeeping attributes (pettingzoo ≥ 1.26's conformance
/// harness opens with `env.max_cycles = n`), and a compiled class without
/// one raises AttributeError before any real API check runs. Foreign
/// attributes are inert to us -- nothing here reads them.
#[pyclass(dict)]
struct ParallelEnv {
    episode: Episode,
    external: Vec<KittyId>,
    live: bool,
    /// PettingZoo requires `observation_space(agent)` and
    /// `action_space(agent)` to return the *same object* on every call
    /// (identity, not equality — trainers cache spaces and the conformance
    /// harness checks `is`). Built once on first ask, then handed out as
    /// references to that one Python object.
    observation_space_obj: std::sync::OnceLock<Py<PyAny>>,
    action_space_obj: std::sync::OnceLock<Py<PyAny>>,
}

/// The (core, rl) config pair with the horizon override applied — parsed
/// once, however many episodes are built from it (third review: VectorEnv
/// used to re-read the config file once per world).
fn prepare_configs(
    config_path: Option<&str>,
    config_toml: Option<&str>,
    horizon: Option<u64>,
) -> PyResult<(Config, RlConfig)> {
    let (core, mut rl) = load_configs(config_path, config_toml)?;
    if let Some(h) = horizon {
        rl.episode.horizon = h;
        rl.validate()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
    }
    Ok((core, rl))
}

impl ParallelEnv {
    fn build(
        config_path: Option<&str>,
        config_toml: Option<&str>,
        horizon: Option<u64>,
        control: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Episode> {
        let (core, rl) = prepare_configs(config_path, config_toml, horizon)?;
        let control = parse_control(control)?;
        Episode::new(core, rl, control).map_err(episode_err)
    }

    fn actions_from_py(
        &self,
        actions: &Bound<'_, PyDict>,
    ) -> PyResult<BTreeMap<KittyId, (usize, usize)>> {
        let mut map = BTreeMap::new();
        for (key, value) in actions.iter() {
            let name: String = key.extract()?;
            let id = parse_agent(&name)
                .ok_or_else(|| PyValueError::new_err(format!("unknown agent '{name}'")))?;
            if !self.external.contains(&id) {
                return Err(PyValueError::new_err(format!(
                    "agent '{name}' is not externally controlled"
                )));
            }
            // Spec 028: a MultiDiscrete pair [activity, message]. Accepts
            // any length-2 int sequence (list, tuple, numpy array).
            let pair: Vec<i64> = value.extract().map_err(|_| {
                PyValueError::new_err(format!(
                    "action for '{name}' must be a length-2 [activity, message] pair"
                ))
            })?;
            if pair.len() != 2 {
                return Err(PyValueError::new_err(format!(
                    "action for '{name}' must have exactly 2 entries \
                     [activity, message], got {}",
                    pair.len()
                )));
            }
            let (index, message) = (pair[0], pair[1]);
            if index < 0 || message < 0 {
                return Err(PyIndexError::new_err(format!(
                    "action pair ({index}, {message}) for '{name}' is negative"
                )));
            }
            if map.insert(id, (index as usize, message as usize)).is_some() {
                return Err(PyValueError::new_err(format!(
                    "duplicate action entry for '{name}'"
                )));
            }
        }
        Ok(map)
    }

    fn step_result<'py>(&self, py: Python<'py>, step: &EpisodeStep) -> PyResult<StepTuple<'py>> {
        let obs = observations_to_py(py, step)?;
        let rewards = PyDict::new(py);
        let terminations = PyDict::new(py);
        let truncations = PyDict::new(py);
        for id in &self.external {
            let name = agent_name(*id);
            rewards.set_item(&name, step.reward)?;
            // Terminations are always False: kitties cannot die (Article II).
            terminations.set_item(&name, false)?;
            truncations.set_item(&name, step.truncated)?;
        }
        let infos = infos_to_py(py, step)?;
        Ok((obs, rewards, terminations, truncations, infos))
    }
}

#[pymethods]
impl ParallelEnv {
    #[new]
    #[pyo3(signature = (config_path=None, *, config_toml=None, horizon=None, control=None))]
    fn new(
        config_path: Option<&str>,
        config_toml: Option<&str>,
        horizon: Option<u64>,
        control: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        let episode = Self::build(config_path, config_toml, horizon, control)?;
        let external = episode.external_agents();
        Ok(ParallelEnv {
            episode,
            external,
            live: false,
            observation_space_obj: std::sync::OnceLock::new(),
            action_space_obj: std::sync::OnceLock::new(),
        })
    }

    /// Live agents: the constant external set while the episode runs, empty
    /// after truncation (PettingZoo convention) until the next reset.
    #[getter]
    fn agents(&self) -> Vec<String> {
        if self.live {
            self.external.iter().copied().map(agent_name).collect()
        } else {
            Vec::new()
        }
    }

    #[getter]
    fn possible_agents(&self) -> Vec<String> {
        self.external.iter().copied().map(agent_name).collect()
    }

    /// PettingZoo's `unwrapped` convention: there are no wrapper layers
    /// here, so the environment is its own unwrapped self.
    #[getter]
    fn unwrapped(slf: PyRef<'_, Self>) -> Py<ParallelEnv> {
        slf.into()
    }

    #[getter]
    fn metadata<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("name", "cloudkitty_v1")?;
        dict.set_item("is_parallelizable", true)?;
        Ok(dict)
    }

    fn observation_space(&self, py: Python<'_>, _agent: &str) -> PyResult<Py<PyAny>> {
        let space = match self.observation_space_obj.get() {
            Some(space) => space,
            None => {
                let built = box_space(py, observation_len(&self.episode.rl_config().observation))?;
                self.observation_space_obj.get_or_init(|| built)
            }
        };
        Ok(space.clone_ref(py))
    }

    fn action_space(&self, py: Python<'_>, _agent: &str) -> PyResult<Py<PyAny>> {
        let space = match self.action_space_obj.get() {
            Some(space) => space,
            None => {
                let built = multi_discrete_space(
                    py,
                    [
                        self.episode.codec().len(),
                        cloudkitty_rl::codec::MessageCodec::LEN,
                    ],
                )?;
                self.action_space_obj.get_or_init(|| built)
            }
        };
        Ok(space.clone_ref(py))
    }

    /// The activity menu's width (39 at the served `kitty_slots` 4, schema 5).
    #[getter]
    fn menu_len(&self) -> usize {
        self.episode.codec().len()
    }

    /// The width of the message head's logit/mask segment (spec 033):
    /// Silent + the 15 head kinds = 16.
    #[getter]
    fn head_len(&self) -> usize {
        cloudkitty_rl::codec::MessageCodec::LEN
    }

    #[pyo3(signature = (seed=None, options=None))]
    fn reset<'py>(
        &mut self,
        py: Python<'py>,
        seed: Option<u64>,
        options: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<(Bound<'py, PyDict>, Bound<'py, PyDict>)> {
        let _ = options;
        // An unseeded reset advances the episode's own deterministic
        // fresh-seed chain (Episode::reset_fresh — the chain has exactly
        // one owner): the standard trainer loop — seed once, then bare
        // reset() per episode — gets a genuinely new episode every time,
        // while the whole sequence replays from the first seed. The reset
        // rides the shared panic guard (Episode::reset_caught; round-one
        // review: this path used to lack the batched reset's guard), so a
        // world-generation panic poisons the episode and raises with the
        // original message instead of unwinding across the FFI boundary.
        let episode = &mut self.episode;
        let step = py
            .detach(|| episode.reset_caught(seed))
            .map_err(episode_err)?;
        self.live = true;
        let obs = observations_to_py(py, &step)?;
        let infos = infos_to_py(py, &step)?;
        Ok((obs, infos))
    }

    fn step<'py>(
        &mut self,
        py: Python<'py>,
        actions: &Bound<'py, PyDict>,
    ) -> PyResult<StepTuple<'py>> {
        let map = self.actions_from_py(actions)?;
        let episode = &mut self.episode;
        let step = py.detach(|| episode.step(&map)).map_err(episode_err)?;
        if step.truncated {
            self.live = false;
        }
        self.step_result(py, &step)
    }

    /// The privileged global state (FR-019): training and evaluation only —
    /// the deployed behavior API cannot receive it. Served by the episode's
    /// own encoder, never a re-implementation (third review).
    fn state<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f32>> {
        self.episode.current_global_state().into_pyarray(py)
    }

    /// The world's live meow stream: (tick, kitty_id, kind) per entry still
    /// inside `[meow] recent_window_ticks`. Read-only forensics surface —
    /// every emitted meow appears here. Since spec 023 nothing is swallowed:
    /// per-(kitty, kind) repeats are legal on consecutive ticks and bounded
    /// only by the window, so do not assume courtesy spacing when counting.
    /// A Purr entry is a deliberate purr (spec 022) or a motor start that
    /// won the `announce_probability` draw (silent by default) — it no
    /// longer implies a spontaneous start.
    fn recent_meows(&self) -> Vec<(u64, u32, String)> {
        self.episode
            .world()
            .recent_meows
            .iter()
            .map(|m| (m.tick, m.kitty_id, m.kind.wire_name().to_owned()))
            .collect()
    }

    /// Every element in the live world: (id, type, x, y) in stored order.
    /// Read-only descriptive surface, sibling to `recent_meows`; type names
    /// match `recent_meows` kind spelling (`Water`, `Chow`, `Bug`, `Greeble`,
    /// `Sunbeam`). Greebles appear here as everywhere — invisibility is a
    /// client rendering rule, never an API filter. Positions and payload-free
    /// types only: enough to join kitty positions against element tiles
    /// (occupancy measurement); payloads (servings, headings, ttl) wait for
    /// a consumer.
    fn elements(&self) -> Vec<(u32, String, u32, u32)> {
        self.episode
            .world()
            .elements
            .iter()
            .map(|e| (e.id, format!("{:?}", e.element_type()), e.pos.x, e.pos.y))
            .collect()
    }

    fn close(&self) {}

    fn render(&self) -> Option<String> {
        None
    }
}

/// N fully independent worlds stepped as a batch (FR-012): separate seeds,
/// separate RNGs, no shared state; arrays stacked on a leading world axis;
/// fan-out across a scoped thread pool with the GIL released.
#[pyclass]
struct VectorEnv {
    /// The batch runner, wrapped for `Sync`: pyo3 0.29 requires pyclass
    /// data to be shareable across threads (free-threaded Python), and
    /// the runner holds a channel receiver that is not. The lock is
    /// uncontended in practice -- the `&mut self` methods already
    /// serialize callers; it satisfies the type system, not contention.
    vector: Mutex<VectorizedEnvironment>,
    /// World count, mirrored out of the runner so read-only paths never
    /// need the lock (it is fixed at construction).
    n_worlds: usize,
    external: Vec<KittyId>,
    obs_len: usize,
    menu_len: usize,
    head_len: usize,
    state_len: usize,
    /// Seeds waiting to be applied verbatim by the next unseeded reset —
    /// the constructor's (or the last explicit reset's) seeds, consumed
    /// exactly once **by a fully successful reset** (a failed reset keeps
    /// them, so the documented replay survives a retry — third review).
    /// After that, unseeded resets advance each episode's own fresh-seed
    /// chain (the chain has one owner: the episode). Batch coherence
    /// itself — refuse step before the first reset or after a partial
    /// failure — is enforced by the Rust `VectorizedEnvironment`, the
    /// layer that owns the batch; this wrapper only translates its errors.
    pending_seeds: Option<Vec<u64>>,
    /// The latest global state per world, refreshed by reset/step.
    last_states: Vec<Vec<f32>>,
}

#[pymethods]
impl VectorEnv {
    #[new]
    #[pyo3(signature = (n_worlds, config_path=None, *, config_toml=None, seeds=None, horizon=None, workers=None, control=None))]
    fn new(
        n_worlds: usize,
        config_path: Option<&str>,
        config_toml: Option<&str>,
        seeds: Option<Vec<u64>>,
        horizon: Option<u64>,
        workers: Option<usize>,
        control: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        if n_worlds == 0 {
            return Err(PyValueError::new_err("n_worlds must be at least 1"));
        }
        let (core, rl) = prepare_configs(config_path, config_toml, horizon)?;
        let control = parse_control(control)?;
        let mut episodes = Vec::with_capacity(n_worlds);
        for _ in 0..n_worlds {
            episodes.push(
                Episode::new(core.clone(), rl.clone(), control.clone()).map_err(episode_err)?,
            );
        }
        let external = episodes[0].external_agents();
        let obs_len = observation_len(&episodes[0].rl_config().observation);
        let menu_len = episodes[0].codec().len();
        let head_len = cloudkitty_rl::codec::MessageCodec::LEN;
        let state_len = global_state_len(
            episodes[0].roster().len(),
            &episodes[0].rl_config().global_state,
        );
        let base = episodes[0].core_config().world.seed;
        let seeds =
            seeds.unwrap_or_else(|| (0..n_worlds as u64).map(|i| base.wrapping_add(i)).collect());
        if seeds.len() != n_worlds {
            return Err(PyValueError::new_err("seeds must have one entry per world"));
        }
        let n = episodes.len();
        Ok(VectorEnv {
            vector: Mutex::new(VectorizedEnvironment::new(episodes, workers)),
            n_worlds: n,
            external,
            obs_len,
            menu_len,
            head_len,
            state_len,
            pending_seeds: Some(seeds),
            last_states: vec![vec![0.0; state_len]; n],
        })
    }

    #[getter]
    fn num_worlds(&self) -> usize {
        self.n_worlds
    }

    #[getter]
    fn possible_agents(&self) -> Vec<String> {
        self.external.iter().copied().map(agent_name).collect()
    }

    #[pyo3(signature = (seeds=None))]
    fn reset<'py>(
        &mut self,
        py: Python<'py>,
        seeds: Option<Vec<u64>>,
    ) -> PyResult<(Bound<'py, PyDict>, Bound<'py, PyDict>)> {
        let explicit = match seeds {
            Some(seeds) => {
                if seeds.len() != self.n_worlds {
                    return Err(PyValueError::new_err("seeds must have one entry per world"));
                }
                self.pending_seeds = None;
                Some(seeds)
            }
            // Unseeded: the constructor's (or last explicit) seeds run
            // verbatim exactly once; after that, every world advances its
            // own deterministic fresh-seed chain (Episode::reset_fresh) —
            // new episodes each call, the sequence reproducible, and the
            // documented `seeds=` argument always means what it says. The
            // one-shot is only spent below, once every world reset — a
            // failed reset keeps the seeds so a retry still replays them.
            None => self.pending_seeds.clone(),
        };
        let vector = &self.vector;
        let results = py.detach(|| {
            let mut vector = vector.lock().expect("vector runner mutex poisoned");
            match &explicit {
                Some(seeds) => vector.reset(seeds),
                None => vector.reset_fresh(),
            }
        });
        let mut steps = Vec::with_capacity(results.len());
        for result in results {
            steps.push(result.map_err(episode_err)?);
        }
        self.pending_seeds = None;
        self.last_states = steps.iter().map(|s| s.global_state.clone()).collect();
        let obs = self.stack_observations(py, &steps)?;
        let infos = self.stack_infos(py, &steps)?;
        Ok((obs, infos))
    }

    fn step<'py>(
        &mut self,
        py: Python<'py>,
        actions: &Bound<'py, PyDict>,
    ) -> PyResult<StepTuple<'py>> {
        let n = self.n_worlds;
        // {agent: sequence[n]} → per-world action maps.
        let mut per_world: Vec<BTreeMap<KittyId, (usize, usize)>> = vec![BTreeMap::new(); n];
        for (key, value) in actions.iter() {
            let name: String = key.extract()?;
            let id = parse_agent(&name)
                .ok_or_else(|| PyValueError::new_err(format!("unknown agent '{name}'")))?;
            // The same guard ParallelEnv applies (third review): an entry
            // for a scripted or out-of-roster kitty would otherwise be
            // silently dropped by the episode, corrupting training with no
            // error.
            if !self.external.contains(&id) {
                return Err(PyValueError::new_err(format!(
                    "agent '{name}' is not externally controlled"
                )));
            }
            // Spec 028: one [activity, message] pair per world (shape
            // [n, 2] -- lists, tuples, or numpy rows).
            let pairs: Vec<Vec<i64>> = value.extract().map_err(|_| {
                PyValueError::new_err(format!(
                    "actions['{name}'] must be {n} [activity, message] pairs"
                ))
            })?;
            if pairs.len() != n {
                return Err(PyValueError::new_err(format!(
                    "actions['{name}'] must have one entry per world ({n})"
                )));
            }
            for (world, pair) in pairs.iter().enumerate() {
                if pair.len() != 2 {
                    return Err(PyValueError::new_err(format!(
                        "actions['{name}'] world {world}: expected \
                         [activity, message], got {} entries",
                        pair.len()
                    )));
                }
                let (index, message) = (pair[0], pair[1]);
                // Validate the whole batch BEFORE any world steps: a bad
                // index must not leave some worlds a tick ahead of others
                // (spec 014 review — silent batch desync).
                if index < 0 || index as usize >= self.menu_len {
                    return Err(PyIndexError::new_err(format!(
                        "action index {index} for '{name}' in world {world} is out of \
                         range (menu has {} entries); no world was stepped",
                        self.menu_len
                    )));
                }
                if message < 0 || message as usize >= self.head_len {
                    return Err(PyIndexError::new_err(format!(
                        "message index {message} for '{name}' in world {world} is out \
                         of range (head has {} entries); no world was stepped",
                        self.head_len
                    )));
                }
                per_world[world].insert(id, (index as usize, message as usize));
            }
        }

        let vector = &self.vector;
        let results = py.detach(|| {
            vector
                .lock()
                .expect("vector runner mutex poisoned")
                .step(&per_world)
        });
        // Batch coherence is the Rust layer's law: before the first reset,
        // or after an earlier partial failure, every world comes back
        // `ResetRequired` — translate it to one clean error.
        if let Some(Err(EpisodeError::ResetRequired { reason })) = results.first() {
            return Err(PyRuntimeError::new_err(format!(
                "reset() required first: {reason}"
            )));
        }
        // A per-world failure (only a panicking world, after pre-validation)
        // means the survivors advanced but this batch's results cannot be
        // surfaced coherently: keep the pre-step states untouched, name
        // every failed world, and require a reset (which also revives the
        // poisoned world) before stepping again.
        let failures: Vec<String> = results
            .iter()
            .enumerate()
            .filter_map(|(world, r)| r.as_ref().err().map(|e| format!("world {world}: {e}")))
            .collect();
        if !failures.is_empty() {
            return Err(PyRuntimeError::new_err(format!(
                "{}; the batch is desynchronized — reset() before stepping again \
                 (this step's transitions are discarded)",
                failures.join("; ")
            )));
        }
        let steps: Vec<EpisodeStep> = results
            .into_iter()
            .map(|r| r.expect("failures handled above"))
            .collect();
        for (world, step) in steps.iter().enumerate() {
            self.last_states[world] = step.global_state.clone();
        }

        let obs = self.stack_observations(py, &steps)?;
        let rewards = PyDict::new(py);
        let terminations = PyDict::new(py);
        let truncations = PyDict::new(py);
        for id in &self.external {
            let name = agent_name(*id);
            let r: Vec<f64> = steps.iter().map(|s| s.reward).collect();
            rewards.set_item(&name, r.into_pyarray(py))?;
            let f: Vec<bool> = steps.iter().map(|_| false).collect();
            terminations.set_item(&name, f.into_pyarray(py))?;
            let t: Vec<bool> = steps.iter().map(|s| s.truncated).collect();
            truncations.set_item(&name, t.into_pyarray(py))?;
        }
        let infos = self.stack_infos(py, &steps)?;
        Ok((obs, rewards, terminations, truncations, infos))
    }

    /// The batched global state, [n_worlds, state_len] — the view the last
    /// reset/step produced (worlds live on their worker threads).
    fn state<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
        let mut flat = Vec::with_capacity(self.n_worlds * self.state_len);
        for state in &self.last_states {
            flat.extend_from_slice(state);
        }
        numpy::PyArray1::from_vec(py, flat)
            .reshape([self.n_worlds, self.state_len])
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    #[getter]
    fn menu_len(&self) -> usize {
        self.menu_len
    }

    /// The width of the message head's logit/mask segment (spec 033):
    /// Silent + the 15 head kinds = 16.
    #[getter]
    fn head_len(&self) -> usize {
        self.head_len
    }

    fn close(&self) {}
}

impl VectorEnv {
    /// Infos stacked on the leading world axis, one entry per agent:
    /// mask [n, menu ∥ head] (uint8), decision_seed [n] (uint64), survived [n]
    /// (int8: 1 passed validation, 0 rewritten, −1 no proposal — reset or
    /// substituted idle), applied_action [n] (int64, −1 when inexpressible
    /// or at reset), applied_action_name (list of str/None), provenance
    /// (list of str/None). Stacked rather than per-world dicts so a vector
    /// step marshals a handful of arrays, not hundreds of small objects —
    /// and carrying the same fields as ParallelEnv's infos (spec 014
    /// review: the schema must not narrow between the two surfaces).
    fn stack_infos<'py>(
        &self,
        py: Python<'py>,
        steps: &[EpisodeStep],
    ) -> PyResult<Bound<'py, PyDict>> {
        let n = steps.len();
        let infos = PyDict::new(py);
        for id in &self.external {
            let mask_width = self.menu_len + self.head_len;
            let mut mask = Vec::with_capacity(n * mask_width);
            let mut seeds = Vec::with_capacity(n);
            let mut survived: Vec<i8> = Vec::with_capacity(n);
            let mut applied = Vec::with_capacity(n);
            let mut applied_names: Vec<Option<&'static str>> = Vec::with_capacity(n);
            let mut applied_messages: Vec<Option<&'static str>> = Vec::with_capacity(n);
            let mut proposed_messages: Vec<Option<&'static str>> = Vec::with_capacity(n);
            let mut provenance: Vec<Option<&'static str>> = Vec::with_capacity(n);
            for step in steps {
                let info = step
                    .infos
                    .get(id)
                    .ok_or_else(|| PyRuntimeError::new_err("missing info"))?;
                mask.extend_from_slice(&info.mask);
                seeds.push(info.decision_seed);
                survived.push(match info.survived {
                    Some(true) => 1,
                    Some(false) => 0,
                    None => -1,
                });
                applied.push(info.applied_action.map(|a| a as i64).unwrap_or(-1));
                applied_names.push(info.applied_action_name);
                applied_messages.push(info.applied_message);
                proposed_messages.push(info.proposed_message);
                provenance.push(info.provenance.map(provenance_str));
            }
            let agent = PyDict::new(py);
            agent.set_item(
                "mask",
                numpy::PyArray1::from_vec(py, mask)
                    .reshape([n, mask_width])
                    .map_err(|e| PyRuntimeError::new_err(e.to_string()))?,
            )?;
            agent.set_item("decision_seed", seeds.into_pyarray(py))?;
            agent.set_item("survived", survived.into_pyarray(py))?;
            agent.set_item("applied_action", applied.into_pyarray(py))?;
            agent.set_item("applied_action_name", applied_names)?;
            agent.set_item("applied_message", applied_messages)?;
            agent.set_item("proposed_message", proposed_messages)?;
            agent.set_item("provenance", provenance)?;
            infos.set_item(agent_name(*id), agent)?;
        }
        Ok(infos)
    }

    fn stack_observations<'py>(
        &self,
        py: Python<'py>,
        steps: &[EpisodeStep],
    ) -> PyResult<Bound<'py, PyDict>> {
        let obs = PyDict::new(py);
        for id in &self.external {
            let mut flat = Vec::with_capacity(steps.len() * self.obs_len);
            for step in steps {
                let o = step
                    .observations
                    .get(id)
                    .ok_or_else(|| PyRuntimeError::new_err("missing observation"))?;
                flat.extend_from_slice(&o.values);
            }
            let arr = numpy::PyArray1::from_vec(py, flat)
                .reshape([steps.len(), self.obs_len])
                .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
            obs.set_item(agent_name(*id), arr)?;
        }
        Ok(obs)
    }
}

/// The `cloudkitty` Python module.
#[pymodule]
fn cloudkitty(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ParallelEnv>()?;
    m.add_class::<VectorEnv>()?;
    m.add(
        "OBSERVATION_SCHEMA_VERSION",
        cloudkitty_rl::observe::OBSERVATION_SCHEMA_VERSION,
    )?;
    m.add(
        "ACTION_SCHEMA_VERSION",
        cloudkitty_rl::codec::ACTION_SCHEMA_VERSION,
    )?;
    m.add(
        "MASK_SCHEMA_VERSION",
        cloudkitty_rl::mask::MASK_SCHEMA_VERSION,
    )?;
    m.add(
        "GLOBAL_STATE_SCHEMA_VERSION",
        cloudkitty_rl::global_state::GLOBAL_STATE_SCHEMA_VERSION,
    )?;
    Ok(())
}
