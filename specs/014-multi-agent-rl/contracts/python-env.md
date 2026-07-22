# Contract: The Python Surface (FR-011, FR-012, FR-018..020)

`cloudkitty-py` — a logic-free PyO3 wrapper over `cloudkitty-rl`,
packaged by maturin as abi3 wheels. Duck-typed PettingZoo parallel
convention; the `pettingzoo` package is at most an optional test extra
(conformance check when present, research.md R10).

## `ParallelEnv`

```text
ParallelEnv(config_path or config_dict, horizon=2000,
            control={kitty: "external" | "<builtin name>"})
```

Config is immutable after construction (new config → new environment).
Horizon must be ≥ 1. Mixed control per FR-020: scripted kitties decide
from their own engine-dealt decision streams; the team reward counts the
full roster.

- `reset(seed) -> (observations, infos)` — fresh world from seed;
  observations: `{agent: float32 ndarray}` for external agents; infos
  carry the initial legal-action mask and decision seed per agent.
- `step(actions: {agent: int}) -> (observations, rewards, terminations,
  truncations, infos)` —
  - `rewards`: the one team scalar broadcast to every external agent.
  - `terminations`: all `False`, always (Article II as API guarantee).
  - `truncations`: all `False` until tick == horizon, then all `True`.
  - `infos` per agent: `applied_action` (menu index of what actually
    applied, when expressible, plus the engine action name), `survived`
    (proposal survived validation), `mask` (next decision's legal-action
    mask, uint8[40]), `decision_seed`, `provenance`
    (`policy`/`fallback` marking for scripted kitties).
  - Out-of-range action indices are a caller error (raise); in-range
    indices naming vacant slots decode and lawfully resolve to idle
    (never raise) — the codec-totality boundary.
- `state() -> float32 ndarray` — the privileged global state (FR-019).
  Present on the training env; absent from anything deployable.
- `agents`, `possible_agents`, `observation_space(agent)`,
  `action_space(agent)` — constant for the environment's life;
  Discrete(40) actions, Box observations with documented bounds.
- The GIL is released for the duration of engine work in `reset`/`step`.

## `VectorEnv`

```text
VectorEnv(config, n_worlds, seeds=[...], horizon=2000, workers=None)
```

- Batched `reset`/`step` over N fully independent worlds (separate seeds,
  RNGs, no shared state); arrays stacked on a leading world axis; fan-out
  across a scoped thread pool with the GIL released (research.md R6).
- Per-world results are positionally deterministic — parallel scheduling
  can never reorder or alter outputs.

## Reproducibility guarantee (SC-002)

Identical seed + config + action sequence → bit-identical observation,
mask, global-state, and reward streams across processes. Guarded by a
two-process CI test on the Python surface.

## Guarding tests

- Random-policy rollout smoke: shapes, bounds, bookkeeping (terminations
  always false; truncation exactly at horizon).
- Two-process bit-reproducibility (SC-002).
- Vectorized independence: world i in a batch == the same world stepped
  alone.
- Mixed-control rollout: scripted kitties deterministic; reward counts
  the full roster.
- Throughput measurement documented beside SC-003's number.
