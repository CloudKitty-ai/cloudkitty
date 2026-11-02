#!/usr/bin/env python3
"""Phase 1e's split (DECLARATION.md §3): Phase 1b's eight sets VERBATIM
(L, W, G, P1..P5, their train / eval lists and the split seed, so the
validation carve of every 1b set is the one the frozen heads trained
under) followed by the ten late-grave training sets, TN1..TN5 and
TE1..TE5, one per scripted-friend block, train only (no evaluation
world: the needy set's confirming half is where the head is read).

Seeds: the band 1096651–1097050 (SEED-BANDS.md, claimed with this
declaration): TN<k> 1096651 + 40·(k−1) … +39, its first N_PER_BLOCK
seeds used; TE<k> 1096851 + 40·(k−1) … +39, its first E_PER_BLOCK. The
rest of each 40-seed stripe stays claimed and unburned (an extension
under the sizing clause, never a confirming seed). Every set carries
its raw directory (relative to experiments/), its config, its tick
count and its scripted seat; the 1b sets point at 1b's raws.

    split_1e.py            # writes split.json beside this script
    split_1e.py --check    # exits non-zero if split.json differs
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
PHASE1B = EXPTS / "minifriend-phase1b-2026-10-23"
NEEDY = EXPTS / "needy-set-2026-10-28"
BAND = (1096651, 1097050)
STRIPE = 40
N_PER_BLOCK, E_PER_BLOCK = 23, 8          # §3: arm N's tuning half per block, arm E's per block
TICKS = {"TN": 6000, "TE": 1000}          # TE at 1,000, not arm E's 800: train_heads.run_epoch trains whole 500-tick chunks
BLOCKS = (1, 2, 3, 4, 5)


def stripe(kind, k):
    base = BAND[0] + (0 if kind == "TN" else 5 * STRIPE) + STRIPE * (k - 1)
    return base, base + STRIPE - 1


def used(kind, k):
    lo, _hi = stripe(kind, k)
    n = N_PER_BLOCK if kind == "TN" else E_PER_BLOCK
    return list(range(lo, lo + n))


def build():
    b = json.loads((PHASE1B / "split.json").read_text())
    sets = {}
    for name, s in b["sets"].items():
        sets[name] = {"train": s["train"], "eval": s["eval"],
                      "raw_dir": f"minifriend-phase1b-2026-10-23/results-raw/{name}", "source": "phase1b verbatim"}
    for kind in ("TN", "TE"):
        for k in BLOCKS:
            lo, hi = stripe(kind, k)
            cfg = f"needy-set-2026-10-28/g2leg-20-N{k}.toml" if kind == "TN" else f"needy-set-2026-10-28/g2leg-20-E{k}-n60.toml"
            sets[f"{kind}{k}"] = {"train": used(kind, k), "eval": [], "raw_dir": f"minifriend-phase1e-2026-11-01/results-raw/{kind}{k}",
                                  "config": cfg, "ticks": TICKS[kind], "scripted_seat": k - 1, "stripe": [lo, hi]}
    assert stripe("TE", 5)[1] == BAND[1], stripe("TE", 5)
    return {"split_seed": b["split_seed"], "phase1b_split": "minifriend-phase1b-2026-10-23/split.json",
            "band": list(BAND), "stripe": STRIPE, "per_block": {"TN": N_PER_BLOCK, "TE": E_PER_BLOCK},
            "rule": "1b's sets verbatim and first in order (their validation carve is unchanged); then TN1..5, TE1..5, "
                    "train only, the first per_block seeds of each 40-seed stripe", "sets": sets}


def main(argv):
    out = HERE / "split.json"
    new = json.dumps(build(), indent=1) + "\n"
    if "--check" in argv:
        if not out.exists() or out.read_text() != new:
            print("split.json differs from split_1e.py")
            return 1
        print("split.json matches split_1e.py")
        return 0
    out.write_text(new)
    s = build()["sets"]
    print(f"wrote {out}: {len(s)} sets; TN {sum(len(s[f'TN{k}']['train']) for k in BLOCKS)} worlds, "
          f"TE {sum(len(s[f'TE{k}']['train']) for k in BLOCKS)} worlds")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
