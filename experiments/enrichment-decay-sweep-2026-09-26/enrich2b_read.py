"""Reader for the enrichment-decay sweep, stage B (PREREG-B.md,
frozen 2026-09-27 at ddd2301). Extends enrich2_read.py per §Reads:
per arm greedy AND training-trace play, closed-gate start share,
banked share, at-cap share and E median, paired happiness, sleep,
bin0, eat+drink, teammate-distressed share, dist ticks and max
streak; family means with per-seed spreads; P1-P6 scored.

    enrich2b_read.py --out read-b.json [--md read-b.md]

Deterministic: battery paths below; the fresh gen1-A comparator leg
and the recorded gen1-A tier 1 cell are stage A's; the stage-A
beta 0.03 pair on this corner (d100-1000-s1/s2) is the curve's
fourth point, read from the recorded stage-A read JSON.
"""
import argparse
import json
import statistics
from pathlib import Path

from enrich2_read import load, team_hap, play_stats, needs_stats, welfare_stats, \
    GEN1A_RECORDED, GEN1A_FRESH, B, HERE

STAGE_A_READ = HERE / "results-raw" / "enrich2-read.json"
FAMILIES = {"b06": ["b06-s1", "b06-s2", "b06-s3"],
            "b10": ["b10-s1", "b10-s2", "b10-s3"],
            "b14": ["b14-s1", "b14-s2", "b14-s3"],
            "ag10": ["ag10-s1", "ag10-s2"]}
SLOTS = [s for f in FAMILIES.values() for s in f]
# PREREG-B bars (sources named in RESULTS-B):
P1_BAR = 0.10                 # standing play bar; b10 and b14 family means
P2_CLOSED_BAR = 0.1043        # stage-A band top (fresh comparator 0.0843 + 0.02)
P2_BANKED_BAR = 0.05          # last-quarter trace banked share
P3_BIN0_BAR = 0.211           # stage-A comparator 0.161 + 0.05
P3_EATDRINK_BAR = 0.0699      # stage-A comparator 0.0499 + 0.02
P4_DELTA_B06_B10 = -0.50
P4_DELTA_B14 = -1.00
P4_SLEEP_CENTER, P4_SLEEP_TOL = 0.1354, 0.015
P4_TMDIST_BAR = 0.001


def fam_stat(vals):
    return {"mean": sum(vals) / len(vals),
            "spread": (max(vals) - min(vals)),
            "per_seed": vals,
            "sd": statistics.stdev(vals) if len(vals) > 1 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    recorded = load(GEN1A_RECORDED)
    fresh = load(GEN1A_FRESH)
    base_seeds = sorted(recorded)
    assert sorted(fresh) == base_seeds
    stage_a = json.loads(STAGE_A_READ.read_text())
    a03 = [stage_a["arms"][s]["pooled_play_share"] for s in ("d100-1000-s1", "d100-1000-s2")]

    out = {"comparators": {
        "gen1A_fresh": {**play_stats(fresh), **needs_stats(fresh), **welfare_stats(fresh),
                        "team_happiness_mean": sum(team_hap(fresh[s]) for s in base_seeds) / 30},
        "gen1A_recorded_hap": sum(team_hap(recorded[s]) for s in base_seeds) / 30,
        "stageA_beta03_d100_1000_play": a03,
    }, "arms": {}, "families": {}, "checks": {}}

    for slot in SLOTS:
        leg = load(B / slot / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl"))
        assert sorted(leg) == base_seeds, slot
        deltas = [team_hap(leg[s]) - team_hap(recorded[s]) for s in base_seeds]
        arm = {**play_stats(leg), **needs_stats(leg), **welfare_stats(leg),
               "team_happiness_mean": sum(team_hap(leg[s]) for s in base_seeds) / 30,
               "vs_recorded_paired_delta_mean": sum(deltas) / 30,
               "vs_recorded_n_worse": sum(x < 0 for x in deltas)}
        rows = [json.loads(l) for l in
                (HERE / "artifacts" / f"ppo-fog-{slot}" / "enrich2b-trace.jsonl").read_text().splitlines() if l.strip()]
        assert rows[0]["beta"] == {"b06": 0.06, "b10": 0.10, "b14": 0.14, "ag10": 0.10}[slot.rsplit("-", 1)[0]], slot
        assert rows[0]["accrual_gate"] == slot.startswith("ag"), slot
        q = rows[3 * len(rows) // 4:]
        arm["trace"] = {
            "n_updates": len(rows),
            "lastq_mean_E": sum(r["mean_E"] for r in q) / len(q),
            "lastq_E_p50": sum(r["E_p50"] for r in q) / len(q),
            "lastq_at_cap_share": sum(r["at_cap_share"] for r in q) / len(q),
            "lastq_banked_payout_share": sum(r["banked_payout_share"] for r in q) / len(q),
            "lastq_play_share": sum(r["play_share"] for r in q) / len(q),
            "E_range_all_updates": [min(r["mean_E"] for r in rows), max(r["mean_E"] for r in rows)],
        }
        out["arms"][slot] = arm

    A = out["arms"]
    for fam, slots in FAMILIES.items():
        out["families"][fam] = {
            "greedy_play": fam_stat([A[s]["pooled_play_share"] for s in slots]),
            "trace_play": fam_stat([A[s]["trace"]["lastq_play_share"] for s in slots]),
            "closed_gate": fam_stat([A[s]["closed_gate_start_share"] for s in slots]),
            "banked": fam_stat([A[s]["trace"]["lastq_banked_payout_share"] for s in slots]),
            "at_cap": fam_stat([A[s]["trace"]["lastq_at_cap_share"] for s in slots]),
            "E_p50": fam_stat([A[s]["trace"]["lastq_E_p50"] for s in slots]),
            "delta": fam_stat([A[s]["vs_recorded_paired_delta_mean"] for s in slots]),
            "bin0": fam_stat([A[s]["bin0_share"] for s in slots]),
            "eat_drink": fam_stat([A[s]["eat_drink_share"] for s in slots]),
            "sleep": fam_stat([A[s]["sleep_share"] for s in slots]),
        }
    F = out["families"]

    curve = [sum(a03) / 2, F["b06"]["greedy_play"]["mean"], F["b10"]["greedy_play"]["mean"], F["b14"]["greedy_play"]["mean"]]
    out["checks"] = {
        "P1_curve_beta03_b06_b10_b14": curve,
        "P1_rises_monotone": curve[0] < curve[1] < curve[2] < curve[3],
        "P1_b10_ge_bar": F["b10"]["greedy_play"]["mean"] >= P1_BAR,
        "P1_b14_ge_bar": F["b14"]["greedy_play"]["mean"] >= P1_BAR,
        "P1_trace_play_families": {f: F[f]["trace_play"]["mean"] for f in FAMILIES},
        "P2_closed_gate": {s: A[s]["closed_gate_start_share"] for s in SLOTS},
        "P2_all_le_bar": all(A[s]["closed_gate_start_share"] <= P2_CLOSED_BAR for s in SLOTS),
        "P2_banked": {s: A[s]["trace"]["lastq_banked_payout_share"] for s in SLOTS},
        "P2_banked_all_lt": all(A[s]["trace"]["lastq_banked_payout_share"] < P2_BANKED_BAR for s in SLOTS),
        "P2_ag_banked_zero": all(A[s]["trace"]["lastq_banked_payout_share"] == 0.0 for s in FAMILIES["ag10"]),
        "P2_ag_closed_le_b10_twins": all(
            A[f"ag10-s{i}"]["closed_gate_start_share"] <= A[f"b10-s{i}"]["closed_gate_start_share"]
            for i in (1, 2)),
        "P3_bin0": {s: A[s]["bin0_share"] for s in SLOTS},
        "P3_bin0_all_le": all(A[s]["bin0_share"] <= P3_BIN0_BAR for s in SLOTS),
        "P3_eatdrink": {s: A[s]["eat_drink_share"] for s in SLOTS},
        "P3_eatdrink_all_le": all(A[s]["eat_drink_share"] <= P3_EATDRINK_BAR for s in SLOTS),
        "P4_family_deltas": {f: F[f]["delta"]["mean"] for f in FAMILIES},
        "P4_b06_b10_hold": F["b06"]["delta"]["mean"] >= P4_DELTA_B06_B10 and F["b10"]["delta"]["mean"] >= P4_DELTA_B06_B10,
        "P4_b14_holds": F["b14"]["delta"]["mean"] >= P4_DELTA_B14,
        "P4_sleep_all_in_band": all(abs(A[s]["sleep_share"] - P4_SLEEP_CENTER) <= P4_SLEEP_TOL for s in SLOTS),
        "P4_tmdist_all_le": all(A[s]["teammate_distressed_share"] <= P4_TMDIST_BAR for s in SLOTS),
        "P4_no_aborts_streaks": all(A[s]["aborted_legs"] == 0 and A[s]["max_distress_age"] < 1000 for s in SLOTS),
        "P4_at_cap_per_arm": {s: A[s]["trace"]["lastq_at_cap_share"] for s in SLOTS},
        "P5_ag10_vs_b10": {
            "play": (F["ag10"]["greedy_play"]["mean"], F["b10"]["greedy_play"]["mean"]),
            "closed_gate": (F["ag10"]["closed_gate"]["mean"], F["b10"]["closed_gate"]["mean"]),
            "delta": (F["ag10"]["delta"]["mean"], F["b10"]["delta"]["mean"]),
        },
        "P6_biscuit_top": all(max(range(5), key=lambda k: A[s]["per_seat_play_share"][k]) == 1 for s in SLOTS),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# Enrichment-decay stage B read", "",
             "| arm | play (greedy) | play (trace lastq) | closed-gate | banked | at-cap | E p50 | happiness | vs recorded | worse/30 | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in SLOTS:
            m = A[s]
            t = m["trace"]
            L.append(f"| {s} | {m['pooled_play_share']:.4f} | {t['lastq_play_share']:.4f} | "
                     f"{m['closed_gate_start_share']:.4f} | {t['lastq_banked_payout_share']:.4f} | "
                     f"{t['lastq_at_cap_share']:.3f} | {t['lastq_E_p50']:.3f} | "
                     f"{m['team_happiness_mean']:.3f} | {m['vs_recorded_paired_delta_mean']:+.3f} | {m['vs_recorded_n_worse']}/30 | "
                     f"{m['sleep_share']:.4f} | {m['bin0_share']:.3f} | {m['eat_drink_share']:.4f} | "
                     f"{m['teammate_distressed_share']:.4f} | {m['dist_ticks']} | {m['max_distress_age']} |")
        L += ["", "| family | greedy play mean (per-seed) | trace play | closed-gate | banked | at-cap | delta | bin0 |",
              "|---|---|---|---|---|---|---|---|"]
        for f in FAMILIES:
            m = F[f]
            L.append(f"| {f} | {m['greedy_play']['mean']:.4f} ({', '.join(f'{x:.4f}' for x in m['greedy_play']['per_seed'])}) | "
                     f"{m['trace_play']['mean']:.4f} | {m['closed_gate']['mean']:.4f} | {m['banked']['mean']:.4f} | "
                     f"{m['at_cap']['mean']:.3f} | {m['delta']['mean']:+.3f} | {m['bin0']['mean']:.3f} |")
        L += ["", "Curve (beta 0.03 -> 0.06 -> 0.10 -> 0.14): " +
              " -> ".join(f"{x:.4f}" for x in out["checks"]["P1_curve_beta03_b06_b10_b14"]),
              "", "Checks: " + json.dumps({k: v for k, v in out["checks"].items() if isinstance(v, bool)}, indent=1), ""]
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
