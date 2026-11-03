#!/usr/bin/env python3
"""Guards g1-g7 of DECLARATION.md §7 for diag_1e.py; each red on record via scripts/mutate.sh --expect
before any read. Run under the needy arc's venv:

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_diag.py [g1 ... g7]
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag_1e as G  # noqa: E402

P1E = G.P1E


def first_world(half, arm="N"):
    for a, k, seed, ticks, path in G.mods()[0].worlds(half):
        if a == arm:
            return a, k, seed, ticks, path
    raise RuntimeError


def g1():
    """persistence: a run of 4 under k = 3 keeps its last 2 ticks, a run of 2 vanishes, k = 1 is identity, burn-in zeros stay."""
    a = np.zeros((12, 1, 1), bool)
    a[2:6, 0, 0] = True      # run of 4 at ticks 2..5
    a[8:10, 0, 0] = True     # run of 2 at ticks 8..9
    p3 = G.persist(a, 3)[:, 0, 0]
    assert p3[2:6].sum() == 2, f"run of 4 under k = 3 keeps {int(p3[2:6].sum())} ticks, expected 2"
    assert p3[4] and p3[5], "the kept ticks are the run's last two"
    assert not p3[8:10].any(), "a run of 2 under k = 3 must vanish"
    assert np.array_equal(G.persist(a, 1), a), "k = 1 is the identity"
    b = a.copy()
    b[:2] = False
    assert not G.persist(b, 2)[:2].any(), "burn-in zeros stay zero"
    assert G.persist(a, 5)[:, 0, 0].sum() == 0, "no run reaches k = 5"


def g2():
    """the partition on hand streams and W's exclusive end; content_world runs on one world with valid classes."""
    T = 200
    needs = np.full((T, 5), 40.0)
    hap = np.full(T, 90.0)
    codes = np.full(T, 2, np.int8)
    t0 = 100
    n1 = needs.copy()
    n1[t0 + 20:, 0] = 80.0                                        # the worst need reaches 80 exactly at t0 + 20
    assert G.classify(n1, hap, codes, t0, W=50)[0] == "approach", "need at 80 inside [t0, t0 + 50) is approach"
    assert G.classify(n1, hap, codes, t0, W=20)[0] == "no_approach", "W's end is exclusive: tick t0 + 20 is outside W = 20"
    assert G.classify(needs, hap, codes, t0)[0] == "no_approach", "a flat friend is no approach"
    c2 = codes.copy()
    c2[t0 + 40] = 0
    assert G.classify(needs, hap, c2, t0)[0] == "grave_after", "a grave tick inside the window is grave_after"
    h3 = hap.copy()
    h3[t0 + 10] = 69.0
    assert G.classify(needs, h3, codes, t0)[0] == "approach", "happiness under 70 inside the window is approach"
    cls, dist, hdist = G.classify(n1, hap, codes, t0, W=50)
    assert dist == 10.0 and hdist == 45.0, (dist, hdist)
    assert G.rising(n1, t0 + 30) is True and G.rising(n1, 10) is None and G.rising(needs, t0) is False
    arm, k, seed, ticks, path = first_world("confirming")
    w = G.load(path, arm, k, seed, "confirming")
    rec = G.content_world(w, arm, k, seed, "confirming", {1: G.R1.load_head_e(1)})
    runs = rec["runs"]["1"]
    assert runs, "the first confirming N world has at least one false run at S for seed 1"
    assert all(r["part"] in G.PARTS and r["cls"] in ("covered_friends", "scripted_from_first_mask") for r in runs)
    tab = G.content_table([rec], arm)
    assert tab["covered_friends"]["per_seed"]["1"]["runs"] == sum(r["cls"] == "covered_friends" for r in runs)
    shares = [tab["covered_friends"]["per_seed"]["1"]["parts"][p]["share_runs"] or 0 for p in G.PARTS]
    assert abs(sum(shares) - 1) < 1e-9 or tab["covered_friends"]["per_seed"]["1"]["runs"] == 0, shares


def g3():
    """covered crossings: the episodes equal needy_read.grave_episodes on each covered seat; the scripted seat yields
    none and is never an observer; each covered friend has exactly three observers."""
    _rise, R, _L = G.mods()
    arm, k, seed, ticks, path = first_world("confirming")
    w = G.load(path, arm, k, seed, "confirming")
    eps = G.covered_episodes(w)
    assert set(eps) == set(R.observers(w)) and w["scripted"][0] not in eps, "the scripted seat yields no covered episode"
    for j, es in eps.items():
        assert es == R.grave_episodes(w["codes"][:, j]), j
    rec = G.covered_world(w, arm, seed, {1: G.R1.load_head_e(1)}, [G.S])
    for e in rec["episodes"]:
        obs = set(map(int, e["observers"]))
        assert w["scripted"][0] not in obs, "the scripted seat admitted as an observer of a covered episode"
        assert len(obs) == 3 and e["friend"] not in obs, (obs, e["friend"])
        for o in e["observers"].values():
            c = o["cells"]["1"][G.S]
            assert c["latency"] is None or 0 <= c["latency"] < e["length"]
            assert c["lead"] is None or (c["latency"] is not None and c["lead"] > 0)
    tab = G.covered_table([rec], G.S)
    assert tab["observer_episodes"] == 3 * tab["friend_episodes"] == 3 * rec["n_covered_episodes"]
    bar = G.p22_bar()
    assert 0.6 < bar["splice_H100_at_S_threshold"] < 0.7 and 0.85 < bar["scripted_N_mean_at_S"] < 0.92 and abs(bar["bar"] - (bar["splice_H100_at_S_threshold"] + bar["scripted_N_mean_at_S"]) / 2) < 1e-12, bar


def g4():
    """reliability: bins partition n; within-h is inclusive at both ends and clipped to the world's end."""
    g = np.zeros(20, bool)
    g[10] = True
    w3 = G.within(g, 3)
    assert w3[7] and w3[10] and not w3[6] and not w3[11], "within-h = any grave in [t, t + h] inclusive: t = 7 at h = 3 sees tick 10"
    assert not G.within(np.zeros(5, bool), 50).any(), "no grave, no within"
    g2 = np.zeros(5, bool)
    g2[4] = True
    assert G.within(g2, 0).tolist() == [False, False, False, False, True]
    p = np.array([0.0, 0.005, 0.01, 0.02, 0.049, 0.05, 0.1, 0.2, 0.5, 0.99, 1.0])
    idx = G.bin_index(p)
    assert idx.tolist() == [0, 0, 1, 2, 2, 3, 4, 5, 6, 6, 6], idx.tolist()
    assert np.bincount(idx, minlength=7).sum() == len(p)
    arm, k, seed, ticks, path = first_world("confirming")
    w = G.load(path, arm, k, seed, "confirming")
    m, pr = G.R1.load_head_e(1)
    P, _M = G.signals(m, pr, w)
    _above, b = G.alarm_S(P)
    acc = G.reliability_world(w, G.mods()[2].first_episode(w, arm), P, b)
    n_cov, n_scr = sum(acc["covered_friends"]["n"]), sum(acc["scripted"]["n"])
    assert n_cov == 12 * (w["ticks"] - b) and n_scr == 4 * (w["ticks"] - b), (n_cov, n_scr)
    assert all(acc[c]["now"][i] <= acc[c]["w10"][i] <= acc[c]["w50"][i] <= acc[c]["n"][i] for c in acc for i in range(7))
    tab = G.reliability_table([acc])
    assert abs(sum(r["n"] for r in tab["covered_friends"]["bins"].values()) - n_cov) == 0


def g5():
    """one forward, two outputs: P equals needy_read.probe_world's to 0.0 (frozen seed 1) and the retrained head's means
    reproduce its committed pred file on P1's first evaluation world."""
    _rise, R, _L = G.mods()
    name, seed = "P1", 1095452
    w = R.load_world(G.EXPTS / "minifriend-phase1b-2026-10-23" / "results-raw" / name / f"streams-{seed}.npz")
    m0, p0, _ = R.load_probe(1)
    P, _M = G.signals(m0, p0, w)
    ref = R.probe_world(m0, p0, w)
    assert np.nanmax(np.abs(P - ref)) == 0.0 and np.isnan(P).sum() == np.isnan(ref).sum(), "P must equal probe_world's exactly"
    m1, p1 = G.R1.load_head_e(1)
    _P1, M = G.signals(m1, p1, w)
    pred = np.load(P1E / "results-raw" / "heads" / "NF1e-h24-s1" / f"pred-{name}-{seed}.npz")["pred"] * 100.0     # (T, R, R, 7) / 100
    worst = float(np.nanmax(np.abs(M - pred[..., :5])))
    assert worst < 1e-2, f"the means differ from the committed pred file by {worst} (0-100 scale)"


def g6():
    """identity: on the first confirming arm N world, D3's k = 1 cell and D4's lambda = 0 cell reproduce Phase 1e's
    committed confirming record at S (retrained seed 1): latency, lead, false runs per class, runs at offset B."""
    arm, k, seed, ticks, path = first_world("confirming")
    cf = json.loads((P1E / "reads" / "confirming.json").read_text())
    ref = [r for r in cf["records"]["new"] if r["arm"] == arm and r["seed"] == seed][0]["cells"]["1"][G.S]
    w = G.load(path, arm, k, seed, "confirming")
    probes = {1: G.R1.load_head_e(1)}
    keys = ("latency", "lead", "lead_not_at_offset_B", "fa", "fa_at_offset_B", "fa_run_ticks", "first_alarmable")
    for kind, base in (("persistence", f"{G.S}-k1"), ("means", f"{G.S}-m0")):
        rec = G.ladder_world(w, arm, k, seed, "confirming", probes, kind)
        got = rec["cells"]["1"][base]
        assert {x: got[x] for x in keys} == {x: ref[x] for x in keys}, f"{kind}'s base cell {base} differs from the committed confirming record at S"
    assert any(v for v in ref["fa"].values()), "the guard world holds at least one false run (the identity is not vacuous)"


def g7():
    """halves: D1 / D2 / D5 run on confirming seeds, D3 / D4 on tuning seeds; the validation list is data_1e.roles()'s 35 worlds."""
    _rise, R, _L = G.mods()
    for cmd, half in G.HALF.items():
        ws = G.worlds_for(cmd)
        assert len(ws) == 180, (cmd, len(ws))
        a, k, seed, _t, _p = ws[0]
        assert R.half_of(a, k, seed) == half, f"{cmd} runs on {half} seeds only"
        other = "tuning" if half == "confirming" else "confirming"
        try:
            G.load(_p, a, k, seed, other)
        except PermissionError:
            pass
        else:
            raise AssertionError(f"{cmd}: a {half} seed loaded under the {other} half")
    assert G.HALF["content"] == G.HALF["covered"] == G.HALF["reliability"] == "confirming" and G.HALF["persistence"] == G.HALF["means"] == "tuning"
    code = "import json, data_1e as E; r = E.roles(); print(json.dumps({n: {'val': r[n]['val'], 'train': r[n]['train']} for n in E.NEW_SETS}))"
    out = subprocess.run([sys.executable, "-B", "-c", code], cwd=str(P1E), capture_output=True, text=True, check=True).stdout
    roles = json.loads(out.strip().splitlines()[-1])
    assert {n: r["val"] for n, r in roles.items()} == G.VALIDATION, "VALIDATION differs from data_1e.roles()"
    assert all(not (set(r["train"]) & set(G.VALIDATION[n])) for n, r in roles.items()), "a training world in the validation list"
    vw = G.validation_worlds()
    assert len(vw) == 35 and all(p.exists() for _n, _s, p in vw)


GUARDS = {f.__name__: f for f in (g1, g2, g3, g4, g5, g6, g7)}


def main():
    import torch
    torch.set_num_threads(1)
    names = sys.argv[1:] or list(GUARDS)
    passed, failed = 0, 0
    for n in names:
        try:
            GUARDS[n]()
            print(f"{n} PASS")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"{n} FAIL: {type(e).__name__}: {e}")
            failed += 1
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
