"""Summary printer: every derived table RESULTS.md uses, from the
reader's JSON (deterministic formatting only; the metrics live in
seating_read.py under its guard).

    seating_summary.py results-raw/seating-read.json
"""
import json
import sys

import numpy as np

CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
MSG = ["Silent", "WantFood", "WantWater", "Mew", "WantSleep", "WantPlay", "Purr",
       "WantCuddle", "WantBath", "HereFood", "HereWater", "HereCritter",
       "HereSunbeam", "Chirp", "Trill", "Ekekek"]
ACTIVITIES = ["Idle", "Rest", "Sleep", "Eat", "Drink", "Play", "Groom"]


def main(path):
    legs = json.load(open(path))["legs"]
    print("legs:", [(l["seed"], l["ticks"], l["aborted_at"]) for l in legs])
    print("nash per seed:", [round(l["welfare"]["nash_mean"], 4) for l in legs])
    print("gap mean/p95 per seed:", [(round(l["welfare"]["gap"]["mean"], 2),
                                      round(l["welfare"]["gap"]["p95"], 2)) for l in legs])

    print("\nPER-CAT (pooled across seeds: activity shares are means of per-seed shares;")
    print("cadences/latencies are means of per-seed medians; totals are sums)")
    hdr = ("| cat | " + " | ".join(ACTIVITIES) + " | contact | company | partnered | "
           "nearest med/p95 | hap mean/p5 | H bits | transH | home |")
    print(hdr)
    print("|" + "---|" * (len(ACTIVITIES) + 10))
    for k in range(5):
        rows = [l["cats"][k] for l in legs]
        acts = np.mean([r["activity_share"] for r in rows], 0)
        g = np.mean([[r["grouped"]["contact"], r["grouped"]["company"], r["grouped"]["partnered"]] for r in rows], 0)
        near = np.mean([[r["nearest_cat"]["median"], r["nearest_cat"]["p95"]] for r in rows], 0)
        hp = np.mean([[r["hap"]["mean"], r["hap"]["p5"]] for r in rows], 0)
        ent = np.mean([r["entropy_bits"] for r in rows])
        te = np.mean([r["transition_entropy_bits"] for r in rows])
        home = np.mean([r["home_range_tiles"] for r in rows])
        print(f"| {CATS[k]} | " + " | ".join(f"{v:.3f}" for v in acts)
              + f" | {g[0]:.3f} | {g[1]:.3f} | {g[2]:.3f} | {near[0]:.1f}/{near[1]:.1f}"
              + f" | {hp[0]:.1f}/{hp[1]:.1f} | {ent:.2f} | {te:.2f} | {home:.0f} |")

    print("\nNEEDS AND TENDING (pooled means of per-seed values; streak max = worst seed)")
    print("| cat | worst-gate med/p95 | max streak>=25 | eat cadence med | drink cadence med | water directness |")
    print("|---|---|---|---|---|---|")
    for k in range(5):
        rows = [l["cats"][k] for l in legs]
        wg = np.mean([r["worst_gate"]["median"] for r in rows])
        wg95 = np.mean([r["worst_gate"]["p95"] for r in rows])
        hs = max(r["high_streaks"]["max"] for r in rows)
        eat = np.mean([r["eat_cadence"]["median"] for r in rows])
        drink = np.mean([r["drink_cadence"]["median"] for r in rows])
        wd = [r["water_directness"] for r in rows if r["water_directness"] is not None]
        print(f"| {CATS[k]} | {wg:.1f}/{wg95:.1f} | {hs} | {eat:.0f} | {drink:.0f} | "
              + (f"{np.mean(wd):+.3f} |" if wd else "n/a |"))

    print("\nPLAY/SLEEP ELEMENT PARTNERS (summed ticks across seeds)")
    print("| cat | play ticks | element-play ticks | sleep ticks | beam-sleep ticks |")
    print("|---|---|---|---|---|")
    for k in range(5):
        rows = [l["cats"][k] for l in legs]
        print(f"| {CATS[k]} | {sum(r['play_ticks'] for r in rows)} | {sum(r['elem_play_ticks'] for r in rows)}"
              f" | {sum(r['sleep_ticks'] for r in rows)} | {sum(r['beam_sleep_ticks'] for r in rows)} |")

    print("\nPAIRS (means across seeds), sorted by pair ticks")
    print("| pair | pair ticks | scenes | dist med | territory JS | reciprocity |")
    print("|---|---|---|---|---|---|")
    pt = {}
    for l in legs:
        for k, v in l["pairs"].items():
            pt.setdefault(k, []).append((v["pair_ticks"], v["scenes"], v["dist"]["median"],
                                         l["territory_js"][k], l["reciprocity"].get(k)))
    for k, v in sorted(pt.items(), key=lambda x: -np.mean([a for a, *_ in x[1]])):
        a = np.mean([x[0] for x in v]); s = np.mean([x[1] for x in v])
        m = np.mean([x[2] for x in v]); j = np.mean([x[3] for x in v])
        rr = [x[4] for x in v if x[4] is not None]
        print(f"| {k} | {a:.0f} | {s:.0f} | {m:.1f} | {j:.3f} | " + (f"{np.mean(rr):.2f} |" if rr else "n/a |"))

    print("\nSOCIAL (pooled): concentration and modal top partner; distress totals")
    print("| cat | concentration | top partner | distress onsets | responded | latency med (mean of seeds) |")
    print("|---|---|---|---|---|---|")
    for k in range(5):
        rows = [l["cats"][k] for l in legs]
        conc = np.mean([r["partner_concentration"] for r in rows])
        tops = [r["top_partner"] for r in rows]
        on = sum(r["distress"]["onsets"] for r in rows)
        resp = sum(r["distress"]["responded"] for r in rows)
        lat = [r["distress"]["latency"]["median"] for r in rows if r["distress"]["latency"]["median"] is not None]
        # deterministic and tie-aware: ties print joined (gate r1 found
        # max(set(...)) hash-seed dependent on two real 2-2 ties)
        mx = max(tops.count(t) for t in tops)
        mode = "/".join(sorted({t for t in tops if tops.count(t) == mx}))
        print(f"| {CATS[k]} | {conc:.2f} | {mode} | {on} | {resp} | "
              + (f"{np.mean(lat):.1f} |" if lat else "n/a |"))

    print("\nSPEECH (pooled shares; top-3 non-silent heads; speak rate by worst-need bin <15 / 15-25 / >=25,")
    print("mean of per-seed rates)")
    for k in range(5):
        m = np.mean([l["cats"][k]["msg_share"] for l in legs], 0)
        top = np.argsort(m[1:])[::-1][:3] + 1
        rb = np.array([[x if x is not None else np.nan for x in l["cats"][k]["speak_rate_by_need_bin"]] for l in legs], float)
        rbm = np.nanmean(rb, 0)
        print(f"  {CATS[k]}: silent {m[0]:.3f}; " + ", ".join(f"{MSG[i]} {m[i]:.4f}" for i in top)
              + f"; rate by bin {rbm[0]:.3f}/{rbm[1]:.3f}/{rbm[2]:.3f}")

    print("\nROUTINE dominant lag per seed (ticks), per cat")
    for k in range(5):
        print(f"  {CATS[k]}: {[l['cats'][k]['routine']['dominant_lag'] for l in legs]}")

    print("\nCONVERGENCE (successive 2,000-tick window JS per seed): mean of first 3, mean of last 3, trend")
    for l in legs:
        c = l["convergence_js"]
        print(f"  {l['seed']}: first3 {np.mean(c[:3]):.3f}  last3 {np.mean(c[-3:]):.3f}  "
              f"min {min(c):.3f}  max {max(c):.3f}  n {len(c)}")


if __name__ == "__main__":
    main(sys.argv[1])
