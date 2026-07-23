# Contract: The Frozen Python Surface (module `cloudkitty`)

This is FR-003 made concrete: the observable Python API as it exists **before** the
upgrade (inventoried from `crates/cloudkitty-py/src/lib.rs` at main, 2026-07-23).
The upgrade MUST NOT change anything on this page. The unmodified pytest suite is
the executable check; this document is the human-readable reference for review.

## Module

`import cloudkitty` — built by maturin from crate `cloudkitty-py` (lib name `cloudkitty`).

**Module constants** (ints, re-exported schema versions):

| Name | Source |
|------|--------|
| `OBSERVATION_SCHEMA_VERSION` | `cloudkitty_rl::observe` |
| `ACTION_SCHEMA_VERSION` | `cloudkitty_rl::codec` |
| `MASK_SCHEMA_VERSION` | `cloudkitty_rl::mask` |
| `GLOBAL_STATE_SCHEMA_VERSION` | `cloudkitty_rl::global_state` |

## Class `ParallelEnv` (PettingZoo-parallel-style, one world)

**Constructor**: `ParallelEnv(config_path=None, *, config_toml=None, horizon=None, control=None)`

**Properties (getters)**:
- `agents` → `list[str]`
- `possible_agents` → `list[str]`
- `metadata` → `dict`

**Methods**:
- `observation_space(agent: str)` → Box-like space (gymnasium object when available, duck-typed dict otherwise)
- `action_space(agent: str)` → Discrete-like space (same duck-typing)
- `reset(seed=None, options=None)` → `(observations: dict, infos: dict)`
- `step(actions: dict)` → `(observations, rewards, terminations, truncations, infos)` — five dicts keyed by agent name; observations are 1-D float32 NumPy arrays; infos carry `mask` as a NumPy array plus provenance fields
- `state()` → 1-D float32 NumPy array (global state)
- `close()` → no-op
- `render()` → `Optional[str]`

## Class `VectorEnv` (batched multi-world runner)

**Constructor**: `VectorEnv(n_worlds, config_path=None, *, config_toml=None, seeds=None, horizon=None, workers=None, control=None)`

**Properties (getters)**:
- `num_worlds` → `int`
- `possible_agents` → `list[str]`
- `menu_len` → `int`

**Methods**:
- `reset(seeds=None)` → `(observations: dict, infos: dict)` — stacked across worlds
- `step(actions: dict)` → `(observations, rewards, terminations, truncations, infos)` — values stacked per agent across worlds (2-D float32 observation arrays; rewards/terminations/truncations as per-agent NumPy arrays; infos stacked, including `decision_seed`, `survived`, `applied_action` arrays)
- `state()` → 2-D float32 NumPy array (n_worlds × global-state length)
- `close()` → no-op

## Error behavior

- Configuration/episode errors surface as Python exceptions (`ValueError`, `RuntimeError`, `IndexError` families via the existing mappings) — same exception types, same conditions.

## Invariants under the upgrade

1. Every name above exists with the same spelling, arity, and keyword-only markers.
2. Array-typed returns keep dtype (`float32` observations/state) and dimensionality.
3. Determinism: identical seeds + config → bit-identical rollouts across processes (014 SC-002, re-asserted as this spec's SC-003).
4. Agent naming (`kitty_<id>` scheme via `agent_name`/`parse_agent`) is unchanged.
5. The gymnasium/PettingZoo duck-typing behavior (real objects when installed, plain dicts otherwise) is unchanged.
