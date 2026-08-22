#!/usr/bin/env python3
"""Scripted-anchor partnered-play start rate (the §3 grind-guard
comparator, report-only).

Measured with the trainer's OWN detector (train_ppo6.duet_starts)
over the anchor demonstrations' state streams — the scripted
bugs-2.0 composition, raw/anchor-playful-v6, 100 x 8k — normalized
per 1k seat-ticks exactly as collect_fragment logs it. The result is
banked in results-raw/duet-anchor-rate.json and hard-coded as
train_ppo6.DUET_ANCHOR_PER_1K.
"""
import json
from pathlib import Path

import numpy as np

from ppo_env6 import PADDED_STATE_DIM
from train_ppo6 import MAX_SEATS, duet_starts

HERE = Path(__file__).resolve().parent
EXP006 = HERE.parent


def main():
    root = EXP006 / "raw/anchor-playful-v6"
    dirs = sorted(root.glob("config-00-rollout-*"))
    assert len(dirs) == 100, len(dirs)
    starts, seat_ticks, per_rollout = 0, 0, []
    for d in dirs:
        st = np.load(d / "state.npy")
        assert st.shape == (8000, PADDED_STATE_DIM), (d.name, st.shape)
        s = int(duet_starts(st[:-1], st[1:]).sum())
        starts += s
        seat_ticks += (st.shape[0] - 1) * MAX_SEATS
        per_rollout.append(s)
    rate = 1000.0 * starts / seat_ticks
    out = {
        "duet_starts_per_1k_seat_ticks": round(rate, 4),
        "starts": starts,
        "seat_ticks": seat_ticks,
        "rollouts": len(dirs),
        "per_rollout_min_max": [min(per_rollout), max(per_rollout)],
        "source": "raw/anchor-playful-v6 (band 1020001-100, "
                  "collect-config-bugs2 composition)",
        "detector": "train_ppo6.duet_starts (PLAY_COL 14, "
                    "PARTNER_COL 16)",
    }
    p = EXP006 / "results-raw" / "duet-anchor-rate.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    print(f"-> {p}")


if __name__ == "__main__":
    main()
