#!/usr/bin/env python3
"""The needy set's reader core (DECLARATION.md §4, §5, §10 n4 / n6 / n8).

What lives here is what every read R1–R8 rests on and what the guards
hold before any read exists: loading a needy-set world (rot2 less one
network plus a scripted friend; the scripted seat records no
observation and is never an observer), the frozen probe NF-h24+p run
over the covered observers' slices exactly as Phase 1d ran it (state
zero at the world's start, carried across 500-tick chunks, the 20-pair
batch when all five seats are covered), the episode / crossing / anchor
definitions of §4, and the tuning/confirming split's enforcement.

    needy_read.py check-probe          # n8: P1's first evaluation world reproduces the committed pgrave file, every seed
    needy_read.py check-probe --seed 2 # one probe seed

Nothing here reads a confirming seed before her pick: `refuse_unless`
is the gate every read calls with the half it is declared on.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
PHASE1 = EXPTS / "minifriend-phase1-2026-10-22"
PHASE1B = EXPTS / "minifriend-phase1b-2026-10-23"
PHASE1D = EXPTS / "minifriend-phase1d-2026-10-24"
os.environ.setdefault("MINIFRIEND_ARC", str(PHASE1B))   # the heads' split and raws (1d reads 1b's)
sys.path.insert(0, str(PHASE1))
import strata as S  # noqa: E402
from count_strata import SELF_BLOCK, KITTY_SLOT, ROSTER, friend_row, truth_streams  # noqa: E402

SPLIT = json.loads((HERE / "split.json").read_text())
PROBE_SEEDS = (1, 2, 3)
HEAD = "NF-h24"
CHUNK = 500
PHASES = ("resting", "held", "released_level", "released_limit")
NEED_NAMES = ("eat", "drink", "sleep", "play", "cuddle", "bath")
# §4 primary strata on H, the crossing's offset from the slice's first tick
STRATA = {"H0": (0, 2), "H1": (2, 100), "H2": (100, 300), "H3": (300, 1250), "H4": (1250, 6000)}
SPLICE_BINS = ((2, 5), (5, 10), (10, 20), (20, 50), (50, 100))


# ---- worlds --------------------------------------------------------------

def load_world(path):
    """A needy-set npz: meta, obs, truth aligned to obs[t] (needs[t-1], needs0
    at t = 0), stratum codes, the covered observers, the needy streams if
    the world seats a needy kitty."""
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    rec = meta["obs_recorded"]
    assert rec is not None and len(rec) == ROSTER, rec
    needs, hap = truth_streams(z)
    w = {"path": str(path), "seed": meta["seed"], "ticks": meta["ticks"], "meta": meta, "obs": z["obs"],
         "needs": needs, "hap": hap, "codes": S.stratum(needs, hap), "obs_recorded": list(rec),
         "scripted": [k for k, r in enumerate(rec) if not r],
         "post_needs": z["needs"], "post_hap": z["hap"]}
    if meta.get("needy_seat") is not None:
        w["needy_seat"] = meta["needy_seat"]
        w["needy_mask"], w["needy_ordinal"], w["needy_phase"] = z["needy_mask"], z["needy_ordinal"], z["needy_phase"]
    return w


def observers(w):
    """The covered seats: the only seats whose observation was recorded."""
    return [k for k in range(ROSTER) if w["obs_recorded"][k]]


def observer_pairs(w):
    """Every ordered (observer, friend) pair whose observer is covered (n4)."""
    return [(k, j) for k in observers(w) for j in range(ROSTER) if j != k]


def pair_x(w, k, j):
    """x (T, 167) float16 for observer k, friend j: the observer's self block
    and the friend's permanent row. Refuses a seat that recorded nothing."""
    assert w["obs_recorded"][k], f"seat {k} recorded no observation (scripted); it is never an observer"
    off = SELF_BLOCK + KITTY_SLOT * friend_row(k, j)
    obs = w["obs"]
    x = np.concatenate([obs[:, k, :SELF_BLOCK], obs[:, k, off:off + KITTY_SLOT]], axis=1)
    vis = obs[:, k, off].astype(np.float32) > 0.5
    return x, vis


# ---- the frozen probe ----------------------------------------------------

def load_probe(seed):
    """NF-h24-s<seed> (frozen) and its 25-parameter grave probe, from the
    committed 1b / 1d raws; returns (model, probe, manifest)."""
    import torch
    import train_heads as T
    base = PHASE1B / "results-raw" / "heads" / f"{HEAD}-s{seed}" / "head-best.pt"
    ck = torch.load(base, map_location="cpu", weights_only=False)
    model = T.BeliefHead(h=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    pk = torch.load(PHASE1D / "results-raw" / "probe" / f"{HEAD}-s{seed}+p" / "probe.pt", map_location="cpu", weights_only=False)
    probe = torch.nn.Linear(ck["manifest"]["hidden"], 1)
    probe.load_state_dict(pk["state_dict"])
    probe.eval()
    for m in (model, probe):
        for p in m.parameters():
            p.requires_grad_(False)
    return model, probe, {"base": str(base), "probe": pk.get("manifest"), "best_epoch": pk.get("best_epoch")}


def probe_world(model, probe, w, pairs=None):
    """P(grave) (T, R, R) [observer, friend], NaN where no pair runs: the
    pairs as one batch, hidden state zero at the world's start, carried
    across CHUNK ticks (grave_probe.states_world / predict_world_p)."""
    import torch
    pairs = observer_pairs(w) if pairs is None else pairs
    x = torch.from_numpy(np.stack([pair_x(w, k, j)[0] for k, j in pairs], 1))      # (T, n, 167) f16
    Tn = w["ticks"]
    out, h = [], None
    with torch.no_grad():
        for c in range(0, Tn, CHUNK):
            z, h = model.gru(torch.relu(model.proj(x[c:min(c + CHUNK, Tn)].float())), h)
            out.append(torch.sigmoid(probe(z).squeeze(-1)))
    p = torch.cat(out).numpy()
    full = np.full((Tn, ROSTER, ROSTER), np.nan, np.float32)
    for i, (k, j) in enumerate(pairs):
        full[:, k, j] = p[:, i]
    return full


def check_probe_reproduces(seeds=PROBE_SEEDS, world=("P1", 1095452)):
    """n8: in this venv, P(grave) on group P's first evaluation world equals
    the committed pgrave file for every probe seed, to 0.0."""
    name, seed = world
    w = load_world(PHASE1B / "results-raw" / name / f"streams-{seed}.npz")
    assert w["scripted"] == [], w["scripted"]
    worst = {}
    for s in seeds:
        model, probe, _m = load_probe(s)
        mine = probe_world(model, probe, w)
        ref = np.load(PHASE1D / "results-raw" / "probe" / f"{HEAD}-s{s}+p" / f"pgrave-{name}-{seed}.npz")["p"]
        assert mine.shape == ref.shape, (mine.shape, ref.shape)
        d = np.abs(np.nan_to_num(mine) - np.nan_to_num(ref)).max()
        assert np.isnan(mine).sum() == np.isnan(ref).sum() == ref.shape[0] * ROSTER
        worst[s] = float(d)
        print(f"n8 seed {s}: {name} {seed} max |p - committed| = {d}")
    bad = {s: d for s, d in worst.items() if d != 0.0}
    assert not bad, f"n8 FAIL: {bad}"
    print("n8 PASS: every probe seed reproduces the committed file to 0.0")
    return worst


# ---- the split (n6) ------------------------------------------------------

def arm_block(arm, k):
    return SPLIT["arms"][f"{arm}{k}"]


def half_of(arm, k, seed):
    b = arm_block(arm, k)
    if seed in b["tuning"]:
        return "tuning"
    if seed in b["confirming"]:
        return "confirming"
    raise KeyError(f"seed {seed} is not in {arm}{k}")


def refuse_unless(arm, k, seed, half):
    """Every read calls this with the half it is declared on (R4 tuning, R5
    confirming); a seed from the other half raises before anything loads."""
    got = half_of(arm, k, seed)
    if got != half:
        raise PermissionError(f"{arm}{k} seed {seed} is a {got} seed; this read is declared on {half} seeds only")
    return seed


def seeds(arm, k, half, w=None):
    """The block's seeds of one half, in order; `w` = the first w seeds of
    the block (the sizing rule) before halving."""
    b = arm_block(arm, k)
    pool = b["seeds"] if w is None else b["seeds"][:w]
    return [s for s in pool if s in b[half]]


# ---- episodes and anchors (§4) ---------------------------------------------

def grave_episodes(codes_j):
    """Maximal runs of GRAVE on a friend's truth stream aligned to obs:
    [(crossing, end)) with H = crossing (the slice starts at tick 0)."""
    g = (np.asarray(codes_j) == S.GRAVE).astype(np.int8)
    d = np.diff(np.concatenate([[0], g, [0]]))
    return list(zip(np.where(d == 1)[0].tolist(), np.where(d == -1)[0].tolist()))


def stratum_of(h):
    for name, (lo, hi) in STRATA.items():
        if lo <= h < hi:
            return name
    return None


def mask_windows(w):
    """Arm N / E: [(onset, release_exclusive, ordinal)] from the recorded
    schedule; the mask anchor is the first tick reported held for that
    ordinal, the window closes the tick after the release tick."""
    phase, ordinal = w["needy_phase"], w["needy_ordinal"]
    held = PHASES.index("held")
    out = []
    for o in range(1, int(ordinal.max()) + 1):
        idx = np.where(ordinal == o)[0]
        on = idx[phase[idx] == held]
        if len(on) == 0:
            continue
        rel = idx[(phase[idx] == PHASES.index("released_level")) | (phase[idx] == PHASES.index("released_limit"))]
        close = int(rel[0]) + 1 if len(rel) else w["ticks"]
        out.append((int(on[0]), close, o))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check-probe"])
    ap.add_argument("--seed", type=int, default=None, help="one probe seed (default all three)")
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    if a.cmd == "check-probe":
        check_probe_reproduces(seeds=(a.seed,) if a.seed else PROBE_SEEDS)


if __name__ == "__main__":
    main()
