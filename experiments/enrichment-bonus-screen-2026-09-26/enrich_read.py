"""Reader for the enrichment-bonus screen (PREREG.md, frozen 2026-09-26).

    enrich_read.py --out read.json [--md read.md]

Deterministic: full battery paths below; play baselines from the FRESH
gen1-A comparator leg (the recorded cell predates the play block);
happiness paired against the RECORDED gen1-A tier 1 cell (same band
and seeds, F-054's comparator); trace summaries from the recorded
enrich traces.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "results-raw" / "battery"
BEAM = HERE.parent / "beam-world-screen-2026-09-19" / "results-raw"
GEN1A_RECORDED = BEAM / "battery" / "s3-b7-t3000-n6" / "gen1-A-c0-eval-30x20000.jsonl"
GEN1A_FRESH = B / "gen1-A" / "gen1-A-c0-eval-30x20000.jsonl"
SLOTS = ["bonus-s1", "bonus-s2", "bonus-lo-s1", "bonus-lo-s2"]
FULL = ("bonus-s1", "bonus-s2")


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return {r["seed"]: r for r in rows[1:]}


def team_hap(run):
    h = run["mean_happiness"]
    return sum(h) / len(h)


def play_stats(runs):
    """Pooled + per-seat play measures over one leg's 30 seeds."""
    ticks = sum(r["ticks"] for r in runs.values())
    pt = [0] * 5
    starts = [0] * 5
    bins = [0, 0, 0]
    tdist = 0
    for r in runs.values():
        p = r["play"]
        for k in range(5):
            pt[k] += p["ticks"][k]
            starts[k] += p["starts"][k]
            for i in range(3):
                bins[i] += p["start_gate_bins"][k][i]
        tdist += sum(p["starts_teammate_distressed"])
    tot_starts = sum(starts)
    return {
        "pooled_play_share": sum(pt) / (5 * ticks),
        "per_seat_play_share": [x / ticks for x in pt],
        "starts": tot_starts,
        "start_gate_bins": bins,
        "closed_gate_start_share": (bins[2] / tot_starts) if tot_starts else None,
        "teammate_distressed_starts": tdist,
    }


def welfare_stats(runs):
    ticks = sum(r["ticks"] for r in runs.values())
    lo = tot = 0
    for r in runs.values():
        for k in range(len(r["beam"]["start_need_bins"])):
            b = r["beam"]["start_need_bins"][k]
            lo += b[0]
            tot += sum(b)
    return {
        "sleep_share": sum(sum(r["beam"]["sleep"]) for r in runs.values()) / (5 * ticks),
        "lowneed_start_share": (lo / tot) if tot else None,
        # the recorded tier 1 cell predates dist_ticks (F-052 addition):
        # absent keys read as 0 there; every leg this screen collected has them
        "dist_ticks": sum(sum(r.get("dist_ticks", [0])) for r in runs.values()),
        "max_distress_age": max(r.get("max_distress_age", 0) for r in runs.values()),
        "aborted_legs": sum(1 for r in runs.values() if "aborted_streak" in r),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    recorded = load(GEN1A_RECORDED)
    fresh = load(GEN1A_FRESH)
    base_seeds = sorted(recorded)
    assert sorted(fresh) == base_seeds, "fresh comparator seed mismatch"
    out = {"comparators": {}, "arms": {}, "checks": {}}
    out["comparators"]["gen1A_recorded"] = {
        "path": str(GEN1A_RECORDED),
        "team_happiness_mean": sum(team_hap(recorded[s]) for s in base_seeds) / len(base_seeds),
        **welfare_stats(recorded),
    }
    out["comparators"]["gen1A_fresh"] = {
        "path": str(GEN1A_FRESH),
        "team_happiness_mean": sum(team_hap(fresh[s]) for s in base_seeds) / len(base_seeds),
        **play_stats(fresh), **welfare_stats(fresh),
    }
    cmp_play = out["comparators"]["gen1A_fresh"]

    for slot in SLOTS:
        d = B / slot
        leg = load(d / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl"))
        assert sorted(leg) == base_seeds, (slot, "seed mismatch")
        deltas = [team_hap(leg[s]) - team_hap(recorded[s]) for s in base_seeds]
        arm = {
            **play_stats(leg), **welfare_stats(leg),
            "team_happiness_mean": sum(team_hap(leg[s]) for s in base_seeds) / len(base_seeds),
            "vs_recorded_paired_delta_mean": sum(deltas) / len(deltas),
            "vs_recorded_n_worse": sum(x < 0 for x in deltas),
        }
        rows = [json.loads(l) for l in
                (HERE / "artifacts" / f"ppo-fog-{slot}" / "enrich-trace.jsonl").read_text().splitlines()
                if l.strip()]
        q = rows[3 * len(rows) // 4:]
        arm["trace"] = {
            "n_updates": len(rows),
            "lastq_mean_term": sum(r["mean_term"] for r in q) / len(q),
            "lastq_mean_E": sum(r["mean_E"] for r in q) / len(q),
            "lastq_mean_g": sum(r["mean_g"] for r in q) / len(q),
            "lastq_play_share": sum(r["play_share"] for r in q) / len(q),
        }
        out["arms"][slot] = arm

    A = out["arms"]
    out["checks"] = {
        "P1_full_play_share": {s: A[s]["pooled_play_share"] for s in FULL},
        "P1_bar_0.10_both": all(A[s]["pooled_play_share"] >= 0.10 for s in FULL),
        "P1_dose_reported": {s: A[s]["pooled_play_share"] for s in SLOTS if s not in FULL},
        "P2_closed_gate_shares": {s: A[s]["closed_gate_start_share"] for s in SLOTS},
        "P2_comparator_share_plus_003": cmp_play["closed_gate_start_share"] + 0.03,
        "P2_holds_all_arms": all(A[s]["closed_gate_start_share"] <= cmp_play["closed_gate_start_share"] + 0.03
                                 for s in SLOTS),
        "P3_teammate_distressed": {s: A[s]["teammate_distressed_starts"] for s in SLOTS},
        "P3_comparator_plus_5": cmp_play["teammate_distressed_starts"] + 5,
        "P3_holds": all(A[s]["teammate_distressed_starts"] <= cmp_play["teammate_distressed_starts"] + 5
                        and A[s]["aborted_legs"] == 0 and A[s]["max_distress_age"] < 1000 for s in SLOTS),
        "P4_paired_delta": {s: A[s]["vs_recorded_paired_delta_mean"] for s in SLOTS},
        "P4_bar_minus_050_full": all(A[s]["vs_recorded_paired_delta_mean"] >= -0.50 for s in FULL),
        "P4_sleep_shares": {**{s: A[s]["sleep_share"] for s in SLOTS},
                            "gen1A_recorded": out["comparators"]["gen1A_recorded"]["sleep_share"]},
        "P4_sleep_within_0015_full": all(
            abs(A[s]["sleep_share"] - out["comparators"]["gen1A_recorded"]["sleep_share"]) <= 0.015
            for s in FULL),
        "P4_lowneed": {**{s: A[s]["lowneed_start_share"] for s in SLOTS},
                       "gen1A_recorded": out["comparators"]["gen1A_recorded"]["lowneed_start_share"]},
        "P5_biscuit_top": {s: (max(range(5), key=lambda k: A[s]["per_seat_play_share"][k]) == 1)
                           for s in SLOTS},
        "P5_lift_positive_seats": {s: sum(A[s]["per_seat_play_share"][k] > cmp_play["per_seat_play_share"][k]
                                          for k in range(5)) for s in FULL},
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# Enrichment-bonus read", "",
             "| arm | play share | closed-gate start share | tm-dist starts | happiness | vs recorded paired | worse/30 | sleep share | low-need starts | dist ticks | mda |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in SLOTS:
            m = A[s]
            L.append(f"| {s} | {m['pooled_play_share']:.4f} | {m['closed_gate_start_share']:.4f} | "
                     f"{m['teammate_distressed_starts']} | {m['team_happiness_mean']:.3f} | "
                     f"{m['vs_recorded_paired_delta_mean']:+.3f} | {m['vs_recorded_n_worse']}/30 | "
                     f"{m['sleep_share']:.4f} | {m['lowneed_start_share']:.3f} | {m['dist_ticks']} | {m['max_distress_age']} |")
        c = out["comparators"]
        L += ["", f"Comparators: recorded gen1-A {c['gen1A_recorded']['team_happiness_mean']:.3f} happiness, "
              f"sleep {c['gen1A_recorded']['sleep_share']:.4f}, low-need {c['gen1A_recorded']['lowneed_start_share']:.3f}; "
              f"fresh gen1-A play {c['gen1A_fresh']['pooled_play_share']:.4f}, closed-gate {c['gen1A_fresh']['closed_gate_start_share']:.4f}, "
              f"tm-dist starts {c['gen1A_fresh']['teammate_distressed_starts']}, happiness {c['gen1A_fresh']['team_happiness_mean']:.3f}.",
              "", f"Per-seat play (fresh comparator): {[round(x, 4) for x in c['gen1A_fresh']['per_seat_play_share']]}"]
        for s in SLOTS:
            L.append(f"Per-seat play ({s}): {[round(x, 4) for x in A[s]['per_seat_play_share']]}")
        L += ["", "Checks: " + json.dumps({k: v for k, v in out["checks"].items() if isinstance(v, (bool, int, float))}),
              "", "Traces: " + "; ".join(
                  f"{s} term {A[s]['trace']['lastq_mean_term']:.5f} E {A[s]['trace']['lastq_mean_E']:.3f} "
                  f"g {A[s]['trace']['lastq_mean_g']:.3f} play {A[s]['trace']['lastq_play_share']:.4f}" for s in SLOTS), ""]
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
