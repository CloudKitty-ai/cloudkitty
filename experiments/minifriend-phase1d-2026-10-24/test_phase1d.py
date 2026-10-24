#!/usr/bin/env python3
"""Guards for Phase 1d (Phase 1 arc venv; this arc's split and symlinked
raws). DECLARATION.md §Instrument names each with its predicted red.

t1  spread arithmetic: half-bin shifts give sd 0.5 after one tick and
    1.0 after four; the implementation equals √(n f (1 − f)) while
    unclamped; a clamped case is flagged
t2  frozen state: the extracted z through the base head's own output
    layer equals 1b's committed prediction on a 600-tick slice; the
    base head's bytes are unchanged by a probe fit
t3  reader arithmetic: calibration_p on a hand case; the above-0.7 gap;
    the decision rule returns A / B / C on hand cases
t4  provenance: split.json equals 1b's; the SD-w16 cells re-read here
    equal 1c's committed read; the base heads' sha256 equal done.json
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
PHASE1B = HERE.parent / "minifriend-phase1b-2026-10-23"
PHASE1C = HERE.parent / "minifriend-phase1c-2026-10-23"
os.environ["MINIFRIEND_ARC"] = str(HERE)
sys.path.insert(0, str(HERE))
import filter_spread as FS  # noqa: E402
import grave_probe as G  # noqa: E402
import read_phase1d as P  # noqa: E402

D = G.D
S = G.S
C = P.C
R = P.R


def test_t1_spread_arithmetic():
    b, clamped = FS.propagate(0.5, 1, start=2)
    assert not clamped and abs(b[2] - 0.5) < 1e-12 and abs(b[3] - 0.5) < 1e-12
    assert abs(FS.belief_sd(b) - 0.5) < 1e-12
    b4, _ = FS.propagate(0.5, 4, start=2)
    assert abs(FS.belief_sd(b4) - 1.0) < 1e-12 and abs(b4.sum() - 1.0) < 1e-12
    for f in (0.02, 0.08, 0.3, 0.91):
        for n in (1, 7, 50, 100):
            row = FS.spread_row(f * FS.M.BIN, n)
            if not row["clamped"]:
                assert row["abs_diff_bins"] < 1e-6, (f, n, row)
                assert abs(row["closed_form_bins"] - math.sqrt(n * f * (1 - f))) < 1e-12
    big = FS.spread_row(0.4, 500)                              # 0.08 bins/tick × 500 = 40 bins: past the top
    assert big["clamped"] and big["top_mass"] > 0.99 and big["sd_bins"] < 0.01 and big["abs_diff_bins"] > 5
    at100 = FS.spread_row(0.4, 100)                            # the Professor's row: a trace of mass at the top, sd within 0.01 of the closed form
    assert at100["clamped"] and at100["top_mass"] < 1e-2 and at100["abs_diff_bins"] < 0.01 and abs(at100["closed_form_bins"] - math.sqrt(7.36)) < 1e-12
    assert FS.spread_row(1.4 * FS.M.BIN, 3)["rate_bins_per_tick"] == 1.4   # the integer part moves, the fraction smears
    assert abs(FS.spread_row(1.4 * FS.M.BIN, 3)["closed_form_bins"] - math.sqrt(3 * 0.4 * 0.6)) < 1e-9


def test_t2_frozen_state():
    base = "NF-h24-s1"
    model, ck = G.load_base(base)
    roles = D.roles()
    s = roles["P1"]["eval"][0]
    w = D.load_world("P1", s)
    pairs, z = G.states_world(model, w, ticks=600)
    assert z.shape == (600, 20, 24)
    worst = G.check_reproduces(model, base, w, pairs, z)                   # asserts < PRED_TOL inside
    assert worst < G.PRED_TOL
    before = {k: v.clone() for k, v in model.state_dict().items()}
    Z, y, vis, code, hap_only = G.collect(model, [("P1", s)], ticks=2 * G.T.CHUNK)
    assert Z.shape == (20 * 1000, 24) and y.shape == (20000,) and vis.shape == (20000,) and hap_only.shape == (20000,)
    assert set(int(c) for c in np.unique(code)).issubset({S.GRAVE, S.ADJACENT, S.COMMON})
    assert abs(float(y.sum()) - int((code == S.GRAVE).sum())) < 1e-6 and y.sum() > 0, float(y.sum())   # P1's first world carries grave ticks early
    probe, best, ran = G.fit(Z, y, Z, y, seed=1, epochs=2)
    assert ran == 2 and best["epoch"] >= 1 and sum(p.numel() for p in probe.parameters()) == 25
    after = model.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before)
    p = G.predict_world_p(model, probe, w)
    assert p.shape == (w["ticks"], 5, 5) and np.isnan(p[:, 0, 0]).all() and np.nanmin(p) >= 0.0 and np.nanmax(p) <= 1.0


def test_t3_reader_arithmetic():
    idx = {"n": 6, "vis": np.array([1, 1, 1, 1, 0, 0], bool),
           "code": np.array([S.GRAVE, S.GRAVE, S.COMMON, S.COMMON, S.GRAVE, S.ADJACENT], np.int8),
           "true": np.array([[95, 0, 0, 0, 0, 0, 0], [10, 0, 0, 0, 0, 0, 0], [0] * 7, [0] * 7, [0] * 7, [0] * 7], np.float64)}
    p = np.array([0.9, 0.5, 0.1, 0.0, 0.8, 0.2])
    c = C.calibration_p(idx, p, idx["vis"])
    assert c["n"] == 4 and c["n_grave"] == 2 and c["n_grave_happiness_only"] == 1
    assert abs(c["brier"] - ((0.1 ** 2 + 0.5 ** 2 + 0.1 ** 2 + 0.0) / 4)) < 1e-12
    assert abs(c["mean_p_on_GRAVE"] - 0.7) < 1e-12 and abs(c["mean_p_on_COMMON"] - 0.05) < 1e-12 and c["mean_p_on_ADJACENT"] is None
    assert sum(r["n"] for r in c["reliability"]) == 4
    c_all = C.calibration_p(idx, p, np.ones(6, bool))
    assert c_all["n"] == 6 and abs(c_all["mean_p_on_ADJACENT"] - 0.2) < 1e-12
    rows = [{"lo": 0.6, "mean_p": {"mean": 0.65}, "frac_grave": {"mean": 0.1}},
            {"lo": 0.7, "mean_p": {"mean": 0.75}, "frac_grave": {"mean": 0.70}},
            {"lo": 0.8, "mean_p": {"mean": 0.85}, "frac_grave": None},
            {"lo": 0.9, "mean_p": {"mean": 0.95}, "frac_grave": {"mean": 0.85}}]
    assert abs(P.gap_above(rows) - 0.075) < 1e-12                          # (0.05 + 0.10) / 2; the 0.6 bin and the empty bin skipped

    def head(m, sd, gap):
        return {"visible": {"mean_p_on_GRAVE": {"mean": m, "sd": sd}, "above_0.7_gap": gap, "mean_p_on_COMMON": {"mean": 0.0}}}
    assert P.decide(head(0.47, 0.11, 0.05), head(0.40, 0.05, 0.08))["outcome"] == "A"     # |Δ| 0.07 ≤ s 0.121
    assert P.decide(head(0.60, 0.02, 0.03), head(0.40, 0.02, 0.08))["outcome"] == "B"     # Δ 0.20 > s 0.028, SD's gap smaller
    assert P.decide(head(0.60, 0.02, 0.09), head(0.40, 0.02, 0.08))["outcome"] == "C"     # Δ > s but SD's gap larger
    assert P.decide(head(0.30, 0.02, 0.03), head(0.50, 0.02, 0.08))["outcome"] == "C"     # reversed
    assert P.score_p2(head(0.41, 0.0, 0.0))["met"] and not P.score_p2(head(0.39, 0.0, 0.0))["met"]


def test_t4_provenance():
    assert (HERE / "split.json").read_bytes() == (PHASE1B / "split.json").read_bytes()
    idx = R.eval_index(C.GROUPS["P"])
    sd = P.head_read([C.grave_probability(C.load_field(run, idx, "grave")) for run in P.SD_RUNS], idx)
    ref = json.loads((PHASE1C / "phase1c-read.json").read_text())["reads"]["16"]["P"]["R4c_calibration"]
    for v in ("visible", "all"):
        for f in ("brier", "mean_p_on_GRAVE", "mean_p_on_COMMON"):
            assert abs(sd[v][f]["mean"] - ref[v][f]["mean"]) < 1e-9 and abs(sd[v][f]["sd"] - ref[v][f]["sd"]) < 1e-9, (v, f)
        assert [r["n"] for r in sd[v]["reliability_seed_mean"]] == [r["n"] for r in ref[v]["reliability_seed_mean"]]
    assert sd["fog"]["n_grave"] + sd["visible"]["n_grave"] == sd["all"]["n_grave"]
    for b in ("NF", "DR"):
        for s in (1, 2, 3):
            base = f"{b}-h24-s{s}"
            done = json.loads((HERE / "results-raw/heads" / base / "done.json").read_text())
            assert hashlib.sha256((HERE / "results-raw/heads" / base / "head-best.pt").read_bytes()).hexdigest() == done["head_sha256"], base


def test_t5_which_need():
    true = np.zeros((6, 7)); true[0, 0] = 95; true[1, 2] = 92; true[1, 3] = 91; true[2, 4] = 90; true[3, 1] = 50; true[4, 0] = 99; true[5, 0] = 93
    idx = {"n": 6, "true": true, "vis": np.ones(6, bool), "code": np.array([S.GRAVE] * 3 + [S.GRAVE, S.GRAVE, S.GRAVE], np.int8)}
    score = np.array([[9, 1, 1, 1, 1], [1, 1, 5, 7, 1], [1, 1, 1, 1, 9], [1, 9, 1, 1, 1], [1, 9, 8, 1, 1], [9, 1, 1, 1, 1]], float)
    old = P.MIN_N
    P.MIN_N = 1
    try:
        w = P.which_need(idx, score, np.ones(6, bool))
        # sample 3 is happiness-only grave (excluded); sample 1 has two grave needs and names play (grave); sample 4 names drink for a grave eat, and eat is not in its top two
        assert w["n"] == 5 and w["n_multi"] == 1 and abs(w["accuracy"] - 0.8) < 1e-12 and abs(w["top2_accuracy"] - 0.8) < 1e-12
        assert w["per_need"]["eat"] == {"n": 3, "accuracy": 2 / 3} and w["per_need"]["sleep"]["n"] == 1 and w["per_need"]["sleep"]["accuracy"] == 1.0
        assert w["confusion_true_x_named"][0] == [2, 1, 0, 0, 0] and w["confusion_true_x_named"][2] == [0, 0, 0, 1, 0]
        w2 = P.which_need(idx, score, np.array([1, 1, 1, 1, 0, 0], bool))
        assert w2["n"] == 3 and abs(w2["accuracy"] - 1.0) < 1e-12
    finally:
        P.MIN_N = old
    w3 = P.which_need(idx, score, np.ones(6, bool))
    assert w3["accuracy"] is None and w3["per_need"]["eat"]["accuracy"] is None and w3["n"] == 5      # under MIN_N = 200: fail closed
    assert P.baseline_which_need(idx, np.ones(6, bool), 0)["accuracy"] is None


def test_t6_latency():
    # one slice of 20 ticks: grave on [4, 9) and [14, 17); visible at tick 4, fog at tick 14
    code = np.full(20, S.COMMON, np.int8); code[4:9] = S.GRAVE; code[14:17] = S.GRAVE
    vis = np.ones(20, bool); vis[12:] = False
    idx = {"n": 20, "code": code, "vis": vis, "true": np.zeros((20, 7)), "slices": [("P1", 1, 0, 1, 0, 20)]}
    eps = P.episodes(idx)
    assert eps == [(4, 9, 0), (14, 17, 0)]
    sig = np.zeros(20); sig[7:9] = 0.9; sig[10:12] = 0.9                  # crosses 3 ticks after the first onset; never in the second; a false-alarm run on [10, 12)
    lat = P.latency(idx, sig, 0.5, eps)
    assert lat["all"]["episodes"] == 2 and abs(lat["all"]["detected_frac"] - 0.5) < 1e-12 and lat["all"]["median_latency"] == 3.0
    assert lat["onset_visible"]["episodes"] == 1 and lat["onset_visible"]["median_latency"] == 3.0 and lat["onset_visible"]["within_10_frac"] == 1.0
    assert lat["onset_fog"]["episodes"] == 1 and lat["onset_fog"]["detected_frac"] == 0.0 and lat["onset_fog"]["median_latency"] is None
    assert lat["all"]["length_median"] == 4.0 and lat["false_alarms"]["runs"] == 1 and lat["false_alarms"]["run_median_length"] == 2.0
    assert abs(lat["false_alarms"]["per_10k_ticks"] - 500.0) < 1e-9
    assert lat["reset"]["episodes"] == 0 and lat["midworld_visible"]["episodes"] == 1 and lat["midworld_fog"]["episodes"] == 1
    sig2 = np.zeros(20); sig2[2:6] = 0.9                                    # above before the onset: latency 0, anticipated
    lat2 = P.latency(idx, sig2, 0.5, eps)
    assert lat2["onset_visible"]["median_latency"] == 0.0 and lat2["onset_visible"]["anticipated_frac"] == 1.0 and lat2["false_alarms"]["runs"] == 0
    # a second slice whose friend is grave from its first tick: a RESET episode; a signal already high there is neither a detection to credit nor anticipated,
    # and a run that starts at the slice's first tick is a reset-transient false alarm, not a mid-world one
    code2 = np.concatenate([code, np.full(10, S.COMMON, np.int8)]); code2[20:23] = S.GRAVE
    vis2 = np.concatenate([vis, np.ones(10, bool)])
    idx2 = {"n": 30, "code": code2, "vis": vis2, "true": np.zeros((30, 7)), "slices": [("P1", 1, 0, 1, 0, 20), ("P1", 1, 2, 1, 20, 30)]}
    eps2 = P.episodes(idx2)
    assert eps2 == [(4, 9, 0), (14, 17, 0), (20, 23, 20)] and P.friend_episode_count(idx2, eps2) == 3
    sig3 = np.zeros(30); sig3[19:22] = 0.9; sig3[25:27] = 0.9                # high across the slice boundary; a reset-start run would need the first tick
    lat3 = P.latency(idx2, sig3, 0.5, eps2)
    assert lat3["reset"]["episodes"] == 1 and lat3["reset"]["median_latency"] == 0.0 and lat3["reset"]["anticipated_frac"] == 0.0   # tick 19 belongs to another slice: never "before onset"
    assert lat3["false_alarms"]["runs"] == 2 and lat3["false_alarms"]["runs_at_reset"] == 0 and lat3["false_alarms"]["midworld_runs"] == 2
    sig4 = np.zeros(30); sig4[20:22] = 0.0; sig4[0:2] = 0.9                   # a run starting at the first slice's first tick with no grave tick: reset transient
    lat4 = P.latency(idx2, sig4, 0.5, eps2)
    assert lat4["false_alarms"]["runs"] == 1 and lat4["false_alarms"]["runs_at_reset"] == 1 and lat4["false_alarms"]["midworld_runs"] == 0 and lat4["false_alarms"]["midworld_per_10k_ticks"] == 0.0


if __name__ == "__main__":
    only = sys.argv[1:]
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and (not only or k in only)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
