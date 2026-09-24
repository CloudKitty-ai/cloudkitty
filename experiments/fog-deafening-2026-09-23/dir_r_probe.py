"""Measure the heard-caller distance distribution on the intact world
(prereg-3: the declared basis for the dir arm's fixed radius R).

    dir_r_probe.py [--seeds 3] [--ticks 5000] --out r-probe.json

Replays the intact composition (gen1-A, anchor-b3, served clock) at the
first collection seeds and collects every heard-only row's Manhattan
distance in tiles (dist float x (width + height)). Prints and records
the count, median, and quartiles. Read-only: no battery is touched.
"""
import argparse
import json
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
from test_deafen_mask import collect, SELF, SLOT, ROWS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--ticks", type=int, default=5000)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    with open(HERE.parent / "fog-gen1-cert" / "anchor-b3.toml", "rb") as f:
        cfg = tomllib.load(f)
    wh = cfg["world"]["width"] + cfg["world"]["height"]
    dists = []
    for i in range(a.seeds):
        for ob in collect(ticks=a.ticks, seed=900101 + i):
            for r in range(ROWS):
                row = SELF + r * SLOT
                heard = (ob[:, row] == 0.0) & (ob[:, row + 3] > 0.0)
                dists.extend((ob[heard, row + 3] * wh).tolist())
    d = np.asarray(dists)
    out = {"seeds": [900101 + i for i in range(a.seeds)], "ticks": a.ticks,
           "n_heard": int(d.size), "median": float(np.median(d)),
           "q25": float(np.percentile(d, 25)), "q75": float(np.percentile(d, 75)),
           "max": float(d.max()), "width_plus_height": wh}
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
