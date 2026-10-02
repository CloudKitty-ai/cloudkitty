"""Reader for the dead-or-held probe (PREREG-C §Reads): stage-B
columns and definitions via enrich2b_read's functions; per-seat
play lift over the stage-B fresh gen1-A baseline; the declared
comparisons against the recorded b14 family.

    enrich2c_read.py --out read-c.json [--md]
"""
import argparse
import json
from pathlib import Path

from enrich2b_read import (load, team_hap, play_stats, needs_stats, welfare_stats,
                           GEN1A_RECORDED, GEN1A_FRESH, B, HERE)

STAGE_B_READ = HERE / "results-raw" / "enrich2b-read.json"
ARMS = ["l14-s1", "l14-s2", "o14-s1", "o14-s2"]
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
P_BAR = 0.10  # the standing play bar (PREREG-C's one fixed reference)


def arm_path(slot):
    if slot.startswith("o14"):
        return B / slot / "o14-legs.jsonl"
    return B / slot / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    recorded = load(GEN1A_RECORDED)
    fresh = load(GEN1A_FRESH)
    base_seeds = sorted(recorded)
    sb = json.loads(STAGE_B_READ.read_text())
    base_seat = sb["comparators"]["gen1A_fresh"]["per_seat_play_share"]
    b14 = sb["families"]["b14"]

    out = {"comparators": {
        "b14_greedy": b14["greedy_play"], "b14_trace": b14["trace_play"],
        "gen1A_fresh_play": sb["comparators"]["gen1A_fresh"]["pooled_play_share"],
        "per_seat_baseline": base_seat,
    }, "arms": {}, "checks": {}}

    for slot in ARMS:
        leg = load(arm_path(slot))
        assert sorted(leg) == base_seeds, slot
        deltas = [team_hap(leg[s]) - team_hap(recorded[s]) for s in base_seeds]
        arm = {**play_stats(leg), **needs_stats(leg), **welfare_stats(leg),
               "team_happiness_mean": sum(team_hap(leg[s]) for s in base_seeds) / 30,
               "vs_recorded_paired_delta_mean": sum(deltas) / 30,
               "vs_recorded_n_worse": sum(x < 0 for x in deltas)}
        arm["seat_lift"] = [arm["per_seat_play_share"][k] - base_seat[k] for k in range(5)]
        arm["ex_biscuit_lift"] = sum(arm["seat_lift"]) - arm["seat_lift"][1]
        rows = [json.loads(l) for l in
                (HERE / "artifacts" / f"ppo-fog-{slot}" / "enrich2b-trace.jsonl").read_text().splitlines() if l.strip()]
        assert rows[0]["beta"] == 0.14 and rows[0]["accrual_gate"] is False, slot
        q = rows[3 * len(rows) // 4:]
        arm["trace"] = {
            "n_updates": len(rows),
            "lastq_play_share": sum(r["play_share"] for r in q) / len(q),
            "lastq_at_cap_share": sum(r["at_cap_share"] for r in q) / len(q),
            "lastq_E_p50": sum(r["E_p50"] for r in q) / len(q),
            "lastq_banked_payout_share": sum(r["banked_payout_share"] for r in q) / len(q),
        }
        out["arms"][slot] = arm

    A = out["arms"]
    b14_range = (min(b14["greedy_play"]["per_seed"]), max(b14["greedy_play"]["per_seed"]))
    out["checks"] = {
        "P1_l14_greedy": [A["l14-s1"]["pooled_play_share"], A["l14-s2"]["pooled_play_share"]],
        "P1_l14_gt_b14_mean": all(A[s]["pooled_play_share"] > b14["greedy_play"]["mean"] for s in ("l14-s1", "l14-s2")),
        "P1_l14_ex_biscuit_pos_both": all(A[s]["ex_biscuit_lift"] > 0 for s in ("l14-s1", "l14-s2")),
        "P2_o14_trace": [A["o14-s1"]["trace"]["lastq_play_share"], A["o14-s2"]["trace"]["lastq_play_share"]],
        "P2_o14_trace_gt_b14": all(A[s]["trace"]["lastq_play_share"] > b14["trace_play"]["mean"] for s in ("o14-s1", "o14-s2")),
        "P2_o14_greedy": [A["o14-s1"]["pooled_play_share"], A["o14-s2"]["pooled_play_share"]],
        "P2_o14_greedy_gt_b14": all(A[s]["pooled_play_share"] > b14["greedy_play"]["mean"] for s in ("o14-s1", "o14-s2")),
        "P2_o14_ex_biscuit_pos_both": all(A[s]["ex_biscuit_lift"] > 0 for s in ("o14-s1", "o14-s2")),
        "P3_flat_within_b14_range": {s: b14_range[0] <= A[s]["pooled_play_share"] <= b14_range[1] for s in ARMS},
        "bar_0.10_any_arm": {s: A[s]["pooled_play_share"] >= P_BAR for s in ARMS},
        "watch_bin0_le_0.211": all(A[s]["bin0_share"] <= 0.211 for s in ARMS),
        "watch_eatdrink_le_0.0699": all(A[s]["eat_drink_share"] <= 0.0699 for s in ARMS),
        "watch_sleep_band": {s: abs(A[s]["sleep_share"] - 0.1354) <= 0.015 for s in ARMS},
        "watch_tmdist_le_0.001": {s: A[s]["teammate_distressed_share"] <= 0.001 for s in ARMS},
        "watch_no_aborts_streaks": all(A[s]["aborted_legs"] == 0 and A[s]["max_distress_age"] < 1000 for s in ARMS),
        "at_cap_per_arm": {s: A[s]["trace"]["lastq_at_cap_share"] for s in ARMS},
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print("wrote", a.out)
    if a.md:
        print("\n| arm | play (greedy) | play (trace lastq) | ex-Biscuit lift | Biscuit lift | closed-gate | at-cap | E p50 | happiness | vs recorded | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in ARMS:
            m = A[s]
            t = m["trace"]
            print(f"| {s} | {m['pooled_play_share']:.4f} | {t['lastq_play_share']:.4f} | "
                  f"{m['ex_biscuit_lift']:+.4f} | {m['seat_lift'][1]:+.4f} | {m['closed_gate_start_share']:.4f} | "
                  f"{t['lastq_at_cap_share']:.3f} | {t['lastq_E_p50']:.3f} | {m['team_happiness_mean']:.3f} | "
                  f"{m['vs_recorded_paired_delta_mean']:+.3f} | {m['sleep_share']:.4f} | {m['bin0_share']:.3f} | "
                  f"{m['eat_drink_share']:.4f} | {m['teammate_distressed_share']:.4f} | {m['dist_ticks']} | {m['max_distress_age']} |")
        print(f"\nComparators: b14 greedy {b14['greedy_play']['mean']:.4f} "
              f"(per-seed {', '.join(f'{x:.4f}' for x in b14['greedy_play']['per_seed'])}); "
              f"b14 trace {b14['trace_play']['mean']:.4f}; baseline play {sb['comparators']['gen1A_fresh']['pooled_play_share']:.4f}.")
        print("\nChecks: " + json.dumps({k: v for k, v in out["checks"].items()
                                         if isinstance(v, (bool, dict)) and k != "at_cap_per_arm"}, indent=1))


if __name__ == "__main__":
    main()
