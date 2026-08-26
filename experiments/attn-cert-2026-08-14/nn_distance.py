#!/usr/bin/env python3
"""nn_distance.py -- nearest-neighbour distance census (the shakeout
clustering criterion, fog-gen1 timeline step 4).

Chebyshev is the engine's adjacency metric (a duet partner is cheb<=1);
Euclidean reported alongside. Baselines pinned 2026-08-26 off the live
roster: cheb median 1.0, mean ~1.9, p90 4-5, contact share 0.66-0.67
(banked ticks 145857-148134 and live 547416-547657 agree).

Usage:
  python3 nn_distance.py results-raw/live-census-145857.json   # banked raw
  python3 nn_distance.py --live [N] [INTERVAL_S]               # poll /world
"""
import json, sys, time, urllib.request, statistics as st

BASE = "https://kitties.ai"


def nn_from_positions(pos, include_self=False):
    """Per-cat nearest-neighbour (cheb, euc) for one snapshot of positions."""
    out = []
    for i, (x, y) in enumerate(pos):
        cands = [(a, b) for j, (a, b) in enumerate(pos) if include_self or j != i]
        if not cands:
            continue
        out.append((min(max(abs(x - a), abs(y - b)) for a, b in cands),
                    min(((x - a) ** 2 + (y - b) ** 2) ** .5 for a, b in cands)))
    return out


def stats(snapshots, include_self=False):
    cheb, euc = [], []
    for pos in snapshots:
        if len(pos) < 2:
            continue
        for dc, de in nn_from_positions(pos, include_self):
            cheb.append(dc); euc.append(de)
    n = len(cheb)
    return dict(samples=n,
                cheb_median=st.median(cheb), cheb_mean=round(st.fmean(cheb), 2),
                cheb_p90=sorted(cheb)[int(.9 * n)],
                euc_median=round(st.median(euc), 2),
                contact_share=round(sum(c <= 1 for c in cheb) / n, 3))


def positions_of(kitties):
    return [(k["pos"]["x"], k["pos"]["y"]) for k in kitties if "pos" in k]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        iv = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
        snaps, ticks = [], []
        for i in range(n):
            with urllib.request.urlopen(f"{BASE}/world", timeout=15) as r:
                w = json.load(r)
            ticks.append(w.get("tick"))
            snaps.append(positions_of(w.get("kitties") or []))
            if i < n - 1:
                time.sleep(iv)
        print(json.dumps(dict(tick_range=[ticks[0], ticks[-1]], **stats(snaps))))
    else:
        d = json.load(open(sys.argv[1]))
        polls = d.get("raw_polls") or d.get("polls") or []
        print(json.dumps(stats([positions_of(p.get("kitties") or []) for p in polls])))
