#!/usr/bin/env python3
"""Phase 1b's by-world split (DECLARATION.md §Data). Sets L, W, G are
Phase 1's split.json VERBATIM (the same train/eval worlds; nothing is
re-drawn). The per-cat grave sets P1..P5 (one per friend, 20 worlds
each, seeds 1095451 + 20·(k−1) …) split 50/50 by world, assignment by a
declared seed before collection; the reserved extension blocks X1..X5
(1095551 + 20·(k−1) …) are split the same way now and sit under
"extension" until `--extend Pk` promotes one (the declared remedy when a
friend's mind-visible GRAVE stratum on the P eval worlds is under
min-n after P; the promotion appends the block's worlds to Pk).

    split.py            # writes split.json beside this file
    split.py --check    # exits non-zero if split.json differs
    split.py --extend P3   # promote X3 into P3 (declared clause only)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PHASE1 = HERE.parent / "minifriend-phase1-2026-10-22"
SPLIT_SEED = 20261023          # declared 2026-10-23, before any P world ran
EVAL_SHARE = 0.5               # P: half the worlds evaluate (grave coverage is the scarce thing)
PER_FRIEND = 20
P_BASE, X_BASE = 1095451, 1095551   # SEED-BANDS row 1095451–1095650
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]


def block(base, k):
    return list(range(base + PER_FRIEND * (k - 1), base + PER_FRIEND * k))


def halve(rng, seeds):
    seeds = sorted(seeds)
    perm = [seeds[i] for i in rng.permutation(len(seeds))]
    ev = sorted(perm[:round(EVAL_SHARE * len(seeds))])
    return {"seeds": seeds, "eval": ev, "train": [s for s in seeds if s not in ev]}


def split():
    p1 = json.loads((PHASE1 / "split.json").read_text())
    out = {"split_seed": SPLIT_SEED, "eval_share_P": EVAL_SHARE, "phase1_split_seed": p1["split_seed"],
           "sets": {n: p1["sets"][n] for n in ("L", "W", "G")}, "extension": {}, "grave_kitty": {}}
    rng = np.random.default_rng(SPLIT_SEED)
    for k, name in enumerate(SEATS, start=1):
        out["sets"][f"P{k}"] = halve(rng, block(P_BASE, k))
        out["grave_kitty"][f"P{k}"] = {"id": k, "name": name}
    for k in range(1, 6):
        out["extension"][f"X{k}"] = halve(rng, block(X_BASE, k))
    return out


def extend(current, pk):
    xk = "X" + pk[1:]
    assert xk in current["extension"], f"{xk} already promoted or unknown"
    x = current["extension"].pop(xk)
    for key in ("seeds", "eval", "train"):
        current["sets"][pk][key] = sorted(current["sets"][pk][key] + x[key])
    current.setdefault("extended", []).append(pk)
    return current


def main():
    p = HERE / "split.json"
    if "--extend" in sys.argv:
        pk = sys.argv[sys.argv.index("--extend") + 1]
        cur = extend(json.loads(p.read_text()), pk)
        p.write_text(json.dumps(cur, indent=1) + "\n")
        print(f"promoted X{pk[1:]} into {pk}: {len(cur['sets'][pk]['seeds'])} worlds")
        return
    out = split()
    if "--check" in sys.argv:
        cur = json.loads(p.read_text())
        for pk in cur.get("extended", []):
            out = extend(out, pk)
        assert cur == out, "split.json differs from split.py"
        print("split.json matches")
        return
    assert not p.exists() or json.loads(p.read_text()).get("extended") is None, "split.json carries a promotion; refusing to rewrite"
    p.write_text(json.dumps(out, indent=1) + "\n")
    for name, s in out["sets"].items():
        print(name, "eval", s["eval"])


if __name__ == "__main__":
    main()
