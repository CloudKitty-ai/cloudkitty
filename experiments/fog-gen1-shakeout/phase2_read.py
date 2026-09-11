#!/usr/bin/env python3
"""Part B phase-2 companion reads (PREREG: responder-approach and
cosleep-on-beam; no gate hangs on either).

    phase2_read.py PROBE_NPZ [--window 10] [--announce 20] [--out FILE]

Both reads run on a probe npz's per-decision rows (partb_read's frame
conventions). Positions are each cat's own self-pos row, so distances
are true world distances; "Seen" and the row bits are the observer's
obs, per the probe-1-verified geometry (A3/A15).

Responder-approach (per listener seat, per word want_cuddle/want_play):
events where a speaker emits the word while NOT in the listener's view;
approach = the listener's Euclidean distance to the speaker falls by
>= 2 within the window. Uptake (scene starts with that speaker) needs
scene spans and is not read here.

Cosleep-on-beam (per seat): of ticks where a settled friend (resting or
sleeping one-hot) on a sunbeam (row sunbeam bit) is Seen while the
seat's own sleep need is at or above the announce threshold, the share
where the seat closes distance to that friend by >= 1 within the
window. The scene-start half of the ruled read needs spans; not here.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
from partb_read import W, rows_by_seed  # noqa: E402

MSG_WANT_PLAY, MSG_WANT_CUDDLE = 4, 5
KITTY_BASE = dict(L.WIDTHS)["self"]
KITTY_W = dict(L.WIDTHS)["kitty"]
ROW_SUNBEAM = 21  # kitty-row on-sunbeam bit (049 ruling 2026-09-04)


def per_tick(rows):
    """(kitty_ids, pos[T,K,2], present[T,K,K], settled_on_beam[T,K,K],
    said[T,K], sleep_need[T,K]) with row axis ordered by kitty id.
    present[t, i, j] = observer i sees kitty j (j != i)."""
    ticks, kitties = rows["tick"], rows["kitty"]
    ids = np.unique(kitties)
    K, T = len(ids), len(np.unique(ticks))
    obs, msg = rows["obs"], rows["msg"]
    pos = np.zeros((T, K, 2))
    said = np.zeros((T, K), int)
    sleep = np.zeros((T, K))
    present = np.zeros((T, K, K), bool)
    beamset = np.zeros((T, K, K), bool)
    tix = {t: n for n, t in enumerate(np.unique(ticks))}
    kix = {k: n for n, k in enumerate(ids)}
    for r in range(len(ticks)):
        t, i = tix[ticks[r]], kix[kitties[r]]
        row = obs[r]
        pos[t, i] = np.round(row[L.SELF_POS:L.SELF_POS + 2] * W)
        said[t, i] = msg[r]
        sleep[t, i] = row[L.SELF_NEEDS + 2] * 100
        others = [k for k in ids if k != kitties[r]]
        for slot, oid in enumerate(others):
            b = KITTY_BASE + slot * KITTY_W
            j = kix[oid]
            if row[b + L.ROW_PRESENT] > 0:
                present[t, i, j] = True
                act = row[b + L.ROW_ACTIVITY:b + L.ROW_ACTIVITY + 7]
                settled = act[1] > 0 or act[2] > 0  # resting or sleeping
                beamset[t, i, j] = settled and row[b + ROW_SUNBEAM] > 0
    return ids, pos, present, beamset, said, sleep


def approach_events(pos, present, said, window, msg_index):
    """(events, approaches): unseen-speaker word events per listener and
    how many saw the listener close >= 2 Euclidean within the window."""
    T, K = said.shape
    events = approaches = 0
    for t in range(T - 1):
        for s in range(K):
            if said[t, s] != msg_index:
                continue
            for li in range(K):
                if li == s or present[t, li, s]:
                    continue
                d0 = float(np.hypot(*(pos[t, li] - pos[t, s])))
                events += 1
                end = min(T, t + 1 + window)
                dmin = min(float(np.hypot(*(pos[u, li] - pos[u, s])))
                           for u in range(t + 1, end))
                if d0 - dmin >= 2.0:
                    approaches += 1
    return events, approaches


def cosleep_approach(pos, present, beamset, sleep, announce, window):
    """(opportunity ticks, closed): ticks with a Seen settled friend on
    a beam while own sleep >= announce; closed if distance to that
    friend falls >= 1 within the window."""
    T, K = sleep.shape
    opps = closed = 0
    for t in range(T - 1):
        for i in range(K):
            if sleep[t, i] < announce:
                continue
            for j in range(K):
                if j == i or not beamset[t, i, j]:
                    continue
                opps += 1
                d0 = float(np.hypot(*(pos[t, i] - pos[t, j])))
                end = min(T, t + 1 + window)
                dmin = min(float(np.hypot(*(pos[u, i] - pos[u, j])))
                           for u in range(t + 1, end))
                if d0 - dmin >= 1.0:
                    closed += 1
                break  # one opportunity per (tick, seat)
    return opps, closed


def read_npz(path, window, announce):
    out = []
    for seed, rows in sorted(rows_by_seed(np.load(path)).items()):
        ids, pos, present, beamset, said, sleep = per_tick(rows)
        res = {"seed": seed}
        for name, ix in (("want_play", MSG_WANT_PLAY),
                         ("want_cuddle", MSG_WANT_CUDDLE)):
            ev, ap = approach_events(pos, present, said, window, ix)
            res[name] = {"unseen_speaker_events": ev, "approaches": ap}
        opps, closed = cosleep_approach(pos, present, beamset, sleep,
                                        announce, window)
        res["cosleep"] = {"beam_opportunity_ticks": opps, "closed": closed}
        out.append(res)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", type=Path)
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--announce", type=float, default=20.0)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = read_npz(args.probe, args.window, args.announce)
    print(json.dumps(rows, indent=1))
    if args.out:
        args.out.write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
