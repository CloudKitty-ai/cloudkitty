#!/usr/bin/env python3
"""Guards g0–g10 of DECLARATION.md §9; each red on record via scripts/mutate.sh --expect before any seed trains.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_phase2.py [g0a g0b ...]

g0a / g0b / g0c read the trunk's recorded probe dumps and one recorded battery row; g0c re-runs one 20k-tick trunk leg
(trunk minds only; ~2 min). Nothing here writes outside the scratch directory.
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402

SCRATCH = Path(os.environ.get("P2_SCRATCH", "/tmp/p2-scratch"))


def _probe_rows(seed=40_001):
    z = np.load(C.last_probe_dump("trunk-s1"))
    return C.dump_rows(z, seed)


def g0a():
    """the binding reproduces the trunk's probe world: replaying trunk-s1's last dumped probe (seed 40,001) by its recorded
    actions gives the dumped observation and mask streams exactly, every tick, every seat."""
    rows = _probe_rows()
    O, M = C.replay_dump(rows, 40_001)
    assert O.shape == rows["obs"].shape, (O.shape, rows["obs"].shape)
    bad = np.flatnonzero(~np.all(O == rows["obs"], axis=(1, 2)))
    assert bad.size == 0, f"replay diverges from the dump at tick {bad[0]} (first of {bad.size})"
    assert np.array_equal(M, rows["mask"]), "masks differ"


def g0b():
    """068 restore-vs-replay equality (DECLARATION §12 call 6b): on three recorded probe worlds, snapshot() mid-way and
    restore() reproduces the replay's own tail exactly; so does fork(). Before any 068 read is cited."""
    z = np.load(C.last_probe_dump("trunk-s1"))
    for seed in C.PROBE_SEEDS:
        rows = C.dump_rows(z, seed)
        for mode in ("restore", "fork"):
            O, _M, OB = C.replay_dump(rows, seed, snapshot_at=999, mode=mode)
            assert np.array_equal(O, rows["obs"]), (seed, "the straight replay diverged")
            bad = np.flatnonzero(~np.all(OB == O[1000:], axis=(1, 2)))
            assert bad.size == 0, f"{mode} tail diverges from the replay at tick {1000 + bad[0]} (seed {seed})"


def g0c():
    """the binding reproduces a recorded battery leg: g2-s1 uniform on world 905001 at 20x20 (cert battery results-raw)
    re-run by the harness's run_one on this binding gives the recorded row's team happiness, nash, distress columns."""
    import cert_harness_fog as H
    rec = C.battery_rows("g2-s1", 20)[905_001]
    row = H.run_one(("g2-s1", 905_001, 20_000, str(C.TRUNK_TOML), None, None, "served", None, None, 1_000))
    for k in ("mean_happiness", "max_distress_age", "max_distress_age_seat", "dist_ticks", "low_share", "floor_touches", "ticks"):
        assert row[k] == rec[k], (k, row[k], rec[k])
    assert abs(row["nash"] - rec["nash"]) < 1e-12, (row["nash"], rec["nash"])


def g1():
    """the graft is the identity: on real probe rows with ARBITRARY appended cells, the widened policy's logits equal
    the trunk's on the un-widened rows BIT-FOR-BIT; parameters 84,450 + 64·C; every trunk weight byte-equal; the
    kitty embedding's new columns zero."""
    import torch
    import graft as G
    import heads_online as HO
    rows = _probe_rows()
    obs = torch.from_numpy(rows["obs"][::20].reshape(-1, C.OBS_DIM))          # 500 real rows
    g = torch.Generator().manual_seed(1)
    for k in C.TRUNK_SEEDS:
        for arm, spec in HO.ARMS.items():
            c = spec["cells"]
            p2, trunk, _ck = G.graft(k, c)
            assert G.n_params(p2) == C.TRUNK_PARAMS + 64 * c, f"params {G.n_params(p2)} != {C.TRUNK_PARAMS + 64 * c}"
            ts, ps = trunk.state_dict(), p2.state_dict()
            assert set(ps) == set(ts) | {"embed_cells.weight"}, set(ps) ^ set(ts)
            for name in ts:
                assert torch.equal(ps[name], ts[name]), f"{name} not byte-equal"
            assert ps["embed_cells.weight"].shape == (64, c) and not ps["embed_cells.weight"].any(), "new columns not zero"
            cells = torch.randn(obs.shape[0], C.N_ROWS * c, generator=g) * 3
            with torch.no_grad():
                a, b = trunk(obs), p2(torch.cat([obs, cells], 1))
            assert torch.equal(a, b), f"logits differ from the trunk's by {float((a - b).abs().max())} (trunk-s{k}, {arm})"


def _tuning_world():
    """The first needy TUNING world (DECLARATION §5: the tuning half serves guard g2 only): (w, observers, z)."""
    import read_act as R
    arm, k, seed, _t, path = list(R.needy_worlds("tuning"))[0]
    w, observers, _scr = R.load_needy(path, arm, k, seed, "tuning")
    return w, observers, np.load(path)


def g2():
    """online head inference reproduces offline: on a recorded needy tuning world the OnlineHeads' per-tick y0
    probabilities equal train_act.probs_from_x's (state from zero at the world's start) to 1e-6 on every live row;
    the frequency prior replaces the eleven probabilities and summaries exactly on SILENT rows; ticks-since-live is
    0 on a live tick and follows (tick − last live) / 40 clamped to 1 after."""
    import heads_online as HO
    import train_act as TA
    from count_strata import friend_row
    w, observers, _z = _tuning_world()
    T, n = w["ticks"], len(observers)
    obs = np.asarray(w["obs"][:, observers], np.float32)                         # (T, n, 399)
    heads = HO.OnlineHeads("act15", n)
    cells = np.stack([heads.step(obs[t]) for t in range(T)])                      # (T, n, 4, 14)
    import data_act as D
    import read_act as R
    pairs, X, _ys, _states, _cls = R.world_inputs(w, observers, w["scripted"][0])   # the needy loader's pair_x, every (k, j)
    off = TA.probs_from_x(heads.head, X)[:, :, 0, :]                               # (T, n_pairs, 11)
    worst = 0.0
    for pi, (k, j) in enumerate(pairs):
        i, r = observers.index(k), friend_row(k, j)
        st = D.row_state(X[:, pi])
        live = st != D.SILENT
        d = np.abs(cells[live, i, r, :11] - off[live, pi]).max() if live.any() else 0.0
        worst = max(worst, float(d))
        assert np.array_equal(cells[~live, i, r, :13], np.broadcast_to(heads.prior_cells, ((~live).sum(), 13))), "silent rows do not carry the prior"
        assert np.all(cells[live, i, r, 13] == 0.0), "ticks-since-live not 0 on a live tick"
        tsl = cells[:, i, r, 13]
        last = -1
        for t in range(T):
            if live[t]:
                last = t
            else:
                want = 1.0 if last < 0 else min(1.0, (t - last) / 40.0)
                assert abs(tsl[t] - want) < 1e-6, f"ticks-since-live at t={t}: {tsl[t]} want {want}"
    assert worst < 1e-6, f"online y0 differs from offline by {worst}"


GUARDS = {"g0a": g0a, "g0b": g0b, "g0c": g0c, "g1": g1, "g2": g2}

if __name__ == "__main__":
    names = sys.argv[1:] or [n for n in GUARDS if n != "g0c"]
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
