"""Vectorized rollout surface for MAPPO (prereg §4, §7.4).

Twelve independent worlds stepped in lockstep: 8 all-external across the
training family, 2 with one scripted kitty, 2 with two — 4/12 = 33%
mixed-control, inside §4's 25–50% band. Each world is its own
ParallelEnv, because configs and control maps vary per world (VectorEnv
takes one of each).

Mixed-control semantics come from the binding: a kitty seated via
`control={'kitty_1': 'needs_driven'}` leaves the agent surface entirely
but still lives in the world and still counts toward the team reward —
the policy learns among teammates it does not control.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import cloudkitty

# Global-state layout (crates/cloudkitty-rl/src/global_state.rs): per-kitty
# blocks first, then the element/clock tail. The critic is pretrained on
# the 5-kitty training-family layout; roster-4 worlds (default world,
# anneal phase) produce a shorter vector, so a zeroed phantom-kitty block
# is spliced in front of the tail. PER_KITTY mirrors global_state.rs and
# every use is guarded by a divisibility assert.
PER_KITTY = 32


@dataclass
class WorldSpec:
    config_path: str
    control: dict | None   # kitty name -> builtin, or None for all-external
    roster: int            # full roster incl. scripted kitties


def training_specs(family_dir: Path, training_toml: Path, n_worlds: int = 12):
    """8 all-external / 2 one-scripted / 2 two-scripted, configs cycling
    over training.toml + the family variants (roster fixed at 5)."""
    configs = [str(training_toml)] + [str(p) for p in sorted(family_dir.glob("family-*.toml"))]
    assert configs, f"no configs under {family_dir}"
    specs = []
    for i in range(n_worlds):
        if i < n_worlds - 4:
            control = None
        elif i < n_worlds - 2:
            control = {"kitty_1": "needs_driven"}
        else:
            control = {"kitty_1": "needs_driven", "kitty_2": "needs_driven"}
        specs.append(WorldSpec(configs[i % len(configs)], control, roster=5))
    return specs


def default_world_specs(default_toml: Path, n_worlds: int = 12):
    """Anneal phase (§4: final ~15% on the default world config): same
    8/2/2 mixed structure, roster 4."""
    specs = []
    for i in range(n_worlds):
        if i < n_worlds - 4:
            control = None
        elif i < n_worlds - 2:
            control = {"kitty_1": "needs_driven"}
        else:
            control = {"kitty_1": "needs_driven", "kitty_2": "needs_driven"}
        specs.append(WorldSpec(str(default_toml), control, roster=4))
    return specs


def adapt_state(state: np.ndarray, roster: int, target_dim: int, target_roster: int):
    """Splice zeroed phantom-kitty blocks so a smaller-roster state fits
    the critic's pretrained input layout (kitty blocks, then tail)."""
    if state.shape[0] == target_dim:
        return state
    tail = state.shape[0] - roster * PER_KITTY
    assert tail == target_dim - target_roster * PER_KITTY and tail > 0, (
        f"state {state.shape[0]} (roster {roster}) does not share a tail "
        f"with target {target_dim} (roster {target_roster})"
    )
    pad = np.zeros((target_roster - roster) * PER_KITTY, dtype=np.float32)
    return np.concatenate([state[: roster * PER_KITTY], pad, state[roster * PER_KITTY:]])


class VecRunner:
    """Steps N ParallelEnvs in lockstep and presents flat batches.

    Seeding: each world gets seed_base + index once; bare reset() after
    each truncation advances the binding's deterministic fresh-seed chain,
    so the entire run is reproducible from seed_base.
    """

    def __init__(self, specs, seed_base: int, state_dim: int, state_roster: int,
                 horizon: int | None = None):
        self.specs = specs
        self.state_dim = state_dim
        self.state_roster = state_roster
        self.envs, self.agent_names, self._obs, self._mask = [], [], [], []
        for i, sp in enumerate(specs):
            env = cloudkitty.ParallelEnv(sp.config_path, control=sp.control,
                                         horizon=horizon)
            obs, infos = env.reset(seed=seed_base + i)
            self.envs.append(env)
            self.agent_names.append(list(env.possible_agents))
            self._obs.append(obs)
            self._mask.append({a: infos[a]["mask"] for a in obs})
        # Flat sample layout: (world w, agent a) pairs in fixed order.
        self.pairs = [(w, a) for w, names in enumerate(self.agent_names) for a in names]
        self.world_of_sample = np.array([w for w, _ in self.pairs], dtype=np.int64)
        self.n_worlds = len(self.envs)
        self.ep_return = np.zeros(self.n_worlds)
        self.ep_len = np.zeros(self.n_worlds, dtype=np.int64)
        self.completed: list[tuple[float, int]] = []  # (mean per-tick reward, len)

    def flat_obs(self):
        obs = np.stack([self._obs[w][a] for w, a in self.pairs])
        mask = np.stack([self._mask[w][a] for w, a in self.pairs]).astype(bool)
        return obs, mask

    def states(self):
        out = np.stack([
            adapt_state(env.state(), sp.roster, self.state_dim, self.state_roster)
            for env, sp in zip(self.envs, self.specs)
        ])
        return out.astype(np.float32)

    def step(self, flat_actions: np.ndarray):
        """flat_actions aligned with self.pairs. Returns (rewards (n,),
        truncated (n,) bool, final_states (n, state_dim) — rows are valid
        only where truncated; truncated worlds are auto-reset)."""
        rewards = np.zeros(self.n_worlds)
        truncated = np.zeros(self.n_worlds, dtype=bool)
        final_states = np.zeros((self.n_worlds, self.state_dim), dtype=np.float32)
        cursor = 0
        for w, env in enumerate(self.envs):
            names = self.agent_names[w]
            acts = {a: int(flat_actions[cursor + j]) for j, a in enumerate(names)}
            cursor += len(names)
            obs, rew, _term, trunc, infos = env.step(acts)
            rewards[w] = rew[names[0]]  # one team scalar, replicated
            self.ep_return[w] += rewards[w]
            self.ep_len[w] += 1
            if any(trunc.values()):
                truncated[w] = True
                final_states[w] = adapt_state(
                    env.state(), self.specs[w].roster, self.state_dim, self.state_roster)
                self.completed.append((self.ep_return[w] / self.ep_len[w], int(self.ep_len[w])))
                self.ep_return[w] = 0.0
                self.ep_len[w] = 0
                obs, infos = env.reset()  # bare: deterministic fresh-seed chain
            self._obs[w] = obs
            self._mask[w] = {a: infos[a]["mask"] for a in obs}
        return rewards, truncated, final_states

    def drain_completed(self):
        done, self.completed = self.completed, []
        return done
