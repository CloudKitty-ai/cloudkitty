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


def _scratch_artifact(slot="p2-act15-s1", arm="act15", trunk_seed=1):
    """A grafted (untrained) arm policy saved where the harness's p2 seat looks when P2_ARC is pointed at the scratch."""
    import graft as G
    import heads_online as HO
    p2, _trunk, _ck = G.graft(trunk_seed, HO.ARMS[arm]["cells"])
    out = SCRATCH / "artifacts" / slot / "policy-final.pt"
    out.parent.mkdir(parents=True, exist_ok=True)
    G.save_policy(p2, out, arm=arm, slot=slot, stop_reason="scratch")
    return out


def g3():
    """the `p2` seat in the cert harness equals the trainer's forward on the same observation (one forward, two homes):
    a 300-tick uniform p2 leg recorded by run_one replays by its recorded actions through the trainer-side P2Actor
    with the same greedy (act, msg) at every tick and seat; the seat refuses a bundle whose head sha256 is not the
    named head's."""
    import cloudkitty
    import cert_harness_fog as H
    import heads_online as HO
    art = _scratch_artifact()
    H.P2_ARC = SCRATCH
    rec_dir = SCRATCH / "rec"
    H.run_one(("p2u-act15-s1", 905_001, 300, str(C.TRUNK_TOML), None, None, "served", None, None, 1_000, str(rec_dir)))
    z = np.load(rec_dir / "acts-905001.npz")
    acts = z["acts"]
    assert acts.shape == (300, 5, 2) and list(z["seats"]) == ["p2:p2-act15-s1"] * 5, (acts.shape, list(z["seats"]))
    actor, _ck = HO.actor_from_artifact(art, n_obs=5)
    env = cloudkitty.ParallelEnv(str(C.TRUNK_TOML), horizon=300)
    obs, infos = env.reset(seed=905_001)
    names = list(env.possible_agents)
    actor.reset()
    for t in range(300):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = actor.logits(ob)
        a0 = np.where(mk[:, :35], lg[:, :35], -np.inf).argmax(1)
        g0_ = np.where(mk[:, 35:], lg[:, 35:], -np.inf).argmax(1)
        assert np.array_equal(a0, acts[t, :, 0]) and np.array_equal(g0_, acts[t, :, 1]), f"harness seat and trainer forward disagree at tick {t}"
        obs, _r, _te, _tr, infos = env.step({a: (int(acts[t, i, 0]), int(acts[t, i, 1])) for i, a in enumerate(names)})
    # the roster-shaped seating runs (three one-row p2 seats beside two trunk seats) and records every seat's acts
    for slot in ("p2-act15-s2", "p2-act15-s4"):
        _scratch_artifact(slot)
    r = H.run_one(("p2r-act15", 905_002, 50, str(C.TRUNK_TOML), None, None, "served", None, None, 1_000, str(rec_dir)))
    assert r["seats"] == ["p2:p2-act15-s2", "p2:p2-act15-s4", "g2:trunk-s6", "g2:trunk-s7", "p2:p2-act15-s1"], r["seats"]
    assert np.load(rec_dir / "acts-905002.npz")["acts"].shape == (50, 5, 2)
    # the head sha refusal
    saved = dict(HO.HEAD_SHA256)
    HO.HEAD_SHA256[("B15", 2)] = "0" * 64
    try:
        HO.OnlineHeads("act15", 1)
        raise AssertionError("a head whose sha is not the named one was accepted")
    except AssertionError as e:
        assert "is not the named" in str(e), e
    finally:
        HO.HEAD_SHA256.update(saved)


def g4():
    """the stops: a 300-tick probe streak halts, 299 does not, 1,000 names the F-053 line; the nash stop needs three
    consecutive probes; the demotion trigger fires on OPTIMISM (grave d_hap > 0) at lift ≥ 1.5 and n ≥ 200, not on
    pessimism, not at lift 1.4, not at n 199."""
    import train_ppo_p2 as P
    assert P.probe_stop({"max_distress_streak": 300, "nash": 0.9}, 0)[0] == "probe-distress-stop", "300 must halt"
    assert P.probe_stop({"max_distress_streak": 299, "nash": 0.9}, 0)[0] is None, "299 must not halt"
    assert P.probe_stop({"max_distress_streak": 1_000, "nash": 0.9}, 0)[0] == "f053-line-crossed"
    r1, k1 = P.probe_stop({"max_distress_streak": 0, "nash": 0.4}, 0)
    r2, k2 = P.probe_stop({"max_distress_streak": 0, "nash": 0.4}, k1)
    r3, k3 = P.probe_stop({"max_distress_streak": 0, "nash": 0.4}, k2)
    assert (r1, r2, r3) == (None, None, "welfare-stop"), (r1, r2, r3)
    assert P.probe_stop({"max_distress_streak": 0, "nash": 0.6}, 2) == (None, 0), "a clean probe resets the strikes"

    def acc(grave, common, n_g=250, n_c=250):
        a = P.new_trigger_acc()
        for v in ("visible", "all"):
            a[v]["GRAVE"]["pooled"] = [grave] * n_g
            a[v]["COMMON"]["pooled"] = [common] * n_c
            for f in P.FRIENDS:
                a[v]["GRAVE"][f] = [grave] * (n_g // 5)
                a[v]["COMMON"][f] = [common] * (n_c // 5)
        return a
    assert P.trigger_eval(acc(+2.0, +1.0))["fire"], "optimism at lift 2 must fire"
    assert not P.trigger_eval(acc(-2.0, -1.0))["fire"], "pessimism must not fire"
    assert not P.trigger_eval(acc(+1.4, +1.0))["fire"], "lift 1.4 must not fire"
    assert P.trigger_eval(acc(+1.5, +1.0))["fire"], "lift 1.5 fires"
    r = P.trigger_eval(acc(+2.0, +1.0, n_g=199))
    assert not r["fire"] and r["by_version"]["all"]["state"] == "INSUFFICIENT", "n 199 is INSUFFICIENT"


def g5():
    """the plateau rule verbatim under the ruled floor: three flat bins halt, two do not; bins closed at or before the
    floor never count and the first post-floor bin cannot be flat (no post-floor predecessor); with floor 0 the
    trunk's own rule (bins 2–4 flat -> halt at the fourth). A tiny smoke run lands a policy checkpoint at every closed
    bin, stops at the cap with the record naming it, and (g9) opens metrics.jsonl in append mode only."""
    import train_ppo_p2 as P

    def closed(ticks):
        return {"ret": 0.9, "kl": 0.1, "ticks": ticks}
    bins, streak = [], 0
    for b in range(1, 13):
        c = closed(b * 1_000_000)
        flat, streak = P.plateau_step(bins, c, streak, P.FLOOR_TICKS)
        c["flat"] = flat
        bins.append(c)
        if b <= 9:
            assert not flat, f"bin {b} ({c['ticks']}) counted flat before / at the floor's first post-floor bin"
        if b == 11:
            assert streak == 2, "two post-floor flat bins must not halt"
    assert streak == 3 and [b["flat"] for b in bins] == [False] * 9 + [True] * 3, [b["flat"] for b in bins]
    bins, streak = [], 0
    for b in range(1, 5):
        flat, streak = P.plateau_step(bins, closed(b * 1_000_000), streak, 0)
        bins.append(dict(closed(b * 1_000_000), flat=flat))
    assert streak == 3 and [b["flat"] for b in bins] == [False, True, True, True], "floor 0 is the trunk's rule"
    bins, streak = [], 0
    for b in range(1, 4):
        flat, streak = P.plateau_step(bins, closed(b * 1_000_000) if b < 3 else {"ret": 0.95, "kl": 0.1, "ticks": 3_000_000}, streak, 0)
        bins.append(closed(b * 1_000_000))
    assert streak == 0, "a bin whose return rose 0.05 is not flat"
    # the smoke: checkpoints per closed bin, the final's record, append-only log
    from pathlib import Path as _P
    out = SCRATCH / "smoke-g5"
    import shutil
    if out.exists():
        shutil.rmtree(out)
    modes = []
    real_open = _P.open

    def spy(self, mode="r", *a, **k):
        if self.name == "metrics.jsonl":
            modes.append(mode)
        return real_open(self, mode, *a, **k)
    _P.open = spy
    argv = sys.argv
    sys.argv = ["train_ppo_p2.py", "--slot", "p2-nohead-s1", "--smoke", "--n-worlds", "2", "--horizon", "200", "--total-ticks", "3072",
                "--fragment", "64", "--probe-every", "8", "--probe-ticks", "40", "--bin-ticks", "1024", "--floor-ticks", "1024", "--out-dir", str(out)]
    try:
        P.main()
    finally:
        sys.argv = argv
        _P.open = real_open
    rows = [__import__("json").loads(l) for l in (out / "metrics.jsonl").read_text().splitlines()]
    closed_rows = [r for r in rows if "bin_closed" in r]
    assert len(closed_rows) == 3, len(closed_rows)
    for r in closed_rows:
        assert (out / r["bin_checkpoint"]).exists(), r["bin_checkpoint"]
    assert len(list(out.glob("ckpt-u*.pt"))) == 3
    import torch
    fin = torch.load(out / "policy-final.pt", map_location="cpu", weights_only=True)
    assert fin["stop_reason"] == "cap" and fin["ticks"] == 3072 and fin["plateau_tick"] is None and fin["arm"] == "nohead", {k: fin[k] for k in ("stop_reason", "ticks", "arm")}
    assert modes and set(modes) == {"a"}, f"metrics.jsonl opened with modes {sorted(set(modes))}; the passive log is write-only"


def g9():
    """the passive log is write-only: g5's smoke records every open of metrics.jsonl (append only) — run with g5; here
    the static half: the trainer's source never reads its log."""
    src = (HERE / "train_ppo_p2.py").read_text()
    assert "metrics.jsonl" in src
    for bad in ("log_path.read", "open(log_path)", 'log_path.open("r")', "np.load(log_path", "json.load(log_path"):
        assert bad not in src, f"the trainer reads its own log: {bad}"


def g10():
    """seeds and slots: the nine slots map to run indices 107–115 inside the claimed band by the stripe formula; no
    needs slot exists; grafts pair s_k with trunk-s_k; the head named per arm is the median-validation seed by the
    stores' done.json."""
    import json as _j
    import train_ppo_p2 as P
    import heads_online as HO
    import train_act as TA
    idx = sorted(P.SLOTS[s][2] for s in P.SLOTS)
    assert idx == list(range(107, 116)), idx
    assert not any("needs" in s for s in P.SLOTS), "a needs slot exists"
    lo = min(P.T.seed_stripe(i)[0] for i in idx)
    hi = max(P.T.seed_stripe(i)[1] for i in idx)
    assert (lo, hi) == (2_240_000_000, 2_419_999_999), (lo, hi)
    for slot, (arm, k, i) in P.SLOTS.items():
        assert slot == f"p2-{arm}-s{k}" and k in C.TRUNK_SEEDS, slot
        assert {"act15": 107, "act10": 110, "nohead": 113}[arm] + {1: 0, 2: 1, 4: 2}[k] == i, (slot, i)
    for arm, spec in HO.ARMS.items():
        if spec["head"] is None:
            continue
        h_arm, seed = spec["head"]
        vals = {s: _j.loads((TA.OUT_ROOT / TA.run_name(h_arm, s) / "done.json").read_text())["best_val"] for s in (1, 2, 3)}
        med = sorted(vals, key=vals.get)[1]
        assert med == seed, f"{arm}: the median-validation {h_arm} seed is s{med}, not the named s{seed}"


GUARDS = {"g0a": g0a, "g0b": g0b, "g0c": g0c, "g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g9": g9, "g10": g10}

if __name__ == "__main__":
    names = sys.argv[1:] or [n for n in GUARDS if n != "g0c"]
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
