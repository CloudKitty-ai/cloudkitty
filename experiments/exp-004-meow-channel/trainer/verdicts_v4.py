"""exp-004 verdicts: the frozen §9 gates over the eval sweep.

Per candidate:
  §9.2 (H5): the settled gate over shapes iii/roster3/roster5 —
      incident rate max(1,floor(0.05n)) at bar 225, low_share > 5%
      backstop, any floor_touches.
  §9.3 (H4): mean subject team welfare on the served world (shape iii,
      all-policy — the deployment shape) >= paired baseline + 0.02.
  Reported: shape-i (mixed) delta, distress ticks, worst
      max_distress_age per shape.

Selection (§9.4-9.5 follow for the selected candidate separately):
eligible = A0/A1 arms passing §9.2 AND §9.3, ranked by shape-iii
subject welfare. D1 is selection-INELIGIBLE by registration and is
reported only.
"""

import glob
import json
import math
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "artifacts" / "eval"
SHAPES = {"iii", "roster3", "roster5"}
INCIDENT_BAR = 225
LOW_SHARE_CAP = 0.05
RATE = 0.05
H4_MARGIN = 0.02


def load_runs(name, shape):
    f = EVAL / f"{name}--shape-{shape}.json"
    return json.load(open(f))


def stress(name):
    reasons, detail = [], {}
    for shape in sorted(SHAPES):
        d = load_runs(name, shape)
        runs = d["runs"]
        mds = [r["report"]["max_distress_age"] for r in runs]
        fts = [sum(k["floor_touches"] for k in r["report"]["kitties"])
               for r in runs]
        low = [max(k["low_share"] for k in r["report"]["kitties"])
               for r in runs]
        n = len(mds)
        allowed = max(1, math.floor(RATE * n))
        incidents = sum(1 for m in mds if m > INCIDENT_BAR)
        if incidents > allowed:
            reasons.append(f"{shape}:rate({incidents}/{n})")
        if any(v > LOW_SHARE_CAP for v in low):
            reasons.append(f"{shape}:low_share({max(low)*100:.1f}%)")
        if any(fts):
            reasons.append(f"{shape}:floor_touches({sum(fts)})")
        detail[shape] = {"worst_mds": max(mds), "incidents": incidents,
                         "allowed": allowed}
    return reasons, detail


def welfare(name, shape):
    d = load_runs(name, shape)
    subj = [r["aggregates"]["team_welfare"] for r in d["runs"]]
    base = [r["aggregates"]["team_welfare"] for r in d["baseline_runs"]]
    return (sum(subj) / len(subj), sum(base) / len(base))


def main():
    names = sorted({Path(f).stem.split("--shape-")[0]
                    for f in glob.glob(str(EVAL / "*--shape-*.json"))})
    rows = []
    for name in names:
        s_w, s_b = welfare(name, "iii")
        m_w, m_b = welfare(name, "i")
        reasons, detail = stress(name)
        h5 = not reasons
        h4 = s_w >= s_b + H4_MARGIN
        rows.append({
            "run": name,
            "arm": name.split("-")[0],
            "welfare_iii": s_w, "baseline_iii": s_b,
            "delta_iii": s_w - s_b,
            "delta_i": m_w - m_b,
            "h4_pass": h4, "h5_pass": h5,
            "gate_reasons": reasons,
            "worst_mds": {s: d["worst_mds"] for s, d in detail.items()},
        })
    print(f"{'run':8s} {'w(iii)':>7s} {'Δiii':>7s} {'Δi':>7s} "
          f"{'H4':>3s} {'H5':>3s}  worst mds (iii/r3/r5)  gate")
    for r in sorted(rows, key=lambda r: -r["delta_iii"]):
        w = r["worst_mds"]
        print(f"{r['run']:8s} {r['welfare_iii']:.4f} "
              f"{r['delta_iii']:+.4f} {r['delta_i']:+.4f} "
              f"{'  Y' if r['h4_pass'] else '  N'}"
              f"{'  Y' if r['h5_pass'] else '  N'}  "
              f"{w.get('iii',0):>5d}/{w.get('roster3',0):>5d}/"
              f"{w.get('roster5',0):>5d}  "
              f"{';'.join(r['gate_reasons']) or '-'}")
    eligible = [r for r in rows
                if r["arm"] in ("A0", "A1") and r["h4_pass"] and r["h5_pass"]]
    eligible.sort(key=lambda r: -r["delta_iii"])
    print(f"\neligible (A0/A1, H4+H5): {len(eligible)}"
          + (f"; leader {eligible[0]['run']} Δiii "
             f"{eligible[0]['delta_iii']:+.4f}" if eligible else ""))
    out = Path(__file__).resolve().parents[1] / "artifacts" / "verdicts.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
