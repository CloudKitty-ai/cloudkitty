#!/usr/bin/env python3
"""Extended rung (iii): the graded degradation suite (MITIGATION.md;
deviations entry 2; rung (ii) superseded — this rung covers its bins).

Scripted-teacher worlds weakened in NAMED ways, derived from the TRUNK
configs by exact-line replacement (screen_dials.py's pattern). Each
variant targets specific welfare bins; worlds cycle into distress,
through strained relief, and out, so both contrast halves come from
the same world. Roster stays scripted (teacher) — exempt under the
covered-minds practice; the added scripted distress ticks are
register-real (the entry's cost line). Derived tomls land INSIDE the
gitignored out dir, never tracked (the shipped-config sweep loads
every tracked experiments toml).

Variants (named weakness → mechanism):
  R-eat3 R-drink3 R-sleep3 R-play3 R-cuddle3 R-bath3
      one world [needs] rate ×3 — one need beyond servicing capacity
  C10   consent_line 30 → 10 (the most-refusing legal value;
        dial-screen v10 was the richest sub-45 dial source)
  SCchow  [elements.chow] min/max 6/8 → 2/3 — scarcity, strained relief
  SCwater [elements.water] min/max 7/9 → 2/3 — as above
  DISP  g2leg-100 verbatim (randomized dispersed starts on 100×100 —
        the teacher-dispersion corners mechanism)

Seeds: --seed-base from the claimed 1095001–1095300 band; each variant
takes a contiguous stride of --stride (default 20) so pilot and fill
phases reuse one allocation map: variant i seeds = base + i*stride ..
base + i*stride + rollouts - 1. The allocation is recorded in each
variant dir's seeds.json.

Usage (pilot = 2 rollouts/variant, fill = more of chosen variants):
  degradation_suite_g2.py --rollouts 2 [--variants R-eat3,C10,...]
      [--seed-offset 0] [--ticks 4000] [--out ../results-raw-extension]
"""
import argparse
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ARC = HERE.parent
EXP = HERE.parents[1]
LEG20 = EXP / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
LEG100 = EXP / "gen2-comparator-legs-2026-10-14/g2leg-100.toml"
BC_COLLECT = EXP / "tools/bc-collect/target/release/bc-collect"
BAND_BASE, BAND_END = 1095001, 1095300

NEEDS_BLOCK = """[needs]
eat = 0.4
drink = 0.4
sleep = 0.3
play = 0.4
cuddle = 0.4
bath = 0.2"""
CONSENT_LINE = ("consent_line = 30.0  # fog-gen1-cert: Biscuit 3.0 anchor "
                "consent gate (owner 2026-09-02); the twin runs it at 0.0")
WATER_BLOCK = "[elements.water]"
CHOW_BLOCK = "[elements.chow]\nmin = 6\nmax = 8"
RATES = {"eat": 0.4, "drink": 0.4, "sleep": 0.3,
         "play": 0.4, "cuddle": 0.4, "bath": 0.2}

VARIANTS = (["R-%s3" % k for k in RATES]
            + ["C10", "SCchow", "SCwater", "DISP"])


def replace_once(text, old, new, what):
    assert text.count(old) == 1, f"{what}: anchor moved or ambiguous"
    return text.replace(old, new)


def derive(variant):
    if variant == "DISP":
        return LEG100.read_text()
    text = LEG20.read_text()
    if variant.startswith("R-") and variant.endswith("3"):
        kind = variant[2:-1]
        block = replace_once(NEEDS_BLOCK, f"{kind} = {RATES[kind]}",
                             f"{kind} = {RATES[kind] * 3:.1f}  # DEGRADED x3",
                             variant)
        return replace_once(text, NEEDS_BLOCK, block, "[needs] block")
    if variant == "C10":
        return replace_once(text, CONSENT_LINE,
                            "consent_line = 10.0  # DEGRADED (most-refusing)",
                            "consent line")
    if variant == "SCchow":
        return replace_once(text, CHOW_BLOCK,
                            "[elements.chow]\nmin = 2\nmax = 3  # DEGRADED scarcity",
                            "chow block")
    if variant == "SCwater":
        # the water block's min/max sit a comment away from the header
        return replace_once(text, "min = 7\nmax = 9",
                            "min = 2\nmax = 3  # DEGRADED scarcity",
                            "water min/max")
    raise SystemExit(f"unknown variant {variant!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", type=int, default=2)
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--seed-offset", type=int, default=0,
                    help="offset within each variant's stride (fill phase)")
    ap.add_argument("--stride", type=int, default=20)
    ap.add_argument("--out", type=pathlib.Path,
                    default=ARC / "results-raw-extension")
    args = ap.parse_args()

    chosen = args.variants.split(",")
    for v in chosen:
        assert v in VARIANTS, v
    for v in chosen:
        i = VARIANTS.index(v)
        seed = BAND_BASE + i * args.stride + args.seed_offset
        top = seed + args.rollouts - 1
        assert top <= BAND_END, f"{v}: seeds {seed}..{top} leave the band"
        assert args.seed_offset + args.rollouts <= args.stride, \
            f"{v}: rollouts spill into the next variant's stride"
        vdir = args.out / v
        vdir.mkdir(parents=True, exist_ok=True)
        cfg = vdir / "config.toml"
        cfg.write_text(derive(v))
        alloc = {"variant": v, "seed_base": seed, "rollouts": args.rollouts,
                 "seed_offset": args.seed_offset, "ticks": args.ticks,
                 "band": [BAND_BASE, BAND_END]}
        seeds_file = vdir / "seeds.json"
        prior = json.loads(seeds_file.read_text()) if seeds_file.exists() else []
        for p in prior:
            lo, hi = p["seed_base"], p["seed_base"] + p["rollouts"] - 1
            assert hi < seed or lo > top, f"{v}: seed overlap with {p}"
        seeds_file.write_text(json.dumps(prior + [alloc], indent=1) + "\n")
        print(f"== {v} seeds {seed}..{top}", flush=True)
        subprocess.run(
            [str(BC_COLLECT), "--config", str(cfg),
             "--rollouts", str(args.rollouts), "--ticks", str(args.ticks),
             "--seed-base", str(seed), "--out-dir", str(vdir)],
            check=True)
    print("== suite done", flush=True)


if __name__ == "__main__":
    main()
