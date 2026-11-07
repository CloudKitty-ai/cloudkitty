#!/usr/bin/env python3
"""Online head inference (DECLARATION.md §3, §4 "Head inference in the trainer", ruling 7): ONE forward, every home —
the PPO trainer, the cert harness's `p2` seat and the readers all build a P2Actor from here (guard g3).

An OnlineHeads runs the arm's one frozen act head as a reader on the observer's own stream: for observer row i and
friend row r (the observation's four kitty rows), x_t = self block (109) ++ friend row (58), the head's GRU state per
(i, r) carried from the episode's start (reset at every episode start), stepped every tick whatever the row's state.
Appended cells per friend row (DECLARATION §3 table):
  act arms  (C = 14): the eleven y0 class probabilities at T = 1, the top probability, the normalised entropy
                      (H / ln 11), ticks-since-live;  on a SILENT row (data_act.row_state) the frequency prior
                      `class_freq_train_y0` of the head's own manifest replaces the eleven probabilities and the two
                      summaries (the GRU still steps);
  nohead    (C = 1):  ticks-since-live only.
ticks-since-live = (tick − last tick the row was seen or heard) / 40 clamped to 1 (docs/encodings.md element-memory
staleness; never-live = 1). Record note (g1's consequence): the trunk's tokenizer pads a kitty row iff its 58 cells are
all zero, so on a SILENT row every appended cell is inert — the cells act on SEEN and HEARD rows only.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import ladder_act as LA  # noqa: E402  (registers B15 in the act arc's tables)
import train_act as TA  # noqa: E402
import data_act as D  # noqa: E402
import graft as G  # noqa: E402

LA.register()
N_CLASSES = D.N_ACTS                                        # 11
LN_K = math.log(N_CLASSES)
# arm -> (act head arm, head seed, cells). Heads by median validation loss (DECLARATION §2), named before training.
ARMS = {"act15": {"head": ("B15", 2), "cells": N_CLASSES + 3},
        "act10": {"head": ("B10", 3), "cells": N_CLASSES + 3},
        "nohead": {"head": None, "cells": 1}}
HEAD_SHA256 = {("B15", 2): "dd0e2d6e84e93052f04111cba5dbb9c58666f22b6aab7e41805208d055bbff08",
               ("B10", 3): "9bde78f8caf50d5926b9c5909d855beee91ab748c1d9ce92afa87e6fe6b09d6b"}
ROW0, ROW1 = C.SELF_BLOCK, C.SELF_BLOCK + C.N_ROWS * C.KITTY_W


def load_head(arm):
    """The arm's frozen head (train_act.load_act, eval, no grad) and its manifest; refuses a store whose head-best.pt
    sha256 is not the named head's (g3)."""
    spec = ARMS[arm]["head"]
    if spec is None:
        return None, None
    h_arm, seed = spec
    p = TA.OUT_ROOT / TA.run_name(h_arm, seed) / "head-best.pt"
    s = C.sha256(p)
    assert s == HEAD_SHA256[spec], f"{h_arm}-s{seed} head sha {s} is not the named {HEAD_SHA256[spec]}"
    model, manifest = TA.load_act(h_arm, seed)
    return model, manifest


def freq_prior(manifest):
    cf = np.asarray(manifest["class_freq_train_y0"], np.float64)
    p = cf / cf.sum()
    return p.astype(np.float32)


def summaries(p):
    """(top-prob, normalised entropy) of probability rows p (..., 11)."""
    top = p.max(-1)
    ent = -(p * np.log(np.clip(p, 1e-12, 1.0))).sum(-1) / LN_K
    return top, ent


def row_states(rows):
    """(n, 4) int8 SEEN / HEARD / SILENT per friend row (data_act.row_state's rule on a (n, 4, 58) block)."""
    seen = rows[..., D.ROW_PRESENT] > 0.5
    heard = ~seen & (np.abs(rows[..., D.ROW_MSG0:D.ROW_MSG1]).max(-1) > 0)
    out = np.full(rows.shape[:-1], D.SILENT, np.int8)
    out[heard] = D.HEARD
    out[seen] = D.SEEN
    return out


class OnlineHeads:
    """Per-observer, per-friend-row recurrent head state for n observer rows fed in a fixed order every tick."""

    def __init__(self, arm, n_obs):
        self.arm, self.n = arm, int(n_obs)
        self.cells = ARMS[arm]["cells"]
        self.head, self.manifest = load_head(arm)
        self.prior = None if self.head is None else freq_prior(self.manifest)
        if self.prior is not None:
            self.prior_cells = np.concatenate([self.prior, [summaries(self.prior)[0]], [summaries(self.prior)[1]]]).astype(np.float32)
        self.reset()

    def reset(self, rows=None):
        """Episode start: zero GRU state, no row ever live, tick 0 — for every observer row, or for `rows` only."""
        if rows is None:
            self.h = None if self.head is None else torch.zeros(1, self.n * C.N_ROWS, self.head.gru.hidden_size)
            self.last_live = np.full((self.n, C.N_ROWS), -1, np.int64)
            self.t = np.zeros(self.n, np.int64)
            return
        for i in rows:
            if self.h is not None:
                self.h[:, i * C.N_ROWS:(i + 1) * C.N_ROWS] = 0.0
            self.last_live[i] = -1
            self.t[i] = 0

    def step(self, obs):
        """obs (n, 399) float32 at the start of a tick -> cells (n, 4, C) float32; steps every head state once."""
        obs = np.asarray(obs, np.float32)
        assert obs.shape == (self.n, C.OBS_DIM), obs.shape
        rows = obs[:, ROW0:ROW1].reshape(self.n, C.N_ROWS, C.KITTY_W)
        st = row_states(rows)
        live = st != D.SILENT
        self.last_live[live] = self.t[:, None].repeat(C.N_ROWS, 1)[live]
        ever = self.last_live >= 0
        tsl = np.ones((self.n, C.N_ROWS), np.float32)
        tsl[ever] = np.clip((self.t[:, None].repeat(C.N_ROWS, 1)[ever] - self.last_live[ever]) / C.STALENESS_NORMALISER, 0.0, 1.0)
        self.t += 1
        if self.head is None:
            return tsl[..., None]
        x = np.concatenate([np.repeat(obs[:, None, :C.SELF_BLOCK], C.N_ROWS, 1), rows], -1).reshape(1, self.n * C.N_ROWS, -1)
        with torch.no_grad():
            o0, _o10, self.h = self.head(torch.from_numpy(x), self.h)
            p = torch.softmax(o0[0], -1).numpy().reshape(self.n, C.N_ROWS, N_CLASSES)
        top, ent = summaries(p)
        cells = np.concatenate([p, top[..., None], ent[..., None]], -1)
        cells[~live] = self.prior_cells
        return np.concatenate([cells, tsl[..., None]], -1).astype(np.float32)


class P2Actor:
    """The arm's policy with its head inline: logits(obs (n, 399)) steps the heads, widens the rows, runs the policy.
    heads may be None with `arm` given: the OnlineHeads are then sized at the first call (the cert harness feeds a
    seat's rows in a fixed order every tick and knows the count only then) and the count is asserted constant."""

    def __init__(self, policy, heads=None, arm=None):
        assert heads is not None or arm is not None
        self.policy, self.heads, self.arm = policy, heads, arm
        if heads is not None:
            assert policy.cells == heads.cells, (policy.cells, heads.cells)
        self.policy.eval()

    def reset(self, rows=None):
        if self.heads is not None:
            self.heads.reset(rows)

    def widen(self, obs):
        if self.heads is None:
            self.heads = OnlineHeads(self.arm, len(obs))
            assert self.policy.cells == self.heads.cells, (self.policy.cells, self.heads.cells)
        assert len(obs) == self.heads.n, f"{len(obs)} rows for a seat sized {self.heads.n}"
        cells = self.heads.step(obs)
        return np.concatenate([np.asarray(obs, np.float32), cells.reshape(len(obs), -1)], 1), cells

    def logits(self, obs):
        x, _cells = self.widen(obs)
        with torch.no_grad():
            return self.policy(torch.from_numpy(x)).numpy()

    def __call__(self, rows, masks=None):
        """The cert harness's seat callable: (rows, masks) -> logits; rows arrive in a fixed order every tick."""
        return self.logits(rows)


def actor_from_artifact(path, n_obs=None):
    """A P2Actor from a saved Phase 2 policy (graft.save_policy's record names its arm); n_obs None = sized at the
    first call."""
    policy, ck = G.load_policy(path)
    arm = ck["arm"]
    assert arm in ARMS, arm
    return P2Actor(policy, None if n_obs is None else OnlineHeads(arm, n_obs), arm=arm), ck


if __name__ == "__main__":
    for arm in ARMS:
        h = OnlineHeads(arm, 5)
        print(json.dumps({"arm": arm, "cells": h.cells, "head": ARMS[arm]["head"],
                          "prior": None if h.prior is None else h.prior.round(4).tolist()}))
