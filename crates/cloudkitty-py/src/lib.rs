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
    name.strip_prefix("kitty_")?.parse().ok()
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
        EpisodeError::ActionOutOfRange { .. } => PyIndexError::new_err(e.to_string()),
        EpisodeError::SteppedAfterTruncation => PyRuntimeError::new_err(e.to_string()),
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
    let dict = PyDict::new_bound(py);
    dict.set_item("applied_action", info.applied_action)?;
    dict.set_item("applied_action_name", info.applied_action_name.clone())?;
    dict.set_item("survived", info.survived)?;
    dict.set_item("mask", info.mask.clone().into_pyarray_bound(py))?;
    dict.set_item("decision_seed", info.decision_seed)?;
    dict.set_item("provenance", info.provenance.map(provenance_str))?;
    Ok(dict)
}

fn observations_to_py<'py>(py: Python<'py>, step: &EpisodeStep) -> PyResult<Bound<'py, PyDict>> {
    let obs = PyDict::new_bound(py);
    for (id, observation) in &step.observations {
        obs.set_item(
            agent_name(*id),
            observation.values.clone().into_pyarray_bound(py),
        )?;
    }
    Ok(obs)
}

fn infos_to_py<'py>(py: Python<'py>, step: &EpisodeStep) -> PyResult<Bound<'py, PyDict>> {
    let infos = PyDict::new_bound(py);
    for (id, info) in &step.infos {
        infos.set_item(agent_name(*id), info_to_py(py, info)?)?;
    }
    Ok(infos)
}

/// A space description: `gymnasium.spaces` objects when gymnasium is
/// importable, plain dicts otherwise (duck-typed convention, FR-011).
fn box_space(py: Python<'_>, len: usize) -> PyResult<PyObject> {
    match py.import_bound("gymnasium.spaces") {
        Ok(spaces) => {
            let numpy = py.import_bound("numpy")?;
            let kwargs = PyDict::new_bound(py);
            kwargs.set_item("low", -1.0)?;
            kwargs.set_item("high", 4.0)?;
            kwargs.set_item("shape", (len,))?;
            kwargs.set_item("dtype", numpy.getattr("float32")?)?;
            Ok(spaces.getattr("Box")?.call((), Some(&kwargs))?.unbind())
        }
        Err(_) => {
            let dict = PyDict::new_bound(py);
            dict.set_item("type", "box")?;
            dict.set_item("low", -1.0)?;
            dict.set_item("high", 4.0)?;
            dict.set_item("shape", (len,))?;
            dict.set_item("dtype", "float32")?;
            Ok(dict.unbind().into())
        }
    }
}

fn discrete_space(py: Python<'_>, n: usize) -> PyResult<PyObject> {
    match py.import_bound("gymnasium.spaces") {
        Ok(spaces) => Ok(spaces.getattr("Discrete")?.call1((n,))?.unbind()),
        Err(_) => {
            let dict = PyDict::new_bound(py);
            dict.set_item("type", "discrete")?;
            dict.set_item("n", n)?;
            Ok(dict.unbind().into())
        }
    }
}

/// The PettingZoo-parallel CloudKitty environment (one world).
#[pyclass]
struct ParallelEnv {
    episode: Episode,
    external: Vec<KittyId>,
    live: bool,
}

impl ParallelEnv {
    fn build(
        config_path: Option<&str>,
        config_toml: Option<&str>,
        horizon: Option<u64>,
        control: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Episode> {
        let (core, mut rl) = load_configs(config_path, config_toml)?;
        if let Some(h) = horizon {
            rl.episode.horizon = h;
            rl.validate()
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
        }
        let control = parse_control(control)?;
        Episode::new(core, rl, control).map_err(episode_err)
    }

    fn actions_from_py(&self, actions: &Bound<'_, PyDict>) -> PyResult<BTreeMap<KittyId, usize>> {
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
            let index: i64 = value.extract()?;
            if index < 0 {
                return Err(PyIndexError::new_err(format!(
                    "action index {index} for '{name}' is negative"
                )));
            }
            map.insert(id, index as usize);
        }
        Ok(map)
    }

    fn step_result<'py>(&self, py: Python<'py>, step: &EpisodeStep) -> PyResult<StepTuple<'py>> {
        let obs = observations_to_py(py, step)?;
        let rewards = PyDict::new_bound(py);
        let terminations = PyDict::new_bound(py);
        let truncations = PyDict::new_bound(py);
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

    #[getter]
    fn metadata<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new_bound(py);
        dict.set_item("name", "cloudkitty_v1")?;
        dict.set_item("is_parallelizable", true)?;
        Ok(dict)
    }

    fn observation_space(&self, py: Python<'_>, _agent: &str) -> PyResult<PyObject> {
        box_space(py, observation_len(&self.episode.rl_config().observation))
    }

    fn action_space(&self, py: Python<'_>, _agent: &str) -> PyResult<PyObject> {
        discrete_space(py, self.episode.codec().len())
    }

    #[pyo3(signature = (seed=None, options=None))]
    fn reset<'py>(
        &mut self,
        py: Python<'py>,
        seed: Option<u64>,
        options: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<(Bound<'py, PyDict>, Bound<'py, PyDict>)> {
        let _ = options;
        let seed = seed.unwrap_or(self.episode.core_config().world.seed);
        let episode = &mut self.episode;
        let step = py.allow_threads(|| episode.reset(seed));
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
        let step = py
            .allow_threads(|| episode.step(&map))
            .map_err(episode_err)?;
        if step.truncated {
            self.live = false;
        }
        self.step_result(py, &step)
    }

    /// The privileged global state (FR-019): training and evaluation only —
    /// the deployed behavior API cannot receive it.
    fn state<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f32>> {
        let snapshot = self.episode.world().snapshot();
        let clock = if self.episode.horizon() > 0 {
            self.episode.tick_in_episode() as f32 / self.episode.horizon() as f32
        } else {
            0.0
        };
        cloudkitty_rl::global_state::encode_global_state(
            &snapshot,
            self.episode.core_config(),
            &self.episode.rl_config().global_state,
            clock,
        )
        .into_pyarray_bound(py)
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
    vector: VectorizedEnvironment,
    external: Vec<KittyId>,
    obs_len: usize,
    menu_len: usize,
    state_len: usize,
    seeds: Vec<u64>,
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
        let mut episodes = Vec::with_capacity(n_worlds);
        for _ in 0..n_worlds {
            episodes.push(ParallelEnv::build(
                config_path,
                config_toml,
                horizon,
                control,
            )?);
        }
        let external = episodes[0].external_agents();
        let obs_len = observation_len(&episodes[0].rl_config().observation);
        let menu_len = episodes[0].codec().len();
        let state_len = global_state_len(
            episodes[0].roster().len(),
            &episodes[0].rl_config().global_state,
        );
        let base = episodes[0].core_config().world.seed;
        let seeds = seeds.unwrap_or_else(|| (0..n_worlds as u64).map(|i| base + i).collect());
        if seeds.len() != n_worlds {
            return Err(PyValueError::new_err("seeds must have one entry per world"));
        }
        let n = episodes.len();
        Ok(VectorEnv {
            vector: VectorizedEnvironment::new(episodes, workers),
            external,
            obs_len,
            menu_len,
            state_len,
            seeds,
            last_states: vec![vec![0.0; state_len]; n],
        })
    }

    #[getter]
    fn num_worlds(&self) -> usize {
        self.vector.len()
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
        if let Some(seeds) = seeds {
            if seeds.len() != self.vector.len() {
                return Err(PyValueError::new_err("seeds must have one entry per world"));
            }
            self.seeds = seeds;
        }
        let vector = &mut self.vector;
        let seeds = self.seeds.clone();
        let steps = py.allow_threads(|| vector.reset(&seeds));
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
        let n = self.vector.len();
        // {agent: sequence[n]} → per-world action maps.
        let mut per_world: Vec<BTreeMap<KittyId, usize>> = vec![BTreeMap::new(); n];
        for (key, value) in actions.iter() {
            let name: String = key.extract()?;
            let id = parse_agent(&name)
                .ok_or_else(|| PyValueError::new_err(format!("unknown agent '{name}'")))?;
            let indices: Vec<i64> = value.extract()?;
            if indices.len() != n {
                return Err(PyValueError::new_err(format!(
                    "actions['{name}'] must have one entry per world ({n})"
                )));
            }
            for (world, &index) in indices.iter().enumerate() {
                if index < 0 {
                    return Err(PyIndexError::new_err(format!(
                        "action index {index} for '{name}' is negative"
                    )));
                }
                per_world[world].insert(id, index as usize);
            }
        }

        let vector = &mut self.vector;
        let results = py.allow_threads(|| vector.step(&per_world));
        let mut steps = Vec::with_capacity(n);
        for result in results {
            steps.push(result.map_err(episode_err)?);
        }
        self.last_states = steps.iter().map(|s| s.global_state.clone()).collect();

        let obs = self.stack_observations(py, &steps)?;
        let rewards = PyDict::new_bound(py);
        let terminations = PyDict::new_bound(py);
        let truncations = PyDict::new_bound(py);
        for id in &self.external {
            let name = agent_name(*id);
            let r: Vec<f64> = steps.iter().map(|s| s.reward).collect();
            rewards.set_item(&name, r.into_pyarray_bound(py))?;
            let f: Vec<bool> = steps.iter().map(|_| false).collect();
            terminations.set_item(&name, f.into_pyarray_bound(py))?;
            let t: Vec<bool> = steps.iter().map(|s| s.truncated).collect();
            truncations.set_item(&name, t.into_pyarray_bound(py))?;
        }
        let infos = self.stack_infos(py, &steps)?;
        Ok((obs, rewards, terminations, truncations, infos))
    }

    /// The batched global state, [n_worlds, state_len] — the view the last
    /// reset/step produced (worlds live on their worker threads).
    fn state<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
        let mut flat = Vec::with_capacity(self.vector.len() * self.state_len);
        for state in &self.last_states {
            flat.extend_from_slice(state);
        }
        numpy::PyArray1::from_vec_bound(py, flat)
            .reshape([self.vector.len(), self.state_len])
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    #[getter]
    fn menu_len(&self) -> usize {
        self.menu_len
    }

    fn close(&self) {}
}

impl VectorEnv {
    /// Infos stacked on the leading world axis, one entry per agent:
    /// mask [n, menu], decision_seed [n], survived [n], applied_action [n]
    /// (−1 when inexpressible or at reset), provenance (list of str/None).
    /// Stacked rather than per-world dicts so a vector step marshals a
    /// handful of arrays, not hundreds of small objects.
    fn stack_infos<'py>(
        &self,
        py: Python<'py>,
        steps: &[EpisodeStep],
    ) -> PyResult<Bound<'py, PyDict>> {
        let n = steps.len();
        let infos = PyDict::new_bound(py);
        for id in &self.external {
            let mut mask = Vec::with_capacity(n * self.menu_len);
            let mut seeds = Vec::with_capacity(n);
            let mut survived = Vec::with_capacity(n);
            let mut applied = Vec::with_capacity(n);
            let mut provenance: Vec<Option<&'static str>> = Vec::with_capacity(n);
            for step in steps {
                let info = step
                    .infos
                    .get(id)
                    .ok_or_else(|| PyRuntimeError::new_err("missing info"))?;
                mask.extend_from_slice(&info.mask);
                seeds.push(info.decision_seed);
                survived.push(info.survived.unwrap_or(true));
                applied.push(info.applied_action.map(|a| a as i64).unwrap_or(-1));
                provenance.push(info.provenance.map(provenance_str));
            }
            let agent = PyDict::new_bound(py);
            agent.set_item(
                "mask",
                numpy::PyArray1::from_vec_bound(py, mask)
                    .reshape([n, self.menu_len])
                    .map_err(|e| PyRuntimeError::new_err(e.to_string()))?,
            )?;
            agent.set_item("decision_seed", seeds.into_pyarray_bound(py))?;
            agent.set_item("survived", survived.into_pyarray_bound(py))?;
            agent.set_item("applied_action", applied.into_pyarray_bound(py))?;
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
        let obs = PyDict::new_bound(py);
        for id in &self.external {
            let mut flat = Vec::with_capacity(steps.len() * self.obs_len);
            for step in steps {
                let o = step
                    .observations
                    .get(id)
                    .ok_or_else(|| PyRuntimeError::new_err("missing observation"))?;
                flat.extend_from_slice(&o.values);
            }
            let arr = numpy::PyArray1::from_vec_bound(py, flat)
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
