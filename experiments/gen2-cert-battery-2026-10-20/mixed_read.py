#!/usr/bin/env python3
"""Mixed-roster reads, as MIXED-DECLARATION.md §Reads declares them
(committed before the run). Rosters come from cert_harness_fog's
SEATINGS (one home). Baselines: the step-8 uniform rows (same worlds,
same seats) and the vision-law scripted comparator.

- POST-STOP uniform baselines (gen2-deviations entry 4: g2-s2 at
  40x40) are excluded from every pooled read and printed separately.
- A pair is FLAGGED when either row aborted (it ran fewer ticks);
  pooled numbers print with and without flagged pairs. P1 and P2 are
  scored on the unflagged numbers (a flagged baseline averages over a
  shorter run); the flagged-inclusive number prints beside them.
- A mixed leg that never ran (its roster stopped first) is reported
  as not run, never as zero.

    mixed_read.py [--out mixed-read.json]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
from cert_harness_fog import SEATINGS  # noqa: E402

_RAW = HERE.parent / "gen2-comparator-legs-2026-10-14/results-raw"
CMP_FILE = {20: _RAW / "legs/size20/scripted-g2cmp-30x20000.jsonl",
            40: _RAW / "vision5-40/legs/size40/scripted-g2cmp-30x20000.jsonl"}
PINNED = {20: 81.921, 40: 81.634}
MIXES = ("g2-mix1", "g2-mix2", "g2-mix3")
SIZES = (20, 40)
POST_STOP = {("s2", 40)}
P1 = (-1.5, 0.5)


def by_seed(p):
    if not p.exists():
        return None
    rs = [json.loads(l) for l in p.read_text().splitlines()[1:]]
    return {r["seed"]: r for r in rs}


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def r3(x):
    return None if x is None else round(x, 3)


def summ(xs):
    return {"n": len(xs), "mean": r3(mean(xs)), "positive": sum(x > 0 for x in xs),
            "range": [r3(min(xs)), r3(max(xs))] if xs else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "mixed-read.json")
    a = ap.parse_args()
    nets = {m: [s.split("-")[-1] for s in SEATINGS[m]] for m in MIXES}
    cmp_, unif, mixed = {}, {}, {}
    for z in SIZES:
        cmp_[z] = by_seed(CMP_FILE[z])
        assert len(cmp_[z]) == 30
        assert round(mean([team(r) for r in cmp_[z].values()]), 3) == PINNED[z]
        for n in ("s1", "s2", "s4"):
            u = by_seed(HERE / f"results-raw/g2-{n}/legs/size{z}/g2-{n}-g2cmp-30x20000.jsonl")
            assert u is not None and set(u) == set(cmp_[z]), (n, z)
            unif[(n, z)] = u
        for m in MIXES:
            mixed[(m, z)] = by_seed(HERE / f"results-raw/{m}/legs/size{z}/{m}-g2cmp-30x20000.jsonl")
            if mixed[(m, z)] is not None:
                assert set(mixed[(m, z)]) == set(cmp_[z]), (m, z)

    ab = lambda r: "aborted_streak" in r  # noqa: E731
    out = {"rosters": {m: nets[m] for m in MIXES}, "by_size": {}}
    for z in SIZES:
        S = out["by_size"][z] = {"rosters": {}, "networks": {}, "post_stop": []}
        pool = {"all": [], "clean": []}
        net_pool = {n: {"all": [], "clean": []} for n in ("s1", "s2", "s4")}
        disp_pool = {"all": [], "clean": []}
        aborts_total = 0
        for m in MIXES:
            M = mixed[(m, z)]
            if M is None:
                S["rosters"][m] = "not run"
                continue
            per_world, per_world_clean = [], []
            team_d = []
            gc_d = []
            for w, r in sorted(M.items()):
                team_d.append(team(r) - team(cmp_[z][w]))
                ds, flag = [], ab(r)
                for k, n in enumerate(nets[m]):
                    u = unif[(n, z)][w]
                    d = r["mean_happiness"][k] - u["mean_happiness"][k]
                    td = (r["dispersion"]["together_share"][k]
                          - u["dispersion"]["together_share"][k])
                    if (n, z) in POST_STOP:
                        S["post_stop"].append({"roster": m, "seed": w, "seat": k,
                                               "net": n, "delta": r3(d)})
                        continue
                    f = ab(r) or ab(u)
                    flag = flag or f
                    ds.append(d)
                    pool["all"].append(d)
                    net_pool[n]["all"].append(d)
                    disp_pool["all"].append(td)
                    if not f:
                        pool["clean"].append(d)
                        net_pool[n]["clean"].append(d)
                        disp_pool["clean"].append(td)
                per_world.append(mean(ds))
                if not flag:
                    per_world_clean.append(mean(ds))
                matched = mean([unif[(n, z)][w]["dispersion"]["mean_group_count"]
                                for n in nets[m]])
                gc_d.append(r["dispersion"]["mean_group_count"] - matched)
            tm = mean([team(r) for r in M.values()])
            md = mean(team_d)
            mda = [r["max_distress_age"] for r in M.values()]
            abr = sorted((w, r["aborted_streak"]["at_tick"]) for w, r in M.items() if ab(r))
            aborts_total += len(abr)
            multi = sum(sum(x >= 300 for x in r["max_distress_age_seat"]) >= 3
                        for r in M.values())
            S["rosters"][m] = {
                "company_effect": summ(per_world),
                "company_effect_unflagged": summ(per_world_clean),
                "team_mean": r3(tm),
                "vs_scripted": {**summ(team_d),
                                "shape": ("PASS-shaped" if md >= 0 and tm >= PINNED[z]
                                          else "MISS-shaped") + " (not a certificate)"},
                "worst_streak_mean": round(mean(mda), 1), "worst_streak_max": max(mda),
                "aborts": abr, "multi_cat_300": multi,
                "group_count_delta_vs_matched_uniform": r3(mean(gc_d)),
            }
        for n in ("s1", "s2", "s4"):
            seats_m = [(m, k) for m in MIXES if mixed[(m, z)] is not None
                       for k, x in enumerate(nets[m]) if x == n]
            worst_mix = max((mixed[(m, z)][w]["max_distress_age_seat"][k]
                             for m, k in seats_m for w in mixed[(m, z)]), default=None)
            worst_uni = max((unif[(n, z)][w]["max_distress_age_seat"][k]
                             for m, k in seats_m for w in unif[(n, z)]), default=None)
            S["networks"][n] = {
                "company_effect": summ(net_pool[n]["all"]),
                "company_effect_unflagged": summ(net_pool[n]["clean"]),
                "post_stop_baseline": (n, z) in POST_STOP,
                "worst_seat_streak_mixed": worst_mix,
                "worst_seat_streak_uniform_same_seats": worst_uni}
        S["pooled_company_effect"] = summ(pool["all"])
        S["pooled_company_effect_unflagged"] = summ(pool["clean"])
        S["pooled_together_share_delta"] = r3(mean(disp_pool["all"]))
        S["pooled_together_share_delta_unflagged"] = r3(mean(disp_pool["clean"]))
        S["aborts_total"] = aborts_total

    s20 = out["by_size"][20]
    p1 = s20["pooled_company_effect_unflagged"]["mean"]
    p2 = s20["pooled_together_share_delta_unflagged"]
    ran = [m for m in MIXES for z in SIZES if mixed[(m, z)] is not None]
    out["predictions"] = {
        "P1_company_effect_20_in_bracket": None if p1 is None else P1[0] <= p1 <= P1[1],
        "P1_value": p1, "P1_bracket": list(P1),
        "P2_together_share_delta_20_negative": None if p2 is None else p2 < 0,
        "P2_value": p2,
        "P3_zero_aborts_20_40": sum(out["by_size"][z]["aborts_total"] for z in SIZES) == 0,
        "legs_run": len(ran), "legs_declared": len(MIXES) * len(SIZES)}

    for z in SIZES:
        S = out["by_size"][z]
        print(f"== {z}x{z}")
        for m in MIXES:
            R = S["rosters"][m]
            if R == "not run":
                print(f"  {m}: NOT RUN")
                continue
            ce, cs = R["company_effect"], R["vs_scripted"]
            print(f"  {m} {nets[m]}: team {R['team_mean']} | vs scripted {cs['mean']:+.3f} "
                  f"({cs['positive']}/30 +) {cs['shape']} | company effect {ce['mean']:+.3f} "
                  f"({ce['positive']}/{ce['n']} worlds +, range {ce['range']}) | streak "
                  f"{R['worst_streak_mean']}/{R['worst_streak_max']} aborts {R['aborts']} "
                  f"multi300 {R['multi_cat_300']} | groups {R['group_count_delta_vs_matched_uniform']:+.3f}")
        for n, N in S["networks"].items():
            ce = N["company_effect"]
            tag = " [s2 baseline POST-STOP: excluded]" if N["post_stop_baseline"] else ""
            print(f"  net {n}: company effect {ce['mean']} over {ce['n']} seat-worlds "
                  f"({ce['positive']} +){tag} | worst seat streak mixed "
                  f"{N['worst_seat_streak_mixed']} vs uniform {N['worst_seat_streak_uniform_same_seats']}")
        pc, pu = S["pooled_company_effect"], S["pooled_company_effect_unflagged"]
        print(f"  pooled company effect {pc['mean']} (n {pc['n']}) | unflagged {pu['mean']} "
              f"(n {pu['n']}) | together_share delta {S['pooled_together_share_delta']} "
              f"(unflagged {S['pooled_together_share_delta_unflagged']})")
        if S["post_stop"]:
            ps = [x["delta"] for x in S["post_stop"]]
            print(f"  POST-STOP-baseline pairs (excluded): n {len(ps)} mean {r3(mean(ps))}")
    print("predictions:", json.dumps(out["predictions"]))
    a.out.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
