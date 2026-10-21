#!/usr/bin/env python3
"""Amendment 1's same-world check (DECLARATION.md): every stream the
original collection recorded must be byte-identical in the re-collection
(same dtype, shape and bytes), seed by seed. Exit 1 on any mismatch.

    same_world.py <roster>    # results-raw/<roster>/ vs results-raw/applied/<roster>/
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
KEYS = ("pos", "activity", "msg", "act", "needs", "hap", "partner", "distress", "nash", "elements")
SEEDS = range(905001, 905006)


def main():
    roster = sys.argv[1]
    bad = []
    for s in SEEDS:
        a = np.load(HERE / f"results-raw/{roster}/streams-{s}.npz")
        b = np.load(HERE / f"results-raw/applied/{roster}/streams-{s}.npz")
        ma, mb = json.loads(str(a["meta"])), json.loads(str(b["meta"]))
        diff = [k for k in KEYS if a[k].dtype != b[k].dtype or a[k].shape != b[k].shape
                or a[k].tobytes() != b[k].tobytes()]
        if (ma["seed"], ma["ticks"]) != (mb["seed"], mb["ticks"]):
            diff.append("meta seed/ticks")
        if mb["aborted_at"]:
            diff.append(f"aborted at {mb['aborted_at']}")
        print(f"{roster} {s}: {'IDENTICAL' if not diff else 'MISMATCH ' + ','.join(diff)}"
              f" ({mb['ticks']} ticks; applied {b['applied'].shape})")
        bad += diff
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
