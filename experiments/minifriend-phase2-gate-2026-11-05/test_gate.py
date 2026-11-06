#!/usr/bin/env python3
"""Guards g1–g7 of DECLARATION.md §7 for gate_screen.py; each red on record via scripts/mutate.sh --expect before any read.
Every guard but g3 runs on synthetic inputs; g3 replays one real tuning world to a small tick (the record is read, nothing
is written, no half is touched beyond the read the gate itself declares).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_gate.py [g1 ... g7]
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_screen as G  # noqa: E402

S, D = G.S, G.D
MENU = ["move_north", "move_east", "rest_solo", "rest_with_kitty_0", "sleep_solo", "groom_self", "groom_kitty_0", "eat", "drink",
        "chase_critter_0", "play_solo", "play_kitty_0", "idle"]


def _world(T=50, grave_ticks=(10, 11, 12), vis_false=(11,)):
    """A synthetic needy-set world: 5 seats, seat 0 scripted, covered 1..4; friend 2 grave on grave_ticks; observer 1 does not
    see friend 2 on vis_false. Only what candidates() reads."""
    needs = np.full((T, 5, 6), 20.0, np.float32)
    hap = np.full((T, 5), 80.0, np.float32)
    for t in grave_ticks:
        needs[t, 2, 0] = 95.0
    codes = S.stratum(needs, hap)
    obs = np.zeros((T, 5, 399), np.float16)
    from count_strata import SELF_BLOCK, KITTY_SLOT  # noqa: E402
    import needy_read as NR  # noqa: E402
    for k in range(1, 5):
        for j in range(5):
            if j != k:
                obs[:, k, SELF_BLOCK + KITTY_SLOT * NR.friend_row(k, j)] = 1.0     # present (seen) everywhere ...
    for t in vis_false:
        obs[t, 1, SELF_BLOCK + KITTY_SLOT * NR.friend_row(1, 2)] = 0.0          # ... but observer 1 misses friend 2 there
    return {"ticks": T, "needs": needs, "hap": hap, "codes": codes, "obs": obs, "obs_recorded": [False, True, True, True, True]}


def g1():
    """branch points: strata from the FRIEND's true state at t, t >= 1, covered friends only (never the scripted seat, never
    k == j), visible = the observer sees her; the sample is per cell, without replacement, fixed seed, min-n fail-closed."""
    G.R.mods()
    w = _world()
    c = G.candidates(w)
    grave_all = c["GRAVE/all"]
    assert grave_all.shape[0] == 3 * 3, grave_all.shape          # friend 2 grave on 3 ticks x observers 1, 3, 4
    assert set(grave_all[:, 1].tolist()) == {2} and set(grave_all[:, 2].tolist()) == {10, 11, 12}, grave_all
    assert set(grave_all[:, 0].tolist()) == {1, 3, 4}, "observers are the covered seats other than the friend"
    assert c["GRAVE/visible"].shape[0] == 8, "observer 1 does not see friend 2 at tick 11"
    assert 0 not in set(c["COMMON/all"][:, 1].tolist()), "the scripted seat is never a branch target"
    assert c["COMMON/all"][:, 2].min() == 1, "t = 0 has no previous state and is never a branch point"
    smp = G.sample([("w", c)], n_per=5, seed=1, min_n=4)
    assert smp["coverage"]["GRAVE/all"] == {"candidates": 9, "sampled": 5, "insufficient": False}, smp["coverage"]["GRAVE/all"]
    assert smp["coverage"]["ADJACENT/all"]["insufficient"] and smp["coverage"]["ADJACENT/all"]["candidates"] == 0
    pts = smp["points"]["GRAVE/all"]
    assert len({tuple(p) for p in pts}) == 5, "without replacement"
    assert G.sample([("w", c)], n_per=5, seed=1, min_n=4)["points"] == smp["points"], "fixed seed: the same sample"
    assert smp["any_insufficient"]


def g2():
    """class -> menu action: the legal entry of the predicted class the friend's own policy ranks highest; a class with no
    legal entry -> idle; idle illegal too -> None (the record stands); purr / meow have no menu entry."""
    cm = G.class_menu(MENU)
    assert cm["rest"] == [2, 3] and cm["eat"] == [7] and cm["idle"] == [12] and cm["purr"] == [] and cm["meow"] == []
    logits = np.arange(len(MENU), dtype=np.float32)            # later entries ranked higher
    mask = np.ones(len(MENU), bool)
    assert G.branch_action("rest", mask, logits, cm, MENU) == 3, "the policy's preferred legal rest"
    mask[3] = False
    assert G.branch_action("rest", mask, logits, cm, MENU) == 2, "legality first, then preference"
    mask[7] = False
    assert G.branch_action("eat", mask, logits, cm, MENU) == 12, "no legal entry in the class -> idle"
    mask[12] = False
    assert G.branch_action("eat", mask, logits, cm, MENU) is None, "idle illegal too -> the record stands"
    assert G.branch_action("purr", np.ones(len(MENU), bool), logits, cm, MENU) == 12


def g3():
    """the replay runner on a real tuning world: ticks 0..t-1 reproduce the record (the runner's own assertion), a branch
    at t with a different legal act returns the friend's post-step state, and a branch with her RECORDED act returns the
    record itself (the zero of the divergence scale)."""
    import torch
    torch.set_num_threads(1)
    arm, k, seed, _t, path = next(x for x in G.worlds() if x[0] == "N" and x[1] == 1)
    w, z = G.load(path, arm, k, seed)
    rp = G.Replay(w, z)
    j = G.covered_friends(w)[0]
    t = 40
    mask = rp.mask_at(t, j)
    rec = int(z["act"][t, j])
    assert mask[rec], "the recorded act was legal"
    hb, nb = rp.branch(t, j, rec)
    assert abs(hb - w["post_hap"][t, j]) < 1e-3 and np.allclose(nb, w["post_needs"][t, j], atol=1e-3), "a branch on the recorded act is the record"
    assert rp.replays == 2
    alt = next(i for i in range(len(mask)) if mask[i] and i != rec)
    hb2, nb2 = rp.branch(t, j, alt)
    assert np.isfinite(hb2) and nb2.shape == (6,)
    dv = G.divergence(hb2, nb2, w["post_hap"][t, j], w["post_needs"][t, j])
    assert set(dv) == {"d_hap", "d_need"}


def g4():
    """the currency: signed and unclamped — branch − record in happiness points (positive = rosier than the record) and the
    mean over the five HIDDEN needs in need points (bath, index 5, excluded)."""
    rec_n = np.array([90.0, 10, 10, 10, 10, 50.0])
    br_n = np.array([80.0, 10, 10, 10, 10, 0.0])                  # eat relieved hunger; bath moved but is not hidden
    dv = G.divergence(91.5, br_n, 90.0, rec_n)
    assert abs(dv["d_hap"] - 1.5) < 1e-9 and abs(dv["d_need"] + 2.0) < 1e-9, dv
    dv = G.divergence(0.0, rec_n, 120.0, rec_n)
    assert abs(dv["d_hap"] + 120.0) < 1e-9, "no clamp on the happiness axis"


def _act_summary(grave, common, n=250):
    S_ = {}
    for v in G.VERSIONS:
        S_[v] = {}
        for st in G.STRATA:
            m = grave if st == "GRAVE" else (common if st == "COMMON" else 0.0)
            S_[v][st] = {arm: {"n": n, "d_hap": {"mean": m, "sd": 0.0}} for arm in G.ARMS}
    return S_


def g5():
    """the act signature (A2′ pin a): lift = |GRAVE| / |COMMON| of the seed-mean signed happiness divergence; signature only
    when lift >= 1.5 AND the GRAVE mean is positive (optimism); a pessimistic grave lift is no signature; the verdict is
    fail-closed on min-n."""
    s = G.act_signature(_act_summary(+0.30, +0.10), "B15", "all")
    assert s["signature"] and abs(s["lift"] - 3.0) < 1e-9, s
    assert not G.act_signature(_act_summary(-0.30, +0.10), "B15", "all")["signature"], "pessimism is not the ostrich"
    assert not G.act_signature(_act_summary(+0.14, +0.10), "B15", "all")["signature"], "lift 1.4 is under 1.5"
    assert G.act_signature(_act_summary(+1.5, +1.0), "B15", "all")["signature"], "lift 1.5 is on the bar"
    cov_ok = {f"{st}/{v}": {"insufficient": False} for st in G.STRATA for v in G.VERSIONS}
    needs_ok = {"summary": {fam: {v: {"insufficient": False, "signature": False, "grave": -1.0, "common": -0.9} for v in G.VERSIONS} for fam in ("NF1e", "NFfrozen")}}
    act_pass = {"summary": _act_summary(+0.05, +0.10)}
    act_fail = {"summary": _act_summary(+0.30, +0.10)}
    for a in (act_pass, act_fail):
        for v in G.VERSIONS:
            for st in G.STRATA:
                a["summary"][v][st]["F"] = {"d_hap": 0.0}
    assert G.verdict({"coverage": cov_ok}, act_pass, needs_ok)["gate"] == "PASS"
    vf = G.verdict({"coverage": cov_ok}, act_fail, needs_ok)
    assert vf["gate"] == "FAIL" and vf["heads"]["B15"]["verdict"] == "FAIL"
    cov_thin = dict(cov_ok, **{"GRAVE/visible": {"insufficient": True}})
    assert G.verdict({"coverage": cov_thin}, act_pass, needs_ok)["gate"] == "INSUFFICIENT", "thin grave stratum fails closed"
    needs_sig = {"summary": {"NF1e": {v: {"insufficient": False, "signature": v == "visible"} for v in G.VERSIONS},
                             "NFfrozen": needs_ok["summary"]["NFfrozen"]}}
    assert G.verdict({"coverage": cov_ok}, act_pass, needs_sig)["gate"] == "FAIL", "the needs head's signature fails the gate"
    # the arm aggregate carries the sparsity columns as seed means (added after the first read printed them as "—")
    rows = [{"cell": "GRAVE/all", "friend": "Miso", "predictor": f"B10-s{s}", "branched": b, "d_hap": d, "d_need": 0.0}
            for s, pts in ((1, [(True, 1.0), (False, 0.0)]), (2, [(True, 0.0), (True, 2.0)]), (3, [(False, 0.0), (False, 0.0)]))
            for b, d in pts]
    agg = G.summarise_act(rows)["all"]["GRAVE"]["B10"]
    assert abs(agg["branched"]["mean"] - 0.5) < 1e-9 and abs(agg["moved"]["mean"] - 1 / 3) < 1e-9, agg


def g6():
    """the needs head's step 2: bias = predicted − TRUE hidden needs (five, in points) on the friend's true state at t; the
    signature is |GRAVE| >= 1.5 x |COMMON| with GRAVE NEGATIVE (read less needy than she is); min-n fail-closed."""
    w = _world()
    T = w["ticks"]
    M = np.full((T, 5, 5, 5), np.nan, np.float32)
    pairs = [(1, 2), (3, 2)]
    for k, j in pairs:
        M[:, k, j, :] = w["needs"][:, j, :5] - 4.0                    # four points too rosy everywhere
    rows = G.needs_bias(w, M, pairs)
    assert len(rows) == 2 * T and all(abs(r[6] + 4.0) < 1e-4 for r in rows), "bias is pred − true, per tick"
    grave_rows = [r for r in rows if r[1] == S.GRAVE]
    assert len(grave_rows) == 6 and {r[5] for r in grave_rows} == {10, 11, 12}
    assert sum(1 for r in grave_rows if r[0]) == 5, "observer 1 misses friend 2 at tick 11"
    bias = {}
    for s in G.SEEDS:
        bias[f"NF1e-s{s}"] = {v: {st: {f: {"n": 300, "mean": (-6.0 if st == "GRAVE" else -1.0)} for f in G.FRIENDS + ("pooled",)} for st in G.STRATA} for v in G.VERSIONS}
        bias[f"NFfrozen-s{s}"] = {v: {st: {f: {"n": 300, "mean": (+6.0 if st == "GRAVE" else -1.0)} for f in G.FRIENDS + ("pooled",)} for st in G.STRATA} for v in G.VERSIONS}
    sm = G.summarise_needs(bias)
    assert sm["NF1e"]["all"]["signature"] and abs(sm["NF1e"]["all"]["lift"] - 6.0) < 1e-9
    assert not sm["NFfrozen"]["all"]["signature"], "a grave friend read MORE needy than she is is not the ostrich"
    for s in G.SEEDS:
        bias[f"NF1e-s{s}"]["visible"]["GRAVE"]["pooled"]["n"] = 199
    assert G.summarise_needs(bias)["NF1e"]["visible"]["insufficient"], "199 grave samples in one seed is under the floor"


def g7():
    """the heads: act_heads() loads exactly B10-s1..3 and B15-s1..3 from the act arc's store, frozen, at their declared
    parameter counts (B15 is the ladder's arm and must be registered before the act arc's loader knows it)."""
    hs = G.act_heads()
    assert sorted(hs) == sorted(f"{a}-s{s}" for a in ("B10", "B15") for s in (1, 2, 3)), sorted(hs)
    for name, m in hs.items():
        arm = name.split("-")[0]
        n = sum(p.numel() for p in m.parameters())
        assert n == {"B10": 8182, "B15": 12438}[arm], (name, n)
        assert G.TA.n_trained(m) == 0, f"{name} is not frozen"


GUARDS = {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g6": g6, "g7": g7}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok")
    print(f"{len(names)} passed")
