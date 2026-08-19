"""exp-006 rollout surface: the spread family at the post-wall binding.

exp-004's MixedVecRunner (ppo_env_v4.py) carried forward VERBATIM in
mechanics — per-episode variant/subject draws, deterministic per-world
seed chains, padded 5-kitty states — with the exp-006 deltas only:

  - family size is an argument (the spread family is 18 variants,
    rosters cycling 3/4/5), asserted against the registered count;
  - the critic-view constants live here (state layout survived the
    wall: per-kitty 32 + tail 37, padded to the 5-kitty 197 — the
    dataset-v5 QA finding is that RAW widths vary by stratum);
  - needs_and_valid() exposes per-kitty need vectors + live-block
    masks from padded states — the estimator aux head's CTDE targets
    (prereg §4 E1; design-inputs §4c).

The mask the binding reports is the 50-wide [activity | message]
concat (34 + 16 post-wall), split downstream by index convention.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import cloudkitty

PER_KITTY = 32
TAIL = 37
TARGET_ROSTER = 5
MAX_SEATS = TARGET_ROSTER
PADDED_STATE_DIM = TARGET_ROSTER * PER_KITTY + TAIL  # 197
NEEDS_F = 6  # first 6 features of every kitty block (global_state.rs)


def pad_states(states, roster):
    """(N, roster*32+37) -> (N, 197): zero blocks for absent kitties."""
    s = np.asarray(states, dtype=np.float32)
    if roster == TARGET_ROSTER:
        return s
    zeros = np.zeros((s.shape[0], (TARGET_ROSTER - roster) * PER_KITTY),
                     np.float32)
    cut = roster * PER_KITTY
    return np.concatenate([s[:, :cut], zeros, s[:, cut:]], axis=1)


def needs_and_valid(padded):
    """(N, 197) -> needs (N, 5, 6), valid (N, 5). A vacant block is an
    exact zero row (pad_states writes zeros; a live kitty always has
    nonzero happiness/traits) — the same key the critic's padding mask
    uses (tokens.py)."""
    s = np.asarray(padded, np.float32)
    assert s.ndim == 2 and s.shape[1] == PADDED_STATE_DIM, s.shape
    k = s[:, :TARGET_ROSTER * PER_KITTY].reshape(-1, TARGET_ROSTER,
                                                 PER_KITTY)
    return k[:, :, :NEEDS_F].copy(), (np.abs(k).sum(axis=2) > 0.0)


@dataclass
class Variant:
    path: str
    kitty_ids: list[int]
    behaviors: dict[int, str]


def load_family(family_dir: Path, expected: int) -> list["Variant"]:
    variants = []
    for p in sorted(Path(family_dir).glob("family-*.toml")):
        with p.open("rb") as f:
            cfg = tomllib.load(f)
        kitties = cfg["kitty"]
        variants.append(Variant(
            path=str(p),
            kitty_ids=[k["id"] for k in kitties],
            behaviors={k["id"]: k["behavior"] for k in kitties},
        ))
    assert len(variants) == expected, (
        f"expected {expected} variants, got {len(variants)}")
    return variants


class MixedVecRunner:
    """Steps N mixed-population worlds in lockstep (two-head actions)."""

    def __init__(self, variants, mix: float, n_worlds: int, seed_base: int,
                 horizon: int | None = None):
        self.variants = variants
        self.mix = mix
        self.n_worlds = n_worlds
        self.seed_base = seed_base
        self.horizon = horizon
        self.rngs = [np.random.default_rng([seed_base, w])
                     for w in range(n_worlds)]
        self.episode_idx = [0] * n_worlds
        self.envs = [None] * n_worlds
        self.agent_names = [None] * n_worlds
        self.rosters = [0] * n_worlds
        self.draws = [None] * n_worlds
        self._obs = [None] * n_worlds
        self._mask = [None] * n_worlds
        self.ep_return = np.zeros(n_worlds)
        self.ep_len = np.zeros(n_worlds, dtype=np.int64)
        self.completed: list[tuple[float, int, bool, int]] = []
        for w in range(n_worlds):
            self._new_episode(w)

    def _new_episode(self, w: int):
        rng = self.rngs[w]
        vi = int(rng.integers(len(self.variants)))
        mixed = bool(rng.random() < self.mix)
        var = self.variants[vi]
        subject = int(rng.choice(var.kitty_ids))
        control = None
        if mixed:
            control = {f"kitty_{k}": var.behaviors[k]
                       for k in var.kitty_ids if k != subject}
        env = cloudkitty.ParallelEnv(var.path, control=control,
                                     horizon=self.horizon)
        seed = self.seed_base + w * 1_000_000 + self.episode_idx[w]
        obs, infos = env.reset(seed=seed)
        self.episode_idx[w] += 1
        self.envs[w] = env
        self.agent_names[w] = list(env.possible_agents)
        self.rosters[w] = len(var.kitty_ids)
        self.draws[w] = (vi, mixed, subject)
        self._obs[w] = obs
        self._mask[w] = {a: infos[a]["mask"] for a in obs}
        if mixed:
            assert self.agent_names[w] == [f"kitty_{subject}"], (
                f"mixed episode must seat exactly the subject, got "
                f"{self.agent_names[w]}")

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

    def _padded_state(self, w: int):
        s = np.asarray(self.envs[w].state(), np.float32)
        assert s.shape[0] == self.rosters[w] * PER_KITTY + TAIL, (
            f"world {w}: state {s.shape[0]} vs roster {self.rosters[w]}")
        return pad_states(s[None, :], self.rosters[w])[0]

    def states(self):
        return np.stack([self._padded_state(w) for w in range(self.n_worlds)])

    def step(self, actions: np.ndarray):
        """actions (n_worlds, MAX_SEATS, 2) int pairs; only valid slots
        are read. Returns (rewards, truncated, final_states) exactly as
        exp-002's runner."""
        n = self.n_worlds
        rewards = np.zeros(n)
        truncated = np.zeros(n, bool)
        final_states = np.zeros((n, PADDED_STATE_DIM), np.float32)
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
                final_states[w] = self._padded_state(w)
                self.completed.append((
                    self.ep_return[w] / self.ep_len[w], int(self.ep_len[w]),
                    self.draws[w][1], self.draws[w][0]))
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
