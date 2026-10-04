"""Reader for the joint release arm (PREREG-D §Instrument and reads,
written before the battery is read): stage-B columns via
enrich2b_read's functions, the declared comparisons against the
recorded b14 family and l14 arms, and the BANDED PRIMARY — per-seat
excess contrast (live high-minus-low play share at the frozen edges,
MINUS the control's same-seat contrast) against the frozen margin.

Edges and margin are PREREG-D literals, restated here as constants;
the control contrasts come fresh from results-raw/e-edges/*.npz, the
live side from results-raw/battery/j14-*/j14-*-ebands.npz.

    enrich2d_read.py --out read-d.json [--md]
"""
import argparse
import json
from pathlib import Path

import numpy as np

from enrich2b_read import (load, team_hap, play_stats, needs_stats, welfare_stats,
                           GEN1A_RECORDED, GEN1A_FRESH, B, HERE)

STAGE_B_READ = HERE / "results-raw" / "enrich2b-read.json"
STAGE_C_READ = HERE / "results-raw" / "enrich2c-read.json"
EDGES_DIR = HERE / "results-raw" / "e-edges"
ARMS = ["j14-s1", "j14-s2"]
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
P_BAR = 0.10
# PREREG-D frozen literals (frozen 2026-10-03, commit 3d274e70)
EDGE_LOW = 0.43660981456438697
EDGE_HIGH = 0.8065612316131592
MARGIN = 0.02804
MIN_OCC = 10_000
NON_BISCUIT = [0, 2, 3, 4]


def banded_contrast(E, playing, valid_ticks=None):
    """Per-seat (play share | E>=EDGE_HIGH) - (play share | E<=EDGE_LOW),
    plus occupancy counts. E may carry NaN padding (aborted legs)."""
    out = {}
    for k in range(5):
        e = E[:, :, k]
        p = playing[:, :, k]
        ok = ~np.isnan(e)
        low = ok & (e <= EDGE_LOW)
        high = ok & (e >= EDGE_HIGH)
        out[k] = {
            "occ_low": int(low.sum()), "occ_high": int(high.sum()),
            "play_low": float(p[low].mean()) if low.any() else None,
            "play_high": float(p[high].mean()) if high.any() else None,
        }
        out[k]["contrast"] = (out[k]["play_high"] - out[k]["play_low"]
                              if low.any() and high.any() else None)
        out[k]["read"] = bool(low.sum() >= MIN_OCC and high.sum() >= MIN_OCC)
    return out


def control_contrasts():
    Es, Ps = [], []
    for p in sorted(EDGES_DIR.glob("l14-*.npz")):
        z = np.load(p)
        Es.append(z["E"])
        Ps.append(z["playing"])
    return banded_contrast(np.concatenate(Es), np.concatenate(Ps))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    recorded = load(GEN1A_RECORDED)
    base_seeds = sorted(recorded)
    sb = json.loads(STAGE_B_READ.read_text())
    sc = json.loads(STAGE_C_READ.read_text())
    base_seat = sb["comparators"]["gen1A_fresh"]["per_seat_play_share"]
    b14 = sb["families"]["b14"]
    ctrl = control_contrasts()

    out = {"comparators": {
        "b14_greedy": b14["greedy_play"], "b14_trace": b14["trace_play"],
        "l14_greedy": [sc["arms"]["l14-s1"]["pooled_play_share"],
                       sc["arms"]["l14-s2"]["pooled_play_share"]],
        "l14_ex_biscuit": [sc["arms"]["l14-s1"]["ex_biscuit_lift"],
                           sc["arms"]["l14-s2"]["ex_biscuit_lift"]],
        "gen1A_fresh_play": sb["comparators"]["gen1A_fresh"]["pooled_play_share"],
        "per_seat_baseline": base_seat,
        "control_banded": ctrl,
        "edges": {"low": EDGE_LOW, "high": EDGE_HIGH, "margin": MARGIN},
    }, "arms": {}, "checks": {}}

    for slot in ARMS:
        leg = load(B / slot / "j14-legs.jsonl")
        assert sorted(leg) == base_seeds, slot
        deltas = [team_hap(leg[s]) - team_hap(recorded[s]) for s in base_seeds]
        arm = {**play_stats(leg), **needs_stats(leg), **welfare_stats(leg),
               "team_happiness_mean": sum(team_hap(leg[s]) for s in base_seeds) / 30,
               "vs_recorded_paired_delta_mean": sum(deltas) / 30,
               "vs_recorded_n_worse": sum(x < 0 for x in deltas)}
        arm["seat_lift"] = [arm["per_seat_play_share"][k] - base_seat[k] for k in range(5)]
        arm["ex_biscuit_lift"] = sum(arm["seat_lift"]) - arm["seat_lift"][1]
        z = np.load(B / slot / f"{slot}-ebands.npz")
        live = banded_contrast(z["E"], z["playing"])
        arm["banded"] = live
        arm["excess"] = {k: (live[k]["contrast"] - ctrl[k]["contrast"]
                             if live[k]["read"] and live[k]["contrast"] is not None
                             else None) for k in range(5)}
        rows = [json.loads(l) for l in
                (HERE / "artifacts" / f"ppo-fog-{slot}" / "enrich2b-trace.jsonl").read_text().splitlines() if l.strip()]
        assert rows[0]["beta"] == 0.14 and rows[0]["accrual_gate"] is False, slot
        q = rows[3 * len(rows) // 4:]
        arm["trace"] = {
            "n_updates": len(rows),
            "lastq_play_share": sum(r["play_share"] for r in q) / len(q),
            "lastq_at_cap_share": sum(r["at_cap_share"] for r in q) / len(q),
            "lastq_E_p50": sum(r["E_p50"] for r in q) / len(q),
        }
        dg = [json.loads(l) for l in
              (HERE / "artifacts" / f"ppo-fog-{slot}" / "clip-diag.jsonl").read_text().splitlines()][-1]
        arm["clip_diag"] = {"main_fired_frac": dg["main_fired"] / dg["steps"],
                            "ecol_ratio_mean": dg["ecol_ratio_sum"] / dg["steps"]}
        out["arms"][slot] = arm

    A = out["arms"]
    out["checks"] = {
        "PRIMARY_excess_gt_margin_per_seat": {
            s: {k: (A[s]["excess"][k] is not None and A[s]["excess"][k] > MARGIN)
                for k in NON_BISCUIT} for s in ARMS},
        "PRIMARY_met_3of4_both_seeds": all(
            sum(A[s]["excess"][k] is not None and A[s]["excess"][k] > MARGIN
                for k in NON_BISCUIT) >= 3 for s in ARMS),
        "secondary_bar_0.10": {s: A[s]["pooled_play_share"] >= P_BAR for s in ARMS},
        "secondary_gt_b14_mean": {s: A[s]["pooled_play_share"] > b14["greedy_play"]["mean"] for s in ARMS},
        "watch_bin0_le_0.211": all(A[s]["bin0_share"] <= 0.211 for s in ARMS),
        "watch_eatdrink_le_0.0699": all(A[s]["eat_drink_share"] <= 0.0699 for s in ARMS),
        "watch_sleep_band": {s: abs(A[s]["sleep_share"] - 0.1354) <= 0.015 for s in ARMS},
        "watch_tmdist_le_0.001": {s: A[s]["teammate_distressed_share"] <= 0.001 for s in ARMS},
        "watch_no_aborts_streaks": all(A[s]["aborted_legs"] == 0 and A[s]["max_distress_age"] < 1000 for s in ARMS),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print("wrote", a.out)
    if a.md:
        print("\n| arm | play (greedy) | ex-Biscuit lift | Biscuit lift | closed-gate | happiness | vs recorded | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in ARMS:
            m = A[s]
            print(f"| {s} | {m['pooled_play_share']:.4f} | {m['ex_biscuit_lift']:+.4f} | "
                  f"{m['seat_lift'][1]:+.4f} | {m['closed_gate_start_share']:.4f} | "
                  f"{m['team_happiness_mean']:.3f} | {m['vs_recorded_paired_delta_mean']:+.3f} | "
                  f"{m['sleep_share']:.4f} | {m['bin0_share']:.3f} | {m['eat_drink_share']:.4f} | "
                  f"{m['teammate_distressed_share']:.4f} | {m['dist_ticks']} | {m['max_distress_age']} |")
        print("\n| seat | ctrl contrast | " + " | ".join(f"{s} contrast / excess" for s in ARMS) + " |")
        print("|---|---|" + "---|" * len(ARMS))
        for k in range(5):
            cells = []
            for s in ARMS:
                c = A[s]["banded"][k]["contrast"]
                e = A[s]["excess"][k]
                cells.append(f"{c:.4f} / {e:+.4f}" if c is not None and e is not None else "UNREAD")
            tag = "" if k != 1 else " (excluded)"
            print(f"| {CATS[k]}{tag} | {ctrl[k]['contrast']:.4f} | " + " | ".join(cells) + " |")
        print(f"\nEdges {EDGE_LOW:.4f}/{EDGE_HIGH:.4f}, margin {MARGIN}; "
              f"PRIMARY met on both seeds: {out['checks']['PRIMARY_met_3of4_both_seeds']}")
        print(f"Comparators: b14 greedy {b14['greedy_play']['mean']:.4f}; "
              f"l14 greedy {out['comparators']['l14_greedy']}; "
              f"baseline play {sb['comparators']['gen1A_fresh']['pooled_play_share']:.4f}.")
        print("Clip diag: " + ", ".join(
            f"{s}: main fired {A[s]['clip_diag']['main_fired_frac']:.3f}, "
            f"e_col ratio {A[s]['clip_diag']['ecol_ratio_mean']:.3f}" for s in ARMS))


if __name__ == "__main__":
    main()
