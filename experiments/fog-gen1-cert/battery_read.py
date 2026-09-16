#!/usr/bin/env python3
"""Battery reader for the step-7 gates (PREREG §Battery), off the harness
JSONL legs in results-raw/battery/.

  floor, team     Nash (p = 0) of the composition >= the all-scripted roster
                  on the same config, paired by seed (nash_state on both;
                  the engine reward on the policy leg is printed beside it)
  floor, per seat each seat's mean happiness >= the scripted cat in that seat,
                  paired by seed; no noise allowance
  catastrophe     max distress age (constitutional 150; watchdog 0 =
                  no world-run with an age >= 150), floor touches 0

    battery_read.py [--legs eval,stress] [--seating gen1-A] [--swaps]
"""
import argparse
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAT = HERE / "results-raw" / "battery"
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
WATCHDOG = 150


def load(name):
    lines = [json.loads(l) for l in (BAT / name).open()]
    return lines[0], lines[1:]


def compare(cand_rows, base_rows, label):
    for r in cand_rows:  # legs run before nash_state existed: the engine reward is the same number at floor_touches 0
        r.setdefault("nash_state", r["nash"])
    base = {r["seed"]: r for r in base_rows}
    pairs = [(r, base[r["seed"]]) for r in cand_rows if r["seed"] in base]
    n = len(pairs)
    team_d = [c["nash_state"] - b["nash_state"] for c, b in pairs]
    team_lose = sum(1 for d in team_d if d < 0)
    print(f"== {label}: {n} paired seeds")
    print(f"  team nash  cand {st.mean(c['nash_state'] for c, _ in pairs):.4f} (engine reward "
          f"{st.mean(c['nash'] for c, _ in pairs):.4f}, min {min(c['nash_state'] for c, _ in pairs):.4f})  "
          f"scripted {st.mean(b['nash_state'] for _, b in pairs):.4f} (min {min(b['nash_state'] for _, b in pairs):.4f})  "
          f"delta {st.mean(team_d):+.4f}  seeds below scripted {team_lose}/{n}  -> {'PASS' if team_lose == 0 else 'MISS'}")
    for i, s in enumerate(SEATS):
        d = [c["mean_happiness"][i] - b["mean_happiness"][i] for c, b in pairs]
        lose = sum(1 for x in d if x < 0)
        print(f"  {s:10s} cand {st.mean(c['mean_happiness'][i] for c, _ in pairs):6.2f}  scripted "
              f"{st.mean(b['mean_happiness'][i] for _, b in pairs):6.2f}  delta {st.mean(d):+.2f}  "
              f"min delta {min(d):+.2f}  seeds below {lose}/{n}  -> {'PASS' if lose == 0 else 'MISS'}")
    mda = [c["max_distress_age"] for c, _ in pairs]
    wd = sum(1 for m in mda if m >= WATCHDOG)
    over = sorted(((c["max_distress_age"], c["seed"], c.get("max_distress_age_seat")) for c, _ in pairs), reverse=True)[:3]
    floors = sum(sum(c["floor_touches"]) for c, _ in pairs)
    print(f"  catastrophe  worst age {max(mda)}  runs >= {WATCHDOG}: {wd}/{n}  >= 225: {sum(1 for m in mda if m >= 225)}  "
          f"floor touches {floors}  -> {'PASS' if wd == 0 and floors == 0 else 'MISS'}   worst three {over}")
    b_mda = [b["max_distress_age"] for _, b in pairs]
    print(f"  (scripted worst age {max(b_mda)}, runs >= {WATCHDOG}: {sum(1 for m in b_mda if m >= WATCHDOG)}/{n})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", default="eval,stress")
    ap.add_argument("--seating", default="gen1-A")
    ap.add_argument("--swaps", action="store_true", help="also read every gen1-A_s*-eval swap leg")
    ap.add_argument("--clock", choices=("served", "train", "episode"), default="served",
                    help="which candidate legs to read: served-clock (-c0 files, default) or episode-clock")
    a = ap.parse_args()
    ap_suffix = {"served": "-c0", "train": "-ctrain", "episode": ""}[a.clock]
    for leg in a.legs.split(","):
        cand = BAT / f"{a.seating}{ap_suffix}-{leg}-30x20000.jsonl"  # the harness puts the clock tag before the band
        base = BAT / f"scripted-{leg}-30x20000.jsonl"
        if cand.exists() and base.exists():
            _h, c = load(cand.name)
            _h, b = load(base.name)
            compare(c, b, f"{a.seating} {leg}")
        else:
            print(f"== {a.seating} {leg}: not yet ({cand.exists()}, {base.exists()})")
    if a.swaps:
        _h, base = load("scripted-eval-30x20000.jsonl")
        _h, ref = load(f"{a.seating}{ap_suffix}-eval-30x20000.jsonl")
        refm = {r["seed"]: r for r in ref}
        basem = {r["seed"]: r for r in base}
        print("\n== swaps (eval band): seat, arm -> seat happiness vs scripted (paired mean delta / seeds below), vs gen1-A's seat, team nash, worst age, runs >= 150")
        for f in sorted(BAT.glob(f"{a.seating}_s*{ap_suffix}-eval-30x20000.jsonl")):
            tag = f.name.split("_s", 1)[1].split("-eval")[0].replace("-c0", "").replace("-ctrain", "")
            i, arm = int(tag[0]), tag[2:]
            _h, rows = load(f.name)
            if len(rows) < 30:
                continue
            for r in rows:
                r.setdefault("nash_state", r["nash"])
            d_s = [r["mean_happiness"][i] - basem[r["seed"]]["mean_happiness"][i] for r in rows]
            d_r = [r["mean_happiness"][i] - refm[r["seed"]]["mean_happiness"][i] for r in rows]
            mda = [r["max_distress_age"] for r in rows]
            print(f"  {SEATS[i]:10s} {arm:11s} hap {st.mean(r['mean_happiness'][i] for r in rows):6.2f}  vs scripted {st.mean(d_s):+.2f} "
                  f"({sum(1 for x in d_s if x < 0)} below)  vs gen1-A {st.mean(d_r):+.2f}  team {st.mean(r['nash_state'] for r in rows):.4f}  "
                  f"worst age {max(mda):4d}  wd {sum(1 for m in mda if m >= WATCHDOG)}")


if __name__ == "__main__":
    main()
