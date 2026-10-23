#!/usr/bin/env python3
"""Stratum occupancy per friend on the EVALUATION worlds (DECLARATION.md
§Strata and §Data: min-n 200 per friend × stratum × version, fail-closed;
G runs only if L + W leave any friend's GRAVE stratum under 200
mind-visible eval samples).

A sample is (observer k, friend j ≠ k, tick t): the observer's saved
observation obs[t] and the friend's TRUE state at that view, needs[t−1]
/ hap[t−1] (needs0 / hap0 at t = 0; see the declaration's alignment
note). Its stratum is strata.stratum on that true state. It is
MIND-VISIBLE when the friend's permanent row in the observer's
observation carries present = 1: schema 6 lays the self block (109) and
then FOUR friend rows of 58, the roster minus the observer ascending by
id (observe.rs, spec 049 FR-011), present at the row's cell 0. Seat
columns are config order = id order (Miso 1 … Clementine 5).

    count_strata.py --out strata-counts.json          # eval worlds of every set present
    count_strata.py --all-worlds                       # occupancy on every world (information only)

Arc root: split.json and results-raw/ come from MINIFRIEND_ARC when set
(Phase 1b), else from this directory (see phase1_data.py).
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARC = Path(os.environ.get("MINIFRIEND_ARC", HERE)).resolve()
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
import strata as S  # noqa: E402

SELF_BLOCK, KITTY_SLOT, PRESENT = 109, 58, 0
ROSTER = 5
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
MIN_N = 200
SPLIT = json.loads((ARC / "split.json").read_text())


def friend_row(observer, friend):
    """Row index of `friend` in `observer`'s observation (both seat/id indices)."""
    assert observer != friend
    return [j for j in range(ROSTER) if j != observer].index(friend)


def present_offset(observer, friend):
    return SELF_BLOCK + KITTY_SLOT * friend_row(observer, friend) + PRESENT


def truth_streams(z):
    """needs/hap aligned to obs[t]: the state the view was built from."""
    needs = np.concatenate([z["needs0"][None], z["needs"][:-1]])
    hap = np.concatenate([z["hap0"][None], z["hap"][:-1]])
    return needs, hap


def count_world(path):
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    assert meta["obs_recorded"] == [True] * ROSTER, meta["obs_recorded"]
    needs, hap = truth_streams(z)
    codes = S.stratum(needs, hap)                      # (T, 5) the friend's stratum per tick
    obs = z["obs"]
    out = {}
    for j in range(ROSTER):
        per = {n: {"all": 0, "visible": 0} for n in S.NAMES}
        for k in range(ROSTER):
            if k == j:
                continue
            vis = obs[:, k, present_offset(k, j)].astype(np.float32) > 0.5
            for i, n in enumerate(S.NAMES):
                m = codes[:, j] == i
                per[n]["all"] += int(m.sum())
                per[n]["visible"] += int((m & vis).sum())
        out[SEATS[j]] = per
    return meta["seed"], meta["ticks"], out


def merge(into, per):
    for f, d in per.items():
        for n, v in d.items():
            into.setdefault(f, {}).setdefault(n, {"all": 0, "visible": 0})
            into[f][n]["all"] += v["all"]
            into[f][n]["visible"] += v["visible"]


def select_sets(sets, requested=None):
    """The sets to count: every set in split.json, or only `requested` (each must exist). Used by
    Phase 1b, whose results-raw also holds Phase 1's L/W/G (symlinks) that its P read must not pool."""
    if requested is None:
        return dict(sets)
    missing = [n for n in requested if n not in sets]
    assert not missing, f"--sets names sets absent from split.json: {missing}"
    return {n: sets[n] for n in sets if n in requested}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ARC / "strata-counts.json")
    ap.add_argument("--all-worlds", action="store_true")
    ap.add_argument("--sets", nargs="+", default=None, help="count only these sets (default: every set present)")
    a = ap.parse_args()
    report = {"min_n": MIN_N, "split_seed": SPLIT["split_seed"], "sets": {}, "pooled_eval": {}}
    if a.sets:
        report["sets_requested"] = list(a.sets)
    pooled = {}
    for name, spec in select_sets(SPLIT["sets"], a.sets).items():
        d = ARC / "results-raw" / name
        worlds = sorted(int(p.stem.split("-")[1]) for p in d.glob("streams-*.npz")) if d.exists() else []
        if not worlds:
            continue
        chosen = worlds if a.all_worlds else [w for w in worlds if w in spec["eval"]]
        tot, per_world = {}, {}
        for w in chosen:
            seed, ticks, per = count_world(d / f"streams-{w}.npz")
            assert seed == w
            per_world[w] = {"ticks": ticks, "friends": per}
            merge(tot, per)
        if not a.all_worlds:
            assert set(chosen) == set(spec["eval"]) & set(worlds), (name, chosen, spec["eval"])
            merge(pooled, tot)
        report["sets"][name] = {"worlds_recorded": worlds, "worlds_counted": chosen, "per_world": per_world, "total": tot}
    if not a.all_worlds:
        report["pooled_eval"] = pooled
        report["grave_visible_under_min_n"] = {f: d["GRAVE"]["visible"] for f, d in pooled.items()
                                               if d["GRAVE"]["visible"] < MIN_N}
    a.out.write_text(json.dumps(report, indent=1))
    for name, s in report["sets"].items():
        print(f"{name}: worlds counted {s['worlds_counted']}")
        for f, d in s["total"].items():
            print(f"  {f:11s} " + "  ".join(f"{n} {d[n]['all']}/{d[n]['visible']}" for n in S.NAMES))
    if not a.all_worlds:
        print("pooled eval (all/visible):")
        for f, d in pooled.items():
            print(f"  {f:11s} " + "  ".join(f"{n} {d[n]['all']}/{d[n]['visible']}" for n in S.NAMES))
        print("GRAVE mind-visible under min-n 200:", report["grave_visible_under_min_n"])
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
