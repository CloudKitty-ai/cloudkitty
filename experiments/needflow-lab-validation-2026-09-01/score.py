#!/usr/bin/env python3
"""Score the needflow lab validation against prereg.md's pinned bars.

Reads results-raw/{arm}-{seed}-census.json (scene_census.py raws) and
{arm}-{seed}-final.json (final /welfare), pools per arm (sum counts /
sum cat-ticks), and prints every gate/bar with its measured value. The
bar definitions here transcribe prereg.md §Pinned bars; written before
the first run finished (2026-09-01), the model rows copied from needflow
RESULTS.md.

usage: score.py [results-raw dir]
"""
import json
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "results-raw"
SEEDS = [20260901, 20260902, 20260903]
ARMS = ["canon", "serve"]
CLASSES = ["rest", "rest-solo", "cosleep", "sleep-solo", "groom-other",
           "groom-self", "play-duet", "play-elem", "play-solo", "eat", "drink"]

# needflow RESULTS.md rows (scenes / 1k cat-ticks; needs on 0-100).
MODEL = {
    "canon": {"rest": 12.8, "cosleep": 16.7, "sleep-solo": 3.0, "groom-self": 4.3,
              "groom-other": 15.8, "play-solo": 13.2, "play-duet": 27.0,
              "cuddle": 7.6, "bath": 5.23, "happiness": 95.4},
    "serve": {"rest": 5.72, "cosleep": 17.23, "groom-self": 1.62, "groom-other": 27.77,
              "cuddle": 6.71, "bath": 3.45, "happiness": 95.83},
}


def load(arm, seed):
    c = json.loads((RAW / f"{arm}-{seed}-census.json").read_text())["summary"]
    f = json.loads((RAW / f"{arm}-{seed}-final.json").read_text())
    return c, f["welfare"]


def pool(summaries):
    cat = sum(s["cat_ticks"] for s in summaries)
    counts = {c: sum(s["counts"].get(c, 0) for s in summaries) for c in CLASSES}
    per_1k = {c: 1000.0 * counts[c] / cat for c in CLASSES}
    polls = sum(s["polls_in_window"] for s in summaries)
    needs = {n: sum(s["need_means"][n] * s["polls_in_window"] for s in summaries) / polls
             for n in summaries[0]["need_means"]}
    happy = sum(s["happiness_mean"] * s["polls_in_window"] for s in summaries) / polls
    spans = {}
    for c in CLASSES:
        w = [(s["mean_span"][c], s["counts"][c]) for s in summaries
             if c in s["mean_span"]]
        if w:
            spans[c] = sum(m * n for m, n in w) / sum(n for _, n in w)
    return {"cat_ticks": cat, "counts": counts, "per_1k": per_1k, "needs": needs,
            "happiness": happy, "mean_span": spans,
            "play_total": per_1k["play-duet"] + per_1k["play-elem"] + per_1k["play-solo"],
            "cosleep_to_solo": per_1k["cosleep"] / per_1k["sleep-solo"]
            if per_1k["sleep-solo"] else None}


def main():
    runs = {(a, s): load(a, s) for a in ARMS for s in SEEDS}
    pooled = {a: pool([runs[(a, s)][0] for s in SEEDS]) for a in ARMS}
    out = {"validity": {}, "emit": {}, "shape": {}, "model": {}, "report": {}}
    ok = lambda b: "PASS" if b else "MISS"

    print("== validity (per run)")
    for (a, s), (c, w) in runs.items():
        # /welfare: {"threshold", "alarm_live", "entries": [...]} (spec 040).
        wd = {"alarm_live": w["alarm_live"], "entries": len(w["entries"]),
              "max_age": max((e.get("age", 0) for e in w["entries"]), default=0)}
        out["validity"][f"{a}-{s}"] = {"polls_in_window": c["polls_in_window"],
                                       "ticks": c["ticks"], "watchdog": wd}
        print(f"  {a}-{s}: polls {c['polls_in_window']} {ok(c['polls_in_window'] >= 1000)}"
              f"  ticks {c['ticks']}  watchdog {wd}")

    print("== emit gates (canon, every seed)")
    for s in SEEDS:
        c = runs[("canon", s)][0]
        e1 = all(n >= 1 for n in c["rest_by_window"])
        t = c["rest_tiers"]
        e2 = t["mutual_emitting"] >= 1 and t["drip_emitting"] >= 1
        e3 = all(c["counts"].get(k, 0) > 0 for k in
                 ("cosleep", "sleep-solo", "groom-self", "groom-other", "play-duet"))
        out["emit"][s] = {"E1": e1, "E2": e2, "E3": e3, "rest_by_window": c["rest_by_window"],
                          "tiers": t}
        print(f"  seed {s}: E1 {ok(e1)} {c['rest_by_window']}  E2 {ok(e2)} {t}  E3 {ok(e3)}")

    P = pooled
    print("== shape bars (canon pooled)")
    s1 = P["canon"]["per_1k"]["rest"] >= 1.0
    s2 = (P["canon"]["cosleep_to_solo"] or 0) >= 3.0
    out["shape"] = {"S1": {"rest_per_1k": P["canon"]["per_1k"]["rest"], "pass": s1},
                    "S2": {"cosleep_to_solo": P["canon"]["cosleep_to_solo"], "pass": s2}}
    print(f"  S1 rest/1k {P['canon']['per_1k']['rest']:.2f} {ok(s1)}")
    print(f"  S2 cosleep:solo {P['canon']['cosleep_to_solo']:.2f}:1 {ok(s2)}")

    print("== comparative model bars (canon vs serve; pooled AND every seed pair)")

    def per_seed(key, getter):
        return [(getter(runs[("canon", s)][0]), getter(runs[("serve", s)][0])) for s in SEEDS]

    def directional(name, key, getter, want_serve_greater, model_pct):
        cv, sv = getter(P["canon"], pooled=True), getter(P["serve"], pooled=True)
        pairs = per_seed(key, lambda c: getter(c, pooled=False))
        sign = (lambda x, y: y > x) if want_serve_greater else (lambda x, y: y < x)
        p_pool = sign(cv, sv)
        p_seeds = all(sign(x, y) for x, y in pairs)
        pct = (sv - cv) / cv * 100 if cv else float("nan")
        out["model"][name] = {"canon": cv, "serve": sv, "delta_pct": pct, "pairs": pairs,
                              "pooled": p_pool, "every_seed": p_seeds,
                              "pass": p_pool and p_seeds, "model_pct": model_pct}
        print(f"  {name} {key}: canon {cv:.3f} serve {sv:.3f} ({pct:+.0f}%, model {model_pct:+d}%)"
              f"  pooled {ok(p_pool)} seeds {ok(p_seeds)} "
              f"{[(round(x, 2), round(y, 2)) for x, y in pairs]}")

    rate = lambda k: (lambda d, pooled: d["per_1k"][k] if pooled else d["per_1k_cat_ticks"][k])
    need = lambda k: (lambda d, pooled: d["needs"][k] if pooled else d["need_means"][k])
    directional("M1", "groom-other", rate("groom-other"), True, 76)
    directional("M2", "groom-self", rate("groom-self"), False, -62)
    directional("M3", "rest", rate("rest"), False, -55)
    directional("M4", "mean bath", need("bath"), False, -34)

    cc, cs = P["canon"]["per_1k"]["cosleep"], P["serve"]["per_1k"]["cosleep"]
    m5 = abs(cs - cc) <= 0.25 * cc
    out["model"]["M5"] = {"canon": cc, "serve": cs, "tol": 0.25 * cc, "pass": m5}
    print(f"  M5 cosleep: canon {cc:.2f} serve {cs:.2f} |Δ| {abs(cs - cc):.2f} ≤ {0.25 * cc:.2f} {ok(m5)}")
    pc, ps = P["canon"]["play_total"], P["serve"]["play_total"]
    tol = max(2.0, 0.10 * pc)
    m6 = abs(ps - pc) <= tol
    out["model"]["M6"] = {"canon": pc, "serve": ps, "tol": tol, "pass": m6}
    print(f"  M6 play total: canon {pc:.2f} serve {ps:.2f} |Δ| {abs(ps - pc):.2f} ≤ {tol:.2f} {ok(m6)}")

    print("== report-only")
    for a in ARMS:
        p = P[a]
        print(f"  [{a}] cat-ticks {p['cat_ticks']}  happiness {p['happiness']:.2f}"
              f" (model {MODEL[a]['happiness']})  cuddle {p['needs']['cuddle']:.2f}"
              f" (model {MODEL[a]['cuddle']})  bath {p['needs']['bath']:.2f} (model {MODEL[a]['bath']})")
        for c in CLASSES:
            m = MODEL[a].get(c)
            ratio = (p["per_1k"][c] / m) if m else None
            rng = [runs[(a, s)][0]["per_1k_cat_ticks"][c] for s in SEEDS]
            flag = "  <-- >3x gap" if ratio is not None and (ratio > 3 or ratio < 1 / 3) else ""
            print(f"    {c:12s} {p['per_1k'][c]:7.2f}/1k  seeds {min(rng):6.2f}-{max(rng):6.2f}"
                  f"  span {p['mean_span'].get(c, float('nan')):6.2f}"
                  + (f"  model {m:6.2f} ratio {ratio:5.2f}{flag}" if m else ""))
        out["report"][a] = {"pooled": p, "per_seed": {
            s: {"per_1k": runs[(a, s)][0]["per_1k_cat_ticks"],
                "needs": runs[(a, s)][0]["need_means"],
                "happiness": runs[(a, s)][0]["happiness_mean"]} for s in SEEDS}}

    allpass = (all(v["E1"] and v["E2"] and v["E3"] for v in out["emit"].values())
               and s1 and s2 and all(out["model"][k]["pass"] for k in
                                     ("M1", "M2", "M3", "M4", "M5", "M6")))
    print(f"== verdict: model {'VALIDATED' if allpass else 'NOT validated'} for step-2 purposes")
    (RAW / "score.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
