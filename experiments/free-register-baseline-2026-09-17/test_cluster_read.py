#!/usr/bin/env python3
"""Guards for cluster_read.py on staged series: exact coincidence
counts (cross-cat only), null A detects a fixed-lag echo, null B keeps
shared-state clustering and removes it. Plain-python asserts."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cluster_read as C  # noqa: E402


def staged_echo():
    """Cat 0 speaks every 10 ticks from 10; cat 1 answers one tick later;
    cat 2 speaks at 55 and 56 (a self pair that must not count; its
    cross pairs with cats 0 and 1 sit at lags 4-6, so only k=10 sees them)."""
    T, K = 300, 3
    E = np.zeros((T, K), bool)
    E[10::10, 0] = True
    E[11::10, 1] = True
    E[55, 2] = E[56, 2] = True
    return E


def staged_shared_state(rng):
    """Two cats rest in the same 40-tick blocks and each speaks on a
    random 30% of its resting ticks; nothing answers anything."""
    T, K = 2000, 2
    actcls = np.zeros((T, K), int)
    for start in range(0, T, 100):
        actcls[start:start + 40, :] = 1  # both resting together
    E = np.zeros((T, K), bool)
    for i in range(K):
        idx = np.nonzero(actcls[:, i] == 1)[0]
        E[rng.choice(idx, int(0.3 * len(idx)), replace=False), i] = True
    return E, actcls


def main():
    rng = np.random.default_rng(1)
    E = staged_echo()
    assert C.coincidences(E, 1) == 29, C.coincidences(E, 1)  # 10..290 -> 11..291; cat 2's self pair excluded
    assert C.coincidences(E, 3) == 29
    # + cat 1 -> cat 0 at lag 9 (11..281 -> 20..290) + cat 2's eight cross
    # pairs (50 -> 55/56, 51 -> 55/56, 55/56 -> 60, 55/56 -> 61)
    assert C.coincidences(E, 10) == 29 + 28 + 8, C.coincidences(E, 10)
    na = np.mean([C.coincidences(C.null_a(E, rng), 1) for _ in range(100)])
    assert na < 29 / 3, na  # a fixed-lag echo is far above independent timing
    E2, act = staged_shared_state(rng)
    obs = C.coincidences(E2, 3)
    na = np.mean([C.coincidences(C.null_a(E2, rng), 3) for _ in range(100)])
    nb = np.mean([C.coincidences(C.null_b(E2, act, rng), 3) for _ in range(100)])
    assert obs / na > 1.5, (obs, na)  # settling together clusters the words in time
    assert 0.8 <= obs / nb <= 1.25, (obs, nb)  # and null B, keeping the shared state, explains it
    # null B keeps the count per class
    nbE = C.null_b(E2, act, rng)
    assert nbE.sum() == E2.sum() and nbE[act == 0].sum() == 0
    print("ok: cluster_read guards")


if __name__ == "__main__":
    main()
