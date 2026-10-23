#!/usr/bin/env python3
"""Guards for train_heads.py / phase1_data.py (arc venv, raws present).

h1  the head is under the cap: 7,807 parameters ≤ 8,445, counted
h2  DR weights come from the TRAIN worlds only: train_weights(train)
    equals a hand computation over those worlds' codes, and differs
    from the same computation over train + evaluation worlds
h3  roles: evaluation worlds are split.json's, untouched by train and
    validation; validation is carved from split.json's train worlds
h4  sample_loss is the w-weighted mean: with w one-hot it returns that
    sample's own (mse5 + hap + 0.1 · bath); bath enters at BATH_WEIGHT
    0.1 (prereg: excluded/downweighted from the estimate loss)
h5  pair_arrays: x is the self block then the friend's row, y the
    friend's aligned truth /100 (own self needs equal y for the pair
    (k, k) built by hand), vis the row's present cell
h6  --hidden (Phase 1b): widths 12 / 24 / 48 count 3,043 / 7,807 /
    22,519 parameters; check_cap refuses 22,519 without --over-cap and
    marks it over-cap with it; the default width is still 24
"""
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phase1_data as D  # noqa: E402
import train_heads as T  # noqa: E402


def test_h1_param_count_under_cap():
    n = T.n_params(T.BeliefHead())
    assert n == 7807 and n <= T.PARAM_CAP, n


def test_h2_dr_weights_from_train_worlds_only():
    roles = D.roles()
    train = [("L", roles["L"]["train"][0]), ("G", roles["G"]["train"][0])]
    ev = [("G", roles["G"]["eval"][0])]
    w, f = T.train_weights(train)
    codes = np.concatenate([D.load_world(n, s)["codes"].ravel() for n, s in train])
    freq = np.array([(codes == i).mean() for i in range(3)])
    assert np.allclose(f, freq), (f, freq)
    inv = np.minimum(1 / freq, 50 / freq[2])
    inv = inv / inv[codes].mean()
    assert np.allclose(w, inv), (w, inv)
    w_all, _ = T.train_weights(train + ev)
    assert not np.allclose(w, w_all), "fixture cannot tell train-only from train+eval"


def test_h3_roles_keep_eval_worlds_out():
    roles = D.roles()
    for name, r in roles.items():
        s = D.SPLIT["sets"][name]
        assert r["eval"] == sorted(s["eval"]), name
        assert set(r["val"]) <= set(s["train"]) and set(r["train"]) <= set(s["train"]), name
        assert not (set(r["train"]) & set(r["val"])) and sorted(r["train"] + r["val"]) == sorted(s["train"]), name
        assert len(r["val"]) == round(0.2 * len(s["train"])), name


def test_h4_sample_loss_is_the_weighted_mean():
    pred = torch.zeros(1, 2, 7)
    y = torch.zeros(1, 2, 7)
    y[0, 0, :5] = 0.2          # sample 0: mse5 = 0.04, hap 0, bath 0
    y[0, 1, 5] = 0.5           # sample 1: hap = 0.25
    w = torch.tensor([[1.0, 0.0]])
    loss, terms = T.sample_loss(pred, y, w)
    assert abs(loss.item() - 0.04) < 1e-6 and abs(terms[0].item() - 0.04) < 1e-6 and terms[1].item() == 0
    loss2, _ = T.sample_loss(pred, y, torch.tensor([[0.0, 1.0]]))
    assert abs(loss2.item() - 0.25) < 1e-6
    loss3, _ = T.sample_loss(pred, y, torch.tensor([[1.0, 1.0]]))
    assert abs(loss3.item() - 0.145) < 1e-6
    # bath is downweighted: a bath error of 0.5 (mse 0.25) adds 0.1 x 0.25 to the loss, the term itself unscaled
    y2 = torch.zeros(1, 1, 7)
    y2[0, 0, 6] = 0.5
    loss4, terms4 = T.sample_loss(torch.zeros(1, 1, 7), y2, torch.ones(1, 1))
    assert T.BATH_WEIGHT == 0.1 and abs(loss4.item() - 0.025) < 1e-6 and abs(terms4[2].item() - 0.25) < 1e-6


def test_h5_pair_arrays_layout():
    roles = D.roles()
    w = D.load_world("G", roles["G"]["train"][0])
    k, j = 1, 3
    x, y, vis, code = D.pair_arrays(w, k, j)
    assert x.shape == (w["ticks"], 167) and y.shape == (w["ticks"], 7) and x.dtype == np.float16
    assert np.array_equal(x[:, :109], w["obs"][:, k, :109])
    off = 109 + 58 * [i for i in range(5) if i != k].index(j)
    assert np.array_equal(x[:, 109:], w["obs"][:, k, off:off + 58])
    assert np.array_equal(vis, w["obs"][:, k, off].astype(np.float32) > 0.5) and 0 < vis.mean() < 1
    assert np.allclose(y[:, :5] * 100, w["needs"][:, j, :5]) and np.allclose(y[:, 6] * 100, w["needs"][:, j, 5])
    assert np.allclose(y[:, 5] * 100, w["hap"][:, j])
    assert np.array_equal(code, w["codes"][:, j]) and (code == 0).any()
    # the observer's own needs in x are its OWN truth (the alignment), not the friend's
    own = x[:, :5].astype(np.float32) * 100
    assert np.abs(own - w["needs"][:, k, :5]).max() < 0.06
    assert np.abs(own - w["needs"][:, j, :5]).max() > 1.0


def test_h6_hidden_widths_and_the_cap_rule():
    assert T.H == 24 and T.n_params(T.BeliefHead()) == T.n_params(T.BeliefHead(h=24))
    counts = {h: T.n_params(T.BeliefHead(h=h)) for h in (12, 24, 48)}
    assert counts == {12: 3043, 24: 7807, 48: 22519}, counts
    assert T.check_cap(counts[12]) is False and T.check_cap(counts[24]) is False
    try:
        T.check_cap(counts[48])
    except SystemExit:
        pass
    else:
        raise AssertionError("over-cap head accepted without --over-cap")
    assert T.check_cap(counts[48], over_cap=True) is True


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
