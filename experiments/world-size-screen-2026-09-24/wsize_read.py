"""Reader for the world-size × density screen (PREREG.md, frozen
2026-09-24). Deterministic: the cell → battery map is written out in
full below; paired per-seed deltas are computed within each config
against that config's intact leg. The size20 hearing cells are the
fog-deafening screen's recorded legs (band 900101), per the prereg.

    wsize_read.py --out read.json [--md read.md]
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "results-raw" / "battery"
DEAF = HERE.parent / "fog-deafening-2026-09-23" / "results-raw" / "battery"

CELLS = {
    "size20": {"intact": DEAF / "gen1-A-c0-deaf-30x20000.jsonl",
               "dir": DEAF / "gen1-A-deaf-dir-r16-c0-deaf-30x20000.jsonl",
               "rows": DEAF / "gen1-A-deaf-rows-c0-deaf-30x20000.jsonl"},
    "size28": {"scripted": B / "size28/scripted-wsize-30x20000.jsonl",
               "intact": B / "size28/gen1-A-c0-wsize-30x20000.jsonl",
               "dir": B / "size28/gen1-A-deaf-dir-r19-c0-wsize-30x20000.jsonl",
               "rows": B / "size28/gen1-A-deaf-rows-c0-wsize-30x20000.jsonl"},
    "size40": {"scripted": B / "size40/scripted-wsize-30x20000.jsonl",
               "intact": B / "size40/gen1-A-c0-wsize-30x20000.jsonl",
               "dir": B / "size40/gen1-A-deaf-dir-r20-c0-wsize-30x20000.jsonl",
               "rows": B / "size40/gen1-A-deaf-rows-c0-wsize-30x20000.jsonl"},
    "size100": {"scripted": B / "size100/scripted-wsize-30x20000.jsonl",
                "intact": B / "size100/gen1-A-c0-wsize-30x20000.jsonl",
                "dir": B / "size100/gen1-A-deaf-dir-r25-c0-wsize-30x20000.jsonl",
                "rows": B / "size100/gen1-A-deaf-rows-c0-wsize-30x20000.jsonl"},
    "size40-d2": {"scripted": B / "size40-d2/scripted-wsize-30x20000.jsonl",
                  "intact": B / "size40-d2/gen1-A-c0-wsize-30x20000.jsonl"},
    "size40-d4": {"scripted": B / "size40-d4/scripted-wsize-30x20000.jsonl",
                  "intact": B / "size40-d4/gen1-A-c0-wsize-30x20000.jsonl"},
    "size100-d2": {"scripted": B / "size100-d2/scripted-wsize-30x20000.jsonl",
                   "intact": B / "size100-d2/gen1-A-c0-wsize-30x20000.jsonl"},
    "size100-d4": {"scripted": B / "size100-d4/scripted-wsize-30x20000.jsonl",
                   "intact": B / "size100-d4/gen1-A-c0-wsize-30x20000.jsonl"},
}
SIZES = ("size20", "size28", "size40", "size100")


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    return {r["seed"]: r for r in rows[1:]}


def team_hap(run):
    h = run["mean_happiness"]
    return sum(h) / len(h)


def summ(vals):
    return {"mean": sum(vals) / len(vals), "min": min(vals), "max": max(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    out = {"cells": {}, "paired": {}, "checks": {}}
    runs = {}
    for cfg, arms in CELLS.items():
        runs[cfg] = {}
        for arm, path in arms.items():
            r = load(path)
            runs[cfg][arm] = r
            seeds = sorted(r)
            assert len(seeds) == 30 and len(set(seeds)) == 30, (cfg, arm)
            out["cells"][f"{cfg}/{arm}"] = {
                "path": str(path),
                "team_happiness": summ([team_hap(r[s]) for s in seeds]),
                "nash_state": summ([r[s]["nash_state"] for s in seeds]),
                "dist_ticks_total": sum(sum(r[s].get("dist_ticks", [0])) for s in seeds),
                "max_distress_age": max(r[s]["max_distress_age"] for s in seeds),
                "low_share_mean": summ([sum(r[s]["low_share"]) / len(r[s]["low_share"]) for s in seeds]),
            }
        base = sorted(runs[cfg]["intact"])
        for arm in arms:
            if arm in ("intact", "scripted"):
                continue
            assert sorted(runs[cfg][arm]) == base, (cfg, arm, "seed mismatch")
            deltas = [team_hap(runs[cfg][arm][s]) - team_hap(runs[cfg]["intact"][s]) for s in base]
            out["paired"][f"{cfg}/{arm}"] = {"team_happiness_delta": summ(deltas),
                                             "n_worse": sum(d < 0 for d in deltas),
                                             "per_seed": {str(s): d for s, d in zip(base, deltas)}}

    gap_rows = {s: -out["paired"][f"{s}/rows"]["team_happiness_delta"]["mean"] for s in SIZES}
    gap_dir = {s: -out["paired"][f"{s}/dir"]["team_happiness_delta"]["mean"] for s in SIZES}
    dir100 = out["paired"]["size100/dir"]["per_seed"]
    spread100 = max(dir100.values()) - min(dir100.values())
    out["checks"] = {
        "P1_rows_gap_by_size": gap_rows,
        "P1_ordered_20_40_100": gap_rows["size20"] < gap_rows["size40"] < gap_rows["size100"],
        "P1_28_and_40_exceed_20": gap_rows["size28"] > gap_rows["size20"] and gap_rows["size40"] > gap_rows["size20"],
        "P2_dir_gap_by_size": gap_dir,
        "P2_100_exceeds_20_by_spread": gap_dir["size100"] - gap_dir["size20"] > spread100,
        "P2_dir100_per_seed_spread": spread100,
        "P3_density_monotone": {},
        "P4_tail_factor": {},
    }
    for size in ("size40", "size100"):
        for who in ("intact", "scripted"):
            h1 = out["cells"][f"{size}/{who}"]["team_happiness"]["mean"]
            h2 = out["cells"][f"{size}-d2/{who}"]["team_happiness"]["mean"]
            h4 = out["cells"][f"{size}-d4/{who}"]["team_happiness"]["mean"]
            out["checks"]["P3_density_monotone"][f"{size}/{who}"] = {
                "d1": h1, "d2": h2, "d4": h4, "monotone_fall": h1 > h2 > h4}
    for key, p in out["paired"].items():
        cfg, arm = key.split("/")
        if abs(p["team_happiness_delta"]["mean"]) > 0.15:
            di = out["cells"][f"{cfg}/intact"]["dist_ticks_total"]
            da = out["cells"][key]["dist_ticks_total"]
            hap_factor = abs(p["team_happiness_delta"]["mean"]) / out["cells"][f"{cfg}/intact"]["team_happiness"]["mean"]
            out["checks"]["P4_tail_factor"][key] = {
                "dist_intact": di, "dist_arm": da,
                "dist_factor": (da / di) if di else None,
                "mean_move_frac": hap_factor,
            }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# World-size x density read", "",
             "| cell | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |",
             "|---|---|---|---|---|---|---|"]
        for key, c in out["cells"].items():
            p = out["paired"].get(key)
            d = f"{p['team_happiness_delta']['mean']:+.3f} [{p['team_happiness_delta']['min']:+.3f}, {p['team_happiness_delta']['max']:+.3f}]" if p else "--"
            w = f"{p['n_worse']}/30" if p else "--"
            L.append(f"| {key} | {c['team_happiness']['mean']:.3f} | {d} | {w} | "
                     f"{c['nash_state']['mean']:.4f} | {c['dist_ticks_total']} | {c['max_distress_age']} |")
        ck = out["checks"]
        L += ["", f"P1 rows gap by size: " + ", ".join(f"{s} {g:.3f}" for s, g in ck["P1_rows_gap_by_size"].items())
              + f"; ordered 20<40<100: {ck['P1_ordered_20_40_100']}; 28 and 40 exceed 20: {ck['P1_28_and_40_exceed_20']}.",
              f"P2 dir gap by size: " + ", ".join(f"{s} {g:.3f}" for s, g in ck["P2_dir_gap_by_size"].items())
              + f"; 100 exceeds 20 by more than the 100-cell per-seed spread ({ck['P2_dir100_per_seed_spread']:.3f}): {ck['P2_100_exceeds_20_by_spread']}.",
              "P3 density: " + "; ".join(f"{k} d1 {v['d1']:.2f} / d2 {v['d2']:.2f} / d4 {v['d4']:.2f} (falls: {v['monotone_fall']})"
                                          for k, v in ck["P3_density_monotone"].items()) + ".",
              "P4 tail factors (cells with |mean| > 0.15): " + "; ".join(
                  f"{k} dist x{v['dist_factor']:.1f}" if v["dist_factor"] else f"{k} dist {v['dist_intact']}->{v['dist_arm']}"
                  for k, v in ck["P4_tail_factor"].items()) + ".", ""]
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
