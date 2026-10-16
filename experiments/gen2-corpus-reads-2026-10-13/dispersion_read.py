#!/usr/bin/env python3
"""Starting-dispersion instrument (owner 2026-10-15: "let's collect
starting dispersion data so we can correlate that with early stage
welfare data (and see if it impacts long-term dispersion and
welfare)"): per rollout, the tick-0 roster geometry, early- and
late-window welfare, and whole-trace dispersion — plus rank
correlations of the start metrics against everything downstream, so a
per-seed start draw's effect is weighable instead of argued about.

Positions and welfare come from the collector's global state
(`state.npy`, ground truth): per-kitty block keyed by global-state
version via coverage_read.infer_block (one home); happiness at block
offset 6, distress flags at 20..26 — the prefix both versions share
(global_state.rs). Distances are Manhattan (the walk cost — house
rule); mutual visibility uses the meta's vision_radius on the
EUCLIDEAN disc, the engine's sight rule.

Per rollout:
  start_mean_pairwise / start_min_pairwise  tick-0 Manhattan distances
  start_visible_pairs                       tick-0 mutually visible pairs
  early_happiness / early_distress_share    mean over ticks [0, E)
  late_happiness / late_distress_share      mean over the last E ticks
  trace_mean_pairwise                       whole-trace mean dispersion

Across rollouts (n >= 5, else reported as n/a): Spearman rank
correlation of each start metric against each downstream metric —
rank-based on purpose; nothing here assumes linearity.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-corpus-reads-2026-10-13/dispersion_read.py \\
        label=path [...] [--early 2000] [--config TOML] [--out OUT.json]

Guard: test_dispersion_read.py.
"""
import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from coverage_read import infer_block, rollout_dirs, world_size  # noqa: E402

HAP_OFF, DIST_OFF, N_DIST = 6, 20, 6   # global_state.rs shared prefix
POS_OFF = 7
MIN_N_FOR_CORRELATION = 5
START_METRICS = ("start_mean_pairwise", "start_min_pairwise", "start_visible_pairs")
DOWNSTREAM = ("early_happiness", "early_distress_share",
              "late_happiness", "late_distress_share",
              "trace_mean_pairwise", "trace_happiness")


def positions(state, pk, roster, w, h):
    """[ticks, roster, 2] integer tiles from the global state."""
    x = np.round(state[:, [i * pk + POS_OFF for i in range(roster)]] * w)
    y = np.round(state[:, [i * pk + POS_OFF + 1 for i in range(roster)]] * h)
    return np.stack([x, y], axis=2).astype(int)


def pairwise_manhattan(pos_t):
    """Mean and min pairwise Manhattan distance for one tick's roster."""
    ds = [abs(a[0] - b[0]) + abs(a[1] - b[1])
          for a, b in combinations(pos_t.tolist(), 2)]
    return float(np.mean(ds)), float(min(ds))


def visible_pairs(pos_t, radius):
    """Mutually visible pairs on the engine's Euclidean disc."""
    n = 0
    for a, b in combinations(pos_t.tolist(), 2):
        n += (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 <= radius * radius
    return n


def max_streaks(dist_any):
    """Per kitty, the longest run of consecutive any-flag distress
    ticks — the F-053 line's own quantity."""
    out = []
    for k in range(dist_any.shape[1]):
        best = cur = 0
        for v in dist_any[:, k]:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        out.append(int(best))
    return out


def read_rollout(rd, early, config_override=None, block=None):
    rd = Path(rd)
    meta = json.load(open(rd / "meta.json"))
    w, h = world_size(meta, config_override)
    roster = len(meta["experts"])
    radius = int(meta["vision_radius"])
    state = np.load(rd / "state.npy")
    _ver, pk, _k = infer_block(state.shape[1], roster)
    ticks = state.shape[0]
    e = min(early, ticks)
    pos = positions(state, pk, roster, w, h)
    hap = state[:, [i * pk + HAP_OFF for i in range(roster)]] * 100.0
    dist_any = np.stack(
        [(state[:, i * pk + DIST_OFF:i * pk + DIST_OFF + N_DIST] > 0).any(1)
         for i in range(roster)], axis=1)
    start_mean, start_min = pairwise_manhattan(pos[0])
    trace_means = [pairwise_manhattan(pos[t])[0] for t in range(ticks)]
    extra = {}
    if block:
        extra["block_ticks"] = int(block)
        extra["block_happiness"] = [
            round(float(hap[i:i + block].mean()), 2)
            for i in range(0, ticks, block)]
        extra["max_distress_streaks"] = max_streaks(dist_any)
    return {
        **extra,
        "dir": str(rd), "ticks": ticks, "roster": roster,
        "world": [w, h], "vision_radius": radius, "early_window": e,
        "start_mean_pairwise": start_mean,
        "start_min_pairwise": start_min,
        "start_visible_pairs": visible_pairs(pos[0], radius),
        "early_happiness": float(hap[:e].mean()),
        "early_distress_share": float(dist_any[:e].mean()),
        "late_happiness": float(hap[-e:].mean()),
        "late_distress_share": float(dist_any[-e:].mean()),
        "trace_mean_pairwise": float(np.mean(trace_means)),
        "trace_happiness": float(hap.mean()),
    }


def spearman(xs, ys):
    """Rank correlation by hand (no scipy in the lab venv's contract):
    Pearson on average ranks; None when either side is constant."""
    def ranks(v):
        v = np.asarray(v, float)
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        r[order] = np.arange(1, len(v) + 1, dtype=float)
        for u in np.unique(v):
            m = v == u
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r
    rx, ry = ranks(xs), ranks(ys)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return None
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def correlations(rollouts):
    n = len(rollouts)
    if n < MIN_N_FOR_CORRELATION:
        return {"n": n, "note": f"n < {MIN_N_FOR_CORRELATION}: correlations "
                                "not computed; per-rollout rows carry the data"}
    out = {"n": n}
    for s in START_METRICS:
        xs = [r[s] for r in rollouts]
        out[s] = {d: spearman(xs, [r[d] for r in rollouts]) for d in DOWNSTREAM}
    return out


def read_source(label, path, early, config_override=None, block=None):
    rollouts = [read_rollout(rd, early, config_override, block)
                for rd in rollout_dirs(path)]
    return {"source": label, "path": str(path), "rollouts": rollouts,
            "spearman": correlations(rollouts)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+", metavar="label=path")
    ap.add_argument("--early", type=int, default=2000,
                    help="early/late window in ticks (default 2000)")
    ap.add_argument("--block", type=int, default=None,
                    help="also report mean happiness per BLOCK ticks and "
                         "per-kitty max distress streaks (trajectory read "
                         "for flag A/Bs and convergence checks)")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    out = []
    for s in a.sources:
        label, _, path = s.partition("=")
        if not path:
            raise SystemExit(f"dispersion_read: source {s!r} is not label=path")
        r = read_source(label, path, a.early, a.config, a.block)
        out.append(r)
        print(f"{r['source']}: {len(r['rollouts'])} rollouts")
        for ro in r["rollouts"]:
            print(f"  {Path(ro['dir']).name}: start mean/min "
                  f"{ro['start_mean_pairwise']:.1f}/{ro['start_min_pairwise']:.0f} "
                  f"visible-pairs {ro['start_visible_pairs']} | early hap "
                  f"{ro['early_happiness']:.2f} distress {ro['early_distress_share']:.4f} "
                  f"| late hap {ro['late_happiness']:.2f} | trace disp "
                  f"{ro['trace_mean_pairwise']:.1f}")
            if "block_happiness" in ro:
                print(f"    hap per {ro['block_ticks']}: "
                      + " ".join(f"{b:.1f}" for b in ro["block_happiness"])
                      + f" | max streaks {ro['max_distress_streaks']}")
        sp = r["spearman"]
        if "note" in sp:
            print(f"  spearman: {sp['note']}")
        else:
            for s_m in START_METRICS:
                row = " ".join(f"{d}={sp[s_m][d] if sp[s_m][d] is None else format(sp[s_m][d], '+.2f')}"
                               for d in DOWNSTREAM)
                print(f"  spearman {s_m}: {row}")
    if a.out:
        a.out.write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    main()
