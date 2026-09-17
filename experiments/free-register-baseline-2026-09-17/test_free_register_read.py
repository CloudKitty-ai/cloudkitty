#!/usr/bin/env python3
"""Guards for free_register_read.py on staged probe-format rows (state,
not wording): event counts, the visibility split, the window boundary,
the control exclusion. Plain-python asserts; run directly."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / "attn-oracle-2026-08-15"))
import obs_layout_v5 as L  # noqa: E402
import free_register_read as R  # noqa: E402

T, IDS, WINDOW, DIGEST = 60, [1, 2, 3], 10, 30
MEW = R.head_index("mew")
EVENT_T = 25


def stage():
    """Kitty 1 says mew at tick 25. Kitty 2 sees kitty 1, sits idle at
    distance 6, closes to 4 exactly at tick 35 (the window's last tick)
    and proposes PlayKitty at kitty 1 at tick 28; it also proposed at
    tick 3, inside the control ticks' windows. Kitty 3 never sees kitty
    1, stays put, echoes mew at tick 30."""
    rows = {k: [] for k in ("obs", "tick", "kitty", "act", "msg", "seed")}
    for t in range(T):
        for kid in IDS:
            o = np.zeros(L.OBS_DIM, np.float32)
            o[L.SELF_ACTIVITY] = 1.0  # idle
            if kid == 1:
                pos = (10, 10)
            elif kid == 2:
                pos = (16, 10) if t < 35 else (14, 10)
            else:
                pos = (10, 2)
            o[L.SELF_POS], o[L.SELF_POS + 1] = pos[0] / R.W, pos[1] / R.W
            others = [k for k in IDS if k != kid]
            for slot, oid in enumerate(others):
                sees = (kid == 2 and oid == 1) or (kid == 1 and oid == 2)
                o[R.KITTY_BASE + slot * R.KITTY_W + L.ROW_PRESENT] = 1.0 if sees else 0.0
            act, msg = 38, 0  # Idle, Silent
            if kid == 1 and t == EVENT_T:
                msg = MEW
            if kid == 2 and t in (3, 28):
                act = 34 + others.index(1)  # PlayKitty at kitty 1's slot
            if kid == 3 and t == 30:
                msg = MEW
            rows["obs"].append(o); rows["tick"].append(t); rows["kitty"].append(kid)
            rows["act"].append(act); rows["msg"].append(msg); rows["seed"].append(1)
    return {k: np.asarray(v) for k, v in rows.items()}


def main():
    rows = stage()
    ids, pos, said, actcls, present, target, top = R.per_tick(rows)
    assert list(ids) == IDS
    assert present[0, 1, 0] and not present[0, 2, 0], "kitty 2 sees 1, kitty 3 does not"
    assert target[28, 1] == 0 and target[3, 1] == 0 and target[10, 1] == -1, "PlayKitty slot decodes to kitty 1"
    for control, match in (("any", False), ("speaker", True)):
        check(R.read_seed(rows, WINDOW, DIGEST, control, match))
    print("ok: free_register_read guards")


def check(res):
    """The stage is built so the declared and amended reads coincide:
    kitty 1 is the only speaker kitty 2 hears, and every cat is idle."""
    up = res["uptake"]["mew"]
    # visibility split: kitty 1's mew has one visible listener (kitty 2)
    # and one unseen (kitty 3); kitty 3's echo at tick 30 is itself an
    # event with two unseen listeners, so unseen events total 3
    assert up["visible"]["proposal_to_speaker"]["events"] == 1, up["visible"]
    assert up["unseen"]["proposal_to_speaker"]["events"] == 3, up["unseen"]
    # window boundary: the drop to 4 lands at t+10 exactly and counts
    assert up["visible"]["approach"]["observed"] == 1, up["visible"]["approach"]
    assert up["unseen"]["approach"]["observed"] == 0
    # proposal in the window; control rate 3/15 from the tick-3 proposal
    # seen by control ticks 0..2 of the 15 untainted ticks 0..14
    p = up["visible"]["proposal_to_speaker"]
    assert p["observed"] == 1 and abs(p["expected"] - 3 / 15) < 1e-9, p
    # echo: kitty 3 says mew inside the window; kitty 2 does not
    assert up["unseen"]["echo"]["observed"] == 1 and up["visible"]["echo"]["observed"] == 0
    # emission census
    e = res["emission"]["mew"]
    assert e["n"] == 2 and e["activity_mix"]["idle"] == 1.0, e


if __name__ == "__main__":
    main()
