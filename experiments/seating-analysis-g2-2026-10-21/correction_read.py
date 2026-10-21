#!/usr/bin/env python3
"""Amendment 1, reads 2 and 3 (DECLARATION.md beside this file), on the
re-collected streams (results-raw/applied/<roster>/), plus Gen 1's
flag-only correction.

Read 2 (method check): per roster and cat, pooled over the five worlds,
each activity's exact share (seating_read.corrected_streams), its flag
share, and seating_read.flag_estimate's eat/drink point estimate or
floor..ceiling for the others. Added beyond the declaration and labeled
so: the same floor..ceiling for the partnered share (the tick after a
partnered flag run that ends in Idle), checked the same way.

Read 3 (report-only): the battery's streak-shape and holding classifiers
(cert_harness_fog shape_update / hold_update, fed as run_one feeds them)
driven twice per tick, with the flags and with the corrected activity
and partner; the share of classified ticks whose class changes, and
each cat's longest-run shape both ways.

Gen 1: flag_estimate on the served gen1-A streams (the Gen 1 page).
Added beyond the declaration and labeled so: the same flag-only ranges
per network over the rotation streams (the model table), and where each
exact share sits inside its range (0 = floor, 1 = ceiling).

    correction_read.py [--out correction-read.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
sys.path.insert(0, str(EXPTS / "fog-gen1-cert"))
import cert_harness_fog as H  # noqa: E402
import seating_read as sr  # noqa: E402

SEEDS = range(905001, 905006)
ROSTERS = {"scripted": HERE / "results-raw/applied/scripted",
           "g2-rot2": HERE / "results-raw/applied/g2-rot2"}
GEN1 = [EXPTS / f"seating-analysis-2026-09-28/results-raw/streams-{s}.npz" for s in range(900501, 900506)]


def partner_range(activity, partner):
    """Flag-only floor..ceiling for partnered ticks, per cat."""
    p = partner[:, :, 0] == 1
    tail = p[:-1] & (activity[1:] == 0)
    return p.sum(0), p.sum(0) + tail.sum(0)


def method_check(files):
    T, n = 0, None
    exact = flag = floor = ceil = None
    eat = drink = one = 0
    pex = pfl = pce = 0
    for f in files:
        z = np.load(f)
        act, part = sr.corrected_streams(z)
        R = act.shape[1]
        est = sr.flag_estimate(z["activity"], z["needs"])
        ex = np.array([np.bincount(act[:, k].astype(int), minlength=7) for k in range(R)])
        fl = np.array([np.bincount(z["activity"][:, k].astype(int), minlength=7) for k in range(R)])
        lo = np.array([e["floor"] for e in est])
        hi = np.array([e["ceiling"] for e in est])
        pf, pc = partner_range(z["activity"], z["partner"])
        if exact is None:
            exact, flag, floor, ceil = ex, fl, lo, hi
            eat, drink = np.array([e["eat"] for e in est]), np.array([e["drink"] for e in est])
            one = np.array([e["one_tick_meals"] for e in est])
            pex, pfl, pce = (part[:, :, 0] == 1).sum(0), pf, pc
        else:
            exact, flag, floor, ceil = exact + ex, flag + fl, floor + lo, ceil + hi
            eat = eat + [e["eat"] for e in est]
            drink = drink + [e["drink"] for e in est]
            one = one + [e["one_tick_meals"] for e in est]
            pex, pfl, pce = pex + (part[:, :, 0] == 1).sum(0), pfl + pf, pce + pc
        T += act.shape[0]
    cats = []
    for k in range(exact.shape[0]):
        row = {"cat": sr.CATS[k], "ticks": T, "one_tick_meals": int(one[k]), "activities": {}}
        for a, name in enumerate(sr.ACTIVITIES):
            r = {"exact": round(exact[k, a] / T, 4), "flag": round(flag[k, a] / T, 4)}
            if a in (3, 4):
                e = eat[k] if a == 3 else drink[k]
                r.update(estimate=round(e / T, 4), error_ticks=int(e - exact[k, a]))
            else:
                span = ceil[k, a] - floor[k, a]
                r.update(floor=round(floor[k, a] / T, 4), ceiling=round(ceil[k, a] / T, 4),
                         inside=bool(floor[k, a] <= exact[k, a] <= ceil[k, a]),
                         position=round((exact[k, a] - floor[k, a]) / span, 3) if span else None)
            row["activities"][name] = r
        row["partnered (added)"] = {"exact": round(pex[k] / T, 4), "flag": round(pfl[k] / T, 4),
                                    "floor": round(pfl[k] / T, 4), "ceiling": round(pce[k] / T, 4),
                                    "inside": bool(pfl[k] <= pex[k] <= pce[k]),
                                    "position": round((pex[k] - pfl[k]) / (pce[k] - pfl[k]), 3)}
        cats.append(row)
    return cats


def gen1_estimate(files):
    T, acc = 0, None
    for f in files:
        z = np.load(f)
        assert "applied" not in z
        est = sr.flag_estimate(z["activity"], z["needs"])
        pf, pc = partner_range(z["activity"], z["partner"])
        cur = np.array([[*e["floor"], *e["ceiling"], e["eat"], e["drink"], e["one_tick_meals"], pf[k], pc[k]]
                        for k, e in enumerate(est)])
        acc = cur if acc is None else acc + cur
        T += z["activity"].shape[0]
    cats = []
    for k in range(acc.shape[0]):
        lo, hi = acc[k, :7], acc[k, 7:14]
        eat, drink, one, pf, pc = acc[k, 14:]
        row = {"cat": sr.CATS[k], "ticks": T, "one_tick_meals": int(one),
               "eat": round(eat / T, 4), "drink": round(drink / T, 4),
               "ranges": {sr.ACTIVITIES[a]: [round(lo[a] / T, 4), round(hi[a] / T, 4)]
                          for a in (0, 1, 2, 5, 6)},
               "flag": {}, "partnered (added)": [round(pf / T, 4), round(pc / T, 4)]}
        cats.append(row)
    # the flag shares as the page printed them
    for f in files:
        z = np.load(f)
        for k in range(len(cats)):
            c = np.bincount(z["activity"][:, k].astype(int), minlength=7)
            for a, name in enumerate(sr.ACTIVITIES):
                cats[k]["flag"][name] = cats[k]["flag"].get(name, 0) + int(c[a])
    for c in cats:
        c["flag"] = {n: round(v / c["ticks"], 4) for n, v in c["flag"].items()}
    return cats


def model_ranges():
    """Flag-only ranges per network over the five rotation rosters (no
    applied stream there): each network's 25 seat-worlds pooled."""
    acc = {}
    for f in sorted(HERE.glob("results-raw/g2-rot[1-5]/streams-*.npz")):
        z = np.load(f)
        seats = json.loads(str(z["meta"]))["seats"]
        est = sr.flag_estimate(z["activity"], z["needs"])
        pf, pc = partner_range(z["activity"], z["partner"])
        for k, spec in enumerate(seats):
            a = acc.setdefault(spec.split("-")[-1], np.zeros(17))
            a += [z["activity"].shape[0], *est[k]["floor"], *est[k]["ceiling"], pf[k], pc[k]]
    out = {}
    for n, a in sorted(acc.items()):
        T = a[0]
        out[n] = {"seat_worlds": int(T // 20000),
                  **{sr.ACTIVITIES[i]: [round(a[1 + i] / T, 3), round(a[8 + i] / T, 3)] for i in (0, 1, 2, 5, 6)},
                  "partnered": [round(a[15] / T, 3), round(a[16] / T, 3)]}
    return out


def components(tiles):
    """Each cat's walk-adjacent group size (disp_account's rule)."""
    R = len(tiles)
    parent = list(range(R))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in range(R):
        for j in range(i + 1, R):
            if H.walk_distance(tiles[i], tiles[j]) <= 1:
                parent[find(i)] = find(j)
    roots = [find(k) for k in range(R)]
    return [roots.count(r) for r in roots]


def reclassify(files):
    out = {"shape": {"classified": 0, "changed": 0, "moves": {}, "longest": []},
           "holding": {"held_flag": 0, "held_corrected": 0, "changed": 0,
                       "shared_flag": 0, "shared_corrected": 0}}
    for f in files:
        z = np.load(f)
        act, part = sr.corrected_streams(z)
        flag_act, flag_p = z["activity"], z["partner"][:, :, 0] == 1
        cor_p = part[:, :, 0] == 1
        bits = ((z["distress"][:, :, None] >> np.arange(6)) & 1).astype(bool)
        pos, needs = z["pos"], z["needs"]
        T, R = flag_act.shape
        acc_f, acc_c = H.shape_acc(R), H.shape_acc(R)
        hold_f, hold_c = H.hold_acc(R), H.hold_acc(R)
        prev = None
        for t in range(T):
            tiles = [(int(pos[t, k, 0]), int(pos[t, k, 1])) for k in range(R)]
            moved = [prev is not None and tiles[k] != prev[k] for k in range(R)]
            fl = [bits[t, k].tolist() for k in range(R)]
            af, ac = [int(x) for x in flag_act[t]], [int(x) for x in act[t]]
            pf, pc = [bool(x) for x in flag_p[t]], [bool(x) for x in cor_p[t]]
            H.shape_update(fl, af, pf, moved, acc_f)
            H.shape_update(fl, ac, pc, moved, acc_c)
            for k in range(R):
                for j in range(6):
                    if fl[k][j]:
                        kf = H.shape_kind(j, af[k], pf[k], moved[k])
                        kc = H.shape_kind(j, ac[k], pc[k], moved[k])
                        out["shape"]["classified"] += 1
                        if kf != kc:
                            out["shape"]["changed"] += 1
                            key = f"{H.SHAPE_KINDS[kf]}->{H.SHAPE_KINDS[kc]}"
                            out["shape"]["moves"][key] = out["shape"]["moves"].get(key, 0) + 1
            sizes = components(tiles)
            eat, drink = needs[t, :, 0].tolist(), needs[t, :, 1].tolist()
            H.hold_update(sizes, eat, drink, af, hold_f)
            H.hold_update(sizes, eat, drink, ac, hold_c)
            out["holding"]["changed"] += sum((hold_f["_run"][k] > 0) != (hold_c["_run"][k] > 0)
                                             for k in range(R))
            prev = tiles
        bf, bc = H.shape_close(acc_f), H.shape_close(acc_c)
        out["shape"]["longest"].append({"seed": json.loads(str(z["meta"]))["seed"],
                                        "flag": bf, "corrected": bc})
        out["holding"]["held_flag"] += sum(hold_f["held_ticks"])
        out["holding"]["held_corrected"] += sum(hold_c["held_ticks"])
        out["holding"]["shared_flag"] += hold_f["shared_hold_ticks"]
        out["holding"]["shared_corrected"] += hold_c["shared_hold_ticks"]
    s = out["shape"]
    s["changed_share"] = round(s["changed"] / s["classified"], 4) if s["classified"] else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "correction-read.json")
    a = ap.parse_args()
    files = {r: [d / f"streams-{s}.npz" for s in SEEDS] for r, d in ROSTERS.items()}
    out = {"method_check": {r: method_check(fs) for r, fs in files.items()},
           "gen1": gen1_estimate(GEN1),
           "model_ranges (added)": model_ranges(),
           "reclassify": {r: reclassify(fs) for r, fs in files.items()}}
    for r, cats in out["method_check"].items():
        print(f"== read 2, {r}: exact / flag / estimate or floor..ceiling (share of ticks)")
        for c in cats:
            cells = []
            for n, v in c["activities"].items():
                if "estimate" in v:
                    cells.append(f"{n} {v['exact']:.3f}/{v['flag']:.3f}/{v['estimate']:.3f} ({v['error_ticks']:+d})")
                else:
                    cells.append(f"{n} {v['exact']:.3f}/{v['flag']:.3f}/{v['floor']:.3f}..{v['ceiling']:.3f}"
                                 + ("" if v["inside"] else " OUTSIDE"))
            p = c["partnered (added)"]
            cells.append(f"partnered {p['exact']:.3f}/{p['flag']:.3f}/..{p['ceiling']:.3f}"
                         + ("" if p["inside"] else " OUTSIDE"))
            print(f"  {c['cat']}: " + " | ".join(cells))
    print("== Gen 1 (flags only): eat, drink, ranges; partnered range (added)")
    for c in out["gen1"]:
        rg = " | ".join(f"{n} {lo:.3f}..{hi:.3f}" for n, (lo, hi) in c["ranges"].items())
        print(f"  {c['cat']}: eat {c['eat']:.3f} (flag {c['flag']['Eat']:.3f}) | drink {c['drink']:.3f} "
              f"(flag {c['flag']['Drink']:.3f}) | {rg} | partnered {c['partnered (added)'][0]:.3f}.."
              f"{c['partnered (added)'][1]:.3f} | one-tick meals {c['one_tick_meals']}")
    print("== rotation, flag-only ranges per network (added)")
    for n, m in out["model_ranges (added)"].items():
        print(f"  {n} ({m['seat_worlds']} seat-worlds): " + " | ".join(f"{k} {v[0]:.3f}..{v[1]:.3f}" for k, v in m.items() if k != "seat_worlds"))
    for r, rc in out["reclassify"].items():
        s, h = rc["shape"], rc["holding"]
        print(f"== read 3, {r}: shape {s['changed']}/{s['classified']} distress cat-need-ticks change class "
              f"({s['changed_share']}); moves {s['moves']}; holding held ticks flag {h['held_flag']} -> "
              f"corrected {h['held_corrected']} (changed {h['changed']}), shared {h['shared_flag']} -> "
              f"{h['shared_corrected']}")
    a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
