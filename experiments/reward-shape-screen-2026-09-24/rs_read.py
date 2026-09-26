"""Reader for the reward-shape screen (PREREG.md, frozen 2026-09-24).

    rs_read.py --out read.json [--md read.md]

Deterministic: full battery paths below; placement pooled over
seatings per rule 10; paired welfare vs the recorded gen1-A leg on the
package world (tier 1 cell s3-b7-t3000-n6, same eval band and seeds);
lambda statistics from the recorded shape traces.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "results-raw" / "battery"
BEAM = HERE.parent / "beam-world-screen-2026-09-19" / "results-raw"
GEN1A_PKG = BEAM / "battery" / "s3-b7-t3000-n6" / "gen1-A-c0-eval-30x20000.jsonl"
PKG_ARMS = {s: BEAM / "tier2" / "battery" / s /
            f"gen1-A_s0-{s}_s1-{s}_s2-{s}_s3-{s}_s4-{s}-c0-eval-30x20000.jsonl"
            for s in ("pkg-s1", "pkg-s2")}
SLOTS = ["hard-s1", "hard-s2", "cvx-s1", "cvx-s2", "lam-s1", "lam-s2"]
D_TARGET = 0.06


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return {r["seed"]: r for r in rows[1:]}


def team_hap(run):
    h = run["mean_happiness"]
    return sum(h) / len(h)


def pooled_placement(runs_and_seats):
    on = sleep = 0
    for runs, seat in runs_and_seats:
        for r in runs.values():
            if seat == "all":
                on += sum(r["beam"]["on_beam"])
                sleep += sum(r["beam"]["sleep"])
            else:
                on += r["beam"]["on_beam"][seat]
                sleep += r["beam"]["sleep"][seat]
    return on / sleep if sleep else None


def lowneed_share(runs):
    lo = tot = 0
    for r in runs.values():
        for k in range(len(r["beam"]["start_need_bins"])):
            bins = r["beam"]["start_need_bins"][k]
            lo += bins[0]
            tot += sum(bins)
    return lo / tot if tot else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    gen1a = load(GEN1A_PKG)
    base_seeds = sorted(gen1a)
    out = {"arms": {}, "comparators": {}, "checks": {}}
    g_ticks = sum(r["ticks"] for r in gen1a.values())
    out["comparators"]["gen1A_package"] = {
        "path": str(GEN1A_PKG),
        "team_happiness_mean": sum(team_hap(gen1a[s]) for s in base_seeds) / len(base_seeds),
        "sleep_share": sum(sum(r["beam"]["sleep"]) for r in gen1a.values()) / (5 * g_ticks),
    }
    for name, path in PKG_ARMS.items():
        runs = load(path)
        out["comparators"][f"{name}_all_arm"] = {
            "path": str(path),
            "team_happiness_mean": sum(team_hap(r) for r in runs.values()) / len(runs),
            "placement_pooled": pooled_placement([(runs, "all")]),
        }

    for slot in SLOTS:
        d = B / slot
        swaps = {i: load(d / f"gen1-A_s{i}-{slot}-c0-eval-30x20000.jsonl") for i in range(5)}
        allarm = load(d / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl"))
        assert sorted(allarm) == base_seeds, (slot, "seed mismatch vs gen1-A")
        deltas = [team_hap(allarm[s]) - team_hap(gen1a[s]) for s in base_seeds]
        arm = {
            "own_seat_placement_pooled": pooled_placement([(swaps[i], i) for i in range(5)]),
            "own_seat_placement_by_seat": {str(i): pooled_placement([(swaps[i], i)]) for i in range(5)},
            "all_arm_placement_pooled": pooled_placement([(allarm, "all")]),
            "all_arm_team_happiness_mean": sum(team_hap(allarm[s]) for s in base_seeds) / len(base_seeds),
            "vs_gen1A_paired_delta_mean": sum(deltas) / len(deltas),
            "vs_gen1A_n_worse": sum(x < 0 for x in deltas),
            "all_arm_dist_ticks": sum(sum(allarm[s].get("dist_ticks", [0])) for s in base_seeds),
            "all_arm_max_distress_age": max(allarm[s]["max_distress_age"] for s in base_seeds),
            "all_arm_lowneed_start_share": lowneed_share(allarm),
        }
        trace_path = HERE / "artifacts" / f"ppo-fog-{slot}" / "shape-trace.jsonl"
        rows = [json.loads(l) for l in trace_path.read_text().splitlines() if l.strip()]
        q = rows[3 * len(rows) // 4:]
        lam_vals = [r["lam_next"] for r in q]
        cf_vals = [r["mean_cf"] for r in q]
        mean_lam = sum(lam_vals) / len(lam_vals)
        var = sum((x - mean_lam) ** 2 for x in lam_vals) / len(lam_vals)
        arm["trace"] = {
            "n_updates": len(rows),
            "final_lam": rows[-1]["lam_next"],
            "final_cf": rows[-1]["mean_cf"],
            "lastq_lam_mean": mean_lam,
            "lastq_lam_std_over_mean": (var ** 0.5 / mean_lam) if mean_lam else None,
            "lastq_mean_cf": sum(cf_vals) / len(cf_vals),
            "lastq_mean_term": sum(r["mean_term"] for r in q) / len(q),
        }
        ticks = sum(r["ticks"] for r in allarm.values())
        arm["all_arm_sleep_share"] = sum(sum(r["beam"]["sleep"]) for r in allarm.values()) / (5 * ticks)
        out["arms"][slot] = arm

    A = out["arms"]
    def spread(shape):
        return abs(A[f"{shape}-s1"]["own_seat_placement_pooled"] - A[f"{shape}-s2"]["own_seat_placement_pooled"])
    def hspread(shape):
        return abs(A[f"{shape}-s1"]["all_arm_team_happiness_mean"] - A[f"{shape}-s2"]["all_arm_team_happiness_mean"])
    def mean2(shape, key):
        return (A[f"{shape}-s1"][key] + A[f"{shape}-s2"][key]) / 2
    band_p = max(spread("hard"), spread("cvx"))
    band_h = max(hspread("hard"), hspread("cvx"))
    out["checks"] = {
        "P1_hard_placement_both_seeds": {s: A[s]["own_seat_placement_pooled"] for s in ("hard-s1", "hard-s2")},
        "P1_bar_0.15_both": all(A[s]["own_seat_placement_pooled"] >= 0.15 for s in ("hard-s1", "hard-s2")),
        "P2_cvx_placement_both_seeds": {s: A[s]["own_seat_placement_pooled"] for s in ("cvx-s1", "cvx-s2")},
        "P2_placement_gap_vs_band": {"gap": abs(mean2("cvx", "own_seat_placement_pooled") - mean2("hard", "own_seat_placement_pooled")), "band": band_p},
        "P2_happiness_gap_vs_band": {"gap": abs(mean2("cvx", "all_arm_team_happiness_mean") - mean2("hard", "all_arm_team_happiness_mean")), "band": band_h},
        "P3_lam_placement_both": {s: A[s]["own_seat_placement_pooled"] for s in ("lam-s1", "lam-s2")},
        "P3_bar_0.15_both": all(A[s]["own_seat_placement_pooled"] >= 0.15 for s in ("lam-s1", "lam-s2")),
        "P3_lam_interior_stable": {s: {"final": A[s]["trace"]["final_lam"],
                                       "std_over_mean": A[s]["trace"]["lastq_lam_std_over_mean"],
                                       "cf_within_0.02_of_d": abs(A[s]["trace"]["lastq_mean_cf"] - D_TARGET) <= 0.02}
                                   for s in ("lam-s1", "lam-s2")},
        "P4_lowneed_start_share": {s: A[s]["all_arm_lowneed_start_share"] for s in SLOTS},
        "P4_sleep_share": {**{s: A[s]["all_arm_sleep_share"] for s in SLOTS},
                           "gen1A": out["comparators"]["gen1A_package"]["sleep_share"]},
        "P4_vs_gen1A": {s: {"delta": A[s]["vs_gen1A_paired_delta_mean"], "n_worse": A[s]["vs_gen1A_n_worse"]} for s in SLOTS},
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# Reward-shape read", "",
             "| arm | own-seat placement (pooled) | all-arm placement | all-arm happiness | vs gen1-A paired | worse/30 | dist ticks | mda | low-need start share |",
             "|---|---|---|---|---|---|---|---|---|"]
        for s in SLOTS:
            m = A[s]
            L.append(f"| {s} | {m['own_seat_placement_pooled']:.3f} | {m['all_arm_placement_pooled']:.3f} | "
                     f"{m['all_arm_team_happiness_mean']:.3f} | {m['vs_gen1A_paired_delta_mean']:+.3f} | {m['vs_gen1A_n_worse']}/30 | "
                     f"{m['all_arm_dist_ticks']} | {m['all_arm_max_distress_age']} | {m['all_arm_lowneed_start_share']:.3f} |")
        c = out["comparators"]
        L += ["", f"Comparators: gen1-A on package {c['gen1A_package']['team_happiness_mean']:.3f} happiness; "
              f"pkg-s1 all-arm placement {c['pkg-s1_all_arm']['placement_pooled']:.3f}, "
              f"pkg-s2 {c['pkg-s2_all_arm']['placement_pooled']:.3f} (the floor-0 null).", ""]
        ck = out["checks"]
        L.append(f"P1 hard placement {ck['P1_hard_placement_both_seeds']}; bar >=0.15 both: {ck['P1_bar_0.15_both']}.")
        L.append(f"P2 cvx placement {ck['P2_cvx_placement_both_seeds']}; placement gap {ck['P2_placement_gap_vs_band']['gap']:.3f} vs band {ck['P2_placement_gap_vs_band']['band']:.3f}; "
                 f"happiness gap {ck['P2_happiness_gap_vs_band']['gap']:.3f} vs band {ck['P2_happiness_gap_vs_band']['band']:.3f}.")
        L.append(f"P3 lam placement {ck['P3_lam_placement_both']}; bar both: {ck['P3_bar_0.15_both']}; lam stats {json.dumps(ck['P3_lam_interior_stable'])}.")
        L.append(f"P4 low-need shares {json.dumps({k: round(v, 3) for k, v in ck['P4_lowneed_start_share'].items()})}.")
        L.append(f"P4 sleep shares {json.dumps({k: round(v, 4) for k, v in ck['P4_sleep_share'].items()})}.")
        L.append("Trace finals: " + "; ".join(f"{s} lam {A[s]['trace']['final_lam']:.4f} cf {A[s]['trace']['final_cf']:.4f}" for s in ("lam-s1", "lam-s2")) + ".")
        L.append("")
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
