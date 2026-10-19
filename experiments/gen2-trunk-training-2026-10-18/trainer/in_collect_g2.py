#!/usr/bin/env python3
"""True rung (ii) (MITIGATION.md §Iteration + §Rung (ii) draw ranges,
owner-ruled 2026-10-19; unblocked by spec 065 landing, main 5fb27cfb):
manufactured-init worlds on the UNALTERED trunk config — g2leg-20 plus
an appended `[initial_needs]` section only — so the supervision is the
MDP the critic will evaluate, not a cranked-rate variant.

Variants (declared draw ranges, keyed to the 065 shape verified at the
landing merge):
  IN-wide   all six needs { min = 0.0, max = 90.0 }   seeds 1095241-1095265
  IN-grave  all six needs { min = 60.0, max = 95.0 }  seeds 1095266-1095290

Derived tomls land INSIDE the gitignored out dir, never tracked (the
shipped-config sweep loads every tracked experiments toml). Welfare:
scripted seats; the path into distress is never run; the distressed
starts are register-real at tick 0 (the spec's record_distress arming).

  in_collect_g2.py [--ticks 4000] [--out ../results-raw-extension-iter]
"""
import argparse
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ARC = HERE.parent
EXP = HERE.parents[1]
LEG20 = EXP / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
BC_COLLECT = EXP / "tools/bc-collect/target/release/bc-collect"
BAND_BASE, BAND_END = 1095001, 1095300
NEEDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")

# variant -> ((min, max), seed_base, rollouts)
VARIANTS = {
    "IN-wide": ((0.0, 90.0), 1095241, 25),
    "IN-grave": ((60.0, 95.0), 1095266, 25),
}


def derive(lo, hi):
    text = LEG20.read_text()
    assert "[initial_needs]" not in text, "trunk toml already has the section"
    lines = [f"{k} = {{ min = {lo}, max = {hi} }}" for k in NEEDS]
    return text + "\n[initial_needs]\n" + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--out", type=pathlib.Path,
                    default=ARC / "results-raw-extension-iter")
    args = ap.parse_args()

    for v, ((lo, hi), seed, rollouts) in VARIANTS.items():
        top = seed + rollouts - 1
        assert BAND_BASE <= seed and top <= BAND_END, \
            f"{v}: seeds {seed}..{top} leave the band"
        vdir = args.out / v
        vdir.mkdir(parents=True, exist_ok=True)
        cfg = vdir / "config.toml"
        cfg.write_text(derive(lo, hi))
        alloc = {"variant": v, "seed_base": seed, "rollouts": rollouts,
                 "draw": {"min": lo, "max": hi}, "ticks": args.ticks,
                 "band": [BAND_BASE, BAND_END]}
        seeds_file = vdir / "seeds.json"
        prior = json.loads(seeds_file.read_text()) if seeds_file.exists() else []
        for p in prior:
            plo, phi = p["seed_base"], p["seed_base"] + p["rollouts"] - 1
            assert phi < seed or plo > top, f"{v}: seed overlap with {p}"
        seeds_file.write_text(json.dumps(prior + [alloc], indent=1) + "\n")
        print(f"== {v} seeds {seed}..{top} draw [{lo}, {hi}]", flush=True)
        subprocess.run(
            [str(BC_COLLECT), "--config", str(cfg),
             "--rollouts", str(rollouts), "--ticks", str(args.ticks),
             "--seed-base", str(seed), "--out-dir", str(vdir)],
            check=True)
    print("== rung (ii) collection done", flush=True)


if __name__ == "__main__":
    main()
