#!/usr/bin/env python3
"""Twin-probe analysis (exp-001 prereg §6): credit-horizon statistics.

Reads a twin-probe JSONL file and reports, with per-tick significance
testing, where the systematic credit signal lives. Methodology:

- The credit signal is the ACROSS-SAMPLE MEAN of signed diffs (chaotic
  diffusion is sign-symmetric and averages out); a tick is "significant"
  when |mean| > 2*SE. With ~K ticks tested, expect ~0.05*K false positives;
  isolated late blips are judged against that base rate, contiguous bands
  are the real signal.
- Never fit decay curves below the noise floor (SE): thresholds are taken
  on significant ticks only.

Usage: analyze.py <probe.jsonl> [gamma_candidates...]
"""

import json
import math
import sys
from collections import Counter


def mean_se(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def contiguous(ks):
    runs, start, prev = [], None, None
    for k in ks:
        if start is None:
            start = prev = k
        elif k == prev + 1:
            prev = k
        else:
            runs.append((start, prev))
            start = prev = k
    if start is not None:
        runs.append((start, prev))
    return runs


def main():
    path = sys.argv[1]
    gammas = [float(g) for g in sys.argv[2:]] or [0.99, 0.995]
    recs = [json.loads(line) for line in open(path)]
    n, k_len = len(recs), len(recs[0]["dr"])
    print(f"file={path} samples={n} trace_len={k_len}")
    print("substituted:", dict(Counter(r["base_applied"] for r in recs)))
    healed = sum(1 for r in recs if all(abs(x) < 1e-12 for x in r["dr"][-100:]))
    print(f"healed by end: {healed}/{n} ({100 * healed / n:.0f}%)")

    def significance_profile(series_per_rec, label):
        stats = [mean_se([tr[k] for tr in series_per_rec]) for k in range(k_len)]
        sig = [k for k, (m, se) in enumerate(stats) if abs(m) > 2 * se]
        expected_fp = 0.05 * k_len
        runs = contiguous(sig)
        absm = {k: abs(stats[k][0]) for k in sig}
        peak_k = max(absm, key=absm.get) if absm else None
        print(f"\n{label}:")
        print(f"  significant ticks: {len(sig)} (chance ~{expected_fp:.0f}); bands: {runs[:10]}")
        if peak_k is not None:
            print(f"  |mean| peak {absm[peak_k]:.3e} at k={peak_k}; last significant k={max(sig)}")
            total = sum(absm.values())
            for w in (18, 50, 100, 200, 300, 400):
                frac = 100 * sum(v for k, v in absm.items() if k <= w) / total
                print(f"  significant-signal mass within k<={w}: {frac:.1f}%")
            for g in gammas:
                weighted = sum(v * g**k for k, v in absm.items()) / total
                print(f"  gamma={g}: fraction of signal mass surviving discount: {weighted:.2f}")
        return sig

    significance_profile([r["dr"] for r in recs], "team reward (signed dr)")
    significance_profile(
        [r["dh"][str(r["kitty_id"])] for r in recs], "substituted kitty happiness (signed dh, self)"
    )

    others = []
    for r in recs:
        kid = str(r["kitty_id"])
        rest = [tr for k_id, tr in r["dh"].items() if k_id != kid]
        others.append([sum(vals) / len(vals) for vals in zip(*rest)])
    significance_profile(others, "teammate happiness (signed dh, others-mean; spillover)")


if __name__ == "__main__":
    main()
