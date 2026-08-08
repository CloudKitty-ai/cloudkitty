"""The proposed §9.2 gate, validated against both cohorts' full runs.

Fails a candidate iff any stress shape (iii = 4-seat all-policy,
roster3, roster5) shows: (i) a run with max_distress_age >= 1000
(saturation), (ii) more than one run over 150 (repetition), or
(iii) any floor_touches. The 1-150 trace region is reported upstream,
never gated. See experiments/exp-004-design-inputs.md §3.

  python gate_check.py    (from the repo root or this directory)
"""
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
COHORTS = {
    "exp-002": REPO / "experiments/exp-002-mixed-population/results/eval-2026-08-03",
    "exp-003": Path(__file__).resolve().parent,
}
SHAPES = {"iii", "roster3", "roster5"}


def load(directory):
    out = {}
    for f in sorted(glob.glob(str(directory / "*--shape-*.json"))):
        name, shape = Path(f).stem.split("--shape-")
        if shape not in SHAPES:
            continue
        runs = json.load(open(f))["runs"]
        out.setdefault(name, {})[shape] = (
            [r["report"]["max_distress_age"] for r in runs],
            [sum(k["floor_touches"] for k in r["report"]["kitties"]) for r in runs],
        )
    return out


def gate(shapes):
    reasons = []
    for shape, (mds, fts) in sorted(shapes.items()):
        over = [m for m in mds if m > 150]
        if any(m >= 1000 for m in mds):
            reasons.append(f"{shape}:saturation({max(mds)})")
        elif len(over) > 1:
            reasons.append(f"{shape}:repetition({len(over)}x>150)")
        if any(fts):
            reasons.append(f"{shape}:floor({sum(fts)})")
    return reasons


for label, directory in COHORTS.items():
    cohort = load(directory)
    print(label)
    fails = 0
    for name, shapes in sorted(cohort.items()):
        reasons = gate(shapes)
        if reasons:
            fails += 1
            worst = max(m for mds, _ in shapes.values() for m in mds)
            print(f"  FAIL {name:22} worst={worst:6}  " + "; ".join(reasons))
    print(f"  -> admits {len(cohort) - fails}/{len(cohort)}")
