#!/usr/bin/env python3
"""Fog Gen 1 radius screen readout (PREREG Part C, owner ruled 2026-09-03):
the scripted anchor's welfare curve over `[vision] radius`, read off
bc-collect --trace rollouts.

    radius_screen.py ROLLOUT_DIR [ROLLOUT_DIR ...] [--out FILE]

Per rollout, from the per-tick snapshots (rates per 1,000 ticks):
  watchdog entries   distress episodes (need >= thresholds.distress,
                     contiguous) whose age reached the watchdog threshold
                     (150); distress episodes of any length; max age
  eat / drink max    highest value the need reached on any cat-tick
  safeguard          upward crossings of thresholds.safeguard per need
  blind-hungry span  cat-ticks with eat >= announce_threshold, no stocked
                     chow inside the disc and no chow memory (the ratified
                     blind price is what the cat is paying then); spans are
                     contiguous runs per cat: count, mean, max. Blind-thirsty
                     is the water analogue
  dispersion         nearest-neighbour Euclidean median and contact share
                     (nn_distance.stats)
  friend in view     share of cat-ticks with another kitty inside the disc

Streams trace.jsonl (a 20k trace is ~160 MB); reads the radius from
meta.json and the thresholds from the recorded config. Run from the repo
root with the exp-006 venv.
"""
import argparse
import json
import statistics
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-cert-2026-08-14"))
sys.path.insert(2, str(HERE.parent / "attn-oracle-2026-08-15"))

from nn_distance import stats as nn_stats  # noqa: E402
from obs_layout_v5 import ELEMENT_KINDS  # noqa: E402
from schema_check import elements_of, stocked, visible  # noqa: E402

WATCHDOG_THRESHOLD = 150
BLIND = {"eat": "chow", "drink": "water"}


def stream_snapshots(rollout_dir):
    with open(Path(rollout_dir) / "trace.jsonl") as f:
        for line in f:
            yield json.loads(line)["snapshot"]


def blind(kitty, snap, r, kind):
    """No stocked element of `kind` inside the disc and no memory of one."""
    if kitty["memory"][ELEMENT_KINDS.index(kind)] is not None:
        return False
    return not any(stocked(e) and visible(kitty["pos"], e["pos"], r)
                   for e in elements_of(snap, kind))


def spans(flags):
    """Lengths of the contiguous True runs."""
    out, run = [], 0
    for f in flags:
        if f:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def screen(snapshots, r, distress, safeguard, announce):
    """The measures over an iterable of snapshots (one per tick)."""
    needs_seen = None
    above_d = {}        # (kitty, need) -> current distress run length
    episodes = {}       # (kitty, need) -> finished run lengths
    above_s = set()     # (kitty, need) currently >= safeguard
    crossings = {}
    maxes = {}
    blind_flags = {k: {} for k in BLIND}   # need -> kitty -> [bool per tick]
    friend_ticks, cat_ticks, positions = 0, 0, []
    n = 0
    for snap in snapshots:
        n += 1
        kitties = snap["kitties"]
        positions.append([(k["pos"]["x"], k["pos"]["y"]) for k in kitties])
        for k in kitties:
            kid = k["id"]
            if needs_seen is None:
                needs_seen = sorted(k["needs"])
            for need, v in k["needs"].items():
                key = (kid, need)
                maxes[need] = max(maxes.get(need, 0.0), v)
                if v >= distress:
                    above_d[key] = above_d.get(key, 0) + 1
                elif key in above_d:
                    episodes.setdefault(key, []).append(above_d.pop(key))
                if v >= safeguard:
                    if key not in above_s:
                        above_s.add(key)
                        crossings[need] = crossings.get(need, 0) + 1
                else:
                    above_s.discard(key)
            for need, kind in BLIND.items():
                blind_flags[need].setdefault(kid, []).append(
                    k["needs"][need] >= announce and blind(k, snap, r, kind))
            cat_ticks += 1
            friend_ticks += any(o["id"] != kid and visible(k["pos"], o["pos"], r)
                                for o in kitties)
    for key, run in above_d.items():        # runs still open at the end
        episodes.setdefault(key, []).append(run)
    all_eps = [e for eps in episodes.values() for e in eps]
    per_k = 1000.0 / n
    wd = sum(e >= WATCHDOG_THRESHOLD for e in all_eps)
    out = {
        "ticks": n, "radius": r,
        "watchdog_entries": wd,
        "watchdog_entries_per_1k": wd * per_k,
        "distress_episodes_per_1k": len(all_eps) * per_k,
        "max_distress_age": max(all_eps, default=0),
        "need_max": {k: round(v, 2) for k, v in maxes.items()},
        "safeguard_crossings_per_1k": {k: crossings.get(k, 0) * per_k
                                       for k in (needs_seen or [])},
        "friend_in_view_share": friend_ticks / max(cat_ticks, 1),
        "dispersion": nn_stats(positions),
    }
    for need in BLIND:
        runs = [s for flags in blind_flags[need].values() for s in spans(flags)]
        out[f"blind_{need}"] = {
            "cat_ticks_per_1k": sum(runs) * per_k,
            "spans": len(runs),
            "span_mean": statistics.fmean(runs) if runs else 0.0,
            "span_max": max(runs, default=0),
        }
    return out


def read_rollout(d):
    d = Path(d)
    meta = json.loads((d / "meta.json").read_text())
    assert meta.get("trace"), f"{d} was not recorded with --trace"
    with open(meta["config"], "rb") as f:
        cfg = tomllib.load(f)
    res = screen(stream_snapshots(d), int(meta["vision_radius"]),
                 cfg["thresholds"]["distress"], cfg["thresholds"]["safeguard"],
                 cfg["meow"]["announce_threshold"])
    res.update({"rollout": str(d), "world_seed": meta["world_seed"],
                "config": meta["config"], "config_sha256": meta["config_sha256"]})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rollouts", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = [read_rollout(d) for d in args.rollouts]
    print(f"{'radius':>6}{'seed':>8}{'wd':>4}{'dist/1k':>8}{'maxage':>7}"
          f"{'eatmax':>7}{'drkmax':>7}{'sg-eat':>7}{'sg-drk':>7}"
          f"{'blindH':>7}{'bHmax':>6}{'blindT':>7}{'nn-euc':>7}{'friend':>7}")
    for x in rows:
        print(f"{x['radius']:>6}{x['world_seed']:>8}{x['watchdog_entries']:>4}"
              f"{x['distress_episodes_per_1k']:>8.2f}{x['max_distress_age']:>7}"
              f"{x['need_max']['eat']:>7.1f}{x['need_max']['drink']:>7.1f}"
              f"{x['safeguard_crossings_per_1k']['eat']:>7.2f}"
              f"{x['safeguard_crossings_per_1k']['drink']:>7.2f}"
              f"{x['blind_eat']['cat_ticks_per_1k']:>7.1f}{x['blind_eat']['span_max']:>6}"
              f"{x['blind_drink']['cat_ticks_per_1k']:>7.1f}"
              f"{x['dispersion']['euc_median']:>7.2f}{x['friend_in_view_share']:>7.3f}")
    if args.out:
        args.out.write_text(json.dumps(rows, indent=2) + "\n")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
