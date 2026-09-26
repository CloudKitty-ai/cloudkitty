"""Reader for the cross-world cost reads (DECLARATION.md, 2026-09-26).

    read_cross.py --out results-raw/cross-read.json [--md ...]

Deterministic: the nine legs below plus the recorded comparators
(gen1-A on floor 0 = the tier 1 cell; beta-0 recipe band = tier 2's
pkg all-arm legs).
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "results-raw"
BEAM = HERE.parent / "beam-world-screen-2026-09-19" / "results-raw"
GEN1A_F0 = BEAM / "battery" / "s3-b7-t3000-n6" / "gen1-A-c0-eval-30x20000.jsonl"
PKG = {s: BEAM / "tier2" / "battery" / s /
       f"gen1-A_s0-{s}_s1-{s}_s2-{s}_s3-{s}_s4-{s}-c0-eval-30x20000.jsonl"
       for s in ("pkg-s1", "pkg-s2")}
SG = ("sg15-s1", "sg15-s2")
SHAPED = ("hard-s1", "hard-s2", "cvx-s1", "cvx-s2", "lam-s1", "lam-s2")


def per_seed_team(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()][1:]
    return {r["seed"]: sum(r["mean_happiness"]) / len(r["mean_happiness"]) for r in rows}


def leg(dirname):
    files = sorted((R / dirname).glob("*.jsonl"))
    assert len(files) == 1, (dirname, files)
    return per_seed_team(files[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    g_f0 = per_seed_team(GEN1A_F0)
    g_f15 = leg("gen1-A-on-floor15")
    seeds = sorted(g_f0)
    assert sorted(g_f15) == seeds
    out = {"comparators": {
        "gen1A_floor0_recorded": sum(g_f0.values()) / 30,
        "gen1A_floor15_fresh": sum(g_f15.values()) / 30,
        **{f"beta0_{s}_floor0": sum(per_seed_team(p).values()) / 30 for s, p in PKG.items()},
    }, "legs": {}}
    for s in SG:
        t = leg(f"{s}-on-floor0")
        assert sorted(t) == seeds
        d = [t[k] - g_f0[k] for k in seeds]
        out["legs"][f"{s}-on-floor0"] = {
            "team_happiness_mean": sum(t.values()) / 30,
            "paired_delta_vs_gen1A_floor0": sum(d) / 30,
            "n_worse": sum(x < 0 for x in d),
        }
    for s in SHAPED:
        t = leg(f"{s}-on-floor15")
        assert sorted(t) == seeds
        d = [t[k] - g_f15[k] for k in seeds]
        out["legs"][f"{s}-on-floor15"] = {
            "team_happiness_mean": sum(t.values()) / 30,
            "paired_delta_vs_gen1A_floor15": sum(d) / 30,
            "n_worse": sum(x < 0 for x in d),
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        L = ["# Cross-world cost read", "",
             f"Comparators: gen1-A floor0 (recorded) {out['comparators']['gen1A_floor0_recorded']:.3f}; "
             f"gen1-A floor15 (fresh) {out['comparators']['gen1A_floor15_fresh']:.3f}; "
             f"beta-0 recipe band floor0 {out['comparators']['beta0_pkg-s1_floor0']:.3f} / "
             f"{out['comparators']['beta0_pkg-s2_floor0']:.3f}.", "",
             "| leg | happiness | paired delta | worse/30 |", "|---|---|---|---|"]
        for k, v in out["legs"].items():
            dkey = [x for x in v if x.startswith("paired_delta")][0]
            L.append(f"| {k} | {v['team_happiness_mean']:.3f} | {v[dkey]:+.3f} | {v['n_worse']}/30 |")
        a.md.write_text("\n".join(L) + "\n")
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
