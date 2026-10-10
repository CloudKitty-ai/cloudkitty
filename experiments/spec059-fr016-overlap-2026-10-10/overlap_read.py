#!/usr/bin/env python3
"""Same-kind want-call overlap at scripted collection density.

Decision input for spec 059 FR-016 (the commitment margin question):
over every bc-corpus rollout of the fog-gen1 shakeout (scripted roster,
schema 5), per want kind, how often two calls from DISTINCT callers are
co-audible under the 30-tick digest window, and how often a fresh
distinct-caller same-kind call lands within a walk after an emission —
the mid-answer-challenger event a commitment margin exists for.

No feasibility or intensity screen is applied: every count is an UPPER
BOUND on margin-relevant events (a challenger must also win
`intensity − k·d` to flip anything).

    overlap_read.py [--out OUT.json]
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "experiments/fog-gen1-shakeout/results-raw/bc-corpus"
WINDOW = 30  # digest_window_ticks in the shakeout anchor.toml
WALK = 15  # generous answer-walk length, ticks (20x20 Manhattan)
KINDS = {4: "want_play", 5: "want_cuddle"}  # label_msg index (HEAD_KINDS[k-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    rollouts = sorted({p.parent.resolve() for p in CORPUS.rglob("label_msg.npy")})
    tot = defaultdict(lambda: defaultdict(int))
    total_ticks = 0
    expert_mixes = Counter()
    min_gap = {name: None for name in KINDS.values()}
    for rd in rollouts:
        meta = json.load(open(rd / "meta.json"))
        assert meta["observation_schema"] == 5
        expert_mixes[tuple(sorted(meta["experts"].values()))] += 1
        ticks = meta["ticks"]
        total_ticks += ticks
        tick = np.load(rd / "tick.npy")
        kitty = np.load(rd / "kitty.npy")
        msg = np.load(rd / "label_msg.npy")
        for idx, name in KINDS.items():
            sel = msg == idx
            ev_t, ev_k = tick[sel], kitty[sel]
            order = np.argsort(ev_t, kind="stable")
            ev_t, ev_k = ev_t[order], ev_k[order]
            n = len(ev_t)
            tot[name]["emissions"] += n
            masks = {}
            for k in np.unique(ev_k):
                m = np.zeros(ticks + WINDOW, bool)
                kt = ev_t[ev_k == k]
                for t in kt:
                    m[t : t + WINDOW] = True
                masks[k] = m
                if len(kt) > 1:
                    g = int(np.diff(np.sort(kt)).min())
                    if min_gap[name] is None or g < min_gap[name]:
                        min_gap[name] = g
                d = np.diff(m.astype(np.int8))
                tot[name]["episodes"] += int((d == 1).sum()) + int(m[0])
            audible = sum(m.astype(np.int16) for m in masks.values())
            if isinstance(audible, np.ndarray):
                tot[name]["ticks_ge1"] += int((audible[:ticks] >= 1).sum())
                tot[name]["ticks_ge2"] += int((audible[:ticks] >= 2).sum())
            starts = {
                k: np.where(np.diff(np.concatenate([[False], m]).astype(np.int8)) == 1)[0]
                for k, m in masks.items()
            }
            for i in range(n):
                t, k = ev_t[i], ev_k[i]
                already = any(k2 != k and m2[t] for k2, m2 in masks.items())
                tot[name]["coaudible_at_emit"] += int(already)
                fresh = any(
                    k2 != k and not masks[k2][t] and ((st > t) & (st <= t + WALK)).any()
                    for k2, st in starts.items()
                )
                tot[name]["fresh_challenger"] += int(fresh)

    out = {
        "rollouts": len(rollouts),
        "total_world_ticks": total_ticks,
        "window_ticks": WINDOW,
        "walk_ticks": WALK,
        "expert_mixes": {" + ".join(k): v for k, v in expert_mixes.items()},
        "min_emission_gap": min_gap,
        "kinds": {},
    }
    for name, d in tot.items():
        n = d["emissions"]
        out["kinds"][name] = {
            "emissions": n,
            "episodes": d["episodes"],
            "episodes_per_1k_ticks_roster": round(1000 * d["episodes"] / total_ticks, 2),
            "ticks_ge1_pct": round(100 * d["ticks_ge1"] / total_ticks, 2),
            "ticks_ge2_pct": round(100 * d["ticks_ge2"] / total_ticks, 3),
            "overlap_share_of_audible_pct": round(100 * d["ticks_ge2"] / d["ticks_ge1"], 2),
            "coaudible_at_emit_pct": round(100 * d["coaudible_at_emit"] / n, 2),
            "fresh_challenger_pct": round(100 * d["fresh_challenger"] / n, 2),
        }
    print(json.dumps(out, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
