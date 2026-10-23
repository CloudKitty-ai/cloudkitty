#!/usr/bin/env python3
"""Sets W and G: the per-world provenance and welfare check (DECLARATION.md
§Welfare). Every recorded world must carry the certified seating on the
set's own config (sha equal to the toml beside this file, arc binding),
its reset needs inside the set's declared band, observations for all
five seats, and either the full tick count or a recorded abort. Aborts
and the worst single-need distress streak per cat are reported; ANY
abort (the F-053 line, streak 1000) stops the set and goes to the
owner — the scouts (the band's first three worlds) are read with this
script before the rest are launched.

    check_set.py W [--out W-check.json]
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ENGINE = "a2e8d0447146f2486f7c6c6e0adbb75f742f1a00"   # BINDING.md
BAND = {"W": (0.0, 90.0, 6000), "G": (60.0, 95.0, 4000)}
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]


def longest_streaks(distress):
    """(T, R) packed distress flags -> per cat the longest single-need run."""
    flags = np.unpackbits(distress[..., None].astype(np.uint8), axis=-1, bitorder="little")[..., :6]  # (T, R, 6)
    T, R, _ = flags.shape
    best = np.zeros(R, np.int64)
    run = np.zeros((R, 6), np.int64)
    for t in range(T):
        run = np.where(flags[t] > 0, run + 1, 0)
        best = np.maximum(best, run.max(1))
    return best.tolist()


def check_world(path, name, cfg_sha):
    lo, hi, ticks = BAND[name]
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    assert meta["seating"] == "g2-rot2", meta["seating"]
    assert meta["config"] == f"g2leg-20-{name}.toml" and meta["provenance"]["config_sha256"] == cfg_sha, \
        (meta["config"], meta["provenance"]["config_sha256"][:8])
    assert meta["provenance"]["binding_engine"] == ENGINE, meta["provenance"]["binding_engine"]
    assert meta["abort_streak"] == 1000 and meta["requested_ticks"] == ticks, (meta["abort_streak"], meta["requested_ticks"])
    assert meta["obs_recorded"] == [True] * 5
    n0 = z["needs0"]
    assert n0.shape == (5, 6) and (n0 >= lo - 1e-3).all() and (n0 <= hi + 1e-3).all(), (path.name, n0.round(1).tolist())
    assert np.ptp(n0) > 1.0, "reset needs did not vary: the section did not take"
    aborted = meta["aborted_at"]
    assert (aborted is None and meta["ticks"] == ticks) or (aborted is not None and meta["ticks"] == aborted), \
        (meta["ticks"], aborted)
    assert z["obs"].shape == (meta["ticks"], 5, 399), z["obs"].shape
    return {"seed": meta["seed"], "ticks": meta["ticks"], "aborted_at": aborted,
            "needs0": n0.round(2).tolist(), "hap0": z["hap0"].round(2).tolist(),
            "longest_streak": longest_streaks(z["distress"]),
            "distress_ticks": (z["distress"] > 0).sum(0).tolist(),
            "mean_happiness": z["hap"].astype(np.float64).mean(0).round(3).tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set", choices=list(BAND))
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    cfg = HERE / f"g2leg-20-{a.set}.toml"
    sha = hashlib.sha256(cfg.read_bytes()).hexdigest()
    d = HERE / "results-raw" / a.set
    seeds = sorted(int(p.stem.split("-")[1]) for p in d.glob("streams-*.npz"))
    assert seeds, f"no {a.set} world recorded"
    res = [check_world(d / f"streams-{s}.npz", a.set, sha) for s in seeds]
    out = a.out or HERE / f"{a.set}-check.json"
    aborts = [r["seed"] for r in res if r["aborted_at"] is not None]
    worst = max(max(r["longest_streak"]) for r in res)
    out.write_text(json.dumps({"set": a.set, "config_sha256": sha, "engine": ENGINE, "worlds": res,
                               "aborts": aborts, "worst_streak": worst}, indent=1))
    for r in res:
        print(f"{r['seed']}: ticks {r['ticks']}" + (f" ABORTED at {r['aborted_at']}" if r["aborted_at"] else "")
              + f"; longest streak {r['longest_streak']}; distress ticks {r['distress_ticks']}; hap {r['mean_happiness']}")
    print(f"{a.set}: {len(res)} worlds, aborts {aborts}, worst streak {worst}; wrote {out}")
    if aborts:
        print("STOP: an abort stops the set; to the owner.")


if __name__ == "__main__":
    main()
