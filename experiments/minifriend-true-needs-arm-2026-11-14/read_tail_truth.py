#!/usr/bin/env python3
"""The tail read on the true-needs arm (DECLARATION.md §6 "the tail read", §7 T4): the needs arm's `diag_lost.world`
(imported, its arm list extended by a root) on the 12M checkpoint's recorded 40×40 leg (30 worlds) and its 100×100
scout (905001–905003), the needs scout's same worlds beside it. Replays of recorded acts; nothing covered decides.
  streaks   each seat's longest distress run of 300+ ticks
  closing   a lonely cat's moves that shorten its walk to the nearest heard friend's call place, by walk length
  rescue    while a cat is LOST (cuddle >= 90, unpartnered, no friend in sight): every unpartnered friend's move and
            whether it closed on the lost cat. T4: under 0.70 of such moves close, scored at a size with 500+ moves.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_tail_truth.py --out reads/tail.json [--md]     (about 5 minutes, 6 workers)
(A = ../minifriend-phase2-2026-11-06.)
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "minifriend-needs-arm-2026-11-12"))
import read_r1_truth as R1T  # noqa: E402
import diag_lost as DL  # noqa: E402

SCOUT = (905001, 905002, 905003)
LEG = tuple(range(905001, 905031))
T4_LINE, T4_MOVES = 0.70, 500
ARMS = {"truth_12M": (R1T.CKPT, str(R1T.RAW)), "needs": ("p2u-needs-s1", None)}


def jobs():
    out = []
    for arm, (seating, root) in ARMS.items():
        for sub, size, seeds in (("legs", 40, LEG), ("scouts", 100, SCOUT)):
            out += [(arm, seating, sub, size, s) + ((root,) if root else ()) for s in seeds]
    return out


def t4(rescue):
    """T4 on {size: {friend_moves, closed_moves}}: at every size with 500+ moves under 0.70 close; a size under 500
    moves is not scored; no size scored reads None."""
    scored = {z: v["closed_moves"] / v["friend_moves"] for z, v in rescue.items() if v["friend_moves"] >= T4_MOVES}
    return {"scored": scored, "met": None if not scored else all(x < T4_LINE for x in scored.values())}


def pool(res):
    out = {}
    for arm in ARMS:
        for size in (40, 100):
            ws = [o for o in res if o["arm"] == arm and o["size"] == size]
            rows = np.asarray([x for o in ws for x in o["closing_rows"]], float).reshape(-1, 9)
            moves, closed = (sum(o["rescue"][k] for o in ws) for k in ("friend_moves", "closed_moves"))
            out[f"{arm}/{size}"] = {
                "worlds": len(ws), "ticks": [o["ticks"] for o in ws],
                "streaks_300": [{"seed": o["seed"], "seat": int(k), "length": s["streak"], "need": s["need"], "nearest_friend_mean": s["nearest_friend_mean"]}
                                for o in ws for k, s in o["seats"].items() if s["streak"] >= 300],
                "lonely_moves": len(rows), "lonely_closed": DL.r(rows[:, 5].mean()) if len(rows) else None, "lonely_closed_by_walk": DL.table(rows, 2, DL.D_BINS),
                "rescue": {"lost_cat_ticks": sum(o["rescue"]["lost_cat_ticks"] for o in ws), "friend_moves": moves, "closed_moves": closed,
                           "closed": DL.r(closed / moves) if moves else None}}
    return out


def read(workers=6):
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(DL.world, jobs()))
    out = {"pooled": pool(res)}
    out["T4"] = t4({z: out["pooled"][f"truth_12M/{z}"]["rescue"] for z in (40, 100)})
    return out


def md(out):
    f = lambda v: "none" if v is None else f"{v[0]:.3f} ({v[1]})"                         # noqa: E731
    L = ["# True-needs arm: the tail read (replays; the 12M checkpoint's 40×40 leg and 100×100 scout, the needs scout's same worlds beside it)", "",
         "| arm / size | worlds | streaks of 300+ | lost cat-ticks | friends' moves while a cat is lost | closing on it | lonely cat's moves | closing on the heard call place | by walk 0-10 | 10-20 | 20-40 | 40-70 | 70+ |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in out["pooled"].items():
        r = v["rescue"]
        L.append(f"| {name} | {v['worlds']} | {len(v['streaks_300'])} | {r['lost_cat_ticks']} | {r['friend_moves']} | {'n/a' if r['closed'] is None else format(r['closed'], '.3f')} | "
                 f"{v['lonely_moves']} | {'n/a' if v['lonely_closed'] is None else format(v['lonely_closed'], '.3f')} | " + " | ".join(f(x) for x in v["lonely_closed_by_walk"].values()) + " |")
    L += ["", "Streaks of 300+ ticks:", "", "| arm / size | world | seat | need | length | nearest friend (mean walk) |", "|---|---|---|---|---|---|"]
    L += [f"| {name} | {s['seed']} | {s['seat']} | {s['need']} | {s['length']} | {s['nearest_friend_mean']} |" for name, v in out["pooled"].items() for s in v["streaks_300"]]
    t = out["T4"]
    L += ["", f"**T4 {'UNSCORED (under ' + str(T4_MOVES) + ' moves at every size)' if t['met'] is None else 'MET' if t['met'] else 'NOT MET'}** "
          f"(the share of unpartnered friends' moves that close on a lost cat, at each size with {T4_MOVES}+ such moves; the line is under {T4_LINE}): "
          + (", ".join(f"{z}×{z} {x:.3f}" for z, x in t["scored"].items()) or "no size scored") + "."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    out = read()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
    print(md(out))
