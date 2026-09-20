"""Tier 5 reader (PREREG-tier5.md): per floor, the arms' own-seat placement from the swap legs, the
roster welfare with the arm against gen1-A on the same floor world and against floor 0, the all-arm
roster, and the prediction checks. Reuses tier2_read's pooling.
Usage: tier5_read.py TIER5_BATTERY_DIR TIER1_BATTERY_DIR [--out JSON]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_read as S, tier2_read as T

FLOORS = (10, 15, 20, 25)
SLOTS = {f"sg{f}-s{s}": f for f in FLOORS for s in (1, 2)}
KEEP, LOSE = 0.15, 0.10
FLOOR0 = "s3-b7-t3000-n6"


def ref(path):
    _h, rows = S.load_rows(path); a = S.aggregate(rows); p = a["pooled"]
    return {"placement": p["start_dist"][0], "in_beam": p["in_beam"], "happiness": p["happiness"], "nash_state": p["nash_state"],
            "sleep_share": p["sleep_share"], "start_need_mean": p["start_need_mean"], "need_lt5": p["start_need_bins"][0],
            "max_distress_age": p["max_distress_age"], "seeds_over_line": p["seeds_over_line"]}


def read(t5, t1):
    t5, t1 = Path(t5), Path(t1)
    out = {"floors": {}, "floor0": {s: ref(t1 / FLOOR0 / fn) for s, fn in S.FILES.items()}}
    for f in FLOORS:
        fl = {"reference": {s: ref(t5 / f"shallow-{f}" / fn) for s, fn in S.FILES.items() if (t5 / f"shallow-{f}" / fn).exists()}, "arms": {}}
        for s in (1, 2):
            slot = f"sg{f}-s{s}"; d = t5 / slot
            swaps = sorted(d.glob(f"gen1-A_s?-{slot}-c0-eval-*.jsonl")); alls = sorted(p for p in d.glob("gen1-A_s0-*-c0-eval-*.jsonl") if p.name.count(slot) == 5)
            arm = {"swap_legs": len(swaps)}
            if swaps:
                arm["own_seat"] = T.arm_in_seat(swaps, slot); r = T.pool(swaps)["pooled"]
                arm["roster_with_arm"] = {"placement": r["start_dist"][0], "in_beam": r["in_beam"], "happiness": r["happiness"], "nash_state": r["nash_state"],
                                          "sleep_share": r["sleep_share"], "need_lt5": r["start_need_bins"][0], "max_distress_age": r["max_distress_age"], "seeds_over_line": r["seeds_over_line"]}
            if alls:
                a = T.pool(alls)["pooled"]
                arm["all_arm"] = {"placement": a["start_dist"][0], "in_beam": a["in_beam"], "happiness": a["happiness"], "nash_state": a["nash_state"],
                                  "sleep_share": a["sleep_share"], "max_distress_age": a["max_distress_age"], "seeds_over_line": a["seeds_over_line"]}
            fl["arms"][slot] = arm
        out["floors"][f] = fl
    out["checks"] = checks(out)
    return out


def checks(out):
    g0 = out["floor0"]["gen1-A"]
    c = {"P1_floor_felt": {}, "P2_placement": {}, "P3_arms_vs_frozen": {}, "P5_over_line": {}}
    for f, fl in out["floors"].items():
        g = fl["reference"].get("gen1-A")
        if g:
            c["P1_floor_felt"][f] = {"gen1A_hap_drop": g0["happiness"] - g["happiness"], "sleep_share": g["sleep_share"], "start_need_mean": g["start_need_mean"],
                                     "felt_over_0.3": (g0["happiness"] - g["happiness"]) > 0.3}
        pl = [fl["arms"].get(f"sg{f}-s{s}", {}).get("own_seat", {}).get("placement") for s in (1, 2)]
        c["P2_placement"][f] = {"own_seat": pl, "both_ge_keep": all(v is not None and v >= KEEP for v in pl), "both_lt_lose": all(v is not None and v < LOSE for v in pl)}
        if g:
            c["P3_arms_vs_frozen"][f] = {}
            for s in (1, 2):
                r = fl["arms"].get(f"sg{f}-s{s}", {}).get("roster_with_arm")
                if r:
                    c["P3_arms_vs_frozen"][f][f"s{s}"] = {"hap_over_frozen": r["happiness"] - g["happiness"], "nash_over_frozen": r["nash_state"] - g["nash_state"],
                                                          "recovers_floor_cost": (r["happiness"] - g["happiness"]) >= (g0["happiness"] - g["happiness"])}
        c["P5_over_line"][f] = {"frozen": (g or {}).get("seeds_over_line"), **{f"s{s}": fl["arms"].get(f"sg{f}-s{s}", {}).get("roster_with_arm", {}).get("seeds_over_line") for s in (1, 2)}}
    p2 = c["P2_placement"]
    c["P2_holds_at_20_and_25"] = all(p2.get(f, {}).get("both_ge_keep") for f in (20, 25)) if all(f in p2 for f in (20, 25)) else None
    return c


def md(out):
    g0 = out["floor0"]; lines = ["| floor | teacher placement | gen1-A placement / hap / Nash / sleep | arm s1 / s2 placement (own seat) | roster hap with arm s1 / s2 | Nash s1 / s2 | all-arm placement s1 / s2 | over 150 (frozen; s1; s2) |", "|---|---|---|---|---|---|---|---|"]
    lines.append(f"| 0 | {g0['scripted']['placement']:.3f} | {g0['gen1-A']['placement']:.3f} / {g0['gen1-A']['happiness']:.2f} / {g0['gen1-A']['nash_state']:.3f} / {g0['gen1-A']['sleep_share']:.3f} | (tier 2: 0.070 / 0.037) | 92.29 / 92.37 | 0.923 / 0.923 | 0.067 / 0.035 | |")
    for f, fl in out["floors"].items():
        r = fl["reference"]; a = fl["arms"]
        def v(slot, key, sub="own_seat", fmt="{:.3f}"):
            x = a.get(slot, {}).get(sub, {}).get(key); return "" if x is None else fmt.format(x)
        s1, s2 = f"sg{f}-s1", f"sg{f}-s2"
        lines.append(f"| {f} | {r['scripted']['placement']:.3f} | {r['gen1-A']['placement']:.3f} / {r['gen1-A']['happiness']:.2f} / {r['gen1-A']['nash_state']:.3f} / {r['gen1-A']['sleep_share']:.3f} | {v(s1,'placement')} / {v(s2,'placement')} | {v(s1,'happiness','roster_with_arm','{:.2f}')} / {v(s2,'happiness','roster_with_arm','{:.2f}')} | {v(s1,'nash_state','roster_with_arm')} / {v(s2,'nash_state','roster_with_arm')} | {v(s1,'placement','all_arm')} / {v(s2,'placement','all_arm')} | {len(r['gen1-A']['seeds_over_line'])}; {len(a.get(s1,{}).get('roster_with_arm',{}).get('seeds_over_line',[]))}; {len(a.get(s2,{}).get('roster_with_arm',{}).get('seeds_over_line',[]))} |")
    return "\n".join(lines)


if __name__ == "__main__":
    res = read(sys.argv[1], sys.argv[2])
    print(md(res)); print(json.dumps(res["checks"], indent=1, default=str))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1, default=str)
