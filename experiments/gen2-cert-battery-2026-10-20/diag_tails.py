#!/usr/bin/env python3
"""The unread s4/s7 tails (owner 2026-10-22: "Run the tail reads"; the
post-cert plan's item, timeline "post-cert analysis plan"). Declared
before results; committed before any replay.

Which tails: every distress streak of 300 ticks or more in the uniform
legs of s4 (the step-8 battery) and s7 (Phase B) (20×20 and 40×40, band g2cmp) that no read
has touched. The s7 investigation read 905029 at 40×40 (Pumpkin, 622)
and the rotation's three runs; the s2 stop and the 100×100 rows were
read separately. That leaves six worlds, seven cat-runs:

| seating | size | seed | cat (seat) | longest streak | that cat's distress ticks |
|---|---|---|---|---|---|
| g2-s4 | 20 | 905029 | Miso (0) | 535 | 535 |
|       |    |        | Biscuit (1) | 468 | 468 |
| g2-s4 | 40 | 905017 | Clementine (4) | 687 | 687 |
| g2-s4 | 40 | 905002 | Biscuit (1) | 602 | 602 |
| g2-s4 | 40 | 905025 | Miso (0) | 389 | 389 |
| g2-s7 | 40 | 905004 | Pumpkin (2) | 641 | 804 |
| g2-s7 | 40 | 905015 | Clementine (4) | 323 | 323 |

(the row's max_distress_age_seat and dist_ticks). In six of the seven
the cat's distress ticks equal its longest streak, so it had ONE run;
Pumpkin in 905004 had more than one (804 > 641).

Method, the s7 investigation's part 2 generalised: one deterministic
pass of the seating collector (held equal to the battery harness by its
own guards) per world, on that leg's config, with the distress stop
watching the TARGET seat alone at 100 ticks (`abort_seat`, added for
this read with a guard). The replay therefore stops 100 ticks into the
target's first run to reach 100 — its only run in six cases, hence the
long one; for Pumpkin 905004 the first run of 100 or more, which may be
an earlier, shorter one (declared; the read is then of a run of 100 or
more of that cat in that world, not necessarily the 641). The world
905029 at 20×20 carries two targets (Miso and Biscuit); its one replay
watches Miso and reads both cats over the stopped window.

Consistency controls per world, before any reading: the stopping seat
is the target with a streak of exactly 100 at the stop; every other
seat's longest streak in the replay is at or under its recorded row
maximum (a replay that diverges from the battery is reported, not
read).

Reads per target (the s7 investigation's `read_run` on the stopped
window, at that size's law radius): the need in distress; the chosen
actions; activity mix; moving share; alone share; for eat and drink,
the nearest relief and its in-sight share; and the water-parking
signature from the s7 read — Drink chosen while thirst is under 10 —
counted over the window. Each run is then placed against the three
shapes already on record: PARKED (alone, still, choosing Drink while
sated: s7's water parking), SEARCHING (moving most of the window with
relief out of sight: the F-053 cousin), or OTHER, by the window's
numbers (moving share ≥ 0.5 → searching; Drink-while-sated ≥ 0.5 of
the window and moving ≤ 0.2 → parked). Descriptive (rule 10); nothing
here is a bar and the certificate stands.

Welfare-cost line: six worlds × 5 covered minds × up to 20,000 ticks
(each replay stops at the window's end, so fewer), with the target's
re-exposed distress capped at about 100 ticks per world by the stop,
against 323–687 recorded; the other seats re-experience only what
precedes the stop. Asymmetric: the stop halts the replay; nothing
continues past it.

    diag_tails.py [--out diag-tails.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
sys.path.insert(0, str(EXPTS / "gen2-trunk-training-2026-10-18" / "trainer"))
sys.path.insert(1, str(EXPTS / "attn-oracle-2026-08-15"))
import seating_read as v1  # noqa: E402
from diag_s7_streaks import CATS, NEEDS, flags_of, longest_run, read_run  # noqa: E402

LEGS = EXPTS / "gen2-comparator-legs-2026-10-14"
RADIUS = {20: 4, 40: 5}
STOP = 100
# (seating, size, seed, target seat, other seats to read in the same window)
CASES = [
    ("g2-s4", 20, 905029, 0, [1]),
    ("g2-s4", 40, 905017, 4, []),
    ("g2-s4", 40, 905002, 1, []),
    ("g2-s4", 40, 905025, 0, []),
    ("g2-s7", 40, 905004, 2, []),
    ("g2-s7", 40, 905015, 4, []),
]


def row_of(seating, size, seed):
    p = HERE / f"results-raw/{seating}/legs/size{size}/{seating}-g2cmp-30x20000.jsonl"
    for l in p.read_text().splitlines()[1:]:
        r = json.loads(l)
        if r["seed"] == seed:
            return r
    raise KeyError((seating, size, seed))


def drink_while_sated(z, k, a, b):
    from data_g2 import ACTION_NAMES
    drink = ACTION_NAMES.index("Drink")
    w = slice(a, b + 1)
    return int(((z["act"][w, k] == drink) & (z["needs"][w, k, 1] < 10)).sum())


def shape(r):
    if r["moving_share"] >= 0.5:
        return "searching"
    if r["drink_while_sated"] >= 0.5 * r["length"] and r["moving_share"] <= 0.2:
        return "parked"
    return "other"


def one(seating, size, seed, target, others):
    import seating_collect_g2 as sc
    row = row_of(seating, size, seed)
    row_max = row["max_distress_age_seat"]
    cfg = LEGS / f"g2leg-{size}.toml"
    arrays, meta = sc.collect(seating, seed, 20000, STOP, config=cfg, abort_seat=target)
    assert meta["aborted_at"], (seating, seed, "the stop never fired")
    fl = flags_of(arrays["distress"])
    longest = [int(max(v1.runs_of(fl[:, k, j]).max() if fl[:, k, j].any() else 0 for j in range(6)))
               for k in range(5)]
    controls = {
        "stopped_at": meta["aborted_at"],
        "longest_in_replay": longest,
        "row_max": row_max,
        "target_streak_is_100": longest[target] == STOP,
        "others_within_row": all(longest[k] <= row_max[k] for k in range(5) if k != target),
    }
    out = {"seating": seating, "size": size, "seed": seed, "target": CATS[target],
           "recorded_longest": row_max[target], "recorded_dist_ticks": row["dist_ticks"][target],
           "controls": controls, "runs": []}
    for k in [target] + others:
        r = read_run(arrays, k, RADIUS[size], meta["element_types"])
        a, b = r["span"]
        r["drink_while_sated"] = drink_while_sated(arrays, k, a, b)
        r["shape"] = shape(r)
        r["seat"] = CATS[k]
        r["recorded_longest"] = row_max[k]
        out["runs"].append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "diag-tails.json")
    a = ap.parse_args()
    # Written after EVERY world, so a late failure cannot discard replays
    # already paid for (the first run lost all six to an int64 in json.dumps).
    res = []
    for c in CASES:
        res.append(one(*c))
        a.out.write_text(json.dumps(res, indent=1, default=int) + "\n")
        print(f"wrote {a.out} ({len(res)}/{len(CASES)})", flush=True)
    print("| case | cat | recorded | window | need | chose (top) | Drink while sated | moving | alone | shape |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c in res:
        for r in c["runs"]:
            top = ", ".join(f"{n} {k}" for n, k in r["chosen_top"][:3])
            print(f"| {c['seating']} {c['size']} {c['seed']} | {r['seat']} | {r['recorded_longest']} | {r['length']} | "
                  f"{r['need']} | {top} | {r['drink_while_sated']} | {r['moving_share']:.2f} | {r['alone_share']:.2f} | {r['shape']} |")
        ctl = c["controls"]
        print(f"|  controls | stop {ctl['stopped_at']} | target=100 {ctl['target_streak_is_100']} | "
              f"others≤row {ctl['others_within_row']} | replay {ctl['longest_in_replay']} vs row {ctl['row_max']} | | | | | |")


if __name__ == "__main__":
    main()
