"""Guard for seating_read.py on the REAL fixture (seed 900506, 300
ticks — a recorded payload, not hand-written). References are
computed by independent code paths in this file with independent
constants (R_*), never imported from the reader (the stage-B
shared-constant lesson). Analytic literals check the math helpers.

Mutate reds on record (predictions in RESULTS §Guard):
  (a) pair_dist Manhattan -> Chebyshev : test_contact_company_nearest
  (b) worst-gate index set loses Bath  : test_worst_gate
  (c) JS divergence loses the mixture  : test_js_analytic
"""
import json
from pathlib import Path

import numpy as np
import seating_read as sr

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture-streams-900506.npz"

# Independent constants (do not import from the reader).
R_CONTACT, R_COMPANY = 1, 4
R_GATE = (0, 1, 2, 4, 5)
R_EAT, R_DRINK, R_PLAY = 3, 4, 5
R_HIGH = 25.0
R_DRINK_NEED = 1


def _leg():
    z = np.load(FIXTURE)
    leg, _heats, _all, _meta = sr.read_leg(z)
    return z, leg


def test_activity_share():
    z, leg = _leg()
    act = z["activity"]
    T = act.shape[0]
    for k in (0, 1):  # Miso, Biscuit
        ref = [round(sum(1 for t in range(T) if act[t, k] == a) / T, 6) for a in range(7)]
        assert leg["cats"][k]["activity_share"] == ref, k


def test_contact_company_nearest():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    T, R = pos.shape[:2]
    for k in (0, 4):
        near = []
        for t in range(T):
            ds = [abs(pos[t, k, 0] - pos[t, j, 0]) + abs(pos[t, k, 1] - pos[t, j, 1])
                  for j in range(R) if j != k]
            near.append(min(ds))
        near = np.array(near)
        g = leg["cats"][k]["grouped"]
        assert abs(g["contact"] - (near <= R_CONTACT).mean()) < 1e-9, k
        assert abs(g["company"] - (near <= R_COMPANY).mean()) < 1e-9, k
        assert leg["cats"][k]["nearest_cat"]["median"] == float(np.median(near)), k


def test_worst_gate():
    z, leg = _leg()
    needs = z["needs"]
    for k in (2,):  # Pumpkin
        worst = np.array([max(needs[t, k, i] for i in R_GATE) for t in range(needs.shape[0])])
        wg = leg["cats"][k]["worst_gate"]
        assert wg["median"] == float(np.median(worst))
        assert wg["p95"] == float(np.percentile(worst, 95))
        # streak reference, independent run finder
        high = worst >= R_HIGH
        n_runs = 0
        prev = False
        for v in high:
            if v and not prev:
                n_runs += 1
            prev = bool(v)
        assert leg["cats"][k]["high_streaks"]["count"] == n_runs


def test_cadence():
    z, leg = _leg()
    act = z["activity"]
    for k in (0,):
        starts = [t for t in range(act.shape[0])
                  if act[t, k] == R_EAT and (t == 0 or act[t - 1, k] != R_EAT)]
        gaps = np.diff(starts)
        cad = leg["cats"][k]["eat_cadence"]
        assert cad["n"] == len(gaps)
        if len(gaps):
            assert cad["median"] == float(np.median(gaps))


def test_distress_latency():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    flags = z["distress"] > 0
    T, R = flags.shape
    for k in range(R):
        onsets, lats = 0, []
        t = 0
        while t < T:
            if flags[t, k] and (t == 0 or not flags[t - 1, k]):
                onsets += 1
                u = t
                found = None
                while u < T and flags[u, k]:
                    ds = [abs(pos[u, k, 0] - pos[u, j, 0]) + abs(pos[u, k, 1] - pos[u, j, 1])
                          for j in range(R) if j != k]
                    if min(ds) <= R_CONTACT:
                        found = u - t
                        break
                    u += 1
                if found is not None:
                    lats.append(found)
            t += 1
        d = leg["cats"][k]["distress"]
        assert d["onsets"] == onsets, k
        assert d["responded"] == len(lats), k
        if lats:
            assert d["latency"]["median"] == float(np.median(lats)), k


def test_home_range():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    for k in (3,):
        counts = {}
        for t in range(pos.shape[0]):
            key = (pos[t, k, 0], pos[t, k, 1])
            counts[key] = counts.get(key, 0) + 1
        vals = sorted(counts.values(), reverse=True)
        total = sum(vals)
        acc, n = 0, 0
        for v in vals:
            acc += v
            n += 1
            if acc >= 0.9 * total:
                break
        assert leg["cats"][k]["home_range_tiles"] == n


def test_water_directness():
    z, leg = _leg()
    meta = json.loads(str(z["meta"]))
    wcode = meta["element_types"]["Water"]
    els = z["elements"][0]
    water = [(int(x), int(y)) for c, x, y in els if c == wcode]
    pos = z["pos"].astype(int)
    needs = z["needs"]
    act = z["activity"]
    T = pos.shape[0]
    for k in range(5):
        deltas = []
        for t in range(T - 1):
            if needs[t, k, R_DRINK_NEED] >= R_HIGH and act[t, k] != R_DRINK:
                d0 = min(abs(pos[t, k, 0] - x) + abs(pos[t, k, 1] - y) for x, y in water)
                d1 = min(abs(pos[t + 1, k, 0] - x) + abs(pos[t + 1, k, 1] - y) for x, y in water)
                deltas.append(d1 - d0)
        got = leg["cats"][k]["water_directness"]
        if deltas:
            assert got is not None and abs(got - float(np.mean(deltas))) < 1e-9, k
        else:
            assert got is None, k


def test_js_analytic():
    one_bit = sr.js_divergence(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    assert abs(one_bit - 1.0) < 1e-12
    same = sr.js_divergence(np.array([0.3, 0.7]), np.array([0.3, 0.7]))
    assert abs(same) < 1e-12
    a, b = np.array([0.9, 0.1]), np.array([0.2, 0.8])
    assert abs(sr.js_divergence(a, b) - sr.js_divergence(b, a)) < 1e-12


def test_entropy_analytic():
    assert abs(sr.entropy(np.array([5, 5, 5, 5])) - 2.0) < 1e-12
    assert sr.entropy(np.array([7, 0, 0, 0])) == 0.0
    # transition entropy of a deterministic alternation is 0 bits
    assert sr.transition_entropy(np.array([0, 1] * 50), n_states=2) == 0.0


def test_welfare_gap():
    z, leg = _leg()
    hap = z["hap"]
    gap = hap.max(1) - hap.min(1)
    assert abs(leg["welfare"]["gap"]["mean"] - float(gap.mean())) < 1e-9
    assert abs(leg["welfare"]["nash_mean"] - float(z["nash"].mean())) < 1e-12


if __name__ == "__main__":
    import sys
    fns = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    for f in fns:
        f()
        print(f"{f.__name__} OK")
    print(f"{len(fns)} tests OK")
