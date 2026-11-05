#!/usr/bin/env python3
"""Guards c1–c7 of DECLARATION.md §7 for calib_act.py; each red on record via scripts/mutate.sh --expect before any
read. Run under the needy arc's venv:

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_calib.py [c1 ... c7]
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calib_act as C  # noqa: E402

D, R, TA = C.D, C.R, C.TA


def c1():
    """entropy_norm: one-hot 0, uniform 1; bin_index: edges land where declared, the last bin closed."""
    one = np.zeros((1, D.N_ACTS)); one[0, 3] = 1.0
    assert abs(C.entropy_norm(one)[0]) < 1e-9, f"one-hot entropy {C.entropy_norm(one)[0]}, expected 0"
    uni = np.full((1, D.N_ACTS), 1.0 / D.N_ACTS)
    assert abs(C.entropy_norm(uni)[0] - 1.0) < 1e-9, f"uniform entropy {C.entropy_norm(uni)[0]}, expected 1"
    b = C.bin_index(np.array([0.05, 0.19, 0.2, 0.55, 0.95, 1.0]), C.CONF_EDGES)
    assert b.tolist() == [0, 0, 1, 4, 8, 8], f"conf bins {b.tolist()}, expected [0, 0, 1, 4, 8, 8]"
    e = C.bin_index(np.array([0.0, 0.1, 0.99, 1.0]), C.ENT_EDGES)
    assert e.tolist() == [0, 1, 9, 9], f"entropy bins {e.tolist()}, expected [0, 1, 9, 9]"


def c2():
    """temper: T = 1 is the identity, T = 2 flattens, T = 0.5 sharpens, per-row T applies per row; ece_from_bins by hand."""
    rng = np.random.default_rng(0)
    p = rng.dirichlet(np.ones(D.N_ACTS), 5)
    assert np.allclose(C.temper(p, 1.0), p, atol=1e-9), "T = 1 must return p"
    h1, h2, hh = C.entropy_norm(p), C.entropy_norm(C.temper(p, 2.0)), C.entropy_norm(C.temper(p, 0.5))
    assert (h2 > h1).all(), "T = 2 must raise every row's entropy"
    assert (hh < h1).all(), "T = 0.5 must lower every row's entropy"
    rows = C.temper(p, np.array([1.0, 2.0, 0.5, 1.0, 1.0]))
    assert np.allclose(rows[1], C.temper(p[1:2], 2.0)[0]) and np.allclose(rows[2], C.temper(p[2:3], 0.5)[0]), "per-row T must apply per row"
    n = np.array([4.0, 6.0]); sconf = np.array([4 * 0.9, 6 * 0.6]); ncorr = np.array([2.0, 6.0])
    hand = (4 * abs(0.9 - 0.5) + 6 * abs(0.6 - 1.0)) / 10
    assert abs(C.ece_from_bins(n, sconf, ncorr) - hand) < 1e-12, f"ECE {C.ece_from_bins(n, sconf, ncorr)}, hand {hand}"
    assert C.ece_from_bins(np.zeros(2), np.zeros(2), np.zeros(2)) is None, "an empty cell has no ECE"


def c3():
    """auroc_from_hist: perfect separation 1, reversed 0, identical 0.5, a hand case with ties."""
    pos = np.array([0.0, 0.0, 5.0]); neg = np.array([5.0, 0.0, 0.0])
    assert C.auroc_from_hist(pos, neg) == 1.0, f"perfect separation {C.auroc_from_hist(pos, neg)}, expected 1"
    assert C.auroc_from_hist(neg, pos) == 0.0, f"reversed {C.auroc_from_hist(neg, pos)}, expected 0"
    assert C.auroc_from_hist(pos, pos) == 0.5, f"identical {C.auroc_from_hist(pos, pos)}, expected 0.5"
    pos = np.array([1.0, 2.0, 1.0]); neg = np.array([2.0, 1.0, 1.0])          # 4 x 4 pairs
    hand = (1 * (0 + 0.5 * 2) + 2 * (2 + 0.5 * 1) + 1 * (3 + 0.5 * 1)) / 16     # 1.0 + 5.0 + 3.5 = 9.5 / 16
    assert abs(C.auroc_from_hist(pos, neg) - hand) < 1e-12, f"ties case {C.auroc_from_hist(pos, neg)}, hand {hand}"
    assert C.auroc_from_hist(np.zeros(3), neg) is None, "no positives: no AUROC"


def c4():
    """fit_temperature recovers a known sharpening: labels from q, p = temper(q, 0.5) fits T near 2; p = q fits near 1."""
    rng = np.random.default_rng(1)
    q = rng.dirichlet(np.full(D.N_ACTS, 0.5), 40_000)
    y = np.array([rng.choice(D.N_ACTS, p=row) for row in q])
    T2 = C.fit_temperature(C.nll_grid(C.temper(q, 0.5), y))
    assert abs(T2 - 2.0) <= 0.06, f"sharpened by 0.5, fitted T {T2}, expected 2.00 ± 0.06"
    T1 = C.fit_temperature(C.nll_grid(q, y))
    assert abs(T1 - 1.0) <= 0.06, f"calibrated input, fitted T {T1}, expected 1.00 ± 0.06"
    g = C.nll_grid(q[:100], y[:100])
    i1 = int(np.argmin(np.abs(C.T_GRID - 1.0)))
    hand = float(-np.log(q[:100][np.arange(100), y[:100]]).sum())
    assert abs(g[i1] - hand) < 1e-6, f"NLL at T = 1 {g[i1]}, hand {hand}"


def c5():
    """the cell-share guard: every registered cell's count in the act arc's accuracy read is at or over the floor, printed first."""
    acc = json.loads((C.ACT / "reads" / "accuracy.json").read_text())["tables"]
    print("registered cells (needy-tuning, covered, y0), n per seed-1 head:")
    for h, hz, rg in C.REGISTERED:
        n = acc[C.head_name(h, 1)]["needy-tuning"][hz][rg]["covered"]["n"]
        print(f"  {h} {hz} {rg}: {n:,} ({n / acc[C.head_name(h, 1)]['needy-tuning'][hz]['all']['covered']['n']:.4f} of the cell's all)")
        assert n >= C.FLOOR_CELL, f"registered cell {h}/{hz}/{rg} holds {n:,} samples, under the floor {C.FLOOR_CELL:,}"
    assert set(C.REGISTERED) == {(h, "y0", r) for h in ("B10", "B30") for r in ("seen", "heard")}, "the registered cells are B10 / B30 x seen / heard at y0"


def c6():
    """reader smoke on one tuning world with B10-s1: regime counts sum to all, all equals the covered pairs' defined ticks, and
    the cell's log-loss and top-1 equal the act arc's metrics_hand on the same arrays."""
    arm, k, seed, ticks, path = next(w for w in R.needy_worlds("tuning") if w[0] == "N")
    w, observers, scripted = R.load_needy(path, arm, k, seed, "tuning")
    pairs, X, ys, states, cls = R.world_inputs(w, observers, scripted)
    m = TA.load_act("B10", 1)[0]
    P = TA.probs_from_x(m, X)
    cells = {rg: C.Cal() for rg in C.REGIMES}
    cov = [pi for pi in range(len(pairs)) if cls[pi] == "covered"]
    T_rows_all = np.ones(ticks)
    for pi in cov:
        yy, st = ys[pi][:, 0], states[pi]
        for rg in C.REGIMES:
            sel = (yy >= 0) if rg == "all" else (yy >= 0) & (st == D.STATE_NAMES.index(rg))
            if sel.any():
                cells[rg].add(P[sel, pi, 0], yy[sel], 1.0, T_rows_all[sel])
    rows = {rg: c.row() for rg, c in cells.items()}
    assert rows["all"]["n"] == ticks * len(cov), f"all n {rows['all']['n']}, expected {ticks * len(cov)} (ticks x covered pairs)"
    assert rows["seen"]["n"] + rows["heard"]["n"] + rows["silent"].get("n", 0) == rows["all"]["n"], "regimes must partition all"
    pi = cov[0]
    yy = ys[pi][:, 0]
    hand = R.metrics_hand(yy, P[:, pi, 0].argmax(1), P[:, pi, 0])
    one = C.Cal(); one.add(P[:, pi, 0], yy, 1.0, np.ones(ticks)); r1 = one.row()
    # metrics_hand sums float32 probabilities, Cal sums float64: agreement to 1e-6, not to the last bit
    assert abs(r1["logloss"] - hand["logloss"]) < 1e-6, f"log-loss {r1['logloss']} vs metrics_hand {hand['logloss']}"
    assert abs(r1["top1"] - hand["top1"]) < 1e-12, f"top-1 {r1['top1']} vs metrics_hand {hand['top1']}"
    assert r1["ece"]["T1"] == r1["ece"]["global"] == r1["ece"]["regime"], "at T = 1 everywhere the three temperings agree"
    assert sum(b["n"] for b in r1["bins"]["T1"]) == ticks and sum(e["n"] for e in r1["entropy_bins"]) == ticks, "bins must hold every tick"


def c7():
    """the temperature fit reads Phase 1e's VALIDATION split only: disjoint from training, 52 worlds, and never a needy-set world."""
    tr, va, ev = D.role_lists()
    fw = C.fit_worlds()
    assert fw == list(va), f"fit_worlds is not the validation split ({len(fw)} worlds against {len(va)})"
    assert not set(fw) & set(tr), "the fit's worlds overlap training"
    assert not set(fw) & set(ev), "the fit's worlds overlap the lived evaluation worlds"
    assert len(fw) == 52, f"validation split has {len(fw)} worlds, expected 52"
    w = D.load_world(*next(v for v in fw if v[0].startswith("TN")))
    assert all(j not in w["scripted"] for _k, j in C.covered_pairs(w)) and len(C.covered_pairs(w)) == 12, "covered_pairs must drop the scripted friend's rows (4 observers x 3 covered friends)"


GUARDS = {"c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5, "c6": c6, "c7": c7}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok")
    print(f"{len(names)} passed")
