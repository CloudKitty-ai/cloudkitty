"""Reader for the lesion probe (PREREG-L §Step 2): lesioned j14
legs (stages 1+2 concatenated) against the recorded intact j14
battery and the recorded gen1-A paired baseline, tail metrics
first. Definitions are enrich2b_read's own functions.

    lesion_read.py --out read-l.json [--md]
"""
import argparse
import json
from pathlib import Path

from enrich2b_read import (load, team_hap, welfare_stats, play_stats,
                           GEN1A_RECORDED, HERE, B)

ARMS = ["j14-s1", "j14-s2"]
L = HERE / "results-raw" / "lesion"


def load_lesion(slot):
    rows = {}
    for st in (1, 2):
        for line in (L / f"{slot}-stage{st}.jsonl").read_text().splitlines():
            r = json.loads(line)
            if "seed" in r:
                rows[r["seed"]] = r
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    recorded = load(GEN1A_RECORDED)
    seeds = sorted(recorded)
    out = {"arms": {}}
    for slot in ARMS:
        les = load_lesion(slot)
        intact = load(B / slot / "j14-legs.jsonl")
        assert sorted(les) == seeds and sorted(intact) == seeds, slot
        arm = {}
        for tag, legs in (("lesioned", les), ("intact", intact)):
            deltas = [team_hap(legs[s]) - team_hap(recorded[s]) for s in seeds]
            arm[tag] = {**welfare_stats(legs), **play_stats(legs),
                        "team_happiness_mean": sum(team_hap(legs[s]) for s in seeds) / 30,
                        "vs_recorded_paired_delta_mean": sum(deltas) / 30,
                        "vs_recorded_n_worse": sum(x < 0 for x in deltas)}
        arm["paired_mean_change_on_lesion"] = (
            arm["lesioned"]["vs_recorded_paired_delta_mean"]
            - arm["intact"]["vs_recorded_paired_delta_mean"])
        out["arms"][slot] = arm
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print("wrote", a.out)
    if a.md:
        print("\n| arm | condition | dist ticks | max streak | tm-dist | aborts | happiness | vs recorded | n worse | play |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for slot in ARMS:
            for tag in ("intact", "lesioned"):
                m = out["arms"][slot][tag]
                print(f"| {slot} | {tag} | {m['dist_ticks']} | {m['max_distress_age']} | "
                      f"{m['teammate_distressed_share']:.4f} | {m['aborted_legs']} | "
                      f"{m['team_happiness_mean']:.3f} | {m['vs_recorded_paired_delta_mean']:+.3f} | "
                      f"{m['vs_recorded_n_worse']} | {m['pooled_play_share']:.4f} |")
        for slot in ARMS:
            print(f"{slot}: lesion changes the paired mean by "
                  f"{out['arms'][slot]['paired_mean_change_on_lesion']:+.3f}")
        print("Comparator (blind twin l14, recorded): dist 3262/1238, streak 952, "
              "tm-dist 0.0039/0.0013 — RESULTS-C.")


if __name__ == "__main__":
    main()
