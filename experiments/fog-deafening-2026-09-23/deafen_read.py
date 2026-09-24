"""Reader for the fog-era deafening ablation (fog-deafening-2026-09-23).

    deafen_read.py INTACT WANT HERE ALL --out read.json [--md read.md]

The four positional arguments are the battery jsonl files (intact,
want-deaf, here-deaf, all-deaf). Deterministic on the same raws:
explicit paths, full-precision JSON, seeds asserted aligned across arms
before any pairing (the paired design is the instrument).
"""
import argparse
import json
from pathlib import Path

ARM_NAMES = ["intact", "want", "here", "all"]


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    header, runs = rows[0], rows[1:]
    return header, {r["seed"]: r for r in runs}


def team_hap(run):
    h = run["mean_happiness"]
    return sum(h) / len(h)


def summarise(vals):
    return {"mean": sum(vals) / len(vals), "min": min(vals), "max": max(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batteries", nargs=4, help="intact, want-deaf, here-deaf, all-deaf jsonl")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path, default=None)
    a = ap.parse_args()

    arms = {}
    for name, path in zip(ARM_NAMES, a.batteries):
        header, runs = load(path)
        arms[name] = {"path": str(path), "provenance": header.get("provenance"), "runs": runs}
    seed_sets = {name: sorted(arm["runs"]) for name, arm in arms.items()}
    base = seed_sets["intact"]
    for name, seeds in seed_sets.items():
        assert seeds == base, f"seed mismatch: {name} has {seeds[:3]}.. vs intact {base[:3]}.."
    assert len(base) == len(set(base)), "duplicate seeds"

    out = {"seeds": base, "n_seeds": len(base), "arms": {}, "paired": {}, "checks": {}}
    for name, arm in arms.items():
        runs = arm["runs"]
        out["arms"][name] = {
            "path": arm["path"],
            "team_happiness": summarise([team_hap(runs[s]) for s in base]),
            "nash_state": summarise([runs[s]["nash_state"] for s in base]),
            "dist_ticks_total": sum(sum(runs[s]["dist_ticks"]) for s in base),
            "max_distress_age": max(runs[s]["max_distress_age"] for s in base),
            "floor_touches_total": sum(sum(runs[s]["floor_touches"]) for s in base),
            "low_share_mean": summarise([sum(runs[s]["low_share"]) / len(runs[s]["low_share"]) for s in base]),
            "per_seat_happiness_mean": [
                sum(runs[s]["mean_happiness"][k] for s in base) / len(base)
                for k in range(len(runs[base[0]]["mean_happiness"]))
            ],
        }
    for name in ("want", "here", "all"):
        deltas = [team_hap(arms[name]["runs"][s]) - team_hap(arms["intact"]["runs"][s]) for s in base]
        out["paired"][name] = {
            "team_happiness_delta": summarise(deltas),
            "n_worse": sum(d < 0 for d in deltas),
            "per_seed": {str(s): d for s, d in zip(base, deltas)},
        }
    intact_dist = out["arms"]["intact"]["dist_ticks_total"]
    out["checks"] = {
        "P1_all_deaf_delta": out["paired"]["all"]["team_happiness_delta"]["mean"],
        "P1_below_minus_0.15": out["paired"]["all"]["team_happiness_delta"]["mean"] < -0.15,
        "P2_families_between": all(
            out["paired"]["all"]["team_happiness_delta"]["mean"]
            <= out["paired"][f]["team_happiness_delta"]["mean"] <= 0.0
            or out["paired"][f]["team_happiness_delta"]["mean"] > 0.0
            for f in ("want", "here")
        ),
        "P3_dist_ratio_all_over_intact": (
            (out["arms"]["all"]["dist_ticks_total"] / intact_dist) if intact_dist else None
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")

    if a.md:
        L = ["# Fog deafening read", "",
             f"{len(base)} paired seeds per arm ({base[0]}..{base[-1]}).", "",
             "| arm | team happiness | paired delta vs intact | worse/n | nash_state | dist ticks | max distress age |",
             "|---|---|---|---|---|---|---|"]
        for name in ARM_NAMES:
            m = out["arms"][name]
            if name == "intact":
                d, w = "--", "--"
            else:
                p = out["paired"][name]
                d = f"{p['team_happiness_delta']['mean']:+.3f} [{p['team_happiness_delta']['min']:+.3f}, {p['team_happiness_delta']['max']:+.3f}]"
                w = f"{p['n_worse']}/{len(base)}"
            L.append(f"| {name} | {m['team_happiness']['mean']:.3f} | {d} | {w} | "
                     f"{m['nash_state']['mean']:.4f} | {m['dist_ticks_total']} | {m['max_distress_age']} |")
        c = out["checks"]
        ratio = c["P3_dist_ratio_all_over_intact"]
        L += ["",
              f"P1 all-deaf paired mean delta {c['P1_all_deaf_delta']:+.4f}; past the -0.15 line: {c['P1_below_minus_0.15']}.",
              f"P2 family arms between intact and all-deaf: {c['P2_families_between']}.",
              f"P3 distress-tick ratio all-deaf / intact: {ratio if ratio is None else f'{ratio:.2f}'}.", ""]
        a.md.write_text("\n".join(L))
        print(f"wrote {a.md}")


if __name__ == "__main__":
    main()
