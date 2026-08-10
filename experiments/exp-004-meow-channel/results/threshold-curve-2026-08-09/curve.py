"""Threshold dose-response: paired deltas vs the T30 control, per
composition, over seeds 820001-010 x 20k. Reuses the T15 probe's
surviving control runs; T15/T30 numbers should reproduce results.md."""
import json
import math
from pathlib import Path

SP = Path(__file__).parent
SEEDS = [820000 + i for i in range(1, 11)]
COMPS = ["scripted", "policy", "mixed"]
THRESHOLDS = [15, 20, 25, 30]
TICKS = 20000


def cell(comp, t):
    rows = []
    for s in SEEDS:
        d = json.load(open(SP / f"{comp}-t{t}" / f"seed-{s}.json"))
        kt = d["kitties"].values()
        n = len(d["kitties"])
        ktick = n * TICKS
        want = sum(v for k in kt for m, v in k["meow_emits"].items()
                   if m != "purr")
        rows.append({
            "seed": s,
            "welfare": d["mean_team_reward"],
            "happiness": sum(k["happiness_sum"] for k in kt) / ktick,
            "want_1k": 1000 * want / ktick,
            "purr_1k": 1000 * sum(k["meow_emits"].get("purr", 0)
                                  for k in kt) / ktick,
            "groom_1k": 1000 * sum(k["groom_actor_ticks"]
                                   for k in kt) / ktick,
            "distress": sum(k["distress_ticks"] for k in kt),
        })
    return rows


def paired(comp, t):
    ctl = {r["seed"]: r for r in cell(comp, 30)}
    var = cell(comp, t)
    dw = [r["welfare"] - ctl[r["seed"]]["welfare"] for r in var]
    n = len(dw)
    mean = sum(dw) / n
    se = math.sqrt(sum((x - mean) ** 2 for x in dw) / (n - 1) / n)
    return {
        "welfare_delta": mean, "se": se,
        "up": sum(1 for x in dw if x > 0),
        "happiness_delta": sum(r["happiness"] for r in var) / n
                           - sum(ctl[s]["happiness"] for s in ctl) / n,
        "want_1k": sum(r["want_1k"] for r in var) / n,
        "purr_1k": sum(r["purr_1k"] for r in var) / n,
        "groom_1k": sum(r["groom_1k"] for r in var) / n,
        "distress": sum(r["distress"] for r in var),
    }


out = {}
for comp in COMPS:
    ctl = cell(comp, 30)
    n = len(ctl)
    base = {
        "welfare": sum(r["welfare"] for r in ctl) / n,
        "want_1k": sum(r["want_1k"] for r in ctl) / n,
        "purr_1k": sum(r["purr_1k"] for r in ctl) / n,
        "groom_1k": sum(r["groom_1k"] for r in ctl) / n,
        "distress": sum(r["distress"] for r in ctl),
    }
    out[comp] = {"t30_baseline": base}
    print(f"\n== {comp}  (T30 baseline: welfare {base['welfare']:.4f}, "
          f"want {base['want_1k']:.2f}/1k, groom {base['groom_1k']:.1f}/1k, "
          f"distress {base['distress']})")
    print(f"{'T':>3} {'Δwelfare':>10} {'±SE':>8} {'up':>5} {'Δhappy':>8} "
          f"{'want/1k':>8} {'purr/1k':>8} {'groom/1k':>9} {'distress':>8}")
    for t in [15, 20, 25]:
        p = paired(comp, t)
        out[comp][f"t{t}"] = p
        print(f"{t:>3} {p['welfare_delta']:>+10.4f} {p['se']:>8.4f} "
              f"{p['up']:>4}/{n} {p['happiness_delta']:>+8.2f} "
              f"{p['want_1k']:>8.2f} {p['purr_1k']:>8.1f} "
              f"{p['groom_1k']:>9.1f} {p['distress']:>8}")

json.dump(out, open(SP / "curve.json", "w"), indent=1)
print(f"\nwrote {SP / 'curve.json'}")
