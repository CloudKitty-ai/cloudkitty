"""Deviations entry 30 (her word 2026-11-10 "1-3 approved", item 2): the R-5 within-regime read on FREE-CHOICE ticks,
every recorded act15 / both leg (mode B: the arm's own head) and every no-head leg (mode A: a B15 shadow head the
policy never saw), tabulated from run_r5cf.sh's per-leg JSON (diag_r5_counterfactual.py). No replay here: a table over
committed read files. A leg file with fewer than 30 worlds, or one whose seating / size / mode is not its name's, is
never tabulated. P44 is NOT re-scored (entry 30): the ordering column is reported beside the frozen read.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_r5cf_table.py --dir reads/r5cf --out reads/r5cf/table.json [--md]
"""
import argparse
import json
import statistics
from pathlib import Path

WORLDS = 30
LEGS = [("B", "p2u-act15-s1", 20), ("B", "p2u-act15-s1", 40), ("B", "p2u-act15-s1", 100), ("B", "p2u-act15-s2", 20),
        ("B", "p2u-act15-s2", 40), ("B", "p2u-act15-s4", 20), ("B", "p2u-act15-s4", 40), ("B", "p2r-act15", 20),
        ("B", "p2r-act15", 40), ("B", "p2u-both-s1", 20), ("B", "p2u-both-s1", 40), ("B", "p2u-both-s1", 100),
        ("A", "p2u-nohead-s1", 20), ("A", "p2u-nohead-s1", 40), ("A", "p2u-nohead-s1", 100), ("A", "p2u-nohead-s2", 20),
        ("A", "p2u-nohead-s2", 40), ("A", "p2u-nohead-s4", 20), ("A", "p2u-nohead-s4", 40), ("A", "p2r-nohead", 20),
        ("A", "p2r-nohead", 40)]
REGIMES, TERCILES = ("seen", "heard"), ("low", "mid", "high")


def table(d):
    out = {"legs": {}}
    for mode, seating, size in LEGS:
        name = f"{mode}-{seating}-{size}"
        r = json.loads((d / f"{name}.json").read_text())
        assert r["worlds"] == WORLDS and (r["mode"], r["seating"], r["size"]) == (mode, seating, size), \
            f"{name}: {r['worlds']} worlds, file says {r['mode']} {r['seating']} {r['size']} — a partial or misnamed leg is never tabulated"
        row = {"mode": mode, "seating": seating, "size": size, "ties": r["ties"],
               "forced_choice_share": r["share_forced_choice_live_rows"], "tick_divergence": r["tick_divergence_live_rows"],
               "spearman_head_vs_trunk_entropy": r["spearman_head_vs_trunk_entropy"]}
        for key, src in (("all_rows", "by_head_entropy"), ("free_choice", "by_head_entropy_free_choice"), ("by_trunk_entropy", "by_trunk_entropy")):
            row[key] = {g: {t: r[src][g][t]["divergence"] for t in TERCILES} for g in REGIMES}
        row["low_gt_high_all_rows"] = r["within_regime_low_gt_high_head"]
        row["low_gt_high_free_choice"] = r["within_regime_low_gt_high_head_free_choice"]
        # the free-choice spread: the largest tercile divergence minus the smallest, per regime
        row["free_choice_spread"] = {g: max(row["free_choice"][g].values()) - min(row["free_choice"][g].values()) for g in REGIMES}
        row["all_rows_high_minus_low"] = {g: row["all_rows"][g]["high"] - row["all_rows"][g]["low"] for g in REGIMES}
        row["free_choice_high_minus_low"] = {g: row["free_choice"][g]["high"] - row["free_choice"][g]["low"] for g in REGIMES}
        out["legs"][name] = row
    L = out["legs"].values()
    out["summary"] = {
        "legs": len(out["legs"]),
        "forced_choice_share_range": [min(v["forced_choice_share"] for v in L), max(v["forced_choice_share"] for v in L)],
        "all_rows_low_gt_high": {g: sum(bool(v["low_gt_high_all_rows"][g]) for v in L) for g in REGIMES},
        "free_choice_low_gt_high": {g: sum(bool(v["low_gt_high_free_choice"][g]) for v in L) for g in REGIMES},
        "free_choice_spread_max": {g: max(v["free_choice_spread"][g] for v in L) for g in REGIMES},
        "all_rows_high_minus_low_range": {g: [min(v["all_rows_high_minus_low"][g] for v in L), max(v["all_rows_high_minus_low"][g] for v in L)] for g in REGIMES},
        "free_choice_high_minus_low_range": {g: [min(v["free_choice_high_minus_low"][g] for v in L), max(v["free_choice_high_minus_low"][g] for v in L)] for g in REGIMES},
        "spearman_head_vs_trunk_entropy_range": [min(v["spearman_head_vs_trunk_entropy"] for v in L), max(v["spearman_head_vs_trunk_entropy"] for v in L)],
        "free_choice_low_gt_high_seen_legs": [f"{v['seating']}-{v['size']}" for v in L if v["low_gt_high_free_choice"]["seen"]],
        "free_choice_high_minus_low_seen_by_size": {str(z): [min(v["free_choice_high_minus_low"]["seen"] for v in L if v["size"] == z),
                                                             max(v["free_choice_high_minus_low"]["seen"] for v in L if v["size"] == z)] for z in (20, 40, 100)},
        "free_choice_high_minus_low_seen_by_mode": {m: [min(v["free_choice_high_minus_low"]["seen"] for v in L if v["mode"] == m),
                                                        max(v["free_choice_high_minus_low"]["seen"] for v in L if v["mode"] == m)] for m in ("B", "A")},
        "seen_by_trunk_entropy_range": {t: [min(v["by_trunk_entropy"]["seen"][t] for v in L), max(v["by_trunk_entropy"]["seen"][t] for v in L)] for t in TERCILES},
        # the free-choice gap as a fraction of the all-rows gap (high minus low), leg by leg
        "free_over_all_gap": {g: {"min": min(v["free_choice_high_minus_low"][g] / v["all_rows_high_minus_low"][g] for v in L),
                                  "median": statistics.median(v["free_choice_high_minus_low"][g] / v["all_rows_high_minus_low"][g] for v in L),
                                  "max": max(v["free_choice_high_minus_low"][g] / v["all_rows_high_minus_low"][g] for v in L),
                                  "legs_free_gap_not_smaller": [f"{v['seating']}-{v['size']}" for v in L
                                                                if v["free_choice_high_minus_low"][g] >= v["all_rows_high_minus_low"][g]]} for g in REGIMES}}
    return out


def md(out):
    f3 = lambda b: " / ".join(f"{b[t]:.3f}" for t in TERCILES)
    L = ["# R-5 on free-choice ticks, every recorded leg (deviations entry 30; 30 worlds a leg)", "",
         "Divergence = share of live friend-rows on ticks where the arm's act differs from its trunk's; terciles low / mid / "
         "high of the head's entropy, fitted within regime. Mode B = the arm's own B15 head; mode A = a B15 shadow head "
         "over the no-head arm's observations. Forced-choice = one legal act (divergence 0 by construction).", "",
         "| leg | mode | forced-choice share | divergence | seen, all rows | seen, free-choice | heard, all rows | heard, free-choice | seen by trunk entropy | Spearman head~trunk entropy | ties |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in out["legs"].items():
        L.append(f"| {v['seating']}-{v['size']} | {v['mode']} | {v['forced_choice_share']:.3f} | {v['tick_divergence']:.3f} | {f3(v['all_rows']['seen'])} | "
                 f"{f3(v['free_choice']['seen'])} | {f3(v['all_rows']['heard'])} | {f3(v['free_choice']['heard'])} | {f3(v['by_trunk_entropy']['seen'])} | "
                 f"{v['spearman_head_vs_trunk_entropy']:+.3f} | {v['ties']} |")
    s = out["summary"]
    L += ["", f"Summary over {s['legs']} legs: forced-choice share {s['forced_choice_share_range'][0]:.3f}–{s['forced_choice_share_range'][1]:.3f}; "
          f"low-entropy divergence above high-entropy (P44's direction) on all rows in {s['all_rows_low_gt_high']['seen']} (seen) / {s['all_rows_low_gt_high']['heard']} (heard) legs, "
          f"on free-choice rows in {s['free_choice_low_gt_high']['seen']} / {s['free_choice_low_gt_high']['heard']}; "
          f"high minus low, all rows: seen {s['all_rows_high_minus_low_range']['seen'][0]:+.3f} to {s['all_rows_high_minus_low_range']['seen'][1]:+.3f}, "
          f"heard {s['all_rows_high_minus_low_range']['heard'][0]:+.3f} to {s['all_rows_high_minus_low_range']['heard'][1]:+.3f}; "
          f"free-choice: seen {s['free_choice_high_minus_low_range']['seen'][0]:+.3f} to {s['free_choice_high_minus_low_range']['seen'][1]:+.3f}, "
          f"heard {s['free_choice_high_minus_low_range']['heard'][0]:+.3f} to {s['free_choice_high_minus_low_range']['heard'][1]:+.3f}; "
          f"largest free-choice tercile spread {s['free_choice_spread_max']['seen']:.3f} (seen) / {s['free_choice_spread_max']['heard']:.3f} (heard); "
          f"Spearman head ~ trunk entropy {s['spearman_head_vs_trunk_entropy_range'][0]:+.3f} to {s['spearman_head_vs_trunk_entropy_range'][1]:+.3f}.", "",
          "Free-choice seen legs with low above high: " + ", ".join(s["free_choice_low_gt_high_seen_legs"]) + ". Free-choice seen high minus low by size: "
          + "; ".join(f"{z}×{z} {r[0]:+.3f} to {r[1]:+.3f}" for z, r in s["free_choice_high_minus_low_seen_by_size"].items())
          + "; by mode: " + "; ".join(f"{m} {r[0]:+.3f} to {r[1]:+.3f}" for m, r in s["free_choice_high_minus_low_seen_by_mode"].items())
          + ". Seen divergence by the trunk's own action-entropy tercile, range over legs: "
          + "; ".join(f"{t} {r[0]:.3f}–{r[1]:.3f}" for t, r in s["seen_by_trunk_entropy_range"].items()) + ".", "",
          "Free-choice gap as a fraction of the all-rows gap (high minus low), leg by leg: "
          + "; ".join(f"{g} {r['min']:+.2f} to {r['max']:+.2f}, median {r['median']:+.2f}, not smaller on "
                      f"{', '.join(r['legs_free_gap_not_smaller']) or 'no leg'}" for g, r in s["free_over_all_gap"].items()) + "."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True); ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = table(a.dir)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(json.dumps(out["summary"], indent=1))
