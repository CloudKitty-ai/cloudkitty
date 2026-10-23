#!/usr/bin/env python3
"""The by-world train/evaluation split (DECLARATION.md §Data: by WORLD,
never by tick; per set 70% of worlds train, 30% evaluate, assignment by
a declared seed before collection). Writes split.json; the reads assert
their evaluation worlds equal it.

    split.py            # writes split.json beside this file
    split.py --check    # exits non-zero if split.json differs
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SPLIT_SEED = 20261022          # declared 2026-10-22, before any L/W/G world ran
EVAL_SHARE = 0.3
SETS = {
    "L": list(range(905001, 905011)),      # 10 lived rot2 worlds (band g2cmp)
    "W": list(range(1095401, 1095426)),    # 25 wide starts   (SEED-BANDS row 1095401–1095450)
    "G": list(range(1095426, 1095451)),    # 25 grave starts  (same row; conditional set)
}


def split():
    rng = np.random.default_rng(SPLIT_SEED)
    out = {"split_seed": SPLIT_SEED, "eval_share": EVAL_SHARE, "sets": {}}
    for name, seeds in SETS.items():
        seeds = sorted(seeds)
        perm = [seeds[i] for i in rng.permutation(len(seeds))]
        n_eval = round(EVAL_SHARE * len(seeds))
        ev = sorted(perm[:n_eval])
        out["sets"][name] = {"seeds": seeds, "eval": ev, "train": [s for s in seeds if s not in ev]}
    return out


def main():
    out = split()
    p = HERE / "split.json"
    if "--check" in sys.argv:
        assert json.loads(p.read_text()) == out, "split.json differs from split.py"
        print("split.json matches")
        return
    p.write_text(json.dumps(out, indent=1) + "\n")
    for name, s in out["sets"].items():
        print(name, "eval", s["eval"])


if __name__ == "__main__":
    main()
