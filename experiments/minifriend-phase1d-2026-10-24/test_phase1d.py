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
t5  which-need on a hand case (§Addendum)
t6  latency on hand slices (§Addendum; extended for reset episodes)
t7  the operating-point sweep (§Addendum 2): a signal sitting exactly
    at the threshold is a crossing (at or over); detected fraction and
    false-alarm runs non-increasing up the ladder; the sweep's 0.20 and
    0.50 rows on group P equal the committed R4d rows; post-read: the
    non-grave-ticks-above column counts ticks and is monotone; the
    false-alarm start detail (offset 1; ≤ 100 inclusive; late per 10k)
t8  the burn-in (§Addendum 3): on the 300-tick slice the run count under
    burn-in 0 / 100 / 101 / 102 is 3 / 2 / 2 / 1 with the boundary run
    counted at 100 and 101, blind fraction B / 300; on the 20-tick slice
    an onset inside the burn-in is missed when its only over-threshold
    tick is masked and caught at B − k + 1 when a later tick is over; an
    onset at or after B keeps its latency; the reader's identities on
    group P at 0.10 / 0.20 with B = 0 / 100; post-read: the onset
    offsets (shared slice with a reset episode; grave after the window)
    and the start-up split (fired within the window, given grave in the
    window / given none); boundary runs cut from a grave run; per-set
    slice composition
t9  history and state (§Addendum 4): convergence windows, slope and
    ratio on a synthetic state and logit; the splice assembly (history
    rows the recipient's, from H the recipient's self block beside the
    donor's rows; the episode [H, H + en); a crossing at H + 3 reads
    latency 3, one at H − 1 does not count); next_seat; the swap
    assembly on a hand world; subindex rebasing; real pins (the re-run
    head reproduces the committed P(grave); H = 0 equals the sweep's
    reset rows; SD's H = 0 equals R4d's; B = 0 equals the sweep; the
    sub-index's unswapped reset rows equal the sweep's)
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
import sweep_threshold as SW  # noqa: E402
import burnin_read as BR  # noqa: E402
import history_read as HR  # noqa: E402
import knee_read as KR  # noqa: E402

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


def test_t7_sweep():
    # the t6 slice; a signal that sits exactly on 0.2 at the first onset, 0.3 at the second onset, and a 0.1 bump with no grave tick
    code = np.full(20, S.COMMON, np.int8); code[4:9] = S.GRAVE; code[14:17] = S.GRAVE
    vis = np.ones(20, bool); vis[12:] = False
    idx = {"n": 20, "code": code, "vis": vis, "true": np.zeros((20, 7)), "slices": [("P1", 1, 0, 1, 0, 20)]}
    sig = np.zeros(20); sig[4] = 0.2; sig[14] = 0.3; sig[10:12] = 0.1
    sw = SW.sweep(idx, [sig])
    rows = sw["rows"]
    assert list(rows) == ["0.05", "0.10", "0.15", "0.20", "0.25", "0.30", "0.40", "0.50"]
    assert rows["0.20"]["midworld_visible"]["detected_frac"]["mean"] == 1.0 and rows["0.20"]["midworld_visible"]["median_latency"]["mean"] == 0.0   # exactly at the threshold counts
    assert rows["0.25"]["midworld_visible"]["detected_frac"]["mean"] == 0.0 and rows["0.25"]["midworld_fog"]["detected_frac"]["mean"] == 1.0
    assert rows["0.10"]["false_alarms"]["midworld_runs"]["mean"] == 1 and rows["0.15"]["false_alarms"]["midworld_runs"]["mean"] == 0
    det = [r["all"]["detected_frac"]["mean"] for r in rows.values()]
    fa = [r["false_alarms"]["runs"]["mean"] for r in rows.values()]
    assert det == sorted(det, reverse=True) and fa == sorted(fa, reverse=True)
    assert det[0] == 1.0 and det[-1] == 0.0
    d = rows["0.10"]["derived"]
    assert d["midworld_detected"]["mean"] == 2.0 and d["midworld_fa_per_100_detected"]["mean"] == 50.0
    # post-read column: non-grave ticks at or over the threshold per 10k (ticks 10, 11 at 0.10; none at 0.15), monotone up the ladder
    assert rows["0.10"]["nongrave_above_per_10k"]["mean"] == 1000.0 and rows["0.15"]["nongrave_above_per_10k"]["mean"] == 0.0
    ng = [r["nongrave_above_per_10k"]["mean"] for r in rows.values()]
    assert ng == sorted(ng, reverse=True)
    assert sw["composition"] == {"P1": {"reset": 0, "midworld": 2}}
    fd = rows["0.10"]["fa_detail"]
    assert fd["midworld_runs"]["mean"] == 1 and fd["start_at_1"]["mean"] == 0 and fd["frac_start_le_early"]["mean"] == 1.0 and fd["late_runs_per_10k"]["mean"] == 0.0
    # post-read (gate round 1): where false-alarm runs start — a 300-tick slice with no grave tick and three runs: at offset 1
    # (a world-start run whose first tick is under the threshold), at offset 100 exactly (early, inclusive), and at offset 200 (late)
    code3 = np.full(300, S.COMMON, np.int8)
    idx3 = {"n": 300, "code": code3, "vis": np.ones(300, bool), "true": np.zeros((300, 7)), "slices": [("P1", 1, 0, 1, 0, 300)]}
    sig5 = np.zeros(300); sig5[1:3] = 0.9; sig5[100:102] = 0.9; sig5[200:203] = 0.9
    fd3 = SW.fa_detail(idx3, sig5, 0.5)
    assert fd3["midworld_runs"] == 3 and fd3["start_at_1"] == 1 and abs(fd3["frac_start_le_early"] - 2 / 3) < 1e-12
    assert abs(fd3["late_runs_per_10k"] - 1 / 300 * 1e4) < 1e-9
    # group P, NF-h24+p: the sweep's 0.20 and 0.50 rows equal the committed R4d rows
    idx_p = R.eval_index(C.GROUPS["P"])
    swp = SW.sweep(idx_p, [P.load_p(run, idx_p) for run in P.PROBES["NF"]], thresholds=(0.2, 0.5))
    SW.pin_r4d(swp)


def test_t8_burnin():
    # the sweep's 300-tick slice: runs at offsets 1, 100 and 200, no grave tick, threshold 0.5
    code3 = np.full(300, S.COMMON, np.int8)
    idx3 = {"n": 300, "code": code3, "vis": np.ones(300, bool), "true": np.zeros((300, 7)), "slices": [("P1", 1, 0, 1, 0, 300)]}
    sig5 = np.zeros(300); sig5[1:3] = 0.9; sig5[100:102] = 0.9; sig5[200:203] = 0.9
    for burnin, runs, at_boundary in ((0, 3, 0), (100, 2, 1), (101, 2, 1), (102, 1, 0)):
        r = BR.burnin_row(idx3, sig5, 0.5, burnin, [])
        assert r["false_alarms"]["runs"] == runs, (burnin, r["false_alarms"])
        assert r["fa_runs_at_boundary"] == at_boundary, (burnin, r["fa_runs_at_boundary"])
        assert abs(r["blind_frac"] - burnin / 300) < 1e-12
        assert r["false_alarms"]["per_10k_ticks"] == runs / 300 * 1e4
    assert BR.mask_burnin(idx3, sig5, 400).max() == BR.MASKED   # a burn-in longer than the slice masks the whole slice
    # the sweep's 20-tick slice (grave 4–8 in sight, 14–16 under fog; 0.2 at the first onset, 0.3 at the second, a 0.1 bump at 10–11)
    code = np.full(20, S.COMMON, np.int8); code[4:9] = S.GRAVE; code[14:17] = S.GRAVE
    vis = np.ones(20, bool); vis[12:] = False
    idx = {"n": 20, "code": code, "vis": vis, "true": np.zeros((20, 7)), "slices": [("P1", 1, 0, 1, 0, 20)]}
    sig = np.zeros(20); sig[4] = 0.2; sig[14] = 0.3; sig[10:12] = 0.1
    eps = P.episodes(idx)
    r0 = BR.burnin_row(idx, sig, 0.1, 0, eps)
    assert r0["midworld_visible"]["detected_frac"] == 1.0 and r0["midworld_onset_in_burnin"]["episodes"] == 0 and r0["midworld_after_burnin"]["episodes"] == 2
    r5 = BR.burnin_row(idx, sig, 0.1, 5, eps)      # onset 4 inside the burn-in, its only over-threshold tick masked → missed
    assert r5["midworld_onset_in_burnin"]["episodes"] == 1 and r5["midworld_onset_in_burnin"]["detected_frac"] == 0.0
    assert r5["midworld_visible"]["detected_frac"] == 0.0 and r5["midworld_after_burnin"]["episodes"] == 1
    assert r5["midworld_fog"]["detected_frac"] == 1.0 and r5["midworld_fog"]["median_latency"] == 0.0   # onset 14 ≥ 5 keeps its latency
    assert r5["false_alarms"]["runs"] == 1 and r5["derived"]["midworld_detected"] == 1 and r5["derived"]["fa_per_100_midworld_detected"] == 100.0
    sig2 = sig.copy(); sig2[6] = 0.5                 # a later tick over: the onset inside the burn-in is caught at latency 2 (B − k + 1)
    r5b = BR.burnin_row(idx, sig2, 0.1, 5, eps)
    assert r5b["midworld_onset_in_burnin"]["detected_frac"] == 1.0 and r5b["midworld_onset_in_burnin"]["median_latency"] == 2.0
    assert BR.burnin_row(idx, sig2, 0.1, 0, eps)["midworld_visible"]["median_latency"] == 0.0
    g = BR.grid(idx, [sig, sig2], burnins=(0, 5), thresholds=(0.1,))
    assert g["episodes_total"] == 2 and g["episodes_midworld"] == 2 and g["rows"]["5"]["0.10"]["midworld_onset_in_burnin"]["detected_frac"]["mean"] == 0.5
    # post-read: onset offsets — the 20-tick slice's two mid-world onsets at 4 and 14, none sharing a slice with a reset episode
    o = g["onsets"]
    assert (o["midworld_n"], o["min"], o["median"], o["max"], o["le_25"], o["le_50"], o["le_100"], o["in_slice_with_reset"]) == (2, 4, 9.0, 14, 2, 2, 2, 0)
    assert (o["slices"], o["slices_grave_in_100"], o["slices_grave_after_100"], o["grave_ticks_after_100"]) == (1, 1, 0, 0)
    # three 300-tick slices: A grave at 0–2 (reset) and again at 10–11 (mid-world, sharing A); B grave at 150–159 only (none in the window,
    # 10 grave ticks after it); C no grave. The signal fires at tick 2 of A and B, nowhere in C.
    code3 = np.full(900, S.COMMON, np.int8); code3[0:3] = S.GRAVE; code3[10:12] = S.GRAVE; code3[450:460] = S.GRAVE
    idx3 = {"n": 900, "code": code3, "vis": np.ones(900, bool), "true": np.zeros((900, 7)),
            "slices": [("P1", 1, 0, 1, 0, 300), ("P1", 1, 0, 2, 300, 600), ("P1", 1, 0, 3, 600, 900)]}
    eps3 = P.episodes(idx3)
    o3 = BR.onset_offsets(idx3, eps3)
    assert (o3["midworld_n"], o3["in_slice_with_reset"], o3["slices"], o3["slices_grave_in_100"], o3["slices_grave_after_100"], o3["grave_ticks_after_100"]) == (2, 1, 3, 1, 1, 10)
    sig3 = np.zeros(900); sig3[2] = 0.9; sig3[302] = 0.9
    sp = BR.startup_split(idx3, sig3, 0.5)
    assert sp["grave_slices"] == 1 and sp["fired_given_grave"] == 1.0
    assert sp["clean_slices"] == 2 and sp["fired_given_clean"] == 0.5
    assert o3["per_set"] == {"P1": {"slices": 3, "ticks": 900, "grave_in_100": 1}}
    # post-read (gate round 1): a boundary run cut from a run that held a grave tick — slice A's signal over the threshold at 0–5
    # with grave at 0–2: at B = 4 the masked run 4–5 begins at the boundary and is the tail of a detection run; the 300-tick
    # case's boundary runs (no grave anywhere) are not
    sig4 = np.zeros(900); sig4[0:6] = 0.9
    r4 = BR.burnin_row(idx3, sig4, 0.5, 4, eps3)
    assert r4["fa_runs_at_boundary"] == 1 and r4["fa_runs_at_boundary_cut_from_grave_run"] == 1
    assert BR.burnin_row(idx3, sig4, 0.5, 6, eps3)["fa_runs_at_boundary"] == 0
    sig6 = np.zeros(900); sig6[100:102] = 0.9             # a run beginning at offset 100 of slice A, no grave tick in it: a boundary run, not a cut one
    r6 = BR.burnin_row(idx3, sig6, 0.5, 100, eps3)
    assert r6["fa_runs_at_boundary"] == 1 and r6["fa_runs_at_boundary_cut_from_grave_run"] == 0
    # group P, NF-h24+p: B = 0 equals the committed sweep rows; at B = 100 the runs equal the sweep's late runs plus the boundary runs
    idx_p = R.eval_index(C.GROUPS["P"])
    gp = BR.grid(idx_p, [P.load_p(run, idx_p) for run in P.PROBES["NF"]], burnins=(0, 100), thresholds=(0.1, 0.2))
    BR.pin_sweep(gp["rows"], idx_p["n"])


def test_t9_history():
    # convergence on a synthetic state: big steps before tick 20, then an exact oscillation of step 2ε; a flat logit and a ramp
    Tn, eps_ = 2000, 0.01
    c, u = np.array([1.0, -2.0]), np.array([0.6, 0.8])
    h = np.tile(c, (Tn, 1)).astype(np.float64)
    h[:20] += np.arange(20)[:, None] * 5.0                                   # steps of 5 before tick 20
    h[20:] += eps_ * ((-1.0) ** np.arange(20, Tn))[:, None] * u              # steps of 2ε from tick 21 on
    z_flat = 0.3 + 0.05 * (-1.0) ** np.arange(Tn)                            # scatter without trend
    z_ramp = 1.0 + 0.001 * np.arange(Tn)
    win = ((1, 10), (10, 30), (30, 100), (100, 500), (500, 2000))
    cv = HR.convergence([(h, z_flat), (h, z_flat)], windows=win, slope_from=30, warm_from=100, profile=(0, 1, 5))
    assert abs(cv["median_step"]["[1, 10)"] - 5.0 * math.sqrt(2)) < 1e-9 and abs(cv["median_step_tail"] - 2 * eps_) < 1e-9
    assert abs(cv["median_step"]["[30, 100)"] - 2 * eps_) < 1e-9
    assert cv["p3"]["band_within_factor"] and cv["p3"]["under_first_window"] and cv["p3"]["ratio_under_1"] and cv["p3"]["met"]
    assert abs(cv["slope_per_1000"]["mean"]) < 1e-3 and cv["drift_to_scatter"] < 0.01 and abs(cv["within_slice_sd"] - 0.05) < 1e-9   # the alternation's slope is ~1e-4 per 1,000
    assert np.allclose(cv["hbar"], c, atol=1e-12) and cv["logit_profile"] == {"0": 0.35, "1": 0.25, "5": 0.25}
    cv2 = HR.convergence([(h, z_ramp)], windows=win, slope_from=30, warm_from=100, profile=(0,))
    assert abs(cv2["slope_per_1000"]["mean"] - 1.0) < 1e-9 and cv2["slope_per_1000"]["sd"] is None
    assert cv2["drift_to_scatter"] > 1 and not cv2["p3"]["ratio_under_1"] and not cv2["p3"]["met"]
    # the splice assembly: recipient cells carry their tick index, donor rows 1000 + tick
    rec = np.tile(np.arange(50, dtype=np.float16)[:, None], (1, 167))
    donor = np.tile((1000 + np.arange(5, dtype=np.float16))[:, None], (1, 58))
    H = 10
    x = HR.splice_inputs(rec, donor, H)
    assert x.shape == (15, 167) and (x[:H] == rec[:H]).all()
    assert (x[H:, :HR.SELF] == rec[H:15, :HR.SELF]).all(), "self block"
    assert (x[H:, HR.SELF:] == donor).all(), "junction: the donor's rows begin at H"
    items = [{"H": H, "en": 5, "vis_hist": np.ones(50, bool), "vis0": True, "grave": True}]
    idx_s, eps_s = HR.splice_index(items)
    assert idx_s["n"] == 15 and eps_s == [(10, 15, 0)] and (idx_s["code"][10:] == S.GRAVE).all() and (idx_s["code"][:10] == S.COMMON).all()
    sig = np.zeros(15); sig[13] = 0.9                                       # crossing at H + 3
    r = P.latency(idx_s, sig, 0.5, eps_s)
    assert r["all"]["detected_frac"] == 1.0 and r["all"]["median_latency"] == 3.0 and r["midworld_visible"]["episodes"] == 1
    assert HR.fired_in_segment(idx_s, sig, 0.5, lambda i: H) == 1.0
    sig2 = np.zeros(15); sig2[9] = 0.9                                      # over at H − 1 only: not a detection, a history false alarm
    r2 = P.latency(idx_s, sig2, 0.5, eps_s)
    assert r2["all"]["detected_frac"] == 0.0 and r2["all"]["anticipated_frac"] == 0.0 and r2["false_alarms"]["runs"] == 1
    assert HR.fired_in_segment(idx_s, sig2, 0.5, lambda i: H) == 0.0
    idx_c, eps_c = HR.splice_index([{**items[0], "grave": False}])
    assert eps_c == [] and (idx_c["code"] == S.COMMON).all()
    # post-read: H = 0 with the recipient's self block — the recipient's self rows 0 … en−1 beside the donor's rows; a reset episode
    x0 = HR.splice_inputs(rec, donor, 0)
    assert x0.shape == (5, 167) and (x0[:, :HR.SELF] == rec[:5, :HR.SELF]).all() and (x0[:, HR.SELF:] == donor).all()
    idx0, eps0 = HR.splice_index([{"H": 0, "en": 5, "vis_hist": np.ones(50, bool), "vis0": False, "grave": True}])
    assert eps0 == [(0, 5, 0)] and P.latency(idx0, np.array([0.0, 0.9, 0, 0, 0]), 0.5, eps0)["reset"]["median_latency"] == 1.0
    # post-read: grave offsets in a set of code columns — friend A grave at 0–2, 100–101 (an onset exactly at the window edge) and 150–151; friend B none
    colA = np.full(400, S.COMMON, np.int8); colA[0:3] = S.GRAVE; colA[100:102] = S.GRAVE; colA[150:152] = S.GRAVE
    go = HR.grave_offsets_from_codes([colA, np.full(400, S.COMMON, np.int8)])
    assert (go["grave_ticks"], go["max_grave_tick_offset"], go["grave_ticks_le_100"], go["grave_ticks_le_300"], go["onsets"], go["max_onset_offset"]) == (7, 151, 4, 7, 3, 150)
    assert go["onsets_after_100"] == 1, "onsets_after_100: an onset exactly at tick 100 is not after it"
    assert HR.grave_offsets_from_codes([np.full(10, S.COMMON, np.int8)])["max_grave_tick_offset"] is None
    # next_seat and the swap assembly on a hand world (obs[:, k, c] = 100 k + c)
    assert HR.next_seat(0, {1}) == 2 and HR.next_seat(4, {0}) == 1 and HR.next_seat(3, {4}) == 0 and HR.next_seat(2, {3}) == 4
    T4 = 4
    obs = (100 * np.arange(5)[None, :, None] + np.arange(399)[None, None, :]).astype(np.float16) * np.ones((T4, 1, 1), np.float16)
    w = {"obs": obs, "needs": np.zeros((T4, 5, 6), np.float32), "hap": np.full((T4, 5), 100.0, np.float32), "codes": np.full((T4, 5), S.COMMON, np.int8), "ticks": T4}
    xs, kp = HR.swap_inputs(w, 0, 1)
    assert kp == 2 and (xs[:, :HR.SELF] == obs[:, 2, :HR.SELF]).all() and (xs[:, HR.SELF:] == obs[:, 0, HR.SELF:HR.SELF + HR.ROW]).all()
    xs4, kp4 = HR.swap_inputs(w, 4, 0)
    assert kp4 == 1 and (xs4[:, :HR.SELF] == obs[:, 1, :HR.SELF]).all() and (xs4[:, HR.SELF:] == HR.pair_x(w, 4, 0)[:, HR.SELF:]).all()
    # subindex rebases positions
    idx3 = {"n": 9, "code": np.arange(9, dtype=np.int8), "vis": np.ones(9, bool), "true": np.zeros((9, 7)),
            "slices": [("P1", 1, 0, 1, 0, 3), ("P1", 1, 0, 2, 3, 6), ("P1", 1, 0, 3, 6, 9)]}
    sub = HR.subindex(idx3, {("P1", 1, 0, 1), ("P1", 1, 0, 3)})
    assert sub["n"] == 6 and sub["slices"] == [("P1", 1, 0, 1, 0, 3), ("P1", 1, 0, 3, 3, 6)] and sub["code"].tolist() == [0, 1, 2, 6, 7, 8]
    # real pins
    idx_p = R.eval_index(C.GROUPS["P"])
    model, probe = HR.load_probe(1)
    assert HR.check_reproduces(model, probe, 1, idx_p) < HR.PRED_TOL
    ps = [P.load_p(run, idx_p) for run in P.PROBES["NF"]]
    HR.pin_h0([HR.h0_rows(idx_p, p_) for p_ in ps])
    HR.pin_h0_sd([HR.h0_rows(idx_p, C.grave_probability(C.load_field(run, idx_p, "grave"))) for run in P.SD_RUNS])
    HR.small_burnin(idx_p, ps, "P")
    keep = HR.grave_start_slices(idx_p)
    assert len(keep) == 200
    sub_p = HR.subindex(idx_p, keep)
    sub_sig = P.load_p(P.PROBES["NF"][0], sub_p)
    rows = P.latency(sub_p, sub_sig, 0.1, P.episodes(sub_p))
    ref = json.loads((HERE / "phase1d-sweep.json").read_text())["by_set"]["P"]["heads"]["NF-h24+p"]["rows"]["0.10"]["per_seed"][0]["reset"]
    assert json.loads(json.dumps(rows["reset"], default=float)) == ref



def test_t10_knee():
    """DECLARATION §Addendum 5: knee_of returns the first H AT OR UNDER the midpoint of the endpoints; score_p9 as
    declared ((i) H = 10 under 0.70; (ii) H = 20 within one committed seed SD of H = 100, inclusive)."""
    k = KR.knee_of({1: 0.90, 2: 0.80, 5: 0.64, 10: 0.30}, top=1.00, plateau=0.28)
    assert abs(k["midpoint"] - 0.64) < 1e-12
    assert k["H"] == 5 and k["detected"] == 0.64, "knee: the first H at or under the midpoint"
    assert KR.knee_of({1: 0.9, 2: 0.8}, 1.0, 0.28)["H"] is None
    def row(mean, sd=0.0):
        return {"0.10": {"all": {"detected_frac": {"mean": mean, "sd": sd}}}}
    committed = {"100": row(0.358, 0.175)}
    p = KR.score_p9({"10": row(0.65), "20": row(0.358 + 0.175)}, committed)
    assert p["i_ok"] and p["ii_ok"] and p["met"], p
    p = KR.score_p9({"10": row(0.70), "20": row(0.358 + 0.175 + 1e-6)}, committed)
    assert not p["i_ok"] and not p["ii_ok"] and not p["met"], p
    assert KR.KNEE_H == (1, 2, 5, 10, 20, 50) and KR.PIN_H == 100

if __name__ == "__main__":
    only = sys.argv[1:]
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and (not only or k in only)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
