#!/usr/bin/env python3
"""Act predictor Phase 1 — the data (DECLARATION.md §3): Phase 1e's split and pairs verbatim (data_1e), with the
friend's applied act as the target. y0[t] = applied[t] of the friend (the act taken in the step the observer is
about to take from obs[t]; collector doc), y10[t] = applied[t + 10], -1 where undefined (the world's last 10
ticks). Row state and the two observable baselines live here too, so the reader and the guards share them.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
P1E = EXPTS / "minifriend-phase1e-2026-11-01"
sys.path.insert(0, str(P1E))
import data_1e as E  # noqa: E402  (pins MINIFRIEND_ARC to Phase 1e's arc; split, roles, pairs, pair_arrays)
from count_strata import SELF_BLOCK, KITTY_SLOT, ROSTER  # noqa: E402

ACT_NAMES = ["move", "rest", "sleep", "groom", "eat", "drink", "chase", "play", "purr", "meow", "idle"]
N_ACTS = len(ACT_NAMES)
H10 = 10                                                   # the second horizon, ticks ahead
# docs/encodings.md kitty row: present 0; activity one-hot 6-12; message block 18-47, want 48-53, answers-me 54-57
ROW_PRESENT, ROW_ACT0, ROW_ACT1, ROW_MSG0, ROW_MSG1 = 0, 6, 13, 18, 58
APPLIED_ACTIVITY = {"rest": 1, "sleep": 2, "eat": 3, "drink": 4, "play": 5, "groom": 6}   # seating_read.APPLIED_ACTIVITY
ACTIVITY_TO_ACT = {v: ACT_NAMES.index(k) for k, v in APPLIED_ACTIVITY.items()}            # activity index -> act code
SEEN, HEARD, SILENT = 0, 1, 2
STATE_NAMES = ("seen", "heard", "silent")


def roles():
    return E.roles()


def role_lists(smoke=False):
    return E.role_lists(smoke)


def world_path(name, seed):
    return E.world_path(name, seed)


def load_world(name, seed):
    """data_1e.load_world plus the applied acts (T, R) int8."""
    w = E.load_world(name, seed)
    w["applied"] = np.load(world_path(name, seed))["applied"]
    assert w["applied"].shape == (w["ticks"], ROSTER), w["applied"].shape
    return w


def applied_of(path):
    """The applied acts of any streams npz (the needy set's worlds in the reader)."""
    return np.load(path)["applied"]


def targets(applied, j):
    """(T, 2) int64: y0 = applied[t] of friend j, y10 = applied[t + 10] (-1 where undefined)."""
    a = np.asarray(applied[:, j], np.int64)
    T = len(a)
    y10 = np.full(T, -1, np.int64)
    if T > H10:
        y10[:T - H10] = a[H10:]
    return np.stack([a, y10], 1)


def pairs(w):
    return E.pairs(w)


def pair_x(w, k, j):
    """x (T, 167) float16 for observer k, friend j (data_1e.pair_arrays's x)."""
    x, _y, _vis, _code = E.pair_arrays(w, k, j)
    return x


def build(name_seeds):
    """Sequences for a role: [{set, x (T, 167) f16, y (T, 2) int64}] over every (observer, friend) pair."""
    seqs = []
    for name, seed in name_seeds:
        w = load_world(name, seed)
        for k, j in pairs(w):
            seqs.append({"set": name, "x": pair_x(w, k, j), "y": targets(w["applied"], j)})
    return seqs


def row_state(x):
    """(T,) int8 from the friend row of x (T, 167): SEEN if present, else HEARD if any message / want / answers-me
    cell is live, else SILENT (58 zeros)."""
    row = np.asarray(x[:, SELF_BLOCK:SELF_BLOCK + KITTY_SLOT], np.float32)
    seen = row[:, ROW_PRESENT] > 0.5
    heard = ~seen & (np.abs(row[:, ROW_MSG0:ROW_MSG1]).max(1) > 0)
    out = np.full(len(row), SILENT, np.int8)
    out[heard] = HEARD
    out[seen] = SEEN
    return out


def baseline_V(x, mode):
    """(T,) the visible-row baseline: in sight, the act the activity one-hot names (rest / sleep / eat / drink / play /
    groom), else the training mode; out of sight the mode."""
    row = np.asarray(x[:, SELF_BLOCK:SELF_BLOCK + KITTY_SLOT], np.float32)
    seen = row[:, ROW_PRESENT] > 0.5
    act_idx = row[:, ROW_ACT0:ROW_ACT1].argmax(1)
    hot = row[:, ROW_ACT0:ROW_ACT1].max(1) > 0.5
    out = np.full(len(row), mode, np.int64)
    for a_idx, code in ACTIVITY_TO_ACT.items():
        out[seen & hot & (act_idx == a_idx)] = code
    return out


def baseline_R(applied_j, mode):
    """(T,) repeat: the friend's previous applied act; the mode at t = 0."""
    a = np.asarray(applied_j, np.int64)
    out = np.empty_like(a)
    out[0] = mode
    out[1:] = a[:-1]
    return out


def class_freq(seqs):
    """Training-set class frequencies of y0 over all pairs (the F baseline's distribution)."""
    c = np.zeros(N_ACTS, np.int64)
    for s in seqs:
        c += np.bincount(s["y"][:, 0], minlength=N_ACTS)
    return c


if __name__ == "__main__":
    tr, va, ev = role_lists()
    print(json.dumps({"train": len(tr), "val": len(va), "eval": len(ev), "acts": ACT_NAMES, "h10": H10}))
