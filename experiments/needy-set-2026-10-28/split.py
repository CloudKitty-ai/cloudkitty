#!/usr/bin/env python3
"""The needy set's tuning/confirming split (DECLARATION.md §3 "The
split", §12 call 6 RULED 2026-10-29 "As drafted"): within each block,
seeds in ascending order alternate tuning, confirming, tuning, … in every
arm. R4's ladder reads tuning seeds only; R5 reads the confirming seeds
after her pick. Committed before any covered world runs.

Arm T's seeds are P's 50 evaluation seeds, 10 per block, from Phase 1b's
split.json verbatim. Arm N's are 1095711 + 60·(k−1) …, arm E's
1096161 + 60·(k−1) … (SEED-BANDS row 1095651–1096650); each block uses
its first w (w_E) seeds in order, so the halves stay balanced at every w.
The scouts' seeds are not split (nothing from a scout is read by R4/R5).

    split.py            # writes split.json beside this file
    split.py --check    # exits non-zero if split.json differs
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE1B = HERE.parent / "minifriend-phase1b-2026-10-23"
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
PER_BLOCK = 60
N_BASE, E_BASE = 1095711, 1096161
SCOUT = {"N": [1095651, 1095700], "covered": [1095701, 1095710], "E": [1096011, 1096160]}
HELD = [1096461, 1096650]


def alternate(seeds):
    seeds = sorted(seeds)
    return {"seeds": seeds, "tuning": seeds[0::2], "confirming": seeds[1::2]}


def block(base, k):
    return list(range(base + PER_BLOCK * (k - 1), base + PER_BLOCK * k))


def split():
    p1b = json.loads((PHASE1B / "split.json").read_text())
    out = {"rule": "ascending seeds alternate tuning, confirming within each block (every arm)",
           "phase1b_split_seed": p1b["split_seed"], "scout_bands": SCOUT, "held": HELD,
           "friend": {f"{k}": {"id": k, "name": SEATS[k - 1]} for k in range(1, 6)}, "arms": {}}
    for k in range(1, 6):
        p_eval = p1b["sets"][f"P{k}"]["eval"]
        assert len(p_eval) == 10, (k, p_eval)
        out["arms"][f"T{k}"] = alternate(p_eval)
        out["arms"][f"N{k}"] = alternate(block(N_BASE, k))
        out["arms"][f"E{k}"] = alternate(block(E_BASE, k))
    return out


def main():
    p = HERE / "split.json"
    out = split()
    if "--check" in sys.argv:
        assert json.loads(p.read_text()) == out, "split.json differs from split.py"
        print("split.json matches")
        return
    p.write_text(json.dumps(out, indent=1) + "\n")
    for name, s in out["arms"].items():
        print(name, "tuning", s["tuning"][:3], "… confirming", s["confirming"][:3], "…")


if __name__ == "__main__":
    main()
