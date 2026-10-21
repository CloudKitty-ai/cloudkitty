#!/usr/bin/env python3
"""s7 streak investigation (owner 2026-10-21: "Can you investigate the S7
streak cause?"). Declared before results.

s7's long distress streaks cluster on Pumpkin's seat (eat rate 0.6, the
roster's highest) and Clementine's: Phase B 20x20 226 / 193 (Pumpkin),
40x40 641 / 622 (Pumpkin) and 323 (Clementine); rotation 121 and 84
(Clementine, rot1) and 94 (Pumpkin, rot3).

Part 1 (no new exposure): the rotation's recorded streams. For each s7
cat-world with a streak >= 50, locate the longest per-(cat, need) run
and read, over the run: the need, what the cat did (activity, chosen
actions, movement), its group size and holding, the nearest relief of
that need's kind (chow for eat, water for drink) and whether it was in
sight (Euclidean <= the 20x20 vision radius, 4), and what followed the
run (eating or drinking within 30 ticks).

Part 2 (replay, early stop): Phase B s7 uniform 40x40, seed 905029,
seat 2 (Pumpkin): streak 622 of 634 distress ticks; every other cat's
longest streak in this world is 31 or less. One deterministic pass of
the seating collector (held equal to the battery harness) with its
distress abort at 100: only Pumpkin's run can reach it, so the replay
stops 100 ticks into that run, about 100 re-exposed distress ticks for
one cat instead of 622 (the welfare mitigation). Consistency control:
the stopping cat is Pumpkin and no other seat exceeds its row maximum.
Same reads as part 1 at vision 5; how the run ended is not observed.

    diag_s7_streaks.py [--part 1|2|both] [--out diag-s7-streaks.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
SA = EXPTS / "seating-analysis-g2-2026-10-21"
sys.path.insert(0, str(SA))
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
sys.path.insert(0, str(EXPTS / "gen2-trunk-training-2026-10-18" / "trainer"))
sys.path.insert(1, str(EXPTS / "attn-oracle-2026-08-15"))
import seating_read as v1  # noqa: E402

NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
ACTS = ["idle", "rest", "sleep", "eat", "drink", "play", "groom"]
RELIEF = {0: "Chow", 1: "Water"}
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]


def flags_of(distress):
    return np.unpackbits(distress[:, :, None].astype(np.uint8), axis=2,
                         bitorder="little")[:, :, :6].astype(bool)


def group_sizes(p):
    R = len(p)
    out = []
    for k in range(R):
        seen, todo = {k}, [k]
        while todo:
            i = todo.pop()
            for j in range(R):
                if j not in seen and abs(int(p[i][0]) - int(p[j][0])) + abs(int(p[i][1]) - int(p[j][1])) <= 1:
                    seen.add(j)
                    todo.append(j)
        out.append(len(seen))
    return out


def longest_run(col):
    best, end, cur = 0, -1, 0
    for t, v in enumerate(col):
        cur = cur + 1 if v else 0
        if cur > best:
            best, end = cur, t
    return best, end - best + 1, end


def read_run(z, k, vision, et):
    from data_g2 import ACTION_NAMES
    fl = flags_of(z["distress"])
    runs = [longest_run(fl[:, k, j]) for j in range(6)]
    j = int(np.argmax([r[0] for r in runs]))
    length, a, b = runs[j]
    w = slice(a, b + 1)
    pos, act, needs = z["pos"], z["activity"], z["needs"]
    rel = []
    if j in RELIEF and RELIEF[j] in et:
        code = et[RELIEF[j]]
        for t in range(a, b + 1):
            els = z["elements"][t]
            xy = els[els[:, 0] == code][:, 1:]
            if len(xy):
                d_man = np.abs(xy - pos[t, k]).sum(1)
                d_euc = np.sqrt(((xy - pos[t, k]).astype(float) ** 2).sum(1))
                rel.append((int(d_man.min()), bool(d_euc.min() <= vision), len(xy)))
            else:
                rel.append((None, False, 0))
    moving = np.r_[False, np.abs(np.diff(pos[:, k].astype(int), axis=0)).sum(1) > 0]
    sizes = np.array([group_sizes(pos[t])[k] for t in range(a, b + 1)])
    chosen = z["act"][w, k]
    top = []
    if (chosen >= 0).all():
        u, c = np.unique(chosen, return_counts=True)
        top = [(ACTION_NAMES[i], int(n)) for i, n in sorted(zip(u, c), key=lambda x: -x[1])[:5]]
    after = act[b + 1:b + 31, k]
    tend = {0: 3, 1: 4}.get(j)
    out = {
        "need": NEEDS[j], "length": int(length), "span": [int(a), int(b)],
        "need_at_start_end": [round(float(needs[a, k, j]), 1), round(float(needs[b, k, j]), 1)],
        "other_needs_mean": {NEEDS[i]: round(float(needs[w, k, i].mean()), 1) for i in range(6) if i != j},
        "activity": {ACTS[i]: round(float((act[w, k] == i).mean()), 3) for i in range(7) if (act[w, k] == i).any()},
        "moving_share": round(float(moving[w].mean()), 3),
        "group3_share": round(float((sizes >= 3).mean()), 3),
        "alone_share": round(float((sizes == 1).mean()), 3),
        "chosen_top": top,
        "ended_by_tending_within_30": (None if tend is None or len(after) == 0
                                       else bool((after == tend).any())),
    }
    if rel:
        d = [r[0] for r in rel if r[0] is not None]
        out["relief"] = {
            "kind": RELIEF[j], "count_median": int(np.median([r[2] for r in rel])),
            "nearest_median": float(np.median(d)) if d else None,
            "nearest_first_last": [rel[0][0], rel[-1][0]],
            "in_sight_share": round(float(np.mean([r[1] for r in rel])), 3),
        }
    return out


def part1():
    out = []
    for p in sorted((SA / "results-raw").glob("g2-rot*/streams-*.npz")):
        z = np.load(p)
        meta = json.loads(str(z["meta"]))
        fl = flags_of(z["distress"])
        for k, spec in enumerate(meta["seats"]):
            if spec != "g2:trunk-s7":
                continue
            best = max(v1.runs_of(fl[:, k, j]).max() if fl[:, k, j].any() else 0 for j in range(6))
            if best >= 50:
                r = read_run(z, k, 4, meta["element_types"])
                out.append({"roster": meta["seating"], "seed": meta["seed"], "seat": CATS[k], **r})
    return out


def part2():
    import seating_collect_g2 as sc
    seed, seat, row_max = 905029, 2, [0, 0, 622, 0, 31]
    cfg = EXPTS / "gen2-comparator-legs-2026-10-14" / "g2leg-40.toml"
    arrays, meta = sc.collect("g2-s7", seed, 20000, 100, config=cfg)
    assert meta["aborted_at"], "the abort at 100 never fired"
    fl = flags_of(arrays["distress"])
    longest = [max(v1.runs_of(fl[:, k, j]).max() if fl[:, k, j].any() else 0 for j in range(6))
               for k in range(5)]
    assert longest[seat] == 100, ("stopping cat", longest)
    assert all(longest[k] <= row_max[k] for k in range(5) if k != seat), ("consistency", longest)
    r = read_run(arrays, seat, 5, meta["element_types"])
    return {"roster": "g2-s7 uniform 40x40", "seed": seed, "seat": CATS[seat],
            "replay_stopped_at": meta["aborted_at"], **r}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="both", choices=("1", "2", "both"))
    ap.add_argument("--out", type=Path, default=HERE / "diag-s7-streaks.json")
    a = ap.parse_args()
    res = {}
    if a.part in ("1", "both"):
        res["part1"] = part1()
    if a.part in ("2", "both"):
        res["part2"] = part2()
    print(json.dumps(res, indent=1))
    a.out.write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
