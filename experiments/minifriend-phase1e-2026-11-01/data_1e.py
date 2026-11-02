#!/usr/bin/env python3
"""Phase 1e's data (DECLARATION.md §3–§4): Phase 1's sample definition
on a world that may seat a scripted friend.

A SAMPLE is (world, observer k, friend j ≠ k, tick t) exactly as
phase1_data defines it — x = the observer's self block (109) ++ the
friend's permanent row (58) from the observer's saved start-of-tick
observation; y = the friend's TRUE state the view was built from
(needs[t−1], needs0 at t = 0), seven targets / 100 — with one
difference: the OBSERVERS of a world are the seats whose observation
was recorded (`meta.obs_recorded`). On a 1b world that is every seat
(20 pairs); on a TN / TE world the scripted seat recorded nothing, is
never an observer, and is a FRIEND of the four covered observers (16
pairs). The scripted friend's truth is recorded like any seat's.

This module pins MINIFRIEND_ARC to this directory (its split.json
holds 1b's sets verbatim, so phase1_data.roles() carves the 1b
validation worlds as 1b did; guard e2), and routes each set to the
raw directory its split entry names. Import it only in the training
processes (train_1e.py, probe_1e.py); the readers run under the
needy set's and Phase 1d's own arc roots.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
os.environ["MINIFRIEND_ARC"] = str(HERE)
PHASE1 = EXPTS / "minifriend-phase1-2026-10-22"
sys.path.insert(0, str(PHASE1))
import phase1_data as D  # noqa: E402
import strata as S  # noqa: E402
from count_strata import SELF_BLOCK, KITTY_SLOT, ROSTER, friend_row, truth_streams  # noqa: E402

SPLIT = json.loads((HERE / "split.json").read_text())
assert D.SPLIT["split_seed"] == SPLIT["split_seed"]
NEW_SETS = [n for n in SPLIT["sets"] if n.startswith(("TN", "TE"))]
OLD_SETS = [n for n in SPLIT["sets"] if n not in NEW_SETS]


def roles():
    """phase1_data.roles() on this arc's split: 1b's carve on 1b's sets, the same rule on TN / TE."""
    return D.roles()


def world_path(name, seed):
    return EXPTS / SPLIT["sets"][name]["raw_dir"] / f"streams-{seed}.npz"


def load_world(name, seed):
    z = np.load(world_path(name, seed))
    meta = json.loads(str(z["meta"]))
    rec = meta["obs_recorded"]
    assert rec is not None and len(rec) == ROSTER and any(rec), (name, seed, rec)
    if name in NEW_SETS:
        assert meta["aborted_at"] is None and meta["ticks"] == SPLIT["sets"][name]["ticks"], (name, seed, meta.get("aborted_at"), meta["ticks"])
        assert rec == [k != SPLIT["sets"][name]["scripted_seat"] for k in range(ROSTER)], (name, seed, rec)
    else:
        assert rec == [True] * ROSTER, (name, seed, rec)
    needs, hap = truth_streams(z)
    return {"set": name, "seed": seed, "ticks": meta["ticks"], "obs": z["obs"], "needs": needs, "hap": hap,
            "codes": S.stratum(needs, hap), "observers": [k for k in range(ROSTER) if rec[k]],
            "scripted": [k for k in range(ROSTER) if not rec[k]], "meta": meta}


def pairs(w):
    """Every (observer, friend) with the observer a recorded seat."""
    for k in w["observers"]:
        for j in range(ROSTER):
            if j != k:
                yield k, j


def pair_arrays(w, k, j):
    """x (T, 167) float16, y (T, 7) float32, vis (T,) bool, code (T,) int8 — phase1_data.pair_arrays
    with the observer checked against the recorded seats."""
    assert k in w["observers"], f"seat {k} recorded no observation (scripted); it is never an observer"
    off = SELF_BLOCK + KITTY_SLOT * friend_row(k, j)
    obs = w["obs"]
    x = np.concatenate([obs[:, k, :SELF_BLOCK], obs[:, k, off:off + KITTY_SLOT]], axis=1)
    y = np.concatenate([w["needs"][:, j, :5], w["hap"][:, j, None], w["needs"][:, j, 5:6]], axis=1) / 100.0
    vis = obs[:, k, off].astype(np.float32) > 0.5
    return x, y.astype(np.float32), vis, w["codes"][:, j]


def build(name_seeds):
    """Sequences for a role (train_heads.build's shape, NF weights): [{set, x f16 (T, 167), y (T, 7), w ones (T,)}]."""
    seqs = []
    for name, seed in name_seeds:
        w = load_world(name, seed)
        for k, j in pairs(w):
            x, y, _vis, _code = pair_arrays(w, k, j)
            seqs.append({"set": name, "x": x, "y": y, "w": np.ones(len(y), np.float32)})
    return seqs


def role_lists(smoke=False):
    """(train, val, eval) as (set, seed) lists; smoke = 2 train / 1 val per set, the first eval world,
    and a set whose raw directory is absent is left out with a note (the smoke exercises the
    pipeline before the training set exists; the real run refuses a missing world)."""
    r = roles()
    if smoke:
        absent = [n for n in r if not (EXPTS / SPLIT["sets"][n]["raw_dir"]).exists()]
        if absent:
            print(f"[smoke] sets without raws left out: {absent}", flush=True)
        r = {n: rr for n, rr in r.items() if n not in absent}
    train = [(n, s) for n, rr in r.items() for s in (rr["train"][:2] if smoke else rr["train"])]
    val = [(n, s) for n, rr in r.items() for s in (rr["val"][:1] if smoke else rr["val"])]
    ev = [(n, s) for n, rr in r.items() for s in rr["eval"]]
    if smoke:
        ev = ev[:1]
    assert not (set(train) & set(ev)) and not (set(val) & set(ev)) and not (set(train) & set(val))
    return train, val, ev


def present(name_seeds):
    return [(n, s) for n, s in name_seeds if world_path(n, s).exists()]
