"""Tier 6 reader (PREREG-tier6.md): per beam count under floor 15, the frozen comparators, the arms'
own-seat read from the swap legs, the roster with the arm, the all-arm roster, the transfer read
(count-6 arms on the other counts), and the prediction checks. Count 6 is tier 5's shallow-15 battery
and sg15 arms. Reuses tier2_read's pooling.
Usage: tier6_read.py TIER6_BATTERY_DIR TIER5_BATTERY_DIR [--out JSON]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_read as S, tier2_read as T

COUNTS = (5, 6, 7, 8)
KEEP = 0.15
FLOOR0_ALLARM = (91.9, 92.3)     # tier 2's all-arm rosters on the package world at floor 0 (RESULTS §Tier 5 table, row 0)
TRANSFER_HAP, TRANSFER_PL = 0.5, 0.10


N_SEEDS = 30


def slot(n, s):
    return f"sg15-s{s}" if n == 6 else f"cnt{n}-s{s}"


def complete(p):
    """A leg is readable once its header and all N_SEEDS rows are on disk (the driver's own skip rule);
    a leg the driver is still writing is not."""
    p = Path(p)
    return p.exists() and sum(1 for _ in p.open()) >= N_SEEDS + 1


def pooled(files):
    p = T.pool(files)["pooled"]
    return {"placement": p["start_dist"][0], "in_beam": p["in_beam"], "conducted": p["conducted"], "happiness": p["happiness"],
            "nash_state": p["nash_state"], "sleep_share": p["sleep_share"], "start_need_mean": p["start_need_mean"],
            "need_lt5": p["start_need_bins"][0], "max_distress_age": p["max_distress_age"], "seeds_over_line": p["seeds_over_line"]}


def read(t6, t5):
    t6, t5 = Path(t6), Path(t5)
    out = {"counts": {}}
    for n in COUNTS:
        ref_dir = t5 / "shallow-15" if n == 6 else t6 / f"count-{n}"
        c = {"reference": {s: pooled([ref_dir / fn]) for s, fn in S.FILES.items() if complete(ref_dir / fn)}, "arms": {}, "transfer": {}}
        for s in (1, 2):
            sl = slot(n, s); d = (t5 if n == 6 else t6) / sl
            swaps = sorted(p for p in d.glob(f"gen1-A_s?-{sl}-c0-eval-*.jsonl") if complete(p)); alls = sorted(p for p in d.glob("gen1-A_s0-*-c0-eval-*.jsonl") if p.name.count(sl) == 5 and complete(p))
            arm = {"swap_legs": len(swaps)}
            if swaps:
                arm["own_seat"] = T.arm_in_seat(swaps, sl); arm["roster_with_arm"] = pooled(swaps)
            if alls:
                arm["all_arm"] = pooled(alls)
            c["arms"][f"s{s}"] = arm
            if n != 6:
                td = t6 / f"transfer-sg15-s{s}-count-{n}"
                talls = sorted(p for p in td.glob("gen1-A_s0-*-c0-eval-*.jsonl") if p.name.count(f"sg15-s{s}") == 5 and complete(p))
                if talls:
                    c["transfer"][f"s{s}"] = pooled(talls)
        out["counts"][n] = c
    out["checks"] = checks(out)
    return out


def _all(out, n, s, key):
    return out["counts"].get(n, {}).get("arms", {}).get(f"s{s}", {}).get("all_arm", {}).get(key)


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if len(vals) == 2 else None


def checks(out):
    c = {}
    # P1: all-arm welfare orders with count on both seeds; the gain shrinks; ends against floor 0
    hap = {n: [_all(out, n, s, "happiness") for s in (1, 2)] for n in COUNTS}
    nash = {n: [_all(out, n, s, "nash_state") for s in (1, 2)] for n in COUNTS}
    have = all(v is not None for n in COUNTS for v in hap[n])
    p1 = {"all_arm_hap": hap, "all_arm_nash": nash}
    if have:
        m = {n: _mean(hap[n]) for n in COUNTS}
        p1["orders_both_seeds"] = all(hap[a][s] < hap[b][s] for a, b in zip(COUNTS, COUNTS[1:]) for s in (0, 1))
        p1["nash_orders_both_seeds"] = all(nash[a][s] < nash[b][s] for a, b in zip(COUNTS, COUNTS[1:]) for s in (0, 1))
        p1["gain_5_6"] = m[6] - m[5]; p1["gain_7_8"] = m[8] - m[7]; p1["gain_shrinks"] = p1["gain_5_6"] > p1["gain_7_8"]
        p1["count8_within_1_of_floor0"] = m[8] >= FLOOR0_ALLARM[0] - 1.0
        p1["count5_over_1p5_under_floor0"] = m[5] < FLOOR0_ALLARM[1] - 1.5
        # the decision line: smallest count whose gain to the next sits inside the two-seed spread at that count
        line = None
        for a, b in zip(COUNTS, COUNTS[1:]):
            if m[b] - m[a] <= abs(hap[a][0] - hap[a][1]):
                line = a; break
        p1["line"] = line if line is not None else COUNTS[-1]
        p1["line_note"] = "gain to the next count inside the seed spread" if line is not None else "every gain exceeds the spread; the largest count screened"
    c["P1_welfare_with_count"] = p1
    # P2: frozen minds flat, teacher placement rises
    g = {n: out["counts"][n]["reference"].get("gen1-A") for n in COUNTS}
    t = {n: out["counts"][n]["reference"].get("scripted") for n in COUNTS}
    p2 = {"gen1A_hap": {n: (g[n] or {}).get("happiness") for n in COUNTS}, "teacher_placement": {n: (t[n] or {}).get("placement") for n in COUNTS},
          "teacher_hap": {n: (t[n] or {}).get("happiness") for n in COUNTS}}
    if all(g.values()):
        hs = [g[n]["happiness"] for n in COUNTS]; p2["gen1A_span"] = max(hs) - min(hs); p2["frozen_flat"] = p2["gen1A_span"] < 0.3
    if all(t.values()):
        pl = [t[n]["placement"] for n in COUNTS]; p2["teacher_placement_rises"] = all(a < b for a, b in zip(pl, pl[1:]))
    c["P2_frozen_flat"] = p2
    # P3: placement kept everywhere, all-arm placement orders with count, conducted falls
    own = {n: [out["counts"][n]["arms"].get(f"s{s}", {}).get("own_seat", {}).get("placement") for s in (1, 2)] for n in COUNTS}
    p3 = {"own_seat_placement": own, "all_kept": all(v is not None and v >= KEEP for n in COUNTS for v in own[n]) if all(v is not None for n in COUNTS for v in own[n]) else None}
    ap = {n: _mean([_all(out, n, s, "placement") for s in (1, 2)]) for n in COUNTS}; cd = {n: _mean([_all(out, n, s, "conducted") for s in (1, 2)]) for n in COUNTS}
    p3["all_arm_placement"] = ap; p3["all_arm_conducted"] = cd
    if all(v is not None for v in ap.values()):
        p3["placement_orders"] = all(ap[a] < ap[b] for a, b in zip(COUNTS, COUNTS[1:]))
        p3["conducted_falls"] = all(cd[a] > cd[b] for a, b in zip(COUNTS, COUNTS[1:]))
    c["P3_placement"] = p3
    # P4: transfer within the lines, seed-matched
    p4 = {}
    for n in (5, 7, 8):
        for s in (1, 2):
            tr = out["counts"][n]["transfer"].get(f"s{s}"); re_ = out["counts"][n]["arms"].get(f"s{s}", {}).get("all_arm")
            if tr and re_:
                dh, dp = tr["happiness"] - re_["happiness"], tr["placement"] - re_["placement"]
                p4[f"{n}-s{s}"] = {"hap_transfer_minus_retrained": dh, "placement_transfer_minus_retrained": dp, "holds": abs(dh) <= TRANSFER_HAP and abs(dp) <= TRANSFER_PL}
    p4["holds_everywhere"] = all(v["holds"] for k, v in p4.items() if k != "holds_everywhere") if len(p4) == 6 else None
    c["P4_transfer"] = p4
    # P5: farming and distress, reported
    c["P5_report"] = {n: {"need_lt5_all_arm": [_all(out, n, s, "need_lt5") for s in (1, 2)], "over_line_all_arm": [_all(out, n, s, "seeds_over_line") for s in (1, 2)],
                          "over_line_frozen": (g[n] or {}).get("seeds_over_line")} for n in COUNTS}
    return c


def md(out):
    L = ["| count | teacher placement / hap | gen1-A placement / hap / Nash | arm own-seat placement s1 / s2 | all-arm hap s1 / s2 | all-arm Nash s1 / s2 | all-arm placement / conducted (mean) | transfer hap s1 / s2 (count-6 arms) | over 150 all-arm s1; s2 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for n, c in out["counts"].items():
        r = c["reference"]; a = c["arms"]; tr = c["transfer"]
        f = lambda x, fmt="{:.3f}": "" if x is None else fmt.format(x)
        L.append(f"| {n} | {f((r.get('scripted') or {}).get('placement'))} / {f((r.get('scripted') or {}).get('happiness'), '{:.2f}')} | "
                 f"{f((r.get('gen1-A') or {}).get('placement'))} / {f((r.get('gen1-A') or {}).get('happiness'), '{:.2f}')} / {f((r.get('gen1-A') or {}).get('nash_state'))} | "
                 f"{f(a.get('s1', {}).get('own_seat', {}).get('placement'))} / {f(a.get('s2', {}).get('own_seat', {}).get('placement'))} | "
                 f"{f(a.get('s1', {}).get('all_arm', {}).get('happiness'), '{:.2f}')} / {f(a.get('s2', {}).get('all_arm', {}).get('happiness'), '{:.2f}')} | "
                 f"{f(a.get('s1', {}).get('all_arm', {}).get('nash_state'))} / {f(a.get('s2', {}).get('all_arm', {}).get('nash_state'))} | "
                 f"{f(out['checks']['P3_placement']['all_arm_placement'].get(n))} / {f(out['checks']['P3_placement']['all_arm_conducted'].get(n))} | "
                 f"{f(tr.get('s1', {}).get('happiness'), '{:.2f}')} / {f(tr.get('s2', {}).get('happiness'), '{:.2f}')} | "
                 f"{len(a.get('s1', {}).get('all_arm', {}).get('seeds_over_line', []))}; {len(a.get('s2', {}).get('all_arm', {}).get('seeds_over_line', []))} |")
    return "\n".join(L)


if __name__ == "__main__":
    res = read(sys.argv[1], sys.argv[2])
    print(md(res)); print(json.dumps(res["checks"], indent=1, default=str))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1, default=str)
