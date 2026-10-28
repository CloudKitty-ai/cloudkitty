"""Gen 2 trunk rollout surface: exp-006's MixedVecRunner mechanics with
the Gen 2 deltas only — ONE config (the trunk world, g2leg-20.toml:
the frozen draft with [starts] armed and explicit x/y stripped), every
seat policy (no family, no mixing; the served composition is the ruled
trunk roster), state read raw at the v2 width (237 — Gen 2 trains on
the 5-seat roster only, so no padding). Per-world deterministic seed
chains carried verbatim: episode seed = seed_base + w*1_000_000 +
episode_index. The engine draws per-episode randomized starts from the
world seed ([starts] 0.25/0.05, frozen §4 — every PPO episode, ruled).

The mask the binding reports is the 51-wide [activity | message]
concat (35 + 16 at schema 6), split downstream by index convention.
"""

import numpy as np
import cloudkitty

from tokens_v2 import STATE_DIM

MAX_SEATS = 5


class TrunkVecRunner:
    """Steps N all-policy trunk worlds in lockstep (two-head actions)."""

    def __init__(self, config_path: str, n_worlds: int, seed_base: int,
                 horizon: int | None = None):
        self.config_path = str(config_path)
        self.n_worlds = n_worlds
        self.seed_base = seed_base
        self.horizon = horizon
        self.episode_idx = [0] * n_worlds
        self.envs = [None] * n_worlds
        self.agent_names = [None] * n_worlds
        self._obs = [None] * n_worlds
        self._mask = [None] * n_worlds
        self.ep_return = np.zeros(n_worlds)
        self.ep_len = np.zeros(n_worlds, dtype=np.int64)
        self.completed: list[tuple[float, int]] = []
        for w in range(n_worlds):
            self._new_episode(w)

    def _new_episode(self, w: int):
        env = cloudkitty.ParallelEnv(self.config_path, horizon=self.horizon)
        seed = self.seed_base + w * 1_000_000 + self.episode_idx[w]
        obs, infos = env.reset(seed=seed)
        self.episode_idx[w] += 1
        self.envs[w] = env
        # The learning step's refusal (owner's observer-stream ruling,
        # 2026-10-27, B): PPO never gathers rollouts beside a needy seat.
        # Checked before the roster-size assert so the refusal names it;
        # a binding without needy() predates spec 067 and cannot load one.
        needy = env.needy() if hasattr(env, "needy") else []
        if needy:
            raise SystemExit(
                f"refusing PPO rollouts beside needy seat(s) "
                f"{[k for k, *_ in needy]} (owner ruling 2026-10-27, "
                "observer streams B)")
        self.agent_names[w] = list(env.possible_agents)
        assert len(self.agent_names[w]) == MAX_SEATS, self.agent_names[w]
        self._obs[w] = obs
        self._mask[w] = {a: infos[a]["mask"] for a in obs}

    @property
    def dims(self) -> tuple[int, int]:
        """(observation width, full mask width = activity + message)."""
        first = self.agent_names[0][0]
        return (int(np.asarray(self._obs[0][first]).shape[0]),
                int(len(self._mask[0][first])))

    def flat_obs(self, obs_dim: int, mask_dim: int):
        n = self.n_worlds
        obs = np.zeros((n, MAX_SEATS, obs_dim), np.float32)
        mask = np.zeros((n, MAX_SEATS, mask_dim), bool)
        valid = np.zeros((n, MAX_SEATS), bool)
        for w in range(n):
            for j, a in enumerate(self.agent_names[w]):
                obs[w, j] = self._obs[w][a]
                mask[w, j] = np.asarray(self._mask[w][a], bool)
                valid[w, j] = True
        return obs, mask, valid

    def _state(self, w: int):
        s = np.asarray(self.envs[w].state(), np.float32)
        assert s.shape[0] == STATE_DIM, (w, s.shape)
        return s

    def states(self):
        return np.stack([self._state(w) for w in range(self.n_worlds)])

    def step(self, actions: np.ndarray):
        """actions (n_worlds, MAX_SEATS, 2) int pairs. Returns
        (rewards, truncated, final_states) exactly as exp-002's runner."""
        n = self.n_worlds
        rewards = np.zeros(n)
        truncated = np.zeros(n, bool)
        final_states = np.zeros((n, STATE_DIM), np.float32)
        for w in range(n):
            names = self.agent_names[w]
            acts = {a: (int(actions[w, j, 0]), int(actions[w, j, 1]))
                    for j, a in enumerate(names)}
            obs, rew, _term, trunc, infos = self.envs[w].step(acts)
            rewards[w] = rew[names[0]]
            self.ep_return[w] += rewards[w]
            self.ep_len[w] += 1
            if any(trunc.values()):
                truncated[w] = True
                final_states[w] = self._state(w)
                self.completed.append((
                    self.ep_return[w] / self.ep_len[w], int(self.ep_len[w])))
                self.ep_return[w] = 0.0
                self.ep_len[w] = 0
                self._new_episode(w)
            else:
                self._obs[w] = obs
                self._mask[w] = {a: infos[a]["mask"] for a in obs}
        return rewards, truncated, final_states

    def drain_completed(self):
        done, self.completed = self.completed, []
        return done
