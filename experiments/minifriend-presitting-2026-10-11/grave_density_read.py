#!/usr/bin/env python3
"""Grave-encounter density at scripted collection density.

Pre-sitting read 1 for the banked approach-propensity differential
(Professor relay 2026-10-10): does LIVED rollout data power a
matched-control approach read, or does it starve? Over every bc-corpus
rollout of the fog-gen1 shakeout (scripted roster, schema 5), per need
kind and severity threshold, how many kitty-ticks sit above the
threshold, how many of those are SIGNALLING (own matching want-call
audible under the 30-tick digest window), how many potential-observer
encounters that yields per Manhattan distance band, and how thin the
matched-control cells get per 20k-tick rollout.

Severity thresholds (need scale /100): >= 90 is the engine distress
line (`distress = 90.0` in the shakeout anchor.toml); 45 and 70 are
read-time choices borrowing the ruled semantic-edge numbers
(happiness 45/70), which the ruling pins for happiness, not need
pressure. Distance bands [0-4]/[5-8]/[9+] are read-time
choices: <= 4 proxies the collector's vision_radius = 4.

    grave_density_read.py [--out OUT.json]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "experiments/fog-gen1-shakeout/results-raw/bc-corpus"
WINDOW = 30  # digest_window_ticks in the shakeout anchor.toml
PK = 32  # global-state v1 per-kitty block width
NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]  # NeedKind::ALL
# label_msg index of each need's want-call (HEAD_KINDS order, 0 = silent):
WANT_IDX = {"eat": 1, "drink": 2, "sleep": 8, "play": 4, "cuddle": 5, "bath": 7}
THRESHOLDS = [0.45, 0.70, 0.90]
DIST_BANDS = [(0, 4), (5, 8), (9, 99)]


def band_of(d):
    for lo, hi in DIST_BANDS:
        if lo <= d <= hi:
            return f"{lo}-{hi}" if hi < 99 else f"{lo}+"
    raise AssertionError(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    rollouts = sorted({p.parent.resolve() for p in CORPUS.rglob("label_msg.npy")})
    total_ticks = 0
    roster = None
    tot = defaultdict(lambda: defaultdict(int))
    # per-rollout treatment-cell counts, keyed (need, thr, dist_band, obs_hot)
    per_rollout_cells = defaultdict(list)
    episodes = defaultdict(int)  # (need, thr) -> runs above thr
    for rd in rollouts:
        meta = json.load(open(rd / "meta.json"))
        assert meta["observation_schema"] == 5
        ticks = meta["ticks"]
        total_ticks += ticks
        state = np.load(rd / "state.npy")
        roster = len(meta["experts"])
        assert state.shape[1] == roster * PK + 37
        tick = np.load(rd / "tick.npy")
        kitty = np.load(rd / "kitty.npy")
        msg = np.load(rd / "label_msg.npy")
        kitty_ids = sorted(int(k) for k in meta["experts"])  # state block order

        needs = np.stack([state[:, i * PK : i * PK + 6] for i in range(roster)], axis=1)
        pos = np.stack(
            [np.round(state[:, i * PK + 7 : i * PK + 9] * 20).astype(int) for i in range(roster)],
            axis=1,
        )  # (T, roster, 2)
        # audibility mask per (kitty block index, need): emitted matching
        # want-call within the last WINDOW ticks
        aud = np.zeros((ticks, roster, 6), bool)
        for bi, kid in enumerate(kitty_ids):
            for ni, need in enumerate(NEEDS):
                sel = (kitty == kid) & (msg == WANT_IDX[need])
                m = np.zeros(ticks + WINDOW, bool)
                for t in tick[sel]:
                    m[t : t + WINDOW] = True
                aud[:, bi, ni] = m[:ticks]

        cells = defaultdict(int)
        for ni, need in enumerate(NEEDS):
            lvl = needs[:, :, ni]  # (T, roster)
            for thr in THRESHOLDS:
                above = lvl >= thr
                key = (need, thr)
                tot[key]["kitty_ticks"] += int(above.sum())
                d = np.diff(above.astype(np.int8), axis=0)
                episodes[key] += int((d == 1).sum()) + int(above[0].sum())
                sig = above & aud[:, :, ni]
                tot[key]["signalling_ticks"] += int(sig.sum())
                ts, ks = np.nonzero(sig)
                for t, k in zip(ts, ks):
                    for j in range(roster):
                        if j == k:
                            continue
                        dist = int(np.abs(pos[t, j] - pos[t, k]).sum())
                        db = band_of(dist)
                        tot[key][f"enc_{db}"] += 1
                        hot = bool((needs[t, j] >= 0.70).any())
                        cells[(need, thr, db, hot)] += 1
        for ck, v in cells.items():
            per_rollout_cells[ck].append(v)

    n_roll = len(rollouts)
    out = {
        "rollouts": n_roll,
        "total_world_ticks": total_ticks,
        "roster": roster,
        "window_ticks": WINDOW,
        "thresholds": THRESHOLDS,
        "needs": {},
    }
    kt_total = total_ticks * roster
    for need in NEEDS:
        out["needs"][need] = {}
        for thr in THRESHOLDS:
            key = (need, thr)
            d = tot[key]
            kt = d["kitty_ticks"]
            entry = {
                "kitty_ticks_above": kt,
                "pct_of_kitty_ticks": round(100 * kt / kt_total, 3),
                "episodes": episodes[key],
                "signalling_ticks": d["signalling_ticks"],
                "signalling_share_pct": round(100 * d["signalling_ticks"] / kt, 2) if kt else None,
                "encounters_per_band": {},
                "treatment_cells_per_rollout": {},
            }
            for lo, hi in DIST_BANDS:
                db = f"{lo}-{hi}" if hi < 99 else f"{lo}+"
                entry["encounters_per_band"][db] = d[f"enc_{db}"]
                for hot in (False, True):
                    v = per_rollout_cells.get((need, thr, db, hot), [])
                    v = v + [0] * (n_roll - len(v))
                    entry["treatment_cells_per_rollout"][f"{db}|obs_hot={hot}"] = {
                        "total": int(sum(v)),
                        "median": float(np.median(v)),
                        "min": int(min(v)),
                        "rollouts_nonzero": int(sum(1 for x in v if x > 0)),
                    }
            out["needs"][need][str(thr)] = entry
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
