"""Analyzer for mix_meow_probe.py raw JSONs -> the economics tables.

Per composition: emission/1k by model x kind; emission context vs
declined-legal baseline; per-kind causal impact (act-flip rate, msg-flip
rate, Move->Move steering), split same-model vs cross-model speakers in
mixed compositions; reply matrix; per-model welfare.

Cross-composition: each model's emission rate and welfare, homogeneous
vs mixed (voice accommodation + mixing cost), and dialect
comprehension: flip rates by (speaker model -> hearer model).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "results-raw"


def load(comp):
    return json.loads((RAW / f"{comp}.json").read_text())


def emissions_per_1k(d):
    kt = d["kitty_ticks"]
    per_model_ticks = defaultdict(int)
    for k, v in d["hap_n"].items():
        per_model_ticks[k] = v
    out = defaultdict(dict)
    for key, n in d["emit"].items():
        model, kind = key.split("|")
        out[model][kind] = round(1000 * n / max(1, per_model_ticks[model]), 2)
    return dict(out), kt


def context_table(d):
    rows = []
    for key, c in d["ctx"].items():
        model, kind, which = key.split("|")
        n = c[4]
        if n == 0:
            continue
        rows.append({"model": model, "kind": kind, "which": which, "n": n,
                     "need": round(c[0] / n, 1), "hap": round(c[1] / n, 1),
                     "dist": round(c[2] / n, 2),
                     "moving": round(c[3] / n, 3)})
    return rows


def flip_table(d):
    agg = defaultdict(lambda: defaultdict(int))
    for key, n in d["flip"].items():
        sp, hr, kind, what = key.split("|")
        rel = "same" if sp == hr else ("unattr" if sp == "?" else "cross")
        agg[(kind, rel)][what] += n
        agg[(kind, "all")][what] += n
        agg[(kind, f"{sp}->{hr}")][what] += n
    steer = defaultdict(lambda: defaultdict(int))
    for key, n in d["steer"].items():
        sp, hr, kind, what = key.split("|")
        steer[(kind, "all")][what] += n
    out = []
    for (kind, rel), c in sorted(agg.items()):
        if c["rows"] < 200:
            continue
        row = {"kind": kind, "who": rel, "rows": c["rows"],
               "act_flip": round(c["act"] / c["rows"], 4),
               "msg_flip": round(c["msg"] / c["rows"], 4)}
        s = steer.get((kind, "all"))
        if rel == "all" and s and s["bm"] > 100:
            row["p_toward_with"] = round(s["base_t"] / s["bm"], 3)
            row["p_toward_without"] = round(s["cf_t"] / s["bm"], 3)
        out.append(row)
    return out


def reply_matrix(d, min_n=20):
    out = []
    for key, n in sorted(d["reply"].items(), key=lambda x: -x[1]):
        if n < min_n:
            continue
        sm, sk, rm, rk = key.split("|")
        out.append({"heard": f"{sm}:{sk}", "replied": f"{rm}:{rk}", "n": n})
    return out


def welfare(d):
    return {m: {"happiness": round(d["hap"][m] / d["hap_n"][m], 2),
                "distress_share": round(
                    d.get("distress", {}).get(m, 0) / d["hap_n"][m], 5)}
            for m in d["hap_n"]}


def main():
    comps = sys.argv[1:] or [p.stem for p in sorted(RAW.glob("*.json"))]
    report = {}
    for comp in comps:
        d = load(comp)
        em, kt = emissions_per_1k(d)
        report[comp] = {
            "kitty_ticks": kt, "emissions_per_1k": em,
            "welfare": welfare(d), "flips": flip_table(d),
            "context": context_table(d), "replies": reply_matrix(d),
        }
    out = HERE / "econ-report.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    for comp, r in report.items():
        print(f"\n== {comp} ({r['kitty_ticks']} kitty-ticks) ==")
        print(" emissions/1k:", r["emissions_per_1k"])
        print(" welfare:", r["welfare"])
        for f in r["flips"]:
            if f["who"] in ("all", "same", "cross"):
                print(" flip:", f)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
