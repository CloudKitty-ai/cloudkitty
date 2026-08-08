"""The settled §9.2 gate (owner, 2026-08-08), validated on both cohorts.

Fails a candidate iff any stress shape (iii = 4-seat all-policy,
roster3, roster5) shows:
  (i)  incident rate: more than max(1, floor(0.05 * n)) runs with
       max_distress_age > 225 (one full untended need rise,
       distress / rise_rate = 90 / 0.4 -- the prereg registers the
       formula and recomputes it from the frozen config's dials);
  (ii) severity backstop: any kitty-run with low_share > 5%;
  (iii) any floor_touches.
Everything below the incident bar is reported upstream, never gated.
Known, accepted flips at the 225 bar: A0-m33-g998-s2 and
M33-g0p998-s3 (repetition-at-150 borderline cases) pass and are
watched via reporting instead. See experiments/exp-004-design-inputs.md
section 3.

  python gate_check.py    (from the repo root or this directory)
"""
import glob
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
COHORTS = {
    "exp-002": REPO / "experiments/exp-002-mixed-population/results/eval-2026-08-03",
    "exp-003": Path(__file__).resolve().parent,
}
SHAPES = {"iii", "roster3", "roster5"}
INCIDENT_BAR = 225  # 90 / 0.4 at the current dials; recompute at freeze
LOW_SHARE_CAP = 0.05
RATE = 0.05


def load(directory):
    out = {}
    for f in sorted(glob.glob(str(directory / "*--shape-*.json"))):
        name, shape = Path(f).stem.split("--shape-")
        if shape not in SHAPES:
            continue
        runs = json.load(open(f))["runs"]
        out.setdefault(name, {})[shape] = dict(
            mds=[r["report"]["max_distress_age"] for r in runs],
            fts=[sum(k["floor_touches"] for k in r["report"]["kitties"]) for r in runs],
            low=[max(k["low_share"] for k in r["report"]["kitties"]) for r in runs],
        )
    return out


def gate(shapes):
    reasons = []
    for shape, v in sorted(shapes.items()):
        n = len(v["mds"])
        allowed = max(1, math.floor(RATE * n))
        incidents = sum(1 for m in v["mds"] if m > INCIDENT_BAR)
        if incidents > allowed:
            reasons.append(f"{shape}:rate({incidents}/{n} over {INCIDENT_BAR})")
        if any(l > LOW_SHARE_CAP for l in v["low"]):
            reasons.append(f"{shape}:low_share({max(v['low']) * 100:.1f}%)")
        if any(v["fts"]):
            reasons.append(f"{shape}:floor({sum(v['fts'])})")
    return reasons


for label, directory in COHORTS.items():
    cohort = load(directory)
    print(label)
    fails = 0
    for name, shapes in sorted(cohort.items()):
        reasons = gate(shapes)
        if reasons:
            fails += 1
            worst = max(m for v in shapes.values() for m in v["mds"])
            print(f"  FAIL {name:22} worst={worst:6}  " + "; ".join(reasons))
    print(f"  -> admits {len(cohort) - fails}/{len(cohort)}")
