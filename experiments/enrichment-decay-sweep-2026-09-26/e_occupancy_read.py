"""E-occupancy read (owner's ask, 2026-10-04: "E occupancy,
sighted versus blind training. If the sighted policy holds the
stock higher at the same play total, the satiation story gets
direct evidence before Gen 3"). Declared before reading: per-slot
EVAL-side E distribution (median, quartiles, share of tick-samples
>= the frozen high edge 0.8065612316131592, share <= the frozen
low edge 0.43660981456438697, share >= 0.95 = enrich2b's
AT_CAP line) from the recorded replay npz — j14 (sighted training)
from results-raw/battery/*-ebands.npz, l14 (blind training) from
results-raw/e-edges/*.npz — each printed beside the slot's
recorded pooled greedy play share. The declared comparison: does
sighted training hold the stock higher at a comparable play total?

    e_occupancy_read.py --out read-occ.json [--md]
"""
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EDGE_HIGH = 0.8065612316131592
EDGE_LOW = 0.43660981456438697
AT_CAP = 0.95
SLOTS = {
    "l14-s1": ("results-raw/e-edges/l14-s1.npz", "blind"),
    "l14-s2": ("results-raw/e-edges/l14-s2.npz", "blind"),
    "j14-s1": ("results-raw/battery/j14-s1/j14-s1-ebands.npz", "sighted"),
    "j14-s2": ("results-raw/battery/j14-s2/j14-s2-ebands.npz", "sighted"),
}


def play_share(slot):
    src = json.loads((HERE / "results-raw" /
                      ("enrich2d-read.json" if slot.startswith("j14")
                       else "enrich2c-read.json")).read_text())
    return src["arms"][slot]["pooled_play_share"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = {}
    for slot, (rel, cond) in SLOTS.items():
        z = np.load(HERE / rel)
        E = z["E"]
        ok = ~np.isnan(E)
        e = E[ok]
        out[slot] = {
            "condition": cond, "n_samples": int(e.size),
            "quartiles": [float(x) for x in np.quantile(e, [0.25, 0.5, 0.75])],
            "share_ge_high_edge": float((e >= EDGE_HIGH).mean()),
            "share_le_low_edge": float((e <= EDGE_LOW).mean()),
            "share_ge_cap": float((e >= AT_CAP).mean()),
            "mean": float(e.mean()),
            "recorded_play_share": play_share(slot),
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print("wrote", a.out)
    if a.md:
        print("\n| slot | training | play (recorded) | E p25 | E p50 | E p75 | E mean | share >= 0.8066 | share <= 0.4366 | share >= 0.95 |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for slot, m in out.items():
            q = m["quartiles"]
            print(f"| {slot} | {m['condition']} | {m['recorded_play_share']:.4f} | "
                  f"{q[0]:.3f} | {q[1]:.3f} | {q[2]:.3f} | {m['mean']:.3f} | "
                  f"{m['share_ge_high_edge']:.3f} | {m['share_le_low_edge']:.3f} | "
                  f"{m['share_ge_cap']:.3f} |")


if __name__ == "__main__":
    main()
