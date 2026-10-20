#!/usr/bin/env python3
"""Play-proposal drift read (owner "Sounds great, let's do it",
2026-10-20): trace-only, no new rollouts, zero welfare cost. For each
trunk run (s1/s2/s3/s4), walk the training probe traces
(probe-u*.npz, every 50 updates, 2k ticks x 3 seeds) and measure the
partner-play proposal pressure that materialized as s3's entry-3
collapse:

- per probe: pooled share of chosen actions in the PlayKitty block,
  the max per-(seed,kitty) cell share, and the share of rows where
  any PlayKitty act was legal (availability context);
- per run: the trajectory over updates, plus the late-training mean
  (last 5 probes) for a cross-seed comparison.

Declared before results. s3's u249 probe is the positive control: its
located cell (seed 40002, kitty 1) must show the entry-3 elevation.

    play_drift_read_g2.py [--out ../artifacts/play-drift-read.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from obs_layout_v6 import N_ACT  # noqa: E402
from data_g2 import ACTION_NAMES  # noqa: E402

PLAY_IDS = np.array([i for i, n in enumerate(ACTION_NAMES)
                     if n.startswith("PlayKitty")])
assert len(PLAY_IDS) == 4 and ACTION_NAMES[PLAY_IDS[0]] == "PlayKitty0"

RUNS = {s: ARC / f"artifacts/ppo-g2-trunk-{s}" for s in
        ("s1", "s2", "s3", "s4")}


def probe_stats(z):
    act = z["act"]
    play = np.isin(act, PLAY_IDS)
    legal_any = z["mask"][:, :N_ACT][:, PLAY_IDS].any(axis=1)
    cells, cell_share = [], []
    for s in np.unique(z["seed"]):
        for k in np.unique(z["kitty"]):
            sel = (z["seed"] == s) & (z["kitty"] == k)
            if sel.any():
                cells.append((int(s), int(k)))
                cell_share.append(float(play[sel].mean()))
    j = int(np.argmax(cell_share))
    return {"share": float(play.mean()),
            "legal_any_share": float(legal_any.mean()),
            "max_cell_share": cell_share[j],
            "max_cell": list(cells[j])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/play-drift-read.json")
    args = ap.parse_args()

    out = {}
    for run, d in RUNS.items():
        rows = []
        for f in sorted(d.glob("probe-u*.npz"),
                        key=lambda p: int(re.search(r"u(\d+)", p.name)[1])):
            u = int(re.search(r"u(\d+)", f.name)[1])
            rows.append({"update": u, **probe_stats(np.load(f))})
        late = rows[-5:]
        best = max(late, key=lambda r: r["max_cell_share"])
        out[run] = {
            "n_probes": len(rows),
            "trajectory": rows,
            "late_mean_share": float(np.mean([r["share"] for r in late])),
            "late_max_cell_share": best["max_cell_share"],
            "late_max_cell": {"update": best["update"],
                              "cell": best["max_cell"]},
            "final": rows[-1]}

    # positive control, exact reproduction against the committed
    # entry-3 record (artifacts/diag-s3.json): s3's halting probe,
    # cell (seed 40002, kitty 1), streak span ticks 820-1136 -> 317
    # rows of which 122 are PlayKitty proposals (act_hist ids 30-33:
    # 4+11+68+39).
    assert out["s3"]["final"]["update"] == 249, out["s3"]["final"]
    z = np.load(RUNS["s3"] / "probe-u249.npz")
    sel = ((z["seed"] == 40002) & (z["kitty"] == 1)
           & (z["tick"] >= 820) & (z["tick"] <= 1136))
    n_play = int(np.isin(z["act"][sel], PLAY_IDS).sum())
    assert (int(sel.sum()), n_play) == (317, 122), (sel.sum(), n_play)
    out["s3"]["entry3_window"] = {"rows": 317, "play": n_play,
                                  "share": n_play / 317}

    for run, r in out.items():
        t = r["trajectory"]
        print(f"{run}: probes {r['n_probes']}, share "
              f"u{t[0]['update']} {t[0]['share']:.4f} -> "
              f"final u{t[-1]['update']} {t[-1]['share']:.4f}, "
              f"late mean {r['late_mean_share']:.4f}, "
              f"late max cell {r['late_max_cell_share']:.4f} "
              f"@ {r['late_max_cell']['cell']} "
              f"u{r['late_max_cell']['update']}")
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
