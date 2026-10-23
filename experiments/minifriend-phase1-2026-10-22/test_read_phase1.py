#!/usr/bin/env python3
"""Guards for read_phase1.py (arc venv; raws and at least one head run
present — the smoke run DR-s1-smoke stands in for both heads here, so
every head-vs-head comparison is an identity and the guards test the
reader's arithmetic, not the result).

r1  the floor equals DR's pooled mind-visible GRAVE loss recomputed from
    the per-friend rows (sample-weighted over the covered friends), and
    the pooled friends are exactly the covered ones
r2  the dissolution verdict flips when NF's GRAVE loss is scaled by 1.11
    (and holds at 1.09)
r3  the ostrich gap equals GRAVE bias minus COMMON bias per friend, and
    the signature needs both the 1.5× lift and a negative GRAVE bias
r4  fail-closed: a friend × stratum × version cell under min-n is None
    (Pumpkin's mind-visible GRAVE, 170 on the recorded eval worlds)
r5  MSE5 is in need points: the pooled all-states COMMON cell equals a
    hand computation from the prediction file and the aligned truth
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_phase1 as R  # noqa: E402
import phase1_data as D  # noqa: E402

RUN = "DR-s1-smoke"
_cache = {}


def _out():
    if "out" not in _cache:
        _cache["out"] = R.read([("NF", RUN), ("DR", RUN)])
    return _cache["out"]


def test_r1_floor_is_the_pooled_grave_loss_over_covered_friends():
    out = _out()
    cells = out["per_run_cells"][RUN]["visible"]["GRAVE"]
    covered = [f for f, c in cells["per_friend"].items() if not c.get("insufficient")]
    n = sum(cells["per_friend"][f]["n"] for f in covered)
    hand = sum(cells["per_friend"][f]["n"] * cells["per_friend"][f]["mse5"] for f in covered) / n
    assert abs(cells["pooled"]["mse5"] - hand) < 1e-9 * hand, (cells["pooled"]["mse5"], hand)
    assert cells["pooled"]["n"] == n and cells["pooled"]["friends"] == sorted(covered)
    assert abs(out["R2"]["floor_dr_grave"] - hand) < 1e-9 * hand
    assert out["R2"]["pooled_friends"] == covered and "Pumpkin" not in covered


def test_r2_verdict_flips_at_the_tolerance():
    out = _out()
    nf, dr = out["heads"]["NF"]["mse5"], out["heads"]["DR"]["mse5"]
    assert R.dissolution(nf, dr)["dissolves"] is True        # identical heads dissolve
    for scale, expect in ((1.09, True), (1.11, False)):
        s = copy.deepcopy(nf)
        for f in R.SEATS + ["pooled"]:
            if s["visible"]["GRAVE"][f] is not None:
                s["visible"]["GRAVE"][f]["mean"] *= scale
        got = R.dissolution(s, dr)
        assert got["dissolves"] is expect, (scale, got["pooled_ok"], got["friends_ok"])
    # a single covered friend over the line by more than its sd fails the second clause alone
    s = copy.deepcopy(nf)
    s["visible"]["GRAVE"]["Miso"]["mean"] *= 1.11
    got = R.dissolution(s, dr)
    assert got["pooled_ok"] is True and got["friends_ok"] is False and got["dissolves"] is False


def test_r3_ostrich_gap_arithmetic_and_signature():
    out = _out()
    b = out["heads"]["DR"]["bias"]
    o = R.ostrich(b)
    for v in R.VERSIONS:
        for f in R.SEATS + ["pooled"]:
            g, c = b[v]["GRAVE"][f], b[v]["COMMON"][f]
            if g is None or c is None:
                assert o[v][f]["covered"] is False
                continue
            assert abs(o[v][f]["gap"] - (g["mean"] - c["mean"])) < 1e-9
            assert o[v][f]["signature"] == (abs(g["mean"]) >= 1.5 * abs(c["mean"]) and g["mean"] < 0)
    # the sign matters: a grave bias of +40 against a common +14 is a lift, not the ostrich signature
    t = copy.deepcopy(b)
    t["all"]["GRAVE"]["Miso"]["mean"] = 40.0
    t["all"]["COMMON"]["Miso"]["mean"] = 14.0
    assert R.ostrich(t)["all"]["Miso"]["signature"] is False and R.ostrich(t)["all"]["Miso"]["lift"] > 1.5


def test_r4_fail_closed_under_min_n():
    out = _out()
    cov = out["coverage"]
    assert cov["visible"]["GRAVE"]["Pumpkin"] < R.MIN_N <= cov["all"]["GRAVE"]["Pumpkin"], cov["visible"]["GRAVE"]
    assert out["heads"]["DR"]["mse5"]["visible"]["GRAVE"]["Pumpkin"] is None
    assert out["heads"]["DR"]["mse5"]["all"]["GRAVE"]["Pumpkin"] is not None
    assert out["per_run_cells"][RUN]["visible"]["GRAVE"]["per_friend"]["Pumpkin"] == {"n": cov["visible"]["GRAVE"]["Pumpkin"], "insufficient": True}


def test_r5_mse5_in_need_points_matches_a_hand_computation():
    out = _out()
    idx = R.eval_index()
    pred = R.load_pred(RUN, idx)
    m = np.isin(idx["code"], [2])
    hand = float(((pred[m, :5].astype(np.float64) - idx["true"][m, :5]) ** 2).mean())
    got = out["per_run_cells"][RUN]["all"]["COMMON"]["pooled"]["mse5"]
    assert abs(got - hand) < 1e-9 * hand, (got, hand)
    # and the prediction file really is read at [observer, friend]: one world, one pair, by hand
    n, s, k, j, a, b = idx["slices"][7]
    z = np.load(HERE / "results-raw/heads" / RUN / f"pred-{n}-{s}.npz")["pred"]
    assert np.allclose(pred[a:b], z[:, k, j] * 100.0)
    w = D.load_world(n, s)
    assert np.allclose(idx["true"][a:b, :5], w["needs"][:, j, :5])


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
