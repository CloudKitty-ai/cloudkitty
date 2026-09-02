#!/usr/bin/env python3
"""Behavioural-collapse detector v0 (prereg.md — read it first).

Offline, over a per-tick global-state array in the `global_state.rs`
layout (32 floats per kitty: needs 0-5, happiness 6, pos 7-8, activity
one-hot 9-15, social 16, partner flag 17, partner index 18, progress
19, distress flags 20-25, traits 26-31). Signals:

  (a) partnered-activity concentration  per seat   FIRES
  (b) mutual-pair persistence           per pair   FIRES
  (c) need spread                        per seat   report only

Each is a trailing-window share (W) that must hold over its bar (0.55 for
(a) since v0.2, 0.50 for (b), 60 for
(c)) for D consecutive ticks to fire. Detect-and-report: nothing here
touches a world.

usage: detector.py <trace.npz> [more.npz ...]   (exp-006 forensics traces)
"""
import json
import sys
from pathlib import Path

import numpy as np

PER_KITTY = 32
OFF_NEEDS, OFF_ACT, OFF_PFLAG, OFF_PIDX, OFF_DIST = 0, 9, 17, 18, 20
ACTIVITIES = ["idle", "resting", "sleeping", "eating", "drinking",
              "playing", "grooming"]
PARTNERED = {"resting", "sleeping", "grooming"}      # the adhesive families
W, D = 200, 200
# v0.2 (owner 2026-09-01): H4's single-family bar (a) is 0.55 (v0.1's 0.65
# dropped a ramping ~500-tick lock); the mutual-pair bar (b) stays at v0's 0.50.
SHARE_BAR_A, SHARE_BAR_B, SPREAD_BAR = 0.55, 0.50, 60.0
WATCHDOG_THRESHOLD = 150


def trailing_mean(x, w):
    """Mean of x over the trailing window ending at each tick; NaN for
    the first w-1 ticks (no full window yet). x: (T,) or (T, K)."""
    x = np.asarray(x, np.float64)
    c = np.cumsum(x, axis=0)
    out = np.full_like(c, np.nan)
    out[w - 1:] = (c[w - 1:] - np.concatenate([np.zeros_like(c[:1]), c[:-w]])) / w
    return out


def sustained(flags, d):
    """First index at which `flags` has been True for d consecutive ticks,
    and the length of that maximal run; (None, 0) if never."""
    run = 0
    first = None
    best = 0
    for i, f in enumerate(flags):
        run = run + 1 if f else 0
        if run >= d and first is None:
            first = i
        best = max(best, run)
    return first, best


def decode(states, roster):
    """Per-tick, per-kitty views of the fields the signals need."""
    base = np.arange(roster) * PER_KITTY
    needs = np.stack([states[:, b + OFF_NEEDS:b + OFF_NEEDS + 6] for b in base], 1) * 100
    act = np.stack([states[:, b + OFF_ACT:b + OFF_ACT + 7] for b in base], 1).argmax(2)
    pflag = np.stack([states[:, b + OFF_PFLAG] for b in base], 1) > 0.5
    pidx = np.rint(np.stack([states[:, b + OFF_PIDX] for b in base], 1) * (roster - 1)).astype(int)
    pidx = np.where(pflag, pidx, -1)
    dist = np.stack([states[:, b + OFF_DIST:b + OFF_DIST + 6] for b in base], 1) > 0
    return needs, act, pidx, dist


def detect(states, roster, names=None, w=W, d=D):
    T = states.shape[0]
    names = names or [f"k{i}" for i in range(roster)]
    needs, act, pidx, dist = decode(states, roster)
    fam_ids = [ACTIVITIES.index(f) for f in sorted(PARTNERED)]
    report = {"fires": [], "max_share": {"a": 0.0, "b": 0.0, "c": 0.0},
              "watchdog_tick": None, "spread_flags": []}

    # (a) one partnered family > SHARE_BAR_A of the trailing window, per seat
    for k in range(roster):
        for f in fam_ids:
            fl = (act[:, k] == f) & (pidx[:, k] >= 0)
            share = trailing_mean(fl, w)
            report["max_share"]["a"] = max(report["max_share"]["a"], float(np.nanmax(share)))
            first, run = sustained(share > SHARE_BAR_A, d)
            if first is not None:
                report["fires"].append({"signal": "a", "seat": names[k],
                                        "family": ACTIVITIES[f],
                                        "tick": int(first), "episode": int(run)})

    # (b) mutual pair > SHARE_BAR_B of the trailing window, per unordered pair
    for i in range(roster):
        for j in range(i + 1, roster):
            mutual = (pidx[:, i] == j) & (pidx[:, j] == i)
            share = trailing_mean(mutual, w)
            report["max_share"]["b"] = max(report["max_share"]["b"], float(np.nanmax(share)))
            first, run = sustained(share > SHARE_BAR_B, d)
            if first is not None:
                report["fires"].append({"signal": "b", "pair": [names[i], names[j]],
                                        "tick": int(first), "episode": int(run)})

    # (c) need spread, report only
    spread = needs.max(2) - needs.min(2)                       # (T, K)
    ms = trailing_mean(spread, w)
    report["max_share"]["c"] = float(np.nanmax(ms))
    for k in range(roster):
        first, run = sustained(ms[:, k] > SPREAD_BAR, d)
        if first is not None:
            report["spread_flags"].append({"seat": names[k], "tick": int(first),
                                           "episode": int(run)})

    # Watchdog equivalent: first tick any distress streak reaches 150.
    wd = None
    for k in range(roster):
        for n in range(6):
            first, _ = sustained(dist[:, k, n], WATCHDOG_THRESHOLD)
            if first is not None and (wd is None or first < wd):
                wd = int(first)
    report["watchdog_tick"] = wd
    report["fires"].sort(key=lambda f: f["tick"])
    report["verdict"] = "FIRE" if report["fires"] else "silent"
    report["first_fire_tick"] = report["fires"][0]["tick"] if report["fires"] else None
    return report


def run_trace(path):
    z = np.load(path)
    sc = json.loads(Path(str(path)[:-4] + ".json").read_text())
    names = [k["name"] for k in sc["kitties"]]
    r = detect(z["states"], sc["roster"], names)
    r.update(trace=Path(path).stem, seating=sc["seating"], seed=sc["seed"])
    return r


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = run_trace(p)
        ff = r["fires"][0] if r["fires"] else None
        print(f"{r['trace']:36s} {r['verdict']:6s} first {r['first_fire_tick']} "
              f"watchdog {r['watchdog_tick']}  max a/b/c "
              f"{r['max_share']['a']:.2f}/{r['max_share']['b']:.2f}/{r['max_share']['c']:.0f}"
              + (f"  {ff}" if ff else ""))
