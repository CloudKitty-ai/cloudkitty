#!/usr/bin/env python3
"""Sets P1..P5: per-world provenance and welfare check (DECLARATION.md
§Welfare; the Phase 1 check_set.py rule, per-kitty). Every recorded
world must carry the certified seating on its set's own config (sha equal
to the toml beside this file, arc binding), the grave kitty's reset needs
inside {60, 95} and varying, the OTHER FOUR kitties' reset needs exactly
the served default (every need 0, happiness 100), observations for all
five seats, and either the full 4,000 ticks or a recorded abort. Aborts
and the worst single-need distress streak per cat are reported; ANY
abort (the F-053 line, streak 1000) stops the set and goes to the owner —
the scouts (one world per friend) are read with this script before the
rest are launched.

    check_P.py            # every P set with a recorded world → P-check.json
    check_P.py 3          # one set
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
sys.path.insert(0, str(PHASE1))
from check_set import ENGINE, SEATS, longest_streaks  # noqa: E402

LO, HI, TICKS = 60.0, 95.0, 4000


def check_world(path, k, cfg_sha):
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    assert meta["seating"] == "g2-rot2", meta["seating"]
    assert meta["config"] == f"g2leg-20-P{k}.toml" and meta["provenance"]["config_sha256"] == cfg_sha, \
        (meta["config"], meta["provenance"]["config_sha256"][:8])
    assert meta["provenance"]["binding_engine"] == ENGINE, meta["provenance"]["binding_engine"]
    assert meta["abort_streak"] == 1000 and meta["requested_ticks"] == TICKS, (meta["abort_streak"], meta["requested_ticks"])
    assert meta["obs_recorded"] == [True] * 5
    n0, h0 = z["needs0"], z["hap0"]
    assert n0.shape == (5, 6)
    g = n0[k - 1]
    assert (g >= LO - 1e-3).all() and (g <= HI + 1e-3).all(), (path.name, g.round(1).tolist())
    assert np.ptp(g) > 1.0, "the grave kitty's reset needs did not vary: the entry did not take"
    others = np.delete(n0, k - 1, axis=0)
    assert (others == 0).all() and (np.delete(h0, k - 1) == 100).all(), (path.name, "a non-grave kitty left the served default")
    aborted = meta["aborted_at"]
    assert (aborted is None and meta["ticks"] == TICKS) or (aborted is not None and meta["ticks"] == aborted), \
        (meta["ticks"], aborted)
    assert z["obs"].shape == (meta["ticks"], 5, 399), z["obs"].shape
    return {"seed": meta["seed"], "ticks": meta["ticks"], "aborted_at": aborted, "grave_kitty": SEATS[k - 1],
            "needs0": n0.round(2).tolist(), "hap0": h0.round(2).tolist(),
            "longest_streak": longest_streaks(z["distress"]),
            "distress_ticks": (z["distress"] > 0).sum(0).tolist(),
            "mean_happiness": z["hap"].astype(np.float64).mean(0).round(3).tolist()}


def check_set(k):
    cfg = HERE / f"g2leg-20-P{k}.toml"
    sha = hashlib.sha256(cfg.read_bytes()).hexdigest()
    d = HERE / "results-raw" / f"P{k}"
    seeds = sorted(int(p.stem.split("-")[1]) for p in d.glob("streams-*.npz")) if d.exists() else []
    res = [check_world(d / f"streams-{s}.npz", k, sha) for s in seeds]
    aborts = [r["seed"] for r in res if r["aborted_at"] is not None]
    worst = max((max(r["longest_streak"]) for r in res), default=0)
    return {"set": f"P{k}", "grave_kitty": SEATS[k - 1], "config_sha256": sha, "engine": ENGINE,
            "worlds": res, "aborts": aborts, "worst_streak": worst}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("k", nargs="*", type=int, default=[1, 2, 3, 4, 5])
    ap.add_argument("--out", type=Path, default=HERE / "P-check.json")
    a = ap.parse_args()
    sets = {f"P{k}": check_set(k) for k in a.k}
    sets = {n: s for n, s in sets.items() if s["worlds"]}
    assert sets, "no P world recorded"
    aborts = {n: s["aborts"] for n, s in sets.items() if s["aborts"]}
    worst = max(s["worst_streak"] for s in sets.values())
    a.out.write_text(json.dumps({"sets": sets, "aborts": aborts, "worst_streak": worst}, indent=1))
    for n, s in sets.items():
        for r in s["worlds"]:
            print(f"{n} {r['seed']}: ticks {r['ticks']}" + (f" ABORTED at {r['aborted_at']}" if r["aborted_at"] else "")
                  + f"; longest streak {r['longest_streak']}; distress ticks {r['distress_ticks']}; hap {r['mean_happiness']}")
        print(f"{n} ({s['grave_kitty']} grave): {len(s['worlds'])} worlds, aborts {s['aborts']}, worst streak {s['worst_streak']}")
    print(f"P: aborts {aborts}, worst streak {worst}; wrote {a.out}")
    if aborts:
        print("STOP: an abort stops the set; to the owner.")


if __name__ == "__main__":
    main()
