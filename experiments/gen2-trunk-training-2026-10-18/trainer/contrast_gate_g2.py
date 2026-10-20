#!/usr/bin/env python3
"""Held-out contrast-pair gate (MITIGATION.md §Round 4 (6)): on the
round-4 RANDOM-leg probe worlds (never trained), for each flagged run
(contrast_pairs_g2 conventions: >= 3 ticks, same kitty) with a nearby
unflagged window (same length, +/-500, same kitty), compare the
critic's value at the run's midpoint state vs the nearest unflagged
window's midpoint state. Correct = flagged valued LOWER. Gate: pooled
exact-binomial (Clopper-Pearson) 99% lower bound > 0.5, and no kind
with >= 50 pairs significantly below 0.5 (one-sided binomial test at
its own p99). Ramp-free by construction: both members sit in the same
world within +/-500 ticks.

    contrast_gate_g2.py --critic <ckpt> [--seed-base 870040]
        [--worlds 10] [--ticks 6000] [--out ../artifacts/contrast-gate.json]
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ARC = HERE.parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from contrast_pairs_g2 import KINDS, MIN_RUN, NEAR, runs_of_ones  # noqa: E402
from critic_probe_g2 import collect  # noqa: E402

N_KITTY, KITTY_F, FLAG_OFF = 5, 40, 20
MIN_PAIRS = 50


def log_binom_sf(x, n, p):
    """log-space P(X <= x) for Binomial(n, p) via lgamma terms."""
    terms = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
             + j * math.log(p) + (n - j) * math.log1p(-p)
             for j in range(0, x + 1)]
    m = max(terms)
    return m + math.log(sum(math.exp(t - m) for t in terms))


def cp_lower(x, n, conf=0.99):
    """One-sided Clopper-Pearson lower bound: the largest p with
    P(X >= x | p) <= 1 - conf. P(X >= x | p) is increasing in p, so
    bisect upward while it stays under the tail mass 1 - conf."""
    if x == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        # P(X >= x | mid) = 1 - P(X <= x-1 | mid)
        if 1.0 - math.exp(log_binom_sf(x - 1, n, mid)) < 1.0 - conf:
            lo = mid
        else:
            hi = mid
    return lo


def select_pairs(state):
    """(kind, flagged_tick, unflagged_tick) rows for one rollout."""
    rows = []
    t_total = state.shape[0]
    for k in range(N_KITTY):
        flags = np.asarray(state[:, k * KITTY_F + FLAG_OFF:
                                 k * KITTY_F + FLAG_OFF + 6], np.int8)
        assert ((flags == 0) | (flags == 1)).all(), "flag column not 0/1"
        for j, kind in enumerate(KINDS):
            f = flags[:, j]
            cs = np.concatenate([[0], np.cumsum(f)])
            for start, length in runs_of_ones(f):
                if length < MIN_RUN:
                    continue
                lo = max(0, start - NEAR)
                hi = min(t_total - length, start + length + NEAR)
                a = np.arange(lo, hi + 1)
                ok = a[(cs[a + length] - cs[a]) == 0] if len(a) else a
                if len(ok):
                    # the nearest unflagged window to the run
                    u = ok[np.argmin(np.abs(ok - start))]
                    rows.append((kind, start + length // 2, u + length // 2))
    return rows


def score_pairs(rows, value_at):
    """(correct, total) per kind: correct = flagged member valued LOWER."""
    correct = dict.fromkeys(KINDS, 0)
    total = dict.fromkeys(KINDS, 0)
    for kind, fa, ua in rows:
        total[kind] += 1
        if value_at[fa] < value_at[ua]:
            correct[kind] += 1
    return correct, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--critic", type=Path, required=True)
    ap.add_argument("--seed-base", type=int, default=870040)
    ap.add_argument("--worlds", type=int, default=10)
    ap.add_argument("--ticks", type=int, default=6000)
    ap.add_argument("--out", type=Path,
                    default=ARC / "artifacts/contrast-gate.json")
    args = ap.parse_args()

    from model_attn_v2 import EntityCriticV2
    from tokens_v2 import tokenize
    art = torch.load(args.critic, map_location="cpu", weights_only=True)
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()

    correct = dict.fromkeys(KINDS, 0)
    total = dict.fromkeys(KINDS, 0)
    rollouts = collect(args.ticks, args.worlds, args.seed_base, 1.0, None)
    for r in rollouts:
        rows = select_pairs(r.state)
        if not rows:
            continue
        idx = sorted({t for _, a, b in rows for t in (a, b)})
        pos = {t: i for i, t in enumerate(idx)}
        k, e, g, p = tokenize(np.asarray(r.state[idx], np.float32))
        with torch.no_grad():
            v = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                 g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                           for i in range(0, k.shape[0], 4096)]).numpy()
        c, t = score_pairs(rows, {tk: v[i] for tk, i in pos.items()})
        for kind in KINDS:
            correct[kind] += c[kind]
            total[kind] += t[kind]

    per_kind = {}
    bad_kind = []
    for kind in KINDS:
        n, x = total[kind], correct[kind]
        row = {"pairs": n, "correct": x,
               "fraction": x / n if n else None,
               "qualifies": n >= MIN_PAIRS}
        if n >= MIN_PAIRS:
            # significantly below 0.5: P(X <= x | 0.5) < 0.01
            row["p_below"] = math.exp(log_binom_sf(x, n, 0.5))
            if row["p_below"] < 0.01:
                bad_kind.append(kind)
        per_kind[kind] = row
    n_all = sum(total.values())
    x_all = sum(correct.values())
    lower = cp_lower(x_all, n_all) if n_all else 0.0
    verdict = bool(n_all and lower > 0.5 and not bad_kind)
    out = {"seed_base": args.seed_base, "worlds": args.worlds,
           "ticks": args.ticks, "critic": str(args.critic),
           "min_pairs": MIN_PAIRS, "pooled_pairs": n_all,
           "pooled_correct": x_all,
           "pooled_fraction": x_all / n_all if n_all else None,
           "cp99_lower": lower, "kinds_below": bad_kind,
           "per_kind": per_kind, "pass": verdict}
    print(json.dumps(out, indent=1))
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"contrast gate: {'PASS' if verdict else 'FAIL'}")


if __name__ == "__main__":
    main()
