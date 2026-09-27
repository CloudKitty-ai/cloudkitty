"""Reader for the enrichment-decay sweep, stage A (PREREG.md, frozen
2026-09-26 at 7f6fab9).

    enrich2_read.py --out read.json [--md read.md]

Deterministic: battery paths below; play/needs baselines from the
FRESH gen1-A comparator leg; happiness paired against the RECORDED
gen1-A tier 1 cell (same band and seeds); trace summaries from the
recorded enrich2 traces. Glow-distribution limitation: the recorded
traces carry per-update MEANS only, so saturation reads from the
last-quarter mean E and the full-trace E range; an at-cap fraction
needs the stage-B trainer's trace extension.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "results-raw" / "battery"
BEAM = HERE.parent / "beam-world-screen-2026-09-19" / "results-raw"
GEN1A_RECORDED = BEAM / "battery" / "s3-b7-t3000-n6" / "gen1-A-c0-eval-30x20000.jsonl"
GEN1A_FRESH = B / "gen1-A" / "gen1-A-c0-eval-30x20000.jsonl"
CORNERS = ["d25-250", "d25-1000", "d100-250", "d100-1000"]
SLOTS = [f"{c}-s{s}" for c in CORNERS for s in (1, 2)]
P1_SLOTS = ("d100-250-s1", "d100-250-s2", "d100-1000-s1", "d100-1000-s2")
P2_SLOTS = ("d25-1000-s1", "d25-1000-s2", "d100-1000-s1", "d100-1000-s2")


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return {r["seed"]: r for r in rows[1:]}


def team_hap(run):
    h = run["mean_happiness"]
    return sum(h) / len(h)


def play_stats(runs):
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
    tot = sum(starts)
    return {
        "pooled_play_share": sum(pt) / (5 * ticks),
        "per_seat_play_share": [x / ticks for x in pt],
        "starts": tot,
        "start_gate_bins": bins,
        "closed_gate_start_share": (bins[2] / tot) if tot else None,
        "teammate_distressed_starts": tdist,
        "teammate_distressed_share": (tdist / tot) if tot else None,
    }


def needs_stats(runs):
    ticks = sum(r["ticks"] for r in runs.values())
    ct = 5 * ticks
    bins = [0] * 6
    eat = drink = 0
    for r in runs.values():
        n = r["needs"]
        for k in range(5):
            for i in range(6):
                bins[i] += n["worst_need_bins"][k][i]
            eat += n["eat_ticks"][k]
            drink += n["drink_ticks"][k]
    return {"worst_bin_shares": [b / ct for b in bins],
            "bin0_share": bins[0] / ct,
            "eat_drink_share": (eat + drink) / ct}


def welfare_stats(runs):
    ticks = sum(r["ticks"] for r in runs.values())
    return {
        "sleep_share": sum(sum(r["beam"]["sleep"]) for r in runs.values()) / (5 * ticks),
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
    assert sorted(fresh) == base_seeds
    out = {"comparators": {}, "arms": {}, "checks": {}}
    out["comparators"]["gen1A_recorded"] = {
        "team_happiness_mean": sum(team_hap(recorded[s]) for s in base_seeds) / 30,
        "sleep_share": welfare_stats(recorded)["sleep_share"],
    }
    out["comparators"]["gen1A_fresh"] = {
        "team_happiness_mean": sum(team_hap(fresh[s]) for s in base_seeds) / 30,
        **play_stats(fresh), **needs_stats(fresh), **welfare_stats(fresh),
    }
    cmp_f = out["comparators"]["gen1A_fresh"]

    for slot in SLOTS:
        leg = load(B / slot / ("gen1-A_" + "_".join(f"s{i}-{slot}" for i in range(5)) + "-c0-eval-30x20000.jsonl"))
        assert sorted(leg) == base_seeds, slot
        deltas = [team_hap(leg[s]) - team_hap(recorded[s]) for s in base_seeds]
        arm = {**play_stats(leg), **needs_stats(leg), **welfare_stats(leg),
               "team_happiness_mean": sum(team_hap(leg[s]) for s in base_seeds) / 30,
               "vs_recorded_paired_delta_mean": sum(deltas) / 30,
               "vs_recorded_n_worse": sum(x < 0 for x in deltas)}
        rows = [json.loads(l) for l in
                (HERE / "artifacts" / f"ppo-fog-{slot}" / "enrich2-trace.jsonl").read_text().splitlines() if l.strip()]
        q = rows[3 * len(rows) // 4:]
        arm["trace"] = {
            "n_updates": len(rows),
            "lastq_mean_E": sum(r["mean_E"] for r in q) / len(q),
            "lastq_mean_g": sum(r["mean_g"] for r in q) / len(q),
            "lastq_mean_term": sum(r["mean_term"] for r in q) / len(q),
            "lastq_banked_payout_share": sum(r["banked_payout_share"] for r in q) / len(q),
            "lastq_play_share": sum(r["play_share"] for r in q) / len(q),
            "E_range_all_updates": [min(r["mean_E"] for r in rows), max(r["mean_E"] for r in rows)],
        }
        out["arms"][slot] = arm

    A = out["arms"]
    out["checks"] = {
        "P1_d100_play": {s: A[s]["pooled_play_share"] for s in P1_SLOTS},
        "P1_bar_0.10_all_d100": all(A[s]["pooled_play_share"] >= 0.10 for s in P1_SLOTS),
        "P1_d25_reported": {s: A[s]["pooled_play_share"] for s in SLOTS if s not in P1_SLOTS},
        "P2_closed_gate": {s: A[s]["closed_gate_start_share"] for s in SLOTS},
        "P2_ceiling": cmp_f["closed_gate_start_share"] + 0.02,
        "P2_10pct_arms_hold": all(A[s]["closed_gate_start_share"] <= cmp_f["closed_gate_start_share"] + 0.02
                                  for s in P2_SLOTS),
        "P2_banked": {s: A[s]["trace"]["lastq_banked_payout_share"] for s in SLOTS},
        "P2_banked_lt_0.05_10pct": all(A[s]["trace"]["lastq_banked_payout_share"] < 0.05 for s in P2_SLOTS),
        "P3_bin0": {**{s: A[s]["bin0_share"] for s in SLOTS}, "comparator": cmp_f["bin0_share"]},
        "P3_bin0_holds": all(A[s]["bin0_share"] <= cmp_f["bin0_share"] + 0.05 for s in SLOTS),
        "P3_eatdrink": {**{s: A[s]["eat_drink_share"] for s in SLOTS}, "comparator": cmp_f["eat_drink_share"]},
        "P3_eatdrink_holds": all(A[s]["eat_drink_share"] <= cmp_f["eat_drink_share"] + 0.02 for s in SLOTS),
        "P4_delta": {s: A[s]["vs_recorded_paired_delta_mean"] for s in SLOTS},
        "P4_holds": all(A[s]["vs_recorded_paired_delta_mean"] >= -0.50 for s in SLOTS),
        "P4_sleep": {**{s: A[s]["sleep_share"] for s in SLOTS}, "gen1A_recorded": out["comparators"]["gen1A_recorded"]["sleep_share"]},
        "P4_tmdist": {s: A[s]["teammate_distressed_share"] for s in SLOTS},
        "P4_tmdist_holds": all(A[s]["teammate_distressed_share"] <= 0.001 for s in SLOTS),
        "P4_aborts_streaks": all(A[s]["aborted_legs"] == 0 and A[s]["max_distress_age"] < 1000 for s in SLOTS),
        "P5_biscuit_top": all(max(range(5), key=lambda k: A[s]["per_seat_play_share"][k]) == 1 for s in SLOTS),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# Enrichment-decay stage A read", "",
             "| arm | play | closed-gate | banked (trace) | E lastq | happiness | vs recorded | worse/30 | sleep | bin0 | eat+drink | dist ticks | mda |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in SLOTS:
            m = A[s]
            L.append(f"| {s} | {m['pooled_play_share']:.4f} | {m['closed_gate_start_share']:.4f} | "
                     f"{m['trace']['lastq_banked_payout_share']:.4f} | {m['trace']['lastq_mean_E']:.3f} | "
                     f"{m['team_happiness_mean']:.3f} | {m['vs_recorded_paired_delta_mean']:+.3f} | {m['vs_recorded_n_worse']}/30 | "
                     f"{m['sleep_share']:.4f} | {m['bin0_share']:.3f} | {m['eat_drink_share']:.4f} | {m['dist_ticks']} | {m['max_distress_age']} |")
        L += ["", f"Comparators: recorded gen1-A {out['comparators']['gen1A_recorded']['team_happiness_mean']:.3f} hap, sleep {out['comparators']['gen1A_recorded']['sleep_share']:.4f}; "
              f"fresh gen1-A play {cmp_f['pooled_play_share']:.4f}, closed-gate {cmp_f['closed_gate_start_share']:.4f}, "
              f"bin0 {cmp_f['bin0_share']:.3f}, eat+drink {cmp_f['eat_drink_share']:.4f}, tm-dist share {cmp_f['teammate_distressed_share']:.4f}, dist ticks {cmp_f['dist_ticks']}.",
              "", "Checks: " + json.dumps({k: v for k, v in out["checks"].items() if isinstance(v, bool)}), ""]
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
