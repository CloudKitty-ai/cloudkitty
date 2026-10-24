#!/usr/bin/env python3
"""Guards for Phase 1c's head and reader (Phase 1 arc venv; this arc's
split and symlinked raws). DECLARATION.md §Instrument names each with
its predicted red.

t1  shift operators: half-bin up-shift splits a delta 0.5 / 0.5; a 2-bin
    down-shift from bin 1 lands wholly in bin 0; the top bin holds under
    an up-shift; mass is conserved
t2  two-hot targets: sum 1; mean equals the value inside the centre
    range; the ends put every unit in the end bin
t3  the residual switch: residual off → the belief is a distribution and
    independent of the correction weights; on → it depends on them
t4  prediction consistency: the prediction file's need columns are the
    histogram means and the grave mass is the belief's mass over bins
    18–19, on a 600-tick slice of one world
t5  reader arithmetic: 1 − ∏(1 − m); reliability-bin counts sum to n;
    AUROC on hand rankings
t6  provenance: split.json equals Phase 1b's; the comparator cells
    re-read here equal 1b's gated read at width 24
t7  widths and the cap (§Addendum): configure builds 3,279 / 6,679 /
    15,783 params at widths 8 / 16 / 32 with the declared run names;
    32 is refused without --over-cap and marked over_cap with it
"""
import copy
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
PHASE1B = HERE.parent / "minifriend-phase1b-2026-10-23"
os.environ["MINIFRIEND_ARC"] = str(HERE)
sys.path.insert(0, str(HERE))
import sd_head as M  # noqa: E402

D = M.D
torch.manual_seed(0)


def delta(k):
    b = torch.zeros(M.K)
    b[k] = 1.0
    return b


def test_t1_shift_operators():
    up_half = M.shift_matrix(torch.tensor(0.5), "up")
    r = delta(3) @ up_half
    assert torch.allclose(r[3], torch.tensor(0.5)) and torch.allclose(r[4], torch.tensor(0.5)), r
    assert torch.allclose(r.sum(), torch.tensor(1.0))
    down_two = M.shift_matrix(torch.tensor(2.0), "down")
    r = delta(1) @ down_two
    assert torch.allclose(r[0], torch.tensor(1.0)), r
    for s in (0.3, 1.0, 7.0):
        r = delta(M.K - 1) @ M.shift_matrix(torch.tensor(s), "up")
        assert torch.allclose(r[M.K - 1], torch.tensor(1.0)), (s, r)
    h = torch.softmax(torch.randn(4, 5, M.K), -1)                       # batched (friend, need) shifts
    up = M.shift_matrix(torch.rand(4, 5) * 3, "up")
    r = torch.einsum("bnk,bnkj->bnj", h, up)
    assert torch.allclose(r.sum(-1), torch.ones(4, 5), atol=1e-6) and (r >= 0).all()


def test_t2_two_hot_targets():
    y = torch.tensor([0.125, 0.1, 0.0, 1.0, 0.5, 0.987])
    t = M.two_hot(y)
    assert torch.allclose(t.sum(-1), torch.ones(6), atol=1e-6)
    assert torch.allclose(t[0], delta(2))                                  # 12.5 points = centre of bin 2
    assert torch.allclose(t[1, 1:3], torch.tensor([0.5, 0.5])) and t[1].sum() == 1
    assert torch.allclose(t[2], delta(0)) and torch.allclose(t[3], delta(M.K - 1))
    means = (t * M.CENTRES).sum(-1)
    assert torch.allclose(means[[0, 1, 4]], y[[0, 1, 4]], atol=1e-6), means  # exact inside [centre_0, centre_19]
    assert (t[5, M.K - 1] > 0.5) and (t[5].argmax() == M.K - 1)


def _model_pair():
    m = M.SDHead()
    m2 = copy.deepcopy(m)
    with torch.no_grad():
        m2.corr.weight.normal_(); m2.corr.bias.normal_()
    return m.eval(), m2.eval()


def test_t3_residual_switch():
    m, m2 = _model_pair()
    x = torch.randn(40, 6, D.X_DIM)
    f = torch.tensor([0, 1, 2, 3, 4, 2])
    with torch.no_grad():
        a, _ = m(x, f, residual=False)
        b, _ = m2(x, f, residual=False)
        c, _ = m(x, f, residual=True)
        d, _ = m2(x, f, residual=True)
    for o in (a, b, c, d):
        assert torch.allclose(o["belief"].sum(-1), torch.ones(40, 6, 5), atol=1e-5) and (o["belief"] >= 0).all()
    assert torch.allclose(a["belief"], b["belief"], atol=1e-6), "residual off must not read the correction weights"
    assert torch.allclose(a["p_rel"], b["p_rel"])
    assert not torch.allclose(c["belief"], d["belief"], atol=1e-3), "residual on must read them"
    assert not torch.allclose(a["belief"], c["belief"], atol=1e-3)


def test_t4_prediction_consistency():
    w = D.load_world("L", 905001)
    Tn = 600
    w = {**w, "ticks": Tn, "obs": w["obs"][:Tn], "needs": w["needs"][:Tn], "hap": w["hap"][:Tn], "codes": w["codes"][:Tn]}
    m = M.SDHead().eval()
    with torch.no_grad():
        m.corr.weight.normal_(); m.rate_raw.normal_()
    pred, grave, prel = M.predict_world(m, w)
    assert pred.shape == (Tn, 5, 5, 7) and grave.shape == (Tn, 5, 5, 5)
    k, j = 2, 4
    x, _y, _v, _c = D.pair_arrays(w, k, j)
    with torch.no_grad():
        out, _ = m(torch.from_numpy(x).float()[:, None], torch.tensor([j]))
    mean = out["mean"][:, 0].numpy()
    gm = out["belief"][:, 0, :, M.GRAVE_BIN:].sum(-1).numpy()
    assert np.allclose(pred[:, k, j, :5], mean, atol=1e-5), np.abs(pred[:, k, j, :5] - mean).max()
    assert np.allclose(grave[:, k, j], gm, atol=1e-5)
    assert np.allclose(prel[:, k, j], out["p_rel"][:, 0].numpy(), atol=1e-5)
    assert np.isnan(pred[:, 0, 0]).all() and not np.isnan(pred[:, 0, 1]).any()
    assert (pred[:, k, j, :5] >= 0).all() and (pred[:, k, j, :5] <= 1).all()


def test_t5_reader_arithmetic():
    import read_phase1c as C
    assert abs(C.grave_probability([[0.5, 0.5, 0.0, 0.0, 0.0]])[0] - 0.75) < 1e-12
    assert C.grave_probability([[1.0, 0.0, 0.0, 0.0, 0.0]])[0] == 1.0 and C.grave_probability([[0.0] * 5])[0] == 0.0
    p = np.array([0.0, 0.05, 0.15, 0.95, 0.999, 0.5, 0.5]); g = np.array([0, 0, 0, 1, 1, 1, 0], float)
    rows = C.reliability(p, g)
    assert sum(r["n"] for r in rows) == 7 and rows[0]["n"] == 2 and rows[-1]["n"] == 2 and rows[5]["n"] == 2
    assert rows[5]["frac_grave"] == 0.5 and rows[-1]["frac_grave"] == 1.0 and rows[1]["mean_p"] == 0.15
    assert C.auroc([0.1, 0.2, 0.3, 0.4], [0, 0, 1, 1]) == 1.0
    assert C.auroc([0.1, 0.2, 0.3, 0.4], [1, 1, 0, 0]) == 0.0
    assert C.auroc([0.3, 0.3, 0.3, 0.3], [1, 0, 1, 0]) == 0.5
    assert abs(C.auroc([1.0, 1.0, 0.0], [1, 0, 0]) - 0.75) < 1e-12          # ties take the average rank
    assert C.auroc([0.1, 0.2], [1, 1]) is None
    rng = np.random.default_rng(1)
    s = rng.integers(0, 4, 2000) / 4.0; lab = rng.random(2000) < 0.3        # heavy ties against a brute-force count
    pos, neg = s[lab], s[~lab]
    brute = (np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg))
    assert abs(C.auroc(s, lab) - brute) < 1e-12


def test_t6_provenance():
    import read_phase1c as C
    assert (HERE / "split.json").read_bytes() == (PHASE1B / "split.json").read_bytes()
    base = C.R.read(C.RUNS_CMP, C.GROUPS["P"])
    prov = C.provenance({"heads": base["heads"]})
    assert prov["width"] == 24 and base["eval_sets"] == ["P1", "P2", "P3", "P4", "P5"]


def test_t7_widths_and_cap():
    import argparse
    import read_phase1c as C

    def ns(h, over=False, seed=1):
        return argparse.Namespace(seed=seed, hidden=h, over_cap=over, smoke=False)
    assert tuple(M.WIDTHS) == (8, 16, 32) and C.DECLARED == 16
    name, m, cfg = M.configure(ns(8))
    assert name == "SD-h8-s1" and cfg["params"] == 3279 == M.T.n_params(m) and not cfg["over_cap"] and cfg["hidden"] == 8, cfg
    name, m, cfg = M.configure(ns(16))
    assert name == "SD-s1" and cfg["params"] == 6679 and not cfg["over_cap"] and cfg["param_cap"] == 8445, cfg
    try:
        M.configure(ns(32))
        refused = False
    except SystemExit:
        refused = True
    assert refused, "width 32 must be refused without --over-cap"
    name, m, cfg = M.configure(ns(32, over=True, seed=3))
    assert name == "SD-h32-s3" and cfg["params"] == 15783 and cfg["over_cap"], cfg
    assert M.run_name(8, 2, smoke=True) == "SD-h8-s2-smoke"
    assert [r for _h, r in C.RUNS_SD[16]] == ["SD-s1", "SD-s2", "SD-s3"] and C.RUNS_SD[32][0][1] == "SD-h32-s1"


def test_t8_md_every_width():
    """The markdown prints every width × group block from the committed read (the first read died on a shadowed loop variable)."""
    import read_phase1c as C
    out = json.loads((HERE / "phase1c-read.json").read_text())
    text = C.md(out)
    for w in out["widths"]:
        for g in out["groups"]:
            assert f"### Width {w} ({C.ROLE[w]}), group {g} (" in text, (w, g)
    assert text.count("#### R2c visible") == len(out["widths"]) * len(out["groups"])
    assert "### R9c" in text and all(f"### R5c width {w}" in text for w in out["widths"])
    for w in out["widths"]:                                   # R4c reliability counts are PER SEED (the first read printed seed 1's only)
        for v in ("visible", "all"):
            rows = out["reads"][str(w)]["P"]["R4c_calibration"][v]["reliability_seed_mean"]
            assert all(isinstance(r["n"], list) and len(r["n"]) == len(out["seeds"]) for r in rows), (w, v)
            per_seed_totals = [sum(r["n"][s] for r in rows) for s in range(len(out["seeds"]))]
            assert len(set(per_seed_totals)) == 1, (w, v, per_seed_totals)   # every seed scores the same samples
    assert "| p bin | n per seed |" in text
    rel = lambda ns, fr: [{"lo": 0.0, "hi": 0.5, "n": ns[0], "mean_p": 0.2, "frac_grave": fr[0]}, {"lo": 0.5, "hi": 1.0, "n": ns[1], "mean_p": 0.8, "frac_grave": fr[1]}]
    cal = [{"brier": 0.1, "mean_p_on_GRAVE": 0.5, "mean_p_on_COMMON": 0.0, "n_grave_happiness_only": 1, "n_grave": 4, "reliability": rel([7, 3], [0.1, 0.9])},
           {"brier": 0.3, "mean_p_on_GRAVE": 0.7, "mean_p_on_COMMON": 0.0, "n_grave_happiness_only": 1, "n_grave": 4, "reliability": rel([10, 0], [0.3, None])}]
    blk = C.calibration_block(cal)
    assert blk["reliability_seed_mean"][0]["n"] == [7, 10] and blk["reliability_seed_mean"][1]["n"] == [3, 0], blk["reliability_seed_mean"]
    assert abs(blk["reliability_seed_mean"][1]["frac_grave"]["mean"] - 0.9) < 1e-12 and blk["reliability_seed_mean"][1]["frac_grave"]["seeds"] == 1
    assert abs(blk["brier"]["mean"] - 0.2) < 1e-12


if __name__ == "__main__":
    only = sys.argv[1:]
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and (not only or k in only)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
