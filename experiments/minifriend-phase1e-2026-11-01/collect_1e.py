#!/usr/bin/env python3
"""Phase 1e — the late-grave training set's collection (DECLARATION.md
§3; runs only after the declaration is ruled, on her word).

TN<k>: `g2leg-20-N<k>.toml` (the needy set's arm N config, byte for
byte), 6,000 ticks; TE<k>: `g2leg-20-E<k>-n60.toml` (arm E's at the
pinned n), 1,000 ticks. Each world is covered_scout's call, world for
world: `g2-rot2` less seat k's network, seat k scripted on its config
behaviour, every covered observation saved, S1 = F-053's 1,000-tick
single-need streak armed on the covered seats only; any covered abort
saves what was collected, exits 3, and goes to her. Seeds and counts
from split.json (split_1e.py). Resumable; burn order TE then TN.

    collect_1e.py plan          # worlds, present, covered cat-ticks
    collect_1e.py run
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "needy-set-2026-10-28"))
sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
import covered_scout as CS  # noqa: E402  (SEATING, S1_STREAK; the needy set's collector call)

SPLIT = json.loads((HERE / "split.json").read_text())
SETS = [n for n in SPLIT["sets"] if n.startswith("TE")] + [n for n in SPLIT["sets"] if n.startswith("TN")]


def worlds():
    """[(set, seed, config, ticks, scripted_seat, out)] in burn order."""
    out = []
    for name in SETS:
        s = SPLIT["sets"][name]
        for seed in s["train"]:
            out.append((name, seed, EXPTS / s["config"], s["ticks"], s["scripted_seat"], EXPTS / s["raw_dir"] / f"streams-{seed}.npz"))
    return out


def plan():
    ws = worlds()
    by = {}
    for name, _seed, _cfg, ticks, _scr, out in ws:
        a = by.setdefault(name[:2], {"worlds": 0, "present": 0, "ticks": ticks, "covered_cat_ticks": 0})
        a["worlds"] += 1
        a["present"] += out.exists()
        a["covered_cat_ticks"] += 4 * ticks
    return {"seating": CS.SEATING, "s1_streak_covered_only": CS.S1_STREAK, "kinds": by, "worlds": len(ws),
            "covered_cat_ticks_total": sum(a["covered_cat_ticks"] for a in by.values()),
            "covered_cat_ticks_remaining": sum(4 * t for _n, _s, _c, t, _k, o in ws if not o.exists())}


def run():
    import torch
    import seating_collect_g2 as C
    torch.set_num_threads(1)
    ws = worlds()
    t0 = time.time()
    for i, (name, seed, cfg, ticks, scr, out) in enumerate(ws):
        if out.exists():
            print(f"[{i + 1}/{len(ws)}] {name} {seed}: present, skipped", flush=True)
            continue
        t1 = time.time()
        arrays, meta = C.collect(CS.SEATING, seed, ticks, CS.S1_STREAK, config=cfg, save_obs=True,
                                 scripted_seat=scr, abort_covered_only=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, meta=json.dumps(meta), **arrays)
        covered = [j for j, s in enumerate(meta["seats"]) if s != "scripted"]
        assert covered == [j for j in range(5) if j != scr] and meta["abort_seats"] == covered, meta["seats"]
        assert meta["needy_seat"] == scr, (name, meta["needy_seat"])
        hap = arrays["hap"][:, covered].mean()
        print(f"[{i + 1}/{len(ws)}] {name} {seed}: {meta['ticks']} ticks, covered mean happiness {hap:.2f}, "
              f"{time.time() - t1:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
        if meta["aborted_at"] is not None:
            print(f"== ABORT: covered seat at the S1 line in {name} {seed} at tick {meta['aborted_at']}; "
                  f"the collection stops here and goes to her (DECLARATION §10)", flush=True)
            sys.exit(3)
    print(f"== training set done: {len(ws)} worlds, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run"])
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(), indent=1))
    else:
        run()
