"""exp-002 rollout surface: mixed-population worlds over the frozen family.

The §3 registered mix semantics, implemented literally: per EPISODE,
with probability = the arm's mix, all non-subject seats run their
family-config behaviors (the `behavior` each [[kitty]] declares —
needs_driven, and playful where the family says so) and the policy
holds exactly one seat, drawn uniformly over the roster; otherwise all
seats are self-play copies. The binding fixes the control map at env
construction, so every episode boundary REBUILDS that world's env with
a fresh draw — episode seeds follow a deterministic per-world chain,
so a run is reproducible from (seed_base, world index, episode index).

Rosters vary 3-5 across the family, and mixed episodes seat one agent
while self-play seats the full roster — so the sample surface is
rectangular (n_worlds, MAX_SEATS) with a validity mask instead of
exp-001's fixed pair list. Critic states are padded to the 5-kitty
layout exactly as the pretrain saw them (trainer/data.py pad_states).
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import cloudkitty

from data import PER_KITTY, TAIL, TARGET_ROSTER, pad_states

MAX_SEATS = TARGET_ROSTER  # 5


@dataclass
class Variant:
    path: str
    kitty_ids: list[int]          # config order == stable state order
    behaviors: dict[int, str]     # id -> declared builtin


def load_family(family_dir: Path) -> list[Variant]:
    variants = []
    for p in sorted(family_dir.glob("family-*.toml")):
        with p.open("rb") as f:
            cfg = tomllib.load(f)
        kitties = cfg["kitty"]
        variants.append(Variant(
            path=str(p),
            kitty_ids=[k["id"] for k in kitties],
            behaviors={k["id"]: k["behavior"] for k in kitties},
        ))
    assert len(variants) == 15, f"expected the 15-variant family, got {len(variants)}"
    return variants


class MixedVecRunner:
    """Steps N mixed-population worlds in lockstep.

    Seeding: world w draws (variant, mixed?, subject) from
    default_rng([seed_base, w]); episode e of world w resets with
    seed_base + w*1_000_000 + e. Training episode seeds therefore live
    in [seed_base, seed_base + 12e6] — disjoint from eval (1..30) and
    probe (40_001..40_003) ranges by construction (§11).
    """

    def __init__(self, variants, mix: float, n_worlds: int, seed_base: int,
                 horizon: int | None = None):
        self.variants = variants
        self.mix = mix
        self.n_worlds = n_worlds
        self.seed_base = seed_base
        self.horizon = horizon
        self.rngs = [np.random.default_rng([seed_base, w]) for w in range(n_worlds)]
        self.episode_idx = [0] * n_worlds
        self.envs = [None] * n_worlds
        self.agent_names = [None] * n_worlds
        self.rosters = [0] * n_worlds
        self.draws = [None] * n_worlds       # (variant_idx, mixed, subject_id)
        self._obs = [None] * n_worlds
        self._mask = [None] * n_worlds
        self.ep_return = np.zeros(n_worlds)
        self.ep_len = np.zeros(n_worlds, dtype=np.int64)
        # (mean per-tick reward, len, mixed, variant_idx) per finished episode
        self.completed: list[tuple[float, int, bool, int]] = []
        for w in range(n_worlds):
            self._new_episode(w)

    def _new_episode(self, w: int):
        rng = self.rngs[w]
        vi = int(rng.integers(len(self.variants)))
        mixed = bool(rng.random() < self.mix)
        var = self.variants[vi]
        subject = int(rng.choice(var.kitty_ids))  # drawn even when unused
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

    def flat_obs(self, obs_dim: int, n_actions: int):
        """(obs (n,5,obs_dim), mask (n,5,n_actions), valid (n,5))."""
        n = self.n_worlds
        obs = np.zeros((n, MAX_SEATS, obs_dim), np.float32)
        mask = np.zeros((n, MAX_SEATS, n_actions), bool)
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
        """actions (n_worlds, MAX_SEATS) int; only valid slots are read.
        Returns (rewards (n,), truncated (n,), final_states (n, 197) —
        valid where truncated; truncated worlds start a fresh episode
        with a fresh §3 draw)."""
        n = self.n_worlds
        rewards = np.zeros(n)
        truncated = np.zeros(n, bool)
        final_states = np.zeros((n, TARGET_ROSTER * PER_KITTY + TAIL), np.float32)
        for w in range(n):
            names = self.agent_names[w]
            acts = {a: int(actions[w, j]) for j, a in enumerate(names)}
            obs, rew, _term, trunc, infos = self.envs[w].step(acts)
            rewards[w] = rew[names[0]]  # one team scalar, replicated
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
                self._new_episode(w)  # fresh draw + deterministic seed
            else:
                self._obs[w] = obs
                self._mask[w] = {a: infos[a]["mask"] for a in obs}
        return rewards, truncated, final_states

    def drain_completed(self):
        done, self.completed = self.completed, []
        return done
