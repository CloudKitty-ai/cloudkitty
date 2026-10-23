#!/usr/bin/env python3
"""Set L's engine check (DECLARATION.md §Welfare: "its first world is
checked byte-equal to the certified rot2 battery row on the same seed
(team happiness and distress ticks)"), extended to every L world present
and, where the Gen 2 lab binding's own rot2 stream exists
(../seating-analysis-g2-2026-10-21/results-raw/g2-rot2/, worlds
905001–905005), to the full needs/happiness/position/activity/distress
streams, array-equal. Any miss is an engine or seating drift between
the arc binding and the certified one: nothing downstream runs on it.

    check_L.py [--out L-check.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
L = HERE / "results-raw/L"
BATTERY = EXPTS / "gen2-cert-battery-2026-10-20/results-raw/g2-rot2/legs/size20/g2-rot2-g2cmp-30x20000.jsonl"
LAB = EXPTS / "seating-analysis-g2-2026-10-21/results-raw/g2-rot2"
ENGINE = "a2e8d0447146f2486f7c6c6e0adbb75f742f1a00"   # BINDING.md
STREAMS = ("needs", "hap", "pos", "activity", "distress", "msg", "act")


def battery_rows():
    lines = BATTERY.read_text().splitlines()
    head = json.loads(lines[0])
    return head, {r["seed"]: r for r in (json.loads(l) for l in lines[1:])}


def check_world(seed, head, rows):
    z = np.load(L / f"streams-{seed}.npz")
    meta = json.loads(str(z["meta"]))
    out = {"seed": seed, "ticks": meta["ticks"], "aborted_at": meta["aborted_at"]}
    assert meta["seating"] == "g2-rot2" and meta["seats"] == head["seats"], (meta["seats"], head["seats"])
    assert meta["ticks"] == 20000 and meta["aborted_at"] is None, (seed, meta["ticks"], meta["aborted_at"])
    assert meta["provenance"]["config_sha256"] == head["provenance"]["config_sha256"], seed
    assert meta["provenance"]["binding_engine"] == ENGINE, meta["provenance"]["binding_engine"]
    assert z["obs"].shape == (20000, 5, 399) and z["obs"].dtype == np.float16, z["obs"].shape
    assert meta["obs_recorded"] == [True] * 5
    row = rows[seed]
    hap = z["hap"].astype(np.float64).mean(0).round(4).tolist()
    dist = (z["distress"] > 0).sum(0).tolist()
    out["battery"] = {"mean_happiness": hap, "row_mean_happiness": row["mean_happiness"],
                      "dist_ticks": dist, "row_dist_ticks": row["dist_ticks"]}
    assert hap == row["mean_happiness"], (seed, hap, row["mean_happiness"])
    assert dist == row["dist_ticks"], (seed, dist, row["dist_ticks"])
    lab = LAB / f"streams-{seed}.npz"
    if lab.exists():
        y = np.load(lab)
        same = {k: bool(np.array_equal(z[k], y[k])) for k in STREAMS}
        out["lab_stream_equal"] = same
        assert all(same.values()), (seed, same)
    else:
        out["lab_stream_equal"] = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "L-check.json")
    a = ap.parse_args()
    head, rows = battery_rows()
    seeds = sorted(int(p.stem.split("-")[1]) for p in L.glob("streams-*.npz"))
    assert seeds, "no L world recorded"
    res = [check_world(s, head, rows) for s in seeds]
    a.out.write_text(json.dumps({"engine": ENGINE, "worlds": res}, indent=1))
    for r in res:
        print(f"{r['seed']}: battery row EQUAL (hap {r['battery']['mean_happiness']}, dist {r['battery']['dist_ticks']});"
              f" lab stream {'EQUAL' if r['lab_stream_equal'] else ('n/a' if r['lab_stream_equal'] is None else 'DIFFERS')}")
    print(f"{len(res)} L worlds checked against the certified battery; wrote {a.out}")


if __name__ == "__main__":
    main()
