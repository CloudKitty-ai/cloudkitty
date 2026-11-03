#!/usr/bin/env python3
"""Guards a1-a7 of DECLARATION.md §7 for the act predictor's instrument; each red on record via scripts/mutate.sh
--expect before any training. Run under the needy arc's venv:

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_act.py [a1 ... a7]
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_act as D  # noqa: E402
import train_act as TA  # noqa: E402
import read_act as RA  # noqa: E402


def a1():
    """the label: y0[t] = applied[t], y10[t] = applied[t + 10], the last 10 ticks masked, the observer never its own friend."""
    tr, _va, _ev = D.role_lists()
    name, seed = next(ws for ws in tr if ws[0] == "TN1")
    w = D.load_world(name, seed)
    T = w["ticks"]
    for j in range(D.ROSTER):
        y = D.targets(w["applied"], j)
        assert y.shape == (T, 2)
        assert np.array_equal(y[:, 0], w["applied"][:, j]), "y0 is applied[t]"
        assert np.array_equal(y[:T - 10, 1], w["applied"][10:, j]), "y10 is applied[t + 10]"
        assert (y[T - 10:, 1] == -1).all() and (y[:T - 10, 1] >= 0).all(), "exactly the last 10 ticks are masked for y10"
    ps = list(D.pairs(w))
    assert len(ps) == 16 and all(k != j for k, j in ps) and all(k in w["observers"] for k, _j in ps), "16 pairs, observer never its own friend, scripted never an observer"
    seqs = D.build([(name, seed)])
    assert len(seqs) == 16 and seqs[0]["x"].shape == (T, 167) and seqs[0]["y"].dtype == np.int64
    cf = D.class_freq(seqs)
    assert cf.sum() == 16 * T and cf[D.ACT_NAMES.index("purr")] == 0 and cf[D.ACT_NAMES.index("meow")] == 0, cf.tolist()


def a2():
    """arm A's state: the frozen part reproduces probe_1e.states_world to 0.0 on a 1b evaluation world, every seed, and does not move under a step."""
    import torch
    sys.path.insert(0, str(D.P1E))
    import probe_1e as GP
    r = D.roles()
    name, seed = "P1", r["P1"]["eval"][0]
    w = D.load_world(name, seed)
    for s in (1, 2, 3):
        model = TA.make_model("A", s)
        pairs, z_ref = GP.states_world(model.belief, w)
        x = torch.from_numpy(np.stack([D.pair_x(w, k, j) for k, j in pairs], 1))
        with torch.no_grad():
            z, _h = model.belief.gru(torch.relu(model.belief.proj(x[:500].float())), None)
        assert float((z - z_ref[:500]).abs().max()) == 0.0, "the belief state must equal probe_1e.states_world's"
        assert all(not p.requires_grad for p in model.belief.parameters()), "the belief head carries no gradient"
    model = TA.make_model("A", 1)
    before = {k: v.clone() for k, v in model.belief.state_dict().items()}
    seqs = D.build([("P1", seed)])[:4]
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=1e-2)
    model.train()
    TA.run_epoch(model, seqs, opt, np.random.default_rng(0), 4, smoke=True)
    after = model.belief.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before), "the belief state must not change"
    assert not model.belief.training, "the frozen part stays in eval under model.train()"


def a3():
    """the budgets: trained parameter counts equal the §4 table; B10 / B20 / B30 under 10 / 20 / 30%; widths 40 / 51 would overshoot."""
    counts = {arm: TA.n_trained(TA.make_model(arm, 1)) for arm in TA.ARMS}
    assert counts == TA.DECLARED_PARAMS, counts
    for arm in ("B10", "B20", "B30"):
        TA.check_budget(arm, counts[arm])
    assert counts["B10"] <= 8445, "B10 is under the needs head's cap"
    assert TA.n_trained(TA.ActHead(40)) > 0.20 * TA.TRUNK_PARAMS, "width 40 would exceed 20%"
    assert TA.n_trained(TA.ActHead(51)) > 0.30 * TA.TRUNK_PARAMS, "width 51 would exceed 30%"
    assert TA.n_trained(TA.ActHead(39)) <= 0.20 * TA.TRUNK_PARAMS, "B20 exceeds 20% of the trunk"
    assert TA.n_trained(TA.ActHead(50)) <= 0.30 * TA.TRUNK_PARAMS, "B30 exceeds 30% of the trunk"


def a4():
    """the reader: textbook metrics on a hand array; row state from the present cell and the message block; the scripted seat excluded from covered cells."""
    y = np.array([0, 0, 1, 1, 7, 7, 7, 10])
    pred = np.array([0, 1, 1, 1, 7, 7, 0, 10])
    p = np.full((8, D.N_ACTS), 0.01)
    p[np.arange(8), pred] = 0.9
    r = RA.metrics_hand(y, pred, p, live=[0, 1, 7, 10])
    assert abs(r["top1"] - 6 / 8) < 1e-12, r["top1"]
    assert abs(r["macro_recall"] - np.mean([0.5, 1.0, 2 / 3, 1.0])) < 1e-12, r["macro_recall"]
    assert abs(r["logloss"] - (-(6 * np.log(0.9) + 2 * np.log(0.01)) / 8)) < 1e-9, r["logloss"]
    x = np.zeros((4, 167), np.float16)
    x[0, D.SELF_BLOCK + D.ROW_PRESENT] = 1                       # seen
    x[1, D.SELF_BLOCK + D.ROW_MSG0 + 3] = 0.4                     # heard: a message cell live, present 0
    x[2, D.SELF_BLOCK + D.ROW_MSG1 - 1] = 1                       # heard: an answers-me bit
    st = D.row_state(x)
    assert st.tolist() == [D.SEEN, D.HEARD, D.HEARD, D.SILENT], f"row states {st.tolist()}: a heard row classed silent"
    _rise, R, _L = RA.mods()
    arm, k, seed, _t, path = next(w for w in RA.needy_worlds("tuning") if w[0] == "N")
    w, observers, scripted = RA.load_needy(path, arm, k, seed, "tuning")
    pairs, X, ys, states, cls = RA.world_inputs(w, observers, scripted)
    assert len(pairs) == 16 and scripted not in observers
    assert all((c == "scripted") == (j == scripted) for (k_, j), c in zip(pairs, cls)), "the scripted seat's rows are classed scripted, never covered"
    assert sum(c == "covered" for c in cls) == 12 and X.shape == (w["ticks"], 16, 167)


def a5():
    """baseline V: the activity one-hot -> act map equals seating_read.APPLIED_ACTIVITY inverted; other activities -> the mode."""
    sys.path.insert(0, str(D.EXPTS / "seating-analysis-2026-09-28"))
    import seating_read as SR
    inv = {v: SR.APPLIED_NAMES.index(k) for k, v in SR.APPLIED_ACTIVITY.items()}
    assert D.ACTIVITY_TO_ACT == inv and D.ACT_NAMES == SR.APPLIED_NAMES, "V's map differs from APPLIED_ACTIVITY"
    x = np.zeros((9, 167), np.float16)
    x[:8, D.SELF_BLOCK + D.ROW_PRESENT] = 1
    for i in range(7):
        x[i, D.SELF_BLOCK + D.ROW_ACT0 + i] = 1                   # activities 0..6 in sight
    x[7, D.SELF_BLOCK + D.ROW_ACT0 + 5] = 1                       # play in sight (duplicate check)
    x[8, D.SELF_BLOCK + D.ROW_ACT0 + 5] = 1                       # play but NOT in sight -> mode
    mode = D.ACT_NAMES.index("play")
    v = D.baseline_V(x, mode)
    want = [mode] + [inv[i] for i in range(1, 7)] + [inv[5], mode]
    assert v.tolist() == want, (v.tolist(), want)
    a = np.array([3, 4, 4, 0])
    assert D.baseline_R(a, 7).tolist() == [7, 3, 4, 4], "R repeats the previous applied act"


def a6():
    """the halves: accuracy / ladder on tuning seeds, confirming on confirming seeds; the loader refuses the other half."""
    _rise, R, _L = RA.mods()
    tun, con = RA.needy_worlds("tuning"), RA.needy_worlds("confirming")
    assert len(tun) == 180 and len(con) == 180
    assert all(R.half_of(a, k, s) == "tuning" for a, k, s, _t, _p in tun) and all(R.half_of(a, k, s) == "confirming" for a, k, s, _t, _p in con)
    a, k, s, _t, p = tun[0]
    try:
        RA.load_needy(p, a, k, s, "confirming")
    except PermissionError:
        pass
    else:
        raise AssertionError("a tuning seed loaded under the confirming half")
    a, k, s, _t, p = con[0]
    try:
        RA.load_needy(p, a, k, s, "tuning")
    except PermissionError:
        pass
    else:
        raise AssertionError("a confirming seed loaded under the tuning half")
    lw = RA.lived_worlds()
    assert len(lw) == 69 and sum(g == "lived-P" for g, _n, _s in lw) == 50 and sum(g == "lived-LWG" for g, _n, _s in lw) == 19, len(lw)


def a7():
    """the trainer: a two-epoch smoke (A and B10) writes its files, ends under the uniform predictor's loss, and its forward gives rows summing to 1."""
    import torch
    A = D.EXPTS / "needy-set-2026-10-28"
    for arm in ("B10", "A"):
        r = subprocess.run([sys.executable, "-B", str(HERE / "train_act.py"), "--arm", arm, "--seed", "1", "--smoke", "--threads", "2"],
                           capture_output=True, text=True, cwd=str(HERE))
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        out = TA.OUT_ROOT / TA.run_name(arm, 1, smoke=True)
        for f in ("run-manifest.json", "metrics.jsonl", "head-best.pt", "done.json"):
            assert (out / f).exists(), f"{arm} smoke wrote no {f}"
        done = json.loads((out / "done.json").read_text())
        assert done["best_val"] < 2 * np.log(D.N_ACTS), f"{arm} smoke val loss {done['best_val']} not under the uniform predictor's"
        model, man = TA.load_act(arm, 1, smoke=True)
        assert man["smoke"] is True and man["trained_params"] == TA.DECLARED_PARAMS[arm]
        name, seed = "P1", D.roles()["P1"]["eval"][0]
        w = D.load_world(name, seed)
        p, pairs = TA.probs_world(model, w)
        assert p.shape == (w["ticks"], 20, 2, D.N_ACTS) and np.isfinite(p).all()
        assert np.abs(p.sum(-1) - 1).max() < 1e-5, "rows must sum to 1"


GUARDS = {f.__name__: f for f in (a1, a2, a3, a4, a5, a6, a7)}


def main():
    import torch
    torch.set_num_threads(2)
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
